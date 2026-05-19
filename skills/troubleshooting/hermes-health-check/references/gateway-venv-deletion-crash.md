# Gateway Venv Deletion Crash — Root Cause & Recovery

## Timeline (2026-05-17)

```
02:41:35  rm -rf /home/agentuser/.hermes/  ← includes the running venv
         → old gateway (PID 3792842) crashes silently
         → Python process simply disappears — no error log, no cleanup

02:41:38  systemd (or --replace watchdog) auto-restarts gateway
         → but now runs from /root/hermes-venv/bin/python instead of
           /home/agentuser/.hermes/hermes-agent/venv/bin/python

02:41:50  First restart attempt:
         → Feishu connection fails: "websockets not installed"
         → Old venv had websockets; /root/hermes-venv/ did not

02:41:59  Second restart attempt (scheduler retries):
         → Feishu WebSocket connects successfully
         → Gateway fully operational

02:42:04  User's "在吗？" received and processed normally
```

## Root Cause

The running gateway (PID 3792842) was using:
```
/home/agentuser/.hermes/hermes-agent/venv/bin/python
```

When `rm -rf /home/agentuser/.hermes/` was executed, it deleted:
- The Python interpreter the process was using
- All `.so` shared libraries currently loaded by the process
- The `site-packages/` directory from which modules were being imported

Python cannot survive losing its own executable and loaded modules. The process crashes immediately with no time to write a shutdown log or notify systemd.

## Recovery

The gateway was launched with `--replace` flag, which is handled by `hermes_cli.main gateway run --replace`. The `--replace` flag:
1. Checks for an existing gateway PID
2. Kills the old process (or detects it's dead)
3. Starts a new gateway in the current Python environment

In this case, systemd (or the process supervisor) detected the crash and restarted. The new process ran from whichever `python` was first in PATH — in this case `/root/hermes-venv/bin/python`.

## Post-Migration Verification Checklist

After deleting an old Hermes installation (venv + all):

1. **Verify the running gateway's Python binary**:
   ```bash
   ls -la /proc/$(pgrep -f "gateway.*run" | head -1)/exe
   ```

2. **Check for critical missing packages**:
   ```bash
   for pkg in websockets lark_oapi openai httpx certifi; do
     python3 -c "import $pkg" 2>/dev/null && echo "✅ $pkg" || echo "❌ $pkg"
   done
   ```

3. **Verify SSL/TLS certs**:
   ```bash
   python3 -c "
   import ssl, certifi
   ctx = ssl.create_default_context(cafile=certifi.where())
   import urllib.request
   r = urllib.request.urlopen('https://open.feishu.cn', context=ctx, timeout=5)
   print(f'SSL OK: {r.status}')
   "
   ```

4. **Check gateway_state.json**:
   ```bash
   cat ~/.hermes/gateway_state.json  # should show running + connected
   ```

5. **Check gateway.log for recent errors**:
   ```bash
   grep -E "ERROR|CRITICAL" ~/.hermes/logs/gateway.log | tail -5
   ```

## Prevention — Proper Migration Workflow

Before deleting an old Hermes venv or home directory, follow this **sync → verify → delete** sequence:

1. **Sync**: Copy all useful data from old location to new (skills, cron jobs, scripts, profiles, memories, SOUL.md, config files)
2. **Verify**: Confirm byte-for-byte that everything is in place:
   ```bash
   diff <(find /old/.hermes/skills -name "SKILL.md" -printf '%P\n' | sort) \
        <(find ~/.hermes/skills -name "SKILL.md" -printf '%P\n' | sort)
   ```
3. **Delete only after full verification**: Only then clean up the old location

⚠️ **Do NOT skip the verify step — always check before deleting.** The user explicitly requires this workflow: "先把...同步到现在的服务器后检查一遍已经完全同步后再删" (sync to new server → verify completeness → delete old).
