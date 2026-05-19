# Debug Trace: DeepSeek "No inference provider configured"

## Symptom
User messages (Feishu gateway) returned: `⚠️ Provider authentication failed: No inference provider configured`

Config had:
```yaml
model:
  default: deepseek-reasoner
  provider: deepseek
  base_url: https://api.deepseek.com/v1
```

`.env` file had `DEEPSEEK_API_KEY=YOUR_DEEPSEEK_KEY`

## Full Provider Resolution Chain

This is the code path Hermes follows when `model.provider: deepseek` is set in config.yaml:

### Step 1: resolve_requested_provider()
`runtime_provider.py:350` — reads `model.provider` from config.yaml → returns `"deepseek"`

### Step 2: _resolve_named_custom_runtime("deepseek")
`runtime_provider.py:1008` — calls `_get_named_custom_provider("deepseek")` which calls `auth_mod.resolve_provider("deepseek")` to check if it's a built-in provider. Since "deepseek" is in `PROVIDER_REGISTRY` (auth.py:309), this returns None (not a custom provider).

### Step 3: resolve_provider("deepseek")
`runtime_provider.py:1017` — calls `auth.resolve_provider("deepseek")` (auth.py:1344):
- Normalizes: "deepseek"
- Not an alias, not "openrouter", not "custom"
- Found in PROVIDER_REGISTRY → returns "deepseek"

### Step 4: _resolve_explicit_runtime(provider="deepseek")
`runtime_provider.py:1023` — no explicit API key or base URL → returns None (line 817)

### Step 5: Credential pool check
`runtime_provider.py:1054` — `load_pool("deepseek")` → returns None (no pool exists)

### Step 6: Special provider handlers
Nous (1090), OpenAI Codex (1113), Qwen (1133), MiniMax OAuth (1151), Google Gemini CLI (1165), Copilot ACP (1185), Anthropic (1199), Bedrock (1266) — none match "deepseek"

### Step 7: Generic API-key handler
**`runtime_provider.py:1336-1388`** — `PROVIDER_REGISTRY.get("deepseek")` finds the deepseek config:
- auth_type is "api_key" → enters this branch
- Calls `resolve_api_key_provider_credentials("deepseek")` (auth.py:4125)
- This calls `_resolve_api_key_provider_secret("deepseek", pconfig)` (auth.py:537)
- Which calls `get_env_value("DEEPSEEK_API_KEY")` (from `hermes_cli.config`)
- `get_env_value()` checks `os.environ` first (not found), then calls `load_env()` which reads `~/.hermes/.env` directly
- **This path CAN find the key even when os.environ is empty**

### Step 8: Return
Returns `{"provider": "deepseek", "api_key": "sk-...", "base_url": "https://api.deepseek.com/v1", ...}`

### Critical Insight
The error *"No inference provider configured"* comes from **step 3** (`resolve_provider()` at runtime_provider.py:1017), which calls `resolve_provider()` in auth.py. That function has an **auto-detection fallback** at line 1440-1457 that iterates `PROVIDER_REGISTRY` checking `has_usable_secret(os.getenv(env_var, ""))`. If `DEEPSEEK_API_KEY` is not in `os.environ`, this auto-detection loop fails even though:

1. The provider IS explicitly configured in config.yaml
2. `resolve_api_key_provider_credentials()` CAN resolve it via `get_env_value()` → `.env` file direct read

**The error comes from the auto-detection fallback, not from credential resolution.** This happens when `resolve_requested_provider()` fails (e.g., `model.provider` missing from config.yaml) and the function falls through to auto-detection.

## Investigation Steps

### 1. Confirmed .env file is valid
`xxd ~/.hermes/.env` showed each KEY=VALUE pair on its own line with `0a` (newline) terminators. The DEEPSEEK_API_KEY value was `YOUR_DEEPSEEK_KEY` (35 chars). The terminal tool redacts secrets — `cat` shows `***` but `xxd` shows the real bytes.

### 2. Confirmed dotenv can load it
```python
from dotenv import load_dotenv, dotenv_values
vals = dotenv_values("/root/.hermes/.env")
load_dotenv("/root/.hermes/.env", override=True)
# Now in os.environ
```

### 3. Confirmed `get_env_value()` works
```python
from hermes_cli.config import load_env, get_env_value, invalidate_env_cache
invalidate_env_cache()
env = load_env()
# get_env_value("DEEPSEEK_API_KEY") returns the key
```

### 4. Identified root cause
`DEEPSEEK_API_KEY` was **NOT** in `os.environ` of the Hermes process or any subprocess. The `load_hermes_dotenv()` calls in `run_agent.py` and `hermes_cli/main.py` were not populating `os.environ`.

Potential contributors:
- `_sanitize_env_file_if_needed()` runs `_sanitize_env_lines()` which can mangle lines if it finds multiple known KEY= patterns
- The `load_dotenv()` call in `_load_dotenv_with_fallback()` could silently fail on encoding issues
- Multiple old gateway processes (PID 70212 running 10+ days, PID 3570427 running 4.5h) may have held stale file handles
- **The `.env` file path resolution** in `load_hermes_dotenv()` uses `Path(hermes_home or os.getenv("HERMES_HOME", Path.home() / ".hermes"))`. If `HERMES_HOME` env var is set and points to a different path, the user .env may be skipped. In `hermes_cli/main.py` line 212, `load_hermes_dotenv(project_env=PROJECT_ROOT / ".env")` is called WITHOUT `hermes_home=`, so it relies on `HERMES_HOME` env or default. If the gateway entry point (`gateway/run.py`) correctly passes `hermes_home=_hermes_home` at line 387, but the initial import from `hermes_cli.main` doesn't, this can cause inconsistent loading.

### 5. Provider resolution flow (detailed)
The `resolve_provider()` auto-detection loop (auth.py:1440-1457) uses `os.getenv()`, which returned empty. However, the configured provider path (`model.provider: deepseek`) causes `resolve_runtime_provider()` to fall through to the generic API-key handler (runtime_provider.py:1336-1388), which calls `resolve_api_key_provider_credentials()` → `_resolve_api_key_provider_secret()` which uses `get_env_value()` — this CAN read the .env directly. The "No provider configured" error comes from the `resolve_provider()` call at runtime_provider.py:1017, not from the credential resolution at line 1336.

### 6. Comprehensive health check
Full diagnosis covered 5 dimensions in parallel via delegate_task:
1. **Config files** — .env, config.yaml, auth.json permissions and contents
2. **Processes** — 3 redundant gateway instances found (2 agentuser, 1 root)
3. **System resources** — 4C/4G VM running Ubuntu, 38% disk used, healthy
4. **API connectivity** — DeepSeek API reachable (24ms connect, 220ms TTFB, SSL valid)
5. **Gateway status** — Feishu websocket connected, messages flowing

## Fix
Two-part fix applied:
1. **Rewrote .env with clean Python UTF-8** — eliminated any hidden encoding/sanitization issues. Used Python script to write all env vars via `open(path, "w", encoding="utf-8")` rather than relying on the sanitization pipeline.
2. **Killed redundant gateway processes** — PIDs 70212 and 3570427 terminated. PID 70212 (agentuser, 10+ days old) required `kill -9`; PID 3570427 (agentuser, 4.5h old) accepted SIGTERM.
3. **Installed TiRith** — `pip3 install tirith` resolved the `tirith spawn failed` warnings in errors.log

## Process Tree
```bash
systemd(1) → systemd(3781119) → python(3792842) → bash(3794808)
```
- 3792842 was the Hermes gateway process (`python -m hermes_cli.main gateway run --replace`)
- DEEPSEEK_API_KEY was absent from `/proc/3792842/environ`
- Two old agentuser gateways (70212, 3570427) were also running

## Legacy System Discovery
The server also hosted a prior installation under user `agentuser` with:
- **299 skills** (across 45 categories, 15MB) — migrated to root's skills dir
- **6 cron jobs** — migrated (daily news, auto-learn collection, learning summary, douyin/视频号 reminders, crossborder study)
- **2706 profile files** (3 profiles including southeast-ecommerce)
- **Memories, SOUL.md, scripts, hooks, pairing data, image/audio cache**
- Full auto-learning system: 7 rounds, 30 topics per round, 3 categories (跨境/AI智能体/短视频)
- **2.3GB total** across `/home/agentuser/.hermes/` and `/tmp/hermes_tmp/` (uploaded tar from old server)

## Key Files Referenced
- `hermes_cli/auth.py` — PROVIDER_REGISTRY (line 309), resolve_provider() (line 1344), has_usable_secret() (line 525), _resolve_api_key_provider_secret() (line 537), resolve_api_key_provider_credentials() (line 4125)
- `hermes_cli/runtime_provider.py` — resolve_requested_provider() (line 350), resolve_runtime_provider() (line 954), _resolve_explicit_runtime() (line 807)
- `hermes_cli/env_loader.py` — load_hermes_dotenv(), _load_dotenv_with_fallback(), _sanitize_env_file_if_needed()
- `hermes_cli/config.py` — get_env_value() (line 4741), load_env() (line 4337), _sanitize_env_lines() (line 4414)
- `gateway/run.py` — _reload_runtime_env_preserving_config_authority() (line 390), _resolve_session_agent_runtime() (line 1815)
