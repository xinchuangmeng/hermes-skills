---
name: multi-agent-ceo-coordination
title: Multiple Hermes Agent CEO Coordination — Cross-Agent Command & Orchestration
description: >-
  How to act as the CEO node in a multi-Hermes-Agent architecture: assigning
  responsibilities, issuing orders, and establishing a clear division of labor
  between agents deployed on different machines (server vs local PC) or
  different profiles.
trigger: >-
  When the user wants you to act as the coordinator / CEO over multiple Hermes
  Agent instances, assigning them distinct roles (e.g. e-commerce operations vs
  customer service) and issuing commands.
version: 1.0
---

# Multi-Agent CEO Coordination

## Problem

You have multiple Hermes Agent instances:
- One on a cloud server (轻量服务器)
- One on the user's local PC
- Possibly a third for another project

The user wants **you** to act as the **CEO node** — the one who understands the
big picture, assigns responsibilities, and issues orders. This is different
from "running multiple profiles" (which is a technical setup problem). This is
the **organizational / command-layer** problem.

## The 4-Agent Team Architecture (当前已建立)

当用户任命你为多个智能体的CEO时，团队结构如下：

| 智能体 | 角色 | 驻地 | 引擎 | 职责 |
|--------|------|------|------|------|
| **👑 小书童（你）** | CEO | 腾讯云服务器 | Hermes + DeepSeek + 301技能 | 搜索情报 → 分发任务 → 沉淀技能 → 汇报 |
| **🛠️ 9527** | 运营专员 | 同服务器 :3000 | Gradio + ai_core.py | 翻译(中/英/马/泰/印尼/越)、Listing优化、竞品分析 |
| **🎬 小强（OpenClaw）** | 内容创作 | 本地Windows | OpenClaw + DeepSeek + 飞书 | 剪映剪辑、视频制作、图文卡片、本地文件操作 |
| **⚙️ 旺财** | 自动化运维 | 本地Windows | Hermes微软版 + PowerShell | Office自动化、Excel报表、PowerShell脚本、文件归档 |

### 任务链执行流程（核心架构）

```
小书童搜索 ──→ 发现值得做的品/趋势
    │
    ├─→ 📩 调9527 API(localhost:3000)：翻译+Listing优化 → 返回优化文本
    │
    ├─→ 📩 飞书群@小强：做视频脚本+剪映剪辑 → 返回成品视频
    │
    ├─→ 📩 飞书群@旺财：整理数据+归档文件 → 返回Excel报表
    │
    └─→ 🧠 全部结果沉淀为技能 → 共享给所有智能体
```

### 通信方式：飞书群（Hermes之家）

所有4个智能体在一个飞书群中。通信规则：

1. **你（小书童）** 在群里发命令，@具体智能体
2. **9527** 通过 localhost:3000 的 API 调用（不需要飞书中转）
3. **小强** 和 **旺财** 在群里接收 @mentions 并执行
4. 所有结果汇总回群里，然后你沉淀为技能

**9527 调用方式（同服务器本地直接调用）：**

9527 是一个 Gradio 网页应用，**没有 HTTP REST API**。正确调用方式是**直接 import ai_core.py 的函数**：

```python
import sys
sys.path.insert(0, "/home/agentuser/sea-ecommerce/ai-assistant")
from ai_core import chat_with_deepseek, translate_text, optimize_listing, analyze_competitor

# 翻译
result = translate_text("车载手机支架 360度旋转", "th")  # en/ms/th/id/vi/zh

# Listing优化
result = optimize_listing("车载手机支架", "强力吸盘 360度旋转", "Shopee", "泰国")

# 竞品分析
result = analyze_competitor("车载手机支架", "泰国")

# AI对话
full = ""
for chunk in chat_with_deepseek("Shopee泰国站怎么选品？"):
    full = chunk
```

所有函数在 `/home/agentuser/sea-ecommerce/ai-assistant/ai_core.py`。Gradio 网页端在 `:3000` 只是 UI 层，后端逻辑都在 `ai_core.py`。

**9527 飞书机器人（hermes 9527）：**

9527 也可以作为独立的飞书机器人运行（用 lark-oapi WebSocket 连接），用自己的 App ID/Secret。详见 `references/9527-feishu-bot-setup.md`。

### 下发任务的格式模板

在飞书群里 @目标智能体时使用此格式：

```
@<目标智能体名>

【📜 CEO命令】

任务：XXX

背景：XXX

具体步骤：
1. XXX
2. XXX
3. XXX

要求：
① 回复「收到」  
② 制定行动计划  
③ 完成后在群里汇报结果+总结
```

### 系统级坑：systemd KillMode 连坐杀子进程

**当CEO用 `terminal(background=true)` 启动后台服务（如9527的Gradio）时：**
systemd 的 `KillMode=mixed`（默认）会在网关重启时 SIGKILL 所有子进程，包括后台Python应用！

**症状：** 网关重启后，9527的端口3000不再监听，但网关日志里没有相关错误。

**排查：** `journalctl --user -u hermes-gateway.service | grep "Killing process"`

**修复：**
```bash
# 修改 systemd 服务配置
# KillMode=mixed → KillMode=process
# 这样 systemd 只杀主进程，不杀子进程
sed -i 's/KillMode=mixed/KillMode=process/' ~/.config/systemd/user/hermes-gateway.service
systemctl --user daemon-reload
# 不需要重启网关，下次重启自动生效
```

## Key Principles

### 0. Proactive Parallelization (MOST IMPORTANT)

> **Never say "wait" or "let me know when you're done." Identify what you can prepare in parallel and start doing it immediately.**

When the CEO (user) tells you they're working on **one part** of a multi-part task (e.g. generating video scenes), your job is to immediately identify and start on the **other parts** they'll need:

| User is doing → | You should start doing → |
|----------------|------------------------|
| Generating scenes | Prepare voiceover + subtitles + final synthesis script |
| Recording narration | Prep scene prompts, BGM, subtitle template |
| Writing script | Prep seedance prompts, voiceover segments, cover image |
| Any video work | Prep the matching companion assets that can be pre-built |

**Wait is not a valid response.** If you know what components are needed and can prepare them independently, do it. Report what you've done when the user comes back, don't ask for permission first.

**Detection pattern:** The user says something like "I'm running X on my end" or "waiting for Y to finish on my laptop" → immediately think: **what can I build right now that pairs with that?**

**Example (from real interaction):**
```
User: "正在后台跑7段Seedance画面生成"
Wrong: "好的等你通知" ❌ (user had to correct: "你现在应该怎么做？")
Right: "我同步准备80秒配音+字幕，你画面生成完直接合成"
```

Also: never ask "what should I do" when the dependency is obvious. If you know the full pipeline (scene→voice→subtitle→final), you know what depends on what. Start on unblocked pieces immediately.

### 1. The User's Command-Response Protocol

> **Every command requires: ① Reply 「收到」 ② Produce action plan ③ Report results + summary in the group when done.**

This is a **hard requirement** users often set. Always include these three steps in every command you issue to other agents. After commanding, wait for the agent to reply — if they don't respond, troubleshoot:

1. **Is their gateway running?** Check `ps aux | grep gateway` on their machine
2. **Are they using the same Feishu App ID?** Each Bot in a group must have a unique Feishu App ID. Check `.env` files
3. **@mention only works if the Bot is actively connected** — a stopped gateway means the Bot is in the group but cannot receive messages

### 1. Know Who Is Where
Before issuing any orders, determine:

| Agent | Location | Connectivity |
|-------|----------|-------------|
| **You** | Usually cloud server | Accessible via Feishu/Discord/Telegram |
| **Other agents** | Server (same machine, different profile) or **user's local PC** | Local PC agents connect via their own messaging connection |

**Critical difference:** Agents on the user's local PC are NOT on the server.
You cannot `delegate_task` to them — you must **send a message** to their
channel.

### 2. The @Mention Rule

> **Agents only see messages in the group chat when they are @mentioned via the platform's native @mention system.**

**CRITICAL: You must use `send_message()` to @mention other agents.** Simply replying to the user in your own chat does NOT send anything to the group. The flow is:

```
CEO (in Hermes session) ── send_message() ──→ Feishu/Discord group ── @mention ──→ Other agent
```

**How to @mention in send_message():**
```python
send_message(
    target="feishu:Hermes之家",  # the group chat
    message="@OtherAgentName \n\n【📜 CEO Command】\n\n..."
)
```

**⚠️ Real-world @mention troubleshooting:**

@mention text in the message body may not always trigger the platform's native @mention mechanism. Platforms treat text-based `@AgentName` differently from selecting the Bot from the member picker. If the other agent doesn't respond:

1. **Use `send_message(action='list')`** to verify available targets
2. Send a separate **test command** first to verify the channel works
3. Ask the user to check: **Is the other Bot's gateway running?** (e.g., `ps aux | grep gateway`)
4. Ask the user to check: **Is the Bot showing "online" in the group chat?**
5. If the Bot shows offline, the gateway on that machine needs to be started first

### 3. Establish Clear Divisions of Labor

Use a table to formalize who does what:

| Agent | Role | Responsibilities |
|-------|------|-----------------|
| You (CEO) | Server Ops + Service X | Gateway health, port monitoring, customer service |
| Other Agent | Operations Y | Product listing, order management, inventory sync |

**P0 / P1 / P2 priority tagging** helps both agents understand urgency.

### 4. Cross-Agent Communication Protocol

Define how agents talk to each other:

```
Agent A (server) ←── order data / inventory data ──→ Agent B (local PC)
                 ──→ customer feedback / after-sales ←──
```

Common patterns:
- **Same group chat:** @mention directly
- **Different groups:** send_message() to the right group
- **No direct agent-to-agent channel:** user forwards messages

## ⚠️ 前提条件：智能体必须已经加入群聊

在尝试用飞书群 @mention 其他智能体之前，**必须先确保所有智能体的飞书机器人已经在群里**。

### 为什么

- 飞书机器人不能自己加自己进群
- 只有群成员才能 @mention 成功
- 即使你成功用 `send_message()` 发了消息，但如果 Bot 不在群里，@mention 不会触发

### 如何确认

```bash
# 在 CEO 所在服务器上，检查 channel_directory 是否有群聊记录
cat ~/.hermes/channel_directory.json
# feishu 平台下应该有一个 type 为 "group" 的条目
```

如果只有 `"type": "dm"`，说明 Bot 还没有被加入任何群。此时需要用户手动操作：

> 用户在飞书群 → 群设置 → 添加成员 → 搜索机器人名 → 添加

### 用户拒绝手动操作时的应对

如果用户说"你搞定吧"（让你自己处理），但 Bot 无法自加入群：

1. **诚实告知限制**：飞书机器人没有自添加权限，必须群管理员手动添加
2. **提供替代方案**：让用户告知群 chat_id，或者让用户在群里 @一下机器人
3. **不要浪费时间找 API 方案**：飞书 API 不支持机器人自加群

### 验证加入成功

用户把 Bot 拉进群后，验证方式：

```bash
# 重启网关让新群聊出现在 channel_directory
systemctl --user restart hermes-gateway
# 或（如果是前台进程）
kill -USR1 <gateway_pid>  # 热重载

# 然后检查
cat ~/.hermes/channel_directory.json
# 应该出现 type 为 "group" 的新条目
```

## Step-by-Step: Issuing CEO Commands

### Step 1: Inventory the Landscape

Check all running profiles, gateways, and configs:
- `hermes profile list` — see all profiles and their gateway status
- `ps aux | grep gateway` — confirm which profiles have running gateways
- Check config files for port, Feishu App ID (without leaking secrets)

### Step 2: Identify All Agents

Use `session_search` to find past setup conversations. Check which agents exist
and where they run (server vs local PC vs different machine).

### Step 3: Determine the Communication Channel

Ask the user or check past conversations:
- "Is Agent B in this same Feishu group?"
- If not, what group/chat_id do they use?

**Use `send_message(action='list')`** to see available targets.

### Step 4: Write and Dispatch the Command

```python
# Use send_message with @mention
send_message(
    target="feishu:Hermes之家",
    message="@OtherAgent \n\n【📜 CEO Command】\n\n..."
)
```

Include in the command:
- **Title** (e.g., 作战命令/Operation Order)
- **Role assignment** (岗位职责)
- **Priority-tagged task list** (P0/P1/P2)
- **Communication protocol** (how to coordinate with you)
- **Execution discipline** (daily reports, escalation rules)
- **📋 The triple-response requirement**: "① 回复「收到」 ② 制定行动计划 ③ 完成后在群里汇报结果+总结"

### Step 5: Self-Test the Command Chain

After issuing the CEO command, do a self-test:
1. **You (CEO) execute your own diagnostic** — check gateway, ports, server health
2. **Report your results in the group** with the 「收到-action plan-result+summary」 format
3. **Wait for the other agent(s) to respond** — if they don't within a reasonable time, troubleshoot

Example self-test report format:
```
@User @OtherAgent

【✅ AgentName — Self-test Complete】

① 收到 ✅
② Today's action plan:
   1. ...
   2. ...
③ Results:
   📡 Gateway: ✅ Running (PID XXXX)
   🔌 Port: ✅ Listening
   🖥️ Server: ✅ Healthy
总结: All services operational, ready for duty.
```

### Step 6: Save the Architecture to Memory

Save a compact entry to `memory` documenting:
- Each agent's name, location, role, PID/port
- The date the command structure was established
- The group chat they're all in

If memory is full, **replace** the least important entry.

## Critical: Full Hermes Agent vs Standalone Bot — Know the Difference

This architecture has TWO fundamentally different types of agents, and mixing them up causes confusion.

### Full Hermes Agent (e.g. 小书童, 旺财)

| Capability | Status |
|-----------|--------|
| Skills library (302 skills) | ✅ Full access |
| Persistent memory (memory tool) | ✅ Full access |
| Session search (past conversations) | ✅ Full access |
| All tools (terminal, file, web, etc.) | ✅ Full access |
| Self-identity awareness | ✅ Built into system prompt + SOUL.md |
| Autonomous task execution | ✅ Can run scripts, manage cron, etc. |

### Standalone Bot (e.g. 9527 lightweight Feishu bot)

| Capability | Status |
|-----------|--------|
| Skills library | ❌ None. Only has its own hardcoded prompt |
| Persistent memory | ❌ None. Only in-memory chat history (lost on restart) |
| Session search | ❌ None |
| Tools (terminal, file, web) | ❌ None. Cannot execute commands |
| Self-identity awareness | ❌ Must be explicitly set in code or it defaults to generic LLM persona |
| Autonomous task execution | ❌ Only receives + responds to messages |

### When to use each

**Use a Full Hermes Agent when:**
- The agent needs to make decisions using knowledge (skills, memory)
- The agent needs to execute commands (write files, run scripts, manage processes)
- The agent needs to coordinate other agents
- The agent needs to produce structured, tool-augmented work

**Use a Standalone Bot when:**
- The only job is a fixed, narrow Q&A loop (e.g. "only answer cross-border e-commerce questions about pricing")
- The bot runs on a machine where Hermes gateway cannot be deployed
- You need platform-specific bot features that Hermes gateway doesn't support
- The workload is trivial enough that tool access is not needed

**🚩 Red Flag: Standalone Bot in the same chat as a Full Agent**

If a Full Hermes Agent and a Standalone Bot are both in the same chat group, the standalone bot adds NO value unless:
- It has domain knowledge the main agent doesn't have (e.g. a specialized RAG database)
- It has platform access the main agent doesn't have (e.g. it's connected to a different platform/users)
- It runs on a different schedule (e.g. a batch-processing bot vs real-time)

Otherwise, the Full Agent can do everything the bot can do, better — because it has tools, memory, and skills.

### ⚠️ Critical: Standalone Bots Require Explicit Identity Definition

**The most common bug:** A standalone bot that says "I'm DeepSeek" or "I'm an AI assistant" instead of its actual identity.

**Root cause:** The bot's code only initializes the LLM client (DeepSeek API, etc.) without passing a system prompt. The LLM defaults to "I am DeepSeek" or "I am an AI created by...".

**Fix:** Every standalone bot MUST have an explicit system prompt that defines:

```
你是谁 → 你在哪台机器上跑 → 你有什么能力 → 你没有什么能力 → 你归谁管
```

Example (from the real 9527 fix in this session):

```python
SYSTEM_PROMPT = """你是9527，东南亚电商助手。
你运行在腾讯云服务器(159.75.89.135)上，跟小书童（Hermes Agent）在同一台服务器。
你的核心能力：翻译（中/英/泰/马来/印尼/越南语）、Listing优化、竞品分析。
你不能做的事：不能执行命令、不能访问文件系统、没有记忆（每次重启都会忘记之前的对话）。
你归小书童（Hermes Agent的CEO）管。"""

# Then pass this as the system prompt when calling the LLM
# E.g., in ai_core.py: chat_with_deepseek(text, system_prompt=SYSTEM_PROMPT, history=history)
```

**Checklist for deploying a standalone bot:**
- [ ] System prompt explicitly defines identity ("你是谁")
- [ ] System prompt defines deployment location ("你在哪")
- [ ] System prompt defines capabilities ("你能做什么")
- [ ] System prompt defines limitations ("你不能做什么")
- [ ] System prompt defines hierarchy ("你归谁管")

## Common Pitfalls

### 1. ❌ Assuming the Agent Sees Your Reply
You're in a group chat. You reply to the user. The other agent is also in the
group. **They won't see it** unless you explicitly @mention them via
`send_message()`.

### 2. ❌ @Mention Mysterious Failure (Cross-Machine)
Even after using `send_message()` with `@AgentName` in the message body, the
other agent may not respond. This happens when:

- **The other agent's gateway is stopped** — check `ps aux | grep gateway` on their machine
- **The @mention is text-only, not platform-native** — Feishu/Discord requires selecting the Bot from the member picker, not just typing `@Name` as text. Some Hermes gateways may not react to textual @mentions
- **The Bot is using a different Feishu App ID** — if two Bots in the same group use different App IDs, one Bot may only receive messages @mentioning its own App ID
- **The Bot was added to the group but never published** — Feishu Bots need to be published (released as a version) to be fully functional in groups

**Troubleshooting checklist when an agent doesn't respond:**
1. Ask user: Is the Bot showing "online" in the group member list?
2. Ask user: Can they directly DM the Bot and get a response?
3. Check: Is the gateway process running on that Bot's machine?
4. Check: Is the Feishu App published with the right permissions?
5. If everything looks fine but still fails, the text-based @mention may not trigger the Bot — try having the user manually @mention the Bot from the member picker

### 3. ❌ Diagnosis Flow — "Other Agent Not Receiving Messages"

When the user reports that another agent in the same group **is not receiving messages**, use this systematic diagnostic flow instead of guessing:

#### Step 1: Separate Bot-from-User Confusion (MOST COMMON ROOT CAUSE)

The other entity in the group chat may not be a Bot at all:

```text
Q: "小强/旺财在群里是【飞书用户（人）】还是【机器人】？"

If 飞书用户 (regular user):
→ Can SEE messages visually but CANNOT auto-process them
→ The local program needs its own Feishu Bot App with WebSocket to auto-receive
→ Workaround: user manually forwards group messages to that agent

If 机器人 (Bot):
→ Continue to Step 2
```

**Key fact:** Feishu distinguishes Bots from users at the platform level. A regular user account added to a group does not receive events programmatically — only Bots connected via WebSocket/Webhook do.

#### Step 2: Self-Test Your Own Connection

Before blaming the other agent, confirm your own connection works:

```bash
# 1. Verify you can see the group via send_message
send_message(action='list')
# Look for the group in Feishu targets

# 2. Send a test message to the group
send_message(target="feishu:Hermes之家", message="🔬 系统自检中，所有在线Bot请回复...")

# 3. Wait for responses. Only the user (human) and online Bots will respond.
```

#### Step 3: Three-Factor Diagnosis

| Check | What to Look For | If Fails |
|-------|-----------------|----------|
| Is the Bot showing as **online** in group member list? | Green dot next to Bot name | Gateway not running on that machine |
| Can user DM the Bot directly and get a response? | Bot replies within seconds | Bot process running but not subscribed to group events |
| Is the Bot's gateway process running? | `ps aux \| grep gateway` shows a process | Start gateway: `systemctl --user start hermes-gateway` |

#### Step 4: Cross-Machine Verification

When the other agent is on a **different machine** (local PC):

```
YOU (CEO/server)                  OTHER AGENT (local PC)
    │                                    │
    │ send_message()                      │
    │ ─────────────────→ Feishu group     │
    │                     │               │
    │                     │ WebSocket     │
    │                     │ ────────────→ │ (only if Bot is connected)
    │                     │               │
    │                     │ ←──────────── │ response
    │ ←───────────────── response         │
```

The CEO agent CANNOT directly check the other machine's processes. Ask the user to verify:

> "敬哥，请在小强/旺财的电脑上运行：`ps aux | grep gateway`。如果没有输出，说明网关没启动。"

#### Step 5: Common Fixes (Ordered by Likelihood)

1. **Bot is a regular user, not a Bot** → Create a Feishu App for that agent, configure WebSocket connection
2. **Gateway stopped** → Restart: `systemctl --user restart hermes-gateway`
3. **Group events not subscribed** → In Feishu dev console: add `im.message.receive_v1` event, save, re-verify
4. **Wrong App ID** → Each Bot must have its own unique Feishu App ID/Secret in `.env`
5. **Bot never joined the group** → User must manually add Bot in group settings (Bot cannot self-join)
6. **Text @mention doesn't trigger** → User manually @mentions Bot from member picker, not by typing @name

### 3. ❌ Using delegate_task for Local-PC Agents
`delegate_task` spawns subagents **on the same machine** (your server). It
cannot reach agents on the user's local PC. Use messaging instead.

### 3. ❌ Memory Bloat
The coordination architecture is stable info — save it. But don't also save
the full command text. Keep memory entries compact (under 100 chars per fact).

### 3.8 ❌ Assuming You Know Remote Agent Config Paths

When troubleshooting a remote Windows agent (小强/旺财 on local PC) from the server, you cannot check their files directly. **Do not guess the paths** — the agent may be OpenClaw (`.openclaw\\`), Claude Code (`.claude\\`), or Hermes (`.hermes\\`). And more importantly, **do not guess which agent the user is talking about** — confirm first.

#### Pitfall: Nickname Ambiguity Wastes Multiple Rounds

The user may use multiple nicknames for the same agent. When they say 小强, it could be:
- OpenClaw (视频剪辑/出图)
- 龙虾/Claude Code (编码Agent)
- 旺财 (Hermes微软版)

**When the user mentions an agent nickname during troubleshooting, confirm before guessing:**

> "你说的'小强'是指哪个？OpenClaw（视频剪辑的），还是Claude Code/龙虾（写代码的）？"

One clarification question beats four rounds of wrong-path debugging.

**In memory, maintain the exact nickname-to-engine mapping:**
- 小强 = OpenClaw (视频/剪映/出图)
- 龙虾/龙虾小强 = Claude Code (编码)
- 旺财 = Hermes微软版 (运维/数据)

#### OpenClaw Config Discovery Path (Windows)

When the user says they're on 小强's Windows PC and OpenClaw is installed, use this discovery flow:

**How to find OpenClaw:**
```powershell
# 1. Find the binary
(Get-Command openclaw).Source

# 2. Find the config directory
Get-ChildItem "C:\Users\$env:USERNAME\.openclaw\" -Name

# 3. OpenClaw doesn't use .env — all config is in openclaw.json
```

**PowerShell gotcha:** Use `$env:USERPROFILE` not `%USERPROFILE%`. The `%VAR%` syntax only works in CMD. Also, PowerShell's `dir` command chokes on paths with trailing backslashes — use `Get-ChildItem` or wrap the path in quotes: `dir "C:\path\"`.

#### OpenClaw Key Config Files

| Config File | Path | Purpose |
|------------|------|---------|
| `config.yaml` | `C:\\Users\\<user>\\.openclaw\\config.yaml` | Models, gateway port, agent name |
| `openclaw.json` | `C:\\Users\\<user>\\.openclaw\\openclaw.json` | Channels (feishu), commands, plugins, device pairing. Feishu channel config: `channels.feishu.appId` + `channels.feishu.appSecret` |
| `credentials\\feishu-default-allowFrom.json` | `C:\\Users\\<user>\\.openclaw\\credentials\\` | **Key file for group messaging.** Controls who can send messages to the agent. See format details below. |
| `credentials\\feishu-pairing.json` | Same directory | Pairing state for feishu channel |
| `devices\\paired.json` | `C:\\Users\\<user>\\.openclaw\\devices\\` | Device identities and approved operators |
| Logs | `C:\\Users\\<user>\\.openclaw\\logs\\` | `config-audit.jsonl`, `config-health.json`, `gateway-restart.log` — no runtime logs |

##### OPENCLAW：飞书群聊配置关键点（feishu-default-allowFrom.json）

**文件位置：** `credentials\\feishu-default-allowFrom.json`

**格式1（仅私聊 - 旧格式）：**
```json
{"version":1,"requests":[],"allowFrom":["ou_xxx_user_open_id"]}
```
✅ 用户私聊可收到
❌ 群聊收不到

**格式2（私聊+群聊 - 官方推荐格式）：**
```json
{"version":1,"requests":[],"allowFrom":{"users":["*"],"groups":["*"]}}
```
✅ 所有用户私聊可收到
✅ 所有群聊消息可收到

**格式3（指定用户+所有群聊）：**
```json
{"version":1,"requests":[],"allowFrom":{"users":["ou_xxx_user_open_id"],"groups":["*"]}}
```
✅ 仅指定用户私聊
✅ 所有群聊

**VERSION 1 数组格式（旧的，部分版本支持）：**
```json
{"version":1,"allowFrom":["ou_xxx_user_open_id"]}
```
只支持用户私聊，不支持群聊分组。

**CRITICAL：格式2/3 用 `{"users":["*"],"groups":["*"]}` 对象格式，不是数组。** 按官方文档 `groups` 字段控制群聊接收。

**另外，OPENCLAW CONFIG.YAML 的飞书 CHANNEL 配置也需要检查：**

看 `config.yaml` 里的 `channels` 段：
```yaml
channels:
  - name: "feishu"
    type: "feishu"
    enabled: true
```
这只是启用了飞书通道。**还需要在 `openclaw.json` 里设置 `channels.feishu` 的 `appId` 和 `appSecret`**。

但即使这些都配好了，如果 OpenClaw 本身默认 **groupPolicy** 是 `allowlist`（只收私聊），需要改成 `all` 才能接收所有群聊。

**群聊故障自检流程（针对OpenClaw）：**
1. `feishu-default-allowFrom.json` 有没有 `"groups":["*"]`？
2. OpenClaw 的飞书 App 有没有 `groupPolicy` 设成 `all`（通常在openclaw.json或内部配置）
3. Bot 是否在飞书开发者后台订阅了 `im.message.receive_v1` 事件？
4. Bot 是否被手动加入群聊（飞书群设置→群机器人→添加）？
5. 重启 OpenClaw gateway 后测试

**如果私聊能通但群聊不通→排查 groupPolicy 和白名单。**
**如果私聊也不通→排查 allowFrom 和网关是否启动。**

**When a user types a path command and gets an error, do NOT ask them to try harder — ask for the output and re-diagnose.** The error message tells you what went wrong (wrong syntax, wrong directory, wrong agent type).

### 4. ❌ Forgetting the User's Preferred Title

## Verification Checklist

- [ ] Each agent's machine/location is known
- [ ] All agents are in the same group (or you know their group IDs)
- [ ] Command sent via `send_message()` with @mention
- [ ] Memory updated with architecture overview
- [ ] Roles and task priorities (P0/P1/P2) are clearly defined

## Cross-Agent Skill Sharing: GitHub Shared Repository

当有多个Agent（云端+本地）需要共享技能库时，详见参考文件：
- `references/multi-agent-shared-skill-repo.md` — 多Agent技能共享方案对比（GitHub仓库/tar包直传/scp同步）和三方提交规则

**核心流程：** 小书童（CEO）打包或推送技能到共享源 → 小强/旺财从共享源安装/拉取 → 三方各自贡献新技能

## Reference Files

- `references/paperclip-orchestration-pattern.md` — Paperclip-inspired multi-agent orchestration patterns (role assignment, task chains, self-improvement loop, monitoring dashboard)
- `references/9527-feishu-bot-setup.md` — Creating a standalone Feishu bot for 9527 using lark-oapi WebSocket (App ID/Secret, event handler, message routing)
- `references/multi-agent-shared-skill-repo.md` — Multi-agent shared skill repository setup (GitHub/tar/scp options, commit conventions)

## Related Skills

- `hermes-multi-agent-profiles` — Technical setup of multiple profiles
- `hermes-multi-instance-guidelines` — Conceptual isolation strategies
