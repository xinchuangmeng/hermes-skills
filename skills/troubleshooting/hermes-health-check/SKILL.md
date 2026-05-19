---
name: hermes-health-check
title: Hermes Agent Comprehensive Health Check
description: Run a multi-dimensional health check on a remote Hermes Agent installation — config files, processes, system resources, API connectivity, and gateway status.
category: troubleshooting
triggers:
  - user reports "Hermes is not working" or "something's wrong with Hermes"
  - user asks for a general health check of the Hermes setup
  - before debugging a specific issue, to establish baseline
  - after troubleshooting steps, to verify fixes
---

# Hermes Agent Comprehensive Health Check

## Overview

When a user reports problems with Hermes Agent, run a **5-dimension health check** before diving into specific debugging. This establishes baseline and often reveals the root cause directly.

Use `delegate_task` with parallel tasks for speed — the 5 checks are independent and can run concurrently (up to 3 at a time).

## The 6 Dimensions

### 1. Config File Integrity
Check `~/.hermes/` directory structure:
- `.env` — API keys present, correct format (use `xxd` for raw bytes, not `cat` — terminal redacts secrets)
- `config.yaml` — provider, model, base_url settings; check `_config_version`
- `auth.json` — valid JSON, credential source (env: vs pool:)
- Permissions should be `600` for secret files

Check for:
- `.tirith-install-failed` marker file (indicates failed security tool install)
- Stale `.lock` files (from old gateway instances)
- `errors.log` for repeated warning patterns

### 2. Process & Service State
```bash
ps aux | grep -E "hermes|python.*gateway" | grep -v grep
```

Check for:
- **Redundant gateway instances**
### Gateway Process Cleanup

⚠️ **CRITICAL: Stop gateways before deleting old venvs.** A running gateway crashes silently when its Python venv directory is deleted. Use `kill <PID>` (SIGTERM first) before removing old installations.

When multiple gateway instances accumulate (e.g., after server migration or --replace restarts):

```bash
# List all Hermes-related Python processes
ps aux | grep -E "hermes|python.*gateway" | grep -v grep

# Identify the correct gateway to keep (usually the one with --replace or the systemd service)
# Kill redundant ones gracefully first:
kill <PID>

# If graceful kill doesn't work within 5 seconds:
kill -9 <PID>

# Verify cleanup
ps aux | grep gateway | grep -v grep
```

Common sources of redundant gateways:
- Old `agentuser` processes persisting after migration to `root`
- `hermes gateway run` started multiple times without `--replace`
- Previous installation's gateway not cleaned up before restart
- Profile-specific gateways (`--profile <name>`) that are no longer needed

### ⚠️ systemd KillMode 导致后台进程被连带杀

**症状：** 网关运行正常，但之前用 `terminal(background=true)` 启动的服务（如Gradio 9527）端口不再监听。

**根因：** systemd 默认 `KillMode=mixed` 会在网关重启时 SIGKILL 所有子进程，包括后台Python应用。

**排查：**
```bash
journalctl --user -u hermes-gateway.service | grep "Killing process"
# 会看到类似：
# Killing process 4144659 (python3) with signal SIGKILL.
```

**修复：**
```bash
# 编辑服务文件
sed -i 's/KillMode=mixed/KillMode=process/' ~/.config/systemd/user/hermes-gateway.service
systemctl --user daemon-reload
# KillMode=process 只杀主进程，不杀子进程
# 不需要重启网关，下次systemd触发重启时自动生效
```

Gateway launched with `--replace` flag will auto-restart if it crashes. However, the restart may use a **different Python venv** than the original:

```bash
# Find the actual running gateway's Python binary
ls -la /proc/$(pgrep -f "gateway.*run" | head -1)/exe
```

If the original venv was deleted, the restart may pick up a backup venv (e.g., `/root/hermes-venv/` instead of `/home/agentuser/.hermes/hermes-agent/venv/`). After any venv-deletion event, verify the new environment:

```bash
# Check the new venv is complete
/root/hermes-venv/bin/python3 -c "
import importlib
for pkg in ['websockets', 'lark_oapi', 'openai', 'httpx', 'certifi']:
    try:
        importlib.import_module(pkg.replace('-','_'))
        print(f'  ✅ {pkg}')
    except ImportError:
        print(f'  ❌ {pkg}')
"
```

Key packages for Feishu gateway:
- **`websockets`** — REQUIRED for Feishu WebSocket mode. Without it, `[Feishu] Failed to connect: websockets not installed; websocket mode unavailable`
- **`certifi`** — TLS CA certificate bundle. If the old venv's certifi path is hardcoded somewhere, deleting that venv causes: `Could not find a suitable TLS CA certificate bundle, invalid path: ...certifi/cacert.pem`

Fix missing packages:
```bash
/root/hermes-venv/bin/pip install websockets certifi -q
```

### 3. System Resources
```bash
uname -a              # OS / kernel
uptime                # how long running + load
free -h               # memory (check available, not just free)
df -h /               # disk space (< 80% is fine)
nproc                 # CPU core count
```

Key thresholds:
- Memory available < 20% → resource pressure
- Disk usage > 80% → space warning
- Load average > CPU count → overload

### 4. API Connectivity
Test the inference provider directly:

```bash
# DeepSeek example
curl -s -w "\nHTTP %{http_code} | Total %{time_total}s | TTFB %{time_starttransfer}s\n" \
  https://api.deepseek.com/v1/models \
  -H "Authorization: Bearer $(python3 -c 'from hermes_cli.config import get_env_value; print(get_env_value("DEEPSEEK_API_KEY"))')"

# Check DNS
getent hosts api.deepseek.com
# Check SSL
openssl s_client -connect api.deepseek.com:443 -servername api.deepseek.com < /dev/null 2>/dev/null | openssl x509 -noout -dates
```

For OpenRouter:
```bash
curl -s https://openrouter.ai/api/v1/models -H "Authorization: Bearer $OPENROUTER_API_KEY" | head -5
```

### 5. Gateway Status
```bash
# Feishu gateway
cat ~/.hermes/gateway_state.json    # shows Feishu connection state
tail -50 ~/.hermes/gateway.log      # recent message processing
tail -50 ~/.hermes/agent.log        # recent API calls
tail -20 ~/.hermes/errors.log       # warning/error patterns
```

Check gateway_state.json for:
- `"status": "running"` — gateway alive
- `"feishu": "connected"` — Feishu websocket active
- Recent `last_seen` timestamp

### 6. TiRith Security Tool

```bash
which tirith                # check if installed
pip3 install tirith          # install if missing
rm -f ~/.hermes/.tirith-install-failed  # clear failed marker if exists
```

Check config.yaml for `tirith_path: tirith` (default — find via PATH). If `tirith_fail_open: true` (default), TiRith failures are logged but non-blocking.

Common TiRith issues:
- **Not installed** → `pip3 install tirith` (installs tirith, autobahn, cbor2, etc.)
- **Install failed marker** → `~/.hermes/.tirith-install-failed` file exists. Remove it after successful install.
- **WAMP connection error** → `tirith --version` tries to connect to a WAMP monitoring server. This is expected to fail in server environments — it does NOT affect Hermes functionality.

## Execution Pattern

Use `delegate_task()` with up to 3 parallel tasks. The 4th-5th check runs in a second batch:

```python
# Batch 1: config files + processes + system
delegate_task(tasks=[
    {"goal": "check ~/.hermes/ config files", "toolsets": ["terminal", "file"]},
    {"goal": "check Hermes processes", "toolsets": ["terminal"]},
    {"goal": "check system resources", "toolsets": ["terminal"]},
])

# Batch 2: API + gateway
delegate_task(tasks=[
    {"goal": "test API connectivity", "toolsets": ["terminal", "web"]},
    {"goal": "check gateway status", "toolsets": ["terminal"]},
])
```

## Pitfalls

- `cat ~/.hermes/.env` output is redacted (secrets shown as `***`). Use `xxd` to verify raw content, or `python3 -c "from hermes_cli.config import get_env_value; print(get_env_value('DEEPSEEK_API_KEY')[:5])"` to verify key presence.
- `delegate_task` max_concurrent_children defaults to 3. If you have 4+ tasks, batch them or increase the limit in config.yaml.
- Checking `os.environ` in terminal()/execute_code() subprocesses shows the CHILD'S environment, not the parent Hermes process. To check the parent, look at `/proc/$PPID/environ`.
- After killing redundant gateways, the remaining gateway may need a restart to release lock files.
- `.env` encoding issues (BOM, mixed line endings) can cause `load_dotenv()` to silently fail. Rewrite the file with clean Python UTF-8 as a definitive fix.
- **Sync → verify → delete**: When migrating Hermes data between users/environments, always verify byte-for-byte that all files are synced before deleting the old location. The user explicitly requires this workflow.
- **Stop gateways before deleting their venv**: A running Hermes gateway crashes silently if its Python venv is deleted from under it. The process disappears with no log entry. Always kill the gateway first, or ensure the new gateway is running from a different venv.

## Reference Files

- `references/gateway-venv-deletion-crash.md` — Full timeline and root cause of gateway crash when the Hermes venv is deleted under a running process. Includes prevention checklist and post-migration verification steps.
