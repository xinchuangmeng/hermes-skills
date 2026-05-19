---
name: hermes-installation-migration
title: Hermes Installation Migration Between Users/Servers
description: Migrate Hermes Agent configuration, skills, cron jobs, scripts, profiles, memories, SOUL.md and other data between users or servers. Covers old->new server transfer, user migration (e.g. agentuser -> root), and partial data sync.
category: troubleshooting
triggers:
  - user migrated Hermes to a new server and lost skills/data
  - skills from old installation not visible in new session
  - multiple Hermes installations on same machine with different users
  - uploaded backup but no skills appeared
  - "uploaded X GB from old server but nothing is here"
---

# Hermes Installation Migration Between Users/Servers

## Overview

When moving Hermes Agent between users (e.g., `agentuser` → `root`) or between servers, the following data needs to be migrated. Not all of it is obvious.

## Complete Data Inventory

| # | Item | Path | Typical Size | Critical? |
|---|------|------|-------------|-----------|
| 1 | **Skills** | `~/.hermes/skills/` | 5-50MB | ✅ Yes |
| 2 | **Cron jobs** | `~/.hermes/cron/jobs.json` | ~50KB | ✅ Yes |
| 3 | **Scripts** | `~/.hermes/scripts/` | 10-100KB | ✅ Yes |
| 4 | **Profiles** | `~/.hermes/profiles/` | 1-50MB | ✅ Yes |
| 5 | **Memories** | `~/.hermes/memories/MEMORY.md` + `USER.md` | 1-100KB | ✅ Yes |
| 6 | **SOUL.md** | `~/.hermes/SOUL.md` | ~1KB | ✅ Yes |
| 7 | **Config** | `~/.hermes/config.yaml` | ~10KB | ✅ Yes |
| 8 | **Auth state** | `~/.hermes/auth.json` | ~1KB | ✅ Yes |
| 9 | **Pairing data** | `~/.hermes/pairing/` | ~1KB | ⚠️ Maybe |
| 10 | **Pastes** | `~/.hermes/pastes/` | ~10KB | ⚠️ Maybe |
| 11 | **Image cache** | `~/.hermes/image_cache/` | 1-10MB | ❌ Optional |
| 12 | **Audio cache** | `~/.hermes/audio_cache/` | 1-10MB | ❌ Optional |
| 13 | **Bin** | `~/.hermes/bin/` | 5-50MB | ⚠️ Maybe |
| 14 | **Migration data** | `~/.hermes/migration/` | ~10KB | ⚠️ Maybe |
| 15 | **Hooks** | `~/.hermes/hooks/` | ~1KB | ⚠️ Maybe |
| 16 | **Sessions** | `~/.hermes/sessions/` | 50-500MB | ❌ Skip (user-local SQLite) |
| 17 | **Checkpoints** | `~/.hermes/checkpoints/` | 1-50MB | ❌ Skip (session-specific) |
| 18 | **Hermes code** | `~/.hermes/hermes-agent/` | 1-2GB | ❌ Skip (reinstall instead) |
| 19 | **Temporary files** | `.clean_shutdown`, `.update_check`, `search_results_tmp.md`, `.hermes_history` | ~10KB | ❌ Skip (transient) |
| 20 | **Lock files** | `config.yaml.lock`, `auth.lock`, `gateway.lock` | 0-200B | ❌ Skip (regenerated) |

## Migration Steps

### Step 1: Assess what exists at the source

```bash
# Source user (old)
su - agentuser
du -sh ~/.hermes/skills/
ls ~/.hermes/cron/jobs.json 2>/dev/null && echo "cron exists"
ls ~/.hermes/scripts/ 2>/dev/null && echo "scripts exist"
```

### Step 2: Copy core data (skills first—most important)

```bash
# Copy skills
cp -a /home/agentuser/.hermes/skills/* /root/.hermes/skills/
# Copy cron
cp /home/agentuser/.hermes/cron/jobs.json /root/.hermes/cron/
# Copy scripts
cp -a /home/agentuser/.hermes/scripts/* /root/.hermes/scripts/
# Copy profiles (can be large)
cp -a /home/agentuser/.hermes/profiles/* /root/.hermes/profiles/
```

### Step 3: Copy configuration and identity

```bash
# SOUL.md (personality—important for agent behavior)
cp /home/agentuser/.hermes/SOUL.md /root/.hermes/

# Auto-learning progress (if exists)
cp /home/agentuser/.hermes/auto_learn_progress.txt /root/.hermes/ 2>/dev/null
cp /home/agentuser/.hermes/auto-learn-core-rules.md /root/.hermes/ 2>/dev/null

# Config (+ adjust user-specific paths if needed)
# auth.json (credential pools, but not .env keys)
```

### Step 4: Merge memories (not overwrite!)

```bash
# Merge MEMORY.md
cat /home/agentuser/.hermes/memories/MEMORY.md >> /root/.hermes/memories/MEMORY.md
# Merge USER.md
cat /home/agentuser/.hermes/memories/USER.md >> /root/.hermes/memories/USER.md
```

Then edit the merged files to remove any duplicate session-specific entries.

### Step 5: Copy remaining data

```bash
for dir in pairing pastes image_cache audio_cache bin migration hooks; do
  [ -d "/home/agentuser/.hermes/$dir" ] && cp -a "/home/agentuser/.hermes/$dir"/* "/root/.hermes/$dir/" 2>/dev/null
done
```

### Step 6: Verify migration

```bash
# Compare skill counts
echo "Source: $(find /home/agentuser/.hermes/skills -name SKILL.md | wc -l)"
echo "Target: $(find /root/.hermes/skills -name SKILL.md | wc -l)"

# Check for missing items
diff <(find /home/agentuser/.hermes/skills -name SKILL.md -printf '%P\n' | sort) \
     <(find /root/.hermes/skills -name SKILL.md -printf '%P\n' | sort) | grep "^<"
```

### Step 7: Fix ownership

```bash
chown -R root:root /root/.hermes/
chmod 600 /root/.hermes/.env /root/.hermes/auth.json /root/.hermes/config.yaml
```

### Step 8: Clean up redundant gateways and restart

```bash
# Kill old gateway processes from the old user
ps aux | grep gateway
kill -9 <old_PID>

# Restart the current gateway
systemctl restart hermes-gateway  # or
# just let it pick up changes on next message
```

## Verification After Migration

### Skills are visible
```bash
# From hermes agent context
skills_list
# Should show old + new skills combined
```

### Cron jobs are running
The `cron/jobs.json` contains origin info (platform, chat_id). After migration, these should still work since they reference the same Feishu chat. If cron jobs point to old user paths (e.g., `/home/agentuser/.hermes/scripts/`), update the paths in the prompt field.

### Memories are loaded
The agent should know about past user preferences from merged memory.

## Pitfalls

### 🔍 Pre-migration: Inventory ALL services dependent on the old user's environment

The old user's home may host more than just the Hermes gateway. Before deleting:

```bash
# 1. Find ALL Python/web processes running from the old user
ps aux | grep -E "python|flask|gradio|uvicorn|gunicorn" | grep "olduser" | grep -v grep

# 2. Check all listening ports and identify which process owns each
ss -tlnp

# 3. Look for Gradio apps, file servers, download servers, webhook listeners
find /home/olduser -name "*.py" -exec grep -l "launch\|run\|server_name\|app.run\|PORT" {} \; 2>/dev/null

# 4. Note the ports and plan to migrate or restart those services on the new user
```

Common services that may be orphaned:
- **Gradio web apps** (跨境AI助手, 东南亚电商助手, etc.) — often started as background processes
- **File download/upload servers** (`http.server`, Flask, etc.)
- **Webhook listeners** (for Feishu/Telegram webhooks)
- **Screen/tmux sessions** that run long-lived scripts

**Strategy:** Either restart these services under the new user after migration, or document which ports need to be reassigned.

### 🚨 CRITICAL: Identify the running gateway's Python venv BEFORE deleting old data

**The running gateway process may be using the OLD user's Python venv as its executable.** Deleting that user's home directory kills the gateway mid-flight:

```
# Before deletion — check which venv the gateway is running from
ps aux | grep "python.*gateway" | grep -v grep
# Example output:
# root  3792842  ... /home/agentuser/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main gateway run --replace
#                                                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#                                        This path will be DELETED if you rm -rf /home/agentuser/.hermes/
```

**Safe deletion protocol:**
1. First copy all data to the target user
2. Verify the target user's gateway is running and processing messages correctly
3. **Then** stop any old gateway processes that still reference the old venv:
   ```bash
   kill <PID_of_old_gateway>
   ```
4. Verify the new gateway stays alive and connected to Feishu
5. **Only then** delete the old user's data

**If you accidentally deleted the old user's home while the gateway was running from it:**
- Gateway crashes → stdout/file handles broken → process dies
- If a fallback venv exists (e.g., `/root/hermes-venv/`), Hermes auto-restarts from it
- The fallback venv may be **missing packages** (`websockets`, SSL certs, etc.)
- Watch the logs for connection errors:
  ```
  ERROR: Feishu startup failed: websockets not installed; websocket mode unavailable
  ERROR: Feishu Send error: Could not find a suitable TLS CA certificate bundle
  ```
- Fix by installing missing packages in the fallback venv:
  ```bash
  /path/to/fallback-venv/bin/pip install websockets certifi
  ```
- The gateway may need 2-3 restart attempts before it fully recovers (first attempt fails → auto-restart → often succeeds)

### Other Pitfalls

- **`cp -a` preserves ownership.** After copying to a different user, run `chown -R newuser:newuser`.
- **Sessions database (state.db) is user-local SQLite.** It cannot be simply copied between users. The old user's Her mes history will not appear in the new user's session search.
- **Cron job prompts may contain hardcoded paths** (e.g., `/home/agentuser/.hermes/scripts/`). After migration, edit the cron job via `cronjob(action='update', job_id='...')` with corrected paths, or copy the referenced scripts to the corresponding new path.
- **Profiles can be very large** (thousands of files, mostly in `.git/` directories). Use `du -sh` before copying to estimate time.
- **Running `hermes gateway run --replace` after migration** will register a new gateway PID and the old one stops being relevant. Kill it explicitly to free memory.
- **Always kill redundant old gateways.** They can hold stale lock files and file handles that interfere with the new installation.
- **The `store` directory under profiles contains checkpointed agent states** — these are user-specific and may not be reusable after migration.
- **Terminal tool venv path is hardcoded.** After migrating users (e.g. `agentuser` → `root`), the Hermes terminal tool still searches for its Python venv at the **old user's path** — typically `/home/agentuser/.hermes/hermes-agent/venv/`. If that directory doesn't exist at the new user's home, every shell command fails with `FileNotFoundError`. **Fix**: create a symlink from the old path to the new venv:
  ```bash
  mkdir -p /home/agentuser/.hermes/hermes-agent/
  ln -s /root/.hermes/hermes-agent/venv /home/agentuser/.hermes/hermes-agent/venv
  ```
  Or, if the old user home no longer exists, reinstall Hermes at the new user (re-running `hermes install` recreates the venv). Do NOT delete the old user's home entirely before verifying the terminal tool works at the new user — keep a stub directory or symlink.
- **Script-based cron jobs (no_agent=True) survive migration because they run via the system shell, not the Hermes terminal toolchain.** They do NOT depend on the venv path. Only LLM-driven cron jobs (that load skills + use enabled_toolsets) are affected by this venv issue.
