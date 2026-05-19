---
name: hermes-multi-agent-profiles
title: Hermes Multi-Agent Profiles Setup
description: Complete guide to creating and managing multiple Hermes Agent instances using official profiles system
trigger: When user wants to run multiple Hermes agents for different projects, or encounters Feishu/configuration conflicts between agents
version: 1.0
---

# Hermes Multi-Agent Profiles Setup

Use this skill when you need to run multiple independent Hermes agents on the same machine — for example, separate agents for different projects like ResearchAudit and Southeast Asia e-commerce.

## Problem Scenario

Users often try to manually create separate Hermes instances by:
- Creating new directories like `~/hermes-project2`
- Copying config files manually
- Running separate processes

This leads to:
1. **Configuration conflicts** (same Feishu App ID, same ports)
2. **State mixing** (shared memory, sessions, skills)
3. **Management complexity** (no unified commands)

## Official Solution: Profiles

Hermes has a built-in profile system. Each profile is a completely independent agent with:
- Own `config.yaml`, `.env`, `SOUL.md`
- Own memory, sessions, skills, cron jobs
- Own gateway state and messaging connections
- Automatic command aliases

## Step-by-Step Guide

### 1. Check Existing Profiles

```bash
hermes profile list
```

Example output:
```
Profile          Model            Gateway      Alias
───────────────  ───────────────  ───────────  ────────────
◆default         deepseek-chat    running      —
agent2           deepseek-chat    stopped      agent2
project2         —                stopped      project2
```

### 2. Create a New Profile

**Option A: Blank profile** (fresh start)
```bash
hermes profile create my-project
```

**Option B: Clone config only** (recommended for same user)
```bash
hermes profile create my-project --clone
```

**Option C: Clone everything** (including memory and sessions)
```bash
hermes profile create my-project --clone-all
```

**Option D: Clone from specific profile**
```bash
hermes profile create work --clone --clone-from coder
```

### 3. Configure Profile-Specific Settings

#### 3.1 Edit Environment Variables
```bash
nano ~/.hermes/profiles/my-project/.env
```

**Critical for messaging platforms (Feishu):**
```bash
# Must use DIFFERENT App ID/Secret than other profiles
FEISHU_APP_ID=cli_xxxxxxxxxxxxxxx
FEISHU_APP_SECRET=your_new_secret_here
```

#### 3.2 Edit Configuration (Optional)
```bash
nano ~/.hermes/profiles/my-project/config.yaml
```

**Add/Modify gateway port** (if running multiple agents simultaneously):
```yaml
gateway:
  host: "0.0.0.0"
  port: 3001  # Different from default (3000)
```

#### 3.3 Edit Personality (Optional)
```bash
nano ~/.hermes/profiles/my-project/SOUL.md
```

### 4. Use the Profile

#### 4.1 Automatic Command Alias
After creation, you get a command alias:
```bash
my-project setup              # Configure API keys
my-project chat               # Start chatting
my-project gateway start      # Start gateway
my-project doctor             # Check health
my-project skills list        # List skills
```

#### 4.2 Using -p Flag
```bash
hermes -p my-project chat
hermes --profile=my-project doctor
```

#### 4.3 Set Default Profile
```bash
hermes profile use my-project
hermes chat                   # Now uses my-project
hermes profile use default    # Switch back
```

### 5. Manage Profiles

```bash
# List all profiles
hermes profile list

# Show profile details
hermes profile

# Remove a profile
hermes profile remove my-project

# Export/import profiles
hermes profile export my-project --output my-project.tar.gz
hermes profile import my-project.tar.gz
```

## Common Issues & Solutions

### Issue 1: Feishu App ID Conflict
**Symptoms**: "App ID already in use", gateway fails to start
**Solution**: Each profile MUST have unique Feishu App ID/Secret

### 💡 Feishu WebSocket Connection — Key Findings (Real-World Experience)

**Background**: When setting up a second Hermes profile with its own Feishu App, the WebSocket connection can fail if the Feishu dev console isn't properly configured.

**Step-by-step Feishu dev console setup** (https://open.feishu.cn/app):
1. Open your app → left menu **事件与回调** → **事件配置** tab
2. Click the **pencil icon** ✏️ next to "订阅方式" → select **使用长连接接收事件** (WebSocket, recommended)
3. Click **添加事件** → add at minimum: `im.message.receive_v1` (receive user messages)
4. Click **保存**
5. Back on the page, click **重新验证** to verify the WebSocket connection status

**⚠️ Critical finding: Encrypt Key & Verification Token are NOT needed for WebSocket mode**
- The `.env` template often includes placeholders like `FEISHU_ENCRYPT_KEY=你的加密密钥` and `FEISHU_VERIFICATION_TOKEN=***`
- **You can comment these out or remove them** when using WebSocket (长连接) mode
- Hermes' native WebSocket client connects without encryption keys
- These fields are only required for HTTP Webhook (回调) mode

**Minimal `.env` for Feishu WebSocket:**
```bash
FEISHU_APP_ID=cli_xxxxxxxxxxxxxxx     # Must be unique per profile
FEISHU_APP_SECRET=your_secret_here    # Unique per profile
FEISHU_DOMAIN=feishu
FEISHU_CONNECTION_MODE=websocket
# No Encrypt Key or Verification Token needed for WebSocket mode!
```

**Verifying the connection**: Run `southeast-ecommerce gateway run` and look for:
```
[Lark] [INFO] connected to wss://msg-frontier.feishu.cn/ws/v2?...
```
This confirms WebSocket handshake succeeded. Then go back to the Feishu dev console and click **重新验证** — the status should change from red "连接失败" to green "连接成功".

**Troubleshooting:**
- If you see `[Lark] [INFO] connected` but the Feishu console still shows "连接失败" → you may need to:
  - Add events (step 3 above) and save
  - Click **重新验证** button
- If the gateway doesn't start at all → check App ID/Secret are correct and unique

### Issue 2: Port Conflict
**Symptoms**: "Address already in use", can't start gateway
**Solution**: Set different port in `config.yaml`:
```yaml
gateway:
  port: 3001  # or any available port
```

### Issue 3: "Gateway already running" Error
**Symptoms**: Trying to start a second gateway fails with "Gateway already running (PID XXXX)"
**Key Insight**: Hermes gateway is **global** - one gateway can serve multiple profiles
**Solution**: 
1. Check if global gateway is running: `systemctl status hermes-gateway`
2. Use the existing gateway - it will automatically route messages to correct profile based on Feishu App ID
3. If you must run separate gateways, ensure they use different ports and different systemd service names

### Issue 4: Deprecated Configuration Warning
**Symptoms**: "Deprecated .env settings detected: TERMINAL_CWD=/home/agentuser"
**Solution**: Move deprecated settings from `.env` to `config.yaml`:
```yaml
terminal:
  cwd: /home/agentuser
```

### Issue 3: Profile Not Found
**Symptoms**: "Profile 'my-project' does not exist"
**Solution**: Check profile exists with `hermes profile list`

### Issue 4: Command Alias Missing
**Symptoms**: `my-project` command not found
**Solution**: Check `~/.local/bin/my-project` exists, or use `hermes -p my-project`

## Best Practices

1. **Naming Convention**: Use descriptive names (e.g., `research-audit`, `ecommerce-assistant`)
2. **Port Planning**: Plan ports in advance (3000, 3001, 3002, etc.)
3. **Feishu Apps**: Create separate Feishu apps for each profile
4. **Backup**: Export important profiles before major changes
5. **Documentation**: Keep notes on each profile's purpose and configuration

## Real-World Example: Two Project Setup

```bash
# Create profiles for two projects
hermes profile create research-audit --clone
hermes profile create ecommerce-assistant --clone

# Configure each with unique Feishu credentials
# Edit ~/.hermes/profiles/research-audit/.env
# Edit ~/.hermes/profiles/ecommerce-assistant/.env

# Set different ports
# Edit ~/.hermes/profiles/ecommerce-assistant/config.yaml
# Add: gateway.port: 3001

# Start both (in separate terminals)
research-audit gateway run
ecommerce-assistant gateway run

# Or use screen/tmux
screen -S research -d -m research-audit gateway run
screen -S ecommerce -d -m ecommerce-assistant gateway run
```

## Verification Checklist

- [ ] Profile created successfully (`hermes profile list`)
- [ ] Unique Feishu App ID/Secret configured
- [ ] Unique port configured (if running simultaneously)
- [ ] Command alias works (`my-project --help`)
- [ ] Gateway starts without errors
- [ ] Can connect via messaging platform
- [ ] Memory and sessions are isolated from other profiles

## Related Skills

- `hermes-multi-instance-guidelines` - Conceptual guidelines
- `project-specific-hermes-configuration` - Project-specific setups
- `learning-hermes-agent` - General Hermes learning path