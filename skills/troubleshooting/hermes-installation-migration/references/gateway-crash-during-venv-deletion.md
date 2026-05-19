# Gateway Crash During Venv Deletion — Incident Report

## Timeline

```
T+0s   rm -rf /home/agentuser/.hermes/
       (This deleted the venv that the running gateway was using)

T+0s   Gateway process crashes — Python can't load modules from deleted directory
       PID 3792842 dies silently

T+3s   systemd/auto-restart kicks in → gateway starts from fallback venv /root/hermes-venv/
       First attempt: FAIL — "websockets not installed; websocket mode unavailable"

T+12s  auto-restart → second attempt: SUCCESS
       Feishu WebSocket connected, messages start flowing again

T+16s  User's next message received and processed normally

Total outage: ~12 seconds
```

## Root Cause

The gateway process (PID 3792842) was running from:

```
/home/agentuser/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main gateway run --replace
```

When `rm -rf /home/agentuser/.hermes/` executed, the Python interpreter's executable, shared libraries, and module search paths all resided under that now-deleted directory tree. The process died immediately.

## Detection

**Before deletion — check what the gateway is running from:**

```bash
ls -la /proc/$(ps aux | grep "gateway" | grep -v grep | awk '{print $2}')/exe
# lrwxrwxrwx ... /home/agentuser/.hermes/hermes-agent/venv/bin/python
#                                     ^^^^^^^^^^^^^^^^^^^^^^^^
#                                   This path = source of crash risk
```

**After accidental deletion — confirm crash + recovery:**

```bash
# Check logs
grep -E "ERROR|Shutdown|start|connected" /root/.hermes/logs/gateway.log | tail -20

# Look for:
# "Shutdown phase: notify_active_sessions" → clean exit (not a crash)
# No shutdown log + process gone = crash
# "Failed to connect: websockets not installed" → fallback venv issue
# "Connected in websocket mode" → recovery successful

# Check for fallback venv
ls /root/hermes-venv/bin/python 2>/dev/null && echo "fallback exists"
```

## Recovery Steps (if still down)

```bash
# 1. Identify which venv is now running
ps aux | grep "gateway"
readlink -f /proc/<NEW_PID>/exe

# 2. Fix missing packages in fallback venv
/root/hermes-venv/bin/pip install websockets certifi

# 3. Restart gateway
systemctl restart hermes-gateway 2>/dev/null || \
  pkill -f "gateway run" && sleep 1 && \
  /root/hermes-venv/bin/python -m hermes_cli.main gateway run --replace

# 4. Verify Feishu connection
tail -f /root/.hermes/logs/gateway.log | grep -E "Connected|connected|error|ERROR"
```

## Prevention

1. **Always check `readlink -f /proc/<GW_PID>/exe` before deleting any user home that contains a Hermes installation.**
2. If the gateway uses the target user's venv, either:
   - Stop the gateway first: `kill <GW_PID> && sleep 2`
   - Or verify the target user has `hermes` installed with a working venv
3. Keep a backup venv at `/root/hermes-venv/` (or similar) as fallback.
4. After migration, test with a real message before declaring success.
