# Multi-Agent Unreachable Diagnosis — May 19, 2026

## Scenario

User (敬哥) reported that two other agents in the Feishu group "Hermes之家" — 小强 (OpenClaw) and 旺财 (Hermes Microsoft version) — were not receiving messages sent to the group. The user wanted to know why and how to fix it.

## What Was Found

### Current Architecture

| Agent | Platform | Location | Type | 
|-------|----------|----------|------|
| 小书童 (me) | Hermes Agent | Tencent Cloud server | Full Hermes Agent (WebSocket Bot) |
| 9527 | Gradio app | Same server, port 3000 | Standalone app (not a Bot in the group) |
| 小强 | OpenClaw | Local Windows PC | Unknown — likely a regular user added to the group |
| 旺财 | Hermes Microsoft | Local Windows PC | Unknown — likely a regular user added to the group |

### Key Findings

1. **The main Hermes gateway** is running as `systemd --user` service (`hermes-gateway.service`), started May 18 19:55 CST. Connected to Feishu WebSocket successfully.

2. **Feishu connection mode**: WebSocket (长连接), using `FEISHU_APP_ID=cli_a96ef9bf23b8dbb4` from `/root/.hermes/.env`.

3. **Feishu pairing file** shows only one approved user: `ou_81a83b935374ca9bc8a3d495ab69d810` (the user's account).

4. **Only 小书童 is a Feishu Bot** — connected via WebSocket, can send/receive messages in the group and DMs.

5. **小强 and 旺财 are NOT Feishu Bots** — they were added to the group as regular user accounts. They cannot:
   - Auto-receive messages programmatically
   - Respond to @mentions automatically
   - Process tasks without manual interaction

### The Core Problem

The user assumed all three agents in the group (小书童, 小强, 旺财) were on equal footing — all Bots that auto-process messages. In reality:

- **小书童** = Feishu Bot (WebSocket) — auto-receives and processes
- **小强/旺财** = Regular users — can see messages visually but need manual operation

### What I Did

1. Checked Hermes config (`config.yaml`, `.env`) — confirmed WebSocket Bot setup
2. Checked gateway process via `systemctl --user status hermes-gateway` — running
3. Verified Feishu WebSocket connection in journal logs — connected successfully
4. Checked pairing files in `~/.hermes/platforms/pairing/` — only one approved user
5. Verified send_message works by sending a test message to the group — success
6. Used `send_message(action='list')` — confirmed the group is a reachable target
7. Reviewed past session history via session_search — found the same issue was diagnosed the day before

##### OpenClaw Feishu Group Messaging — Actual Configuration Found

When we finally got access to 小强's Windows PC and inspected OpenClaw's config:

**Config (`config.yaml`):**
```yaml
gateway:
  port: 18789
  name: "MyLobster"
models:
  - name: "default"
    model: "deepseek-chat"
    type: "openai"
    apiKey: "YOUR_DEEPSEEK_KEY"
    baseURL: "https://api.deepseek.com/v1"
channels:
  - name: "feishu"
    type: "feishu"
    enabled: true
```

**OpenClaw JSON (`openclaw.json`) — feishu channel:**
```json
"feishu": {
  "enabled": true,
  "appId": "cli_a9722ac8a1b89bb7",
  "appSecret": "OXAmU572TkxHKXXNH4cXif5QK8DbYiLK"
}
```

**Feishu allowFrom (`feishu-default-allowFrom.json`):**
```json
{"version": 1, "requests": [], "allowFrom": ["ou_ebd8da0dffba8843e2272da5671eae5e"]}
```

**Key problem found:** `allowFrom` only has the user's personal open_id (`ou_ebd8da0dffba8843e2272da5671eae5e`), NOT a wildcard `"*"` or group chat ID. This means OpenClaw only accepts messages from that specific user DM — it rejects group messages.

**Deeper issue: OpenClaw's channel config model vs Hermes**

Unlike Hermes (which has `FEISHU_GROUP_POLICY=open` in `.env`), OpenClaw uses a different permission model:
- `feishu-default-allowFrom.json` controls who can reach the agent
- The `openclaw.json` `"commands.ownerAllowFrom"` field also restricts who can send commands
- OpenClaw's feishu channel may need explicit group chat configuration (the config only shows `appId`/`appSecret` — no `groups` or `allowedChats` field)
- Unlike Hermes, OpenClaw does NOT automatically listen to all group messages where the Bot is present — it uses an allowlist approach

**Fix attempted but not confirmed:**
```json
{"version": 1, "requests": [], "allowFrom": ["*"]}
```
Change `allowFrom` to wildcard, then restart OpenClaw.

#### Discovery Pattern: How to Help a Remote User Find Config

When the user is on a remote Windows machine and you need to find config files, the conversation looks like this. Here's the effective pattern:

1. **Start with where — find the binary:**
   ```
   (Get-Command openclaw).Source
   ```

2. **List config directory:**
   ```
   Get-ChildItem "C:\Users\Administrator\.openclaw\" -Name
   ```

3. **Read config files one by one:**
   ```
   Get-Content "C:\Users\Administrator\.openclaw\config.yaml"
   ```

4. **Read JSON files:**
   ```
   Get-Content "C:\Users\Administrator\.openclaw\openclaw.json"
   ```

5. **Check subdirectories:**
   ```
   Get-ChildItem "C:\Users\Administrator\.openclaw\feishu\" -Name
   Get-ChildItem "C:\Users\Administrator\.openclaw\credentials\" -Name
   Get-ChildItem "C:\Users\Administrator\.openclaw\logs\" -Name
   ```

**PowerShell-specific pitfalls encountered:**
- `dir C:\Users\Administrator\.openclaw\ /b` fails with "第二个路径段不得为驱动器" — wrap in quotes: `dir "C:\Users\Administrator\.openclaw\" /b` or use `Get-ChildItem ... -Name`
- `%USERPROFILE%` is CMD syntax — in PowerShell use `$env:USERPROFILE`
- `head` doesn't exist — use `Select-Object -First N` or `-Tail N`
- `| Select-String -Pattern "feishu" -Context 0,5` works but the `>` prompts from the command itself get mixed into output

## What Was Lacking

No centralized diagnostic flow for "why can't other agents receive messages." The multi-agent-ceo-coordination skill had scattered troubleshooting in multiple sections but no single flow that starts from the first question: "Is the other entity a Bot or a user?"

## Solution Path

**Option A (Current reality):** User manually forwards messages from the group to 小强 and 旺财 individually. Not automated but works immediately.

**Option B (Recommended):** Create separate Feishu Bot Apps for 小强 and 旺财, each with their own:
- Feishu App ID/Secret
- WebSocket connection to the same group
- Independent gateway process

**Option C (For OpenClaw specifically):** OpenClaw has its own Feishu plugin support — install `openclaw-plugin-feishu` and configure its own App credentials.

## Diagnostic Commands Used

```bash
# Check gateway service status
systemctl --user status hermes-gateway

# Check gateway logs for Feishu connection
journalctl --user -u hermes-gateway --since "12 hours ago" --no-pager | grep -iE "feishu|websocket|connect|error|warn|fail"

# Check for Feishu WebSocket connection
journalctl --user -u hermes-gateway --since "12 hours ago" --no-pager | grep "connected to wss://"

# Check pairing/approved users
cat ~/.hermes/platforms/pairing/feishu-approved.json

# Check available messaging targets
send_message(action='list')

# Send test message to group
send_message(target="feishu:Hermes之家", message="测试消息")

# Check gateway processes
ps aux | grep gateway | grep -v grep

# Show all running Hermes processes
ps aux | grep -E "hermes|gateway" | grep -v grep

# Check channel directory for group membership
cat ~/.hermes/channel_directory.json
```

## Lessons Learned

1. **First question when debugging cross-agent messaging**: "Is it a Bot or a regular user?" This determines the entire troubleshooting path.
2. **Regular users in a Feishu group DO NOT auto-process messages** — only Bots connected via WebSocket/Webhook do.
3. **The CEO agent can only check its own machine's processes** — for remote agents, ask the user to verify on the other machine.
4. **Text @mention vs platform-native @mention**: typing @Name in a message does not always trigger the Bot; the user may need to select from the member picker.
5. **Do not assume all agents in the group are equal** — the group chat UI shows them all as members, but their message processing capabilities differ fundamentally.

### Follow-up Session (May 19) — Ambiguity in Agent Nicknames & OpenClaw Config Paths

#### Problem: Nickname Ambiguity Wastes Rounds

When the user returned the next day to troubleshoot why 小强 couldn't receive group messages, a **second-order problem** surfaced — I kept guessing the wrong identity:

| User said | What I guessed | What it actually was | Rounds wasted |
|-----------|---------------|---------------------|---------------|
| "小强" | OpenClaw ✅ (from prior skill table) | OpenClaw | 0 |
| "是小强" | OpenClaw (confirmed) | OpenClaw | 0 |
| "是龙虾小强" | OpenClaw (ignored 龙虾) ❌ | Claude Code (龙虾) | 1 |
| "不是旺财" | Reverted to OpenClaw ✅ | OpenClaw (after confusion) | 1 |

**Root cause:** The user nicknames his agents fluidly (小强 = OpenClaw / 龙虾 / Claude Code / generic "helper agent"), while the team architecture table permanently mapped 小强 = OpenClaw. When the user added "龙虾" as a qualifier, I treated it as noise instead of a signal.

**Lesson:** When the user mentions an agent nickname and starts troubleshooting its setup, **confirm before guessing**:

> "你说的'小强'是指哪个？是OpenClaw（视频剪辑的），还是Claude Code/龙虾（写代码的）？"

**Add to memory the exact mapping:**
- 小强 = OpenClaw (视频/剪映/出图)
- 龙虾 = Claude Code (编码/代码任务) — can also be called "龙虾小强"
- 旺财 = Hermes微软版 (运维/数据)

#### OpenClaw Configuration Location (Windows)

When troubleshooting OpenClaw (小强) on Windows, the config paths are:

| Config Item | Windows Path | Notes |
|------------|-------------|-------|
| OpenClaw binary | `(Get-Command openclaw).Source` | PowerShell command to find binary |
| Config directory | `C:\Users\<username>\.openclaw\` | Hidden directory in user home |
| Config file | `C:\Users\<username>\.openclaw\config.yaml` | Main config |
| Environment file | `C:\Users\<username>\.openclaw\.env` | Feishu credentials, group policy |
| Workspace | `C:\Users\<username>\.openclaw\workspace\.openclaw\` | Work files |

**PowerShell path gotcha:** Use `$env:USERPROFILE` not `%USERPROFILE%` in PowerShell. The `%VAR%` syntax only works in CMD.

**OpenClaw Feishu group messaging checklist:**
1. Check `.env` has `FEISHU_GROUP_POLICY=open`
2. Check `config.yaml` has `group_sessions_per_user: true`
3. Verify the Bot is added to the target group (群设置 → 群机器人 → check list)
4. Restart gateway after changes: `hermes gateway restart`
