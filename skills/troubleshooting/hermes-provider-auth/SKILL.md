---
name: hermes-provider-auth
title: Hermes Provider Authentication Troubleshooting
description: Diagnose and fix "No inference provider configured" and other provider auth failures in Hermes Agent.
category: troubleshooting
triggers:
  - user reports "No inference provider configured" error
  - user reports "Provider authentication failed" in gateway
  - API key exists in .env but provider not recognized
  - running `hermes doctor` shows unconfigured provider despite valid .env
---

# Hermes Provider Authentication Troubleshooting

## Full Provider Resolution Chain

When a user configures `model.provider: deepseek` in config.yaml, Hermes follows this path:

```
resolve_runtime_provider()                          # runtime_provider.py:954
  ├─ resolve_requested_provider()                   # reads model.provider from config
  ├─ _resolve_named_custom_runtime()                # checks if it's a custom provider → NO
  ├─ resolve_provider()                             # auth.py:1344 → checks PROVIDER_REGISTRY
  ├─ _resolve_explicit_runtime()                    # no explicit key/url → None
  ├─ credential pool check                          # load_pool(provider) → None
  ├─ (skips: nous, openai-codex, qwen, minimax,)
  │  (gemini-cli, copilot-acp, anthropic, bedrock)  # not deepseek
  └─ generic API-key handler                        # runtime_provider.py:1336
       └─ resolve_api_key_provider_credentials()    # auth.py:4125
            └─ _resolve_api_key_provider_secret()   # auth.py:537
                 └─ get_env_value("DEEPSEEK_API_KEY")  # config.py:4741
                      ├─ os.environ check (fast path)
                      └─ load_env() → reads .env directly
```

### Why "No inference provider configured" fires

The error comes from `resolve_provider()` (auth.py:1468) — its **auto-detection fallback** at lines 1440-1457 iterates `PROVIDER_REGISTRY` checking `has_usable_secret(os.getenv(env_var, ""))`. This uses `os.getenv()` which reads `os.environ` only. If the .env wasn't loaded into `os.environ`, auto-detection fails *even though*:

1. The provider IS explicitly configured in config.yaml (`model.provider: deepseek`)
2. Later in `resolve_runtime_provider()`, the generic API-key handler at line 1336 uses `resolve_api_key_provider_credentials()` which calls `get_env_value()` — **this CAN read the .env file directly** and does NOT depend on `os.environ`

**The error fires when `resolve_requested_provider()` fails** (config.yaml doesn't have `model.provider`, or it's set to `"auto"`) and `resolve_provider()` falls through to auto-detection.

### Diagnostic hierarchy

1. If `model.provider` IS set in config.yaml → check `resolve_api_key_provider_credentials()` directly
2. If `model.provider` is NOT set (or `"auto"`) → check `os.environ` for the relevant env var
3. Either way → check `get_env_value()` which verifies the .env file is readable

## Architecture: Two Credential Resolution Paths

Hermes has **two separate code paths** for reading API keys, and knowing which one is in play is the key to debugging:

| Path | Function | Checks | Used by |
|------|----------|--------|---------|
| Process env | `os.getenv("VARIABLE")` | `os.environ` dict only | `resolve_provider()` auto-detection, `_resolve_explicit_runtime()`, `_resolve_named_custom_runtime()` |
| .env direct | `get_env_value("VARIABLE")` | `os.environ` first, then reads `~/.hermes/.env` via `load_env()` | `resolve_api_key_provider_credentials()` → `_resolve_api_key_provider_secret()` |

### Critical implication

The **auto-detection** in `resolve_provider()` (auth.py ~line 1440-1457) uses `os.getenv()` — it iterates `PROVIDER_REGISTRY` checking `has_usable_secret(os.getenv(env_var))`. If the .env wasn't loaded into `os.environ`, auto-detection fails even though the key is present in the file.

However, once a provider is *explicitly configured* in config.yaml (e.g. `model.provider: deepseek`), the runtime resolution falls through to `resolve_api_key_provider_credentials()` which uses `get_env_value()` — **this path CAN read the .env file directly** and works even when `os.environ` is empty.

## Diagnostic Steps

### 1. Check if the env var is in the process environment

```bash
python3 -c "import os; print('KEY' in os.environ, os.environ.get('KEY', 'NOT SET')[:8])"
```

### 2. Check if `load_env()` can read it from the .env file

```bash
python3 -c "
import sys; sys.path.insert(0, '.../site-packages')
from hermes_cli.config import load_env, invalidate_env_cache
invalidate_env_cache(); env = load_env()
v = env.get('DEEPSEEK_API_KEY', '')
print(f'key_len={len(v)} start={v[:5] if v else \"EMPTY\"}')"
```

### 3. Check if `get_env_value()` resolves it

```bash
python3 -c "
import sys; sys.path.insert(0, '.../site-packages')
from hermes_cli.config import get_env_value
v = get_env_value('DEEPSEEK_API_KEY')
print(f'resolved: {bool(v)} len={len(v) if v else 0}')"
```

### 4. Trace the full auth resolution for a provider

```bash
python3 -c "
import sys; sys.path.insert(0, '.../site-packages')
from hermes_cli.auth import resolve_api_key_provider_credentials
creds = resolve_api_key_provider_credentials('deepseek')
print(f'OK: key={creds[\"api_key\"][:8]}... url={creds[\"base_url\"]}')"
```

### 5. Test full runtime resolution

```bash
python3 -c "
import sys; sys.path.insert(0, '.../site-packages')
from hermes_cli.runtime_provider import resolve_runtime_provider
r = resolve_runtime_provider(requested='deepseek')
print(f'OK: provider={r[\"provider\"]} key={r[\"api_key\"][:8]}...')"
```

## Root Causes and Fixes

> **OpenRouter 配置参考**：见 `references/openrouter-setup.md` — 包含模型选择、手动 config.yaml 配置、结合 SkillClaw 使用的注意事项。

### Cause A: .env not loaded into os.environ (most common)

**Fix — export in shell profile:**
```bash
echo 'export DEEPSEEK_API_KEY="sk-..."' >> ~/.bashrc
source ~/.bashrc
```

**Fix — reload .env manually:**
```python
from dotenv import load_dotenv; import os
load_dotenv(os.path.expanduser("~/.hermes/.env"), override=True)
```

### Cause B: .env file corruption / encoding issues

The `_sanitize_env_lines()` function (in `hermes_cli/config.py`) is called by `_sanitize_env_file_if_needed()` before `load_dotenv()` runs. It looks for multiple known KEY= patterns on one line (concatenation corruption). If the .env file has subtle encoding issues (BOM, mixed line endings, non-ASCII whitespace), the sanitization can produce mangled values or the `load_dotenv()` call can silently return without loading any variables.

**Diagnostic:**
```bash
xxd ~/.hermes/.env   # Verify each KEY=VALUE is on its own line (terminated by 0a)
                      # Check there's no BOM (EF BB BF) at the start
```

**Fix — rewrite .env with clean UTF-8 from Python:**
```python
from pathlib import Path
env_path = Path.home() / ".hermes" / ".env"
env_vars = {
    "DEEPSEEK_API_KEY": "sk-...",
    # ... all other vars
}
with open(env_path, "w", encoding="utf-8") as f:
    for k, v in env_vars.items():
        f.write(f"{k}={v}\n")
import os; os.chmod(env_path, 0o600)
```

Then restart the gateway. The rewrite eliminates any hidden BOM, encoding artifact, or sanitizer corruption.

### Cause C: .env file with stale `***` placeholder

Incomplete setup runs can leave `KEY=***` entries in .env. Unlike `has_usable_secret()` which filters `***` as a placeholder, `get_env_value()` returns the raw value — so if `DEEPSEEK_API_KEY=***` ended up in the file, the credential resolves to a 3-char `***` string that the API server rejects.

**Fix:** Delete the `***` line and replace with the real key, or rewrite the entire .env from a clean template.

### Cause D: Provider not in PROVIDER_REGISTRY

Add to config.yaml with explicit `base_url` or use the `custom` provider type.

## Pitfalls

- `cat ~/.hermes/.env` may show `***` due to terminal-tool redaction — use `xxd` for raw bytes.
- `execute_code()` / `terminal()` run in subprocesses — they inherit the agent's `os.environ`. If the agent lacks the var, so do they.
- `load_env()` caches by (path, mtime, size). Call `invalidate_env_cache()` after editing .env.
- The auto-detection loop skips `copilot` and `lmstudio` even if keys are present.
- The error "⚠️ Provider authentication failed: {exc}" in gateway means `_resolve_session_agent_runtime()` caught an exception; check if `_reload_runtime_env_preserving_config_authority()` actually populated `os.environ`.
- **Redundant gateway processes** can hold stale file handles or lock files, causing the current gateway to fail reading .env or credentials. If a user has been running multiple `hermes gateway` sessions, check with `ps aux | grep gateway` and kill old/stale instances with `kill <PID>` (or `kill -9` if SIGTERM doesn't work).
- **`.env` rewriting is a valid fix** — when encoding corruption or sanitization issues prevent `load_dotenv()` from loading variables, rewriting the entire .env via Python `open(path, "w", encoding="utf-8")` eliminates the problem. This is not just a diagnostic step, it's a repair procedure.
- **"No inference provider configured" vs "credential resolved"** — these come from different code paths. The `resolve_provider()` auto-detection (auth.py ~1440) uses `os.getenv()` and can fail even when `resolve_api_key_provider_credentials()` (which uses `get_env_value()/.env direct`) succeeds. If config.yaml explicitly sets `model.provider`, the credential path works; the error comes from the auto-detection fallback at runtime_provider.py:1017.
