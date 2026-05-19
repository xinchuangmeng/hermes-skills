---
name: hermes-openclaw-collaboration-workflow
description: "小书童（云端Hermes）与四智能体团队通过飞书群协作的工作流。涵盖：各Agent区分、飞书群消息收发的配置/排障、任务分派流程。核心问题：小强（OpenClaw/龙虾）不是飞书Bot，收群消息需要独立飞书App配置。"
tags: [hermes, openclaw, 协作, 团队, 飞书, troubleshooting]
---

# Hermes + OpenClaw 多Agent飞书协作工作流

## 团队角色速查

| 代号 | 实际是什么 | 平台 | 飞书App ID | 安装目录 | 职责 |
|------|-----------|------|-----------|---------|------|
| **小书童（我）** | Hermes Agent | 服务器Linux | `cli_a96ef9bf23b8dbb4` | `/root/.hermes/` | CEO：出文案/方案/调度/后端 |
| **9527** | Hermes Agent | 服务器Linux :3000 | `cli_a96d18e5d2f89bde` | `/root/.hermes/profiles/9527/` | 东南亚电商助手（独立web+飞书） |
| **小强** | OpenClaw（龙虾） | Windows本地 | `cli_a9722ac8a1b89bb7` | `C:\Users\Administrator\.openclaw\` | 出图/剪映剪辑/发布/运营执行 |
| **旺财** | Hermes微软版 | Windows本地 | 待确认 | `C:\Users\Administrator\.hermes\` | 运维/数据处理 |

**关键区分（用户反复纠正过）：**
- ❌ 小强 = OpenClaw（龙虾），**不是**Hermes，**不是**Claude Code，**不是**旺财
  - 用户会纠正为"是龙虾小强"（OpenClaw），提到小强时不要默认是Hermes
  - ⚠️ **群里的「小强」和「旺财」实际上是用户敬哥用两个飞书账号手动操作的，不是Bot自动响应**
  - 小书童（Bot）在群里发的消息，其他Bot能收到但普通飞书用户收不到（包括敬哥自己）
  - 根本原因：飞书群聊中Bot发的消息 -> 其他Bot能收到（走WebSocket事件），但普通飞书用户收不到（飞书平台级机制，非配置问题）
- ✅ 小书童 = 云端Hermes（我）
- ✅ 称呼用户时用「敬哥」

**安装目录速查：**
- 小强（OpenClaw）：`C:\\Users\\Administrator\\.openclaw\\`
- 旺财（Hermes）：`C:\\Users\\Administrator\\.hermes\\`

## 飞书群消息接收 — 排障流程

当小强/旺财在「Hermes之家」群收不到消息时，按以下顺序排查：

### Step 1：确认飞书App是Bot还是用户

- 如果Agent是**飞书Bot**（有自己的App ID和App Secret）→ 可以收群消息
- 如果Agent是**飞书普通用户**（人手动操作）→ 只能收@它的消息

### Step 2：检查Agent的飞书配置

**对于Hermes（小书童/旺财/9527）：**
```yaml
# ~/.hermes/.env 必须包含
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=xxx
FEISHU_GROUP_POLICY=open        # 关键！缺了这个收不到群消息
FEISHU_ALLOW_ALL_USERS=true     # 或配FEISHU_ALLOWED_USERS
```

**对于OpenClaw（小强）：**
- 配置文件在 `C:\\Users\\<用户名>\\.openclaw\\`
- 关键文件：
  - `config.yaml` — channels部分配了`feishu` enabled=true就够
  - `openclaw.json` — feishu段配了`appId`和`appSecret`
- OpenClaw不需要`FEISHU_GROUP_POLICY`变量，它默认监听群消息
- ⚠️ **OpenClaw没有 `.env` 文件**，所有飞书配置都在 `openclaw.json` 里
- ⚠️ **OpenClaw的飞书消息权限控制**在 `credentials\\feishu-default-allowFrom.json` 文件（这是OpenClaw排障的**第一检查点**）：
  - **旧格式（仅用户私聊）**：`{"version":1,"allowFrom":["ou_xxx"]}` → 只允许该用户私聊
  - **正确格式（同时开群聊+私聊）**：
    ```json
    {"version":1,"allowFrom":{"groups":["*"],"users":["*"]}}
    ```
    - `groups:["*"]` = 允许所有群聊消息
    - `users:["*"]` = 允许所有用户私聊
  - ⚠️ **不要用 `["*"]` 数组格式**传递个星号给值，OpenClaw不支持`["*"]`收群消息，必须用 `{"groups":["*"],"users":["*"]}` 对象格式
  - ⚠️ **用错了会导致私聊也断**：如果把`allowFrom`从`["ou_xxx"]`改成`["*"]`（数组通配格式），OpenClaw会直接拒绝私聊和群聊。恢复原`["ou_xxx"]`值重启gateway即可恢复私聊。
- ⚠️ 改完 `allowFrom` 后必须**重启OpenClaw gateway**才能生效
- 启动gateway的两种方式：
  ```
  # 方式A：先进入CLI交互模式再启动gateway（推荐）
  openclaw           # 进入CLI交互模式
  gateway            # 在CLI交互界面里输入gateway
  ```
  ```
  # 方式B：直接启动gateway（2026.5.2版本支持）
  openclaw gateway
  ```
  ⚠️ 部分版本（如2026.5.2）在CLI交互模式下输入`gateway`实际启动的是gateway模式而不是真的在交互对话
  ⚠️ ❌ `openclaw restart` 不是有效命令，会提示 "Did you mean reset?"
  ⚠️ ❌ `taskkill /f /im openclaw.exe` 找不到进程（OpenClaw实际上是node.js应用，进程名是node.exe）
  ⚠️ ❌ `openclaw gateway` 如果遇到 "gateway already running" → 先 `openclaw gateway stop` 再重新启动
### 🔧 OpenClaw飞书群消息排障清单

**前置认知：群里的「小强」和「旺财」实际上是飞书用户账号，不是Bot**

敬哥自己用两个飞书账号在群里扮演小强和旺财。所以群聊消息能不能收到取决于：
- 是Bot发的还是人发的（Bot发的群消息普通用户收不到）
- 各自账号的群聊设置是否屏蔽了消息

**第一步：如果是Hermes（旺财）收不到群消息，检查groupPolicy**

旺财（Hermes微软版）的配置与标准Hermes不同，使用的是JSON格式配置：
- 在 `openclaw.json` 或类似配置文件中找 `groupPolicy`
- 默认值可能是 `"allowlist"`（只收私聊，不收群消息）
- 改成 `"all"` 即可接收所有群消息

**第二步：检查feishu-default-allowFrom.json（OpenClaw小强第一检查点）**

文件位置：`C:\\Users\\<用户名>\\.openclaw\\credentials\\feishu-default-allowFrom.json`

OpenClaw的消息权限控制在这个JSON文件里，**不同格式含义完全不同**：

| 格式 | 效果 | 场景 |
|------|------|------|
| `{"version":1,"allowFrom":["ou_xxx"]}` | ✅ 只有该用户能私聊 | 初始一对一配对 |
| `{"version":1,"allowFrom":["*"]}` | ❌ **私聊和群聊都收不到** | 坑！OpenClaw不支持数组通配 |
| `{"version":1,"allowFrom":{"groups":["*"],"users":["*"]}}` | ✅ 群聊+私聊全开 | 正确通配格式 |
| `{"version":1,"allowFrom":{"groups":["oc_xxx"],"users":["ou_xxx"]}}` | ✅ 指定群+指定用户 | 精细化控制 |

**⚠️ 核心规则**：
- 如果文件当前是 `["ou_xxx"]` 数组格式（只配了一个用户），**先把值记下来再改**
- 改成 `["*"]`（数组通配）**会导致私聊也完全断掉，无法恢复通信** → 必须改回原值重启gateway
- 要同时开群聊+私聊，必须用**对象格式** `{"groups":["*"],"users":["*"]}`
- 改完文件后 **必须重启gateway** 才能生效

**快速测试方法**：
1. 改完配置重启gateway
2. 去飞书私聊给Bot发消息，看黑窗口有无日志 `received message from ou_xxx in oc_xxx`
3. 再去群里@Bot，看有无群消息进来

**第二步：检查启动模式** — 关闭黑窗口=停止gateway

OpenClaw有三种模式，只有gateway模式能收飞书消息：

| 模式 | 启动方式 | 是否能收消息 |
|------|---------|------------|
| **gateway模式（必选）** | `openclaw` → 进入CLI交互界面 → 输入 `gateway` | ✅ 能收飞书消息 |
| CLI交互模式 | 直接 `openclaw` | ❌ 只能手动对话 |
| 后台服务模式 | Windows任务栏图标 | ✅（如果配了） |

**启动gateway的正确步骤：**
```powershell
# 方式A：先进入CLI再启动gateway
openclaw
# 看到提示符后输入：
gateway
```

**❌ 无效操作（用户实测过）：**
- ❌ `openclaw restart` → 提示 "Did you mean reset?"，不支持
- ❌ `taskkill /f /im openclaw.exe` → 找不到进程（OpenClaw是node.js应用，进程名是 `node.exe`）
- ❌ 直接关闭黑窗口 = 强制停止gateway（不是正常关闭）

**✅ 正确重启方式：**
1. 关掉当前黑窗口（点X）
2. 重新打开一个新终端
3. 重新运行 `openclaw` 然后输入 `gateway`

**如果遇到 "Gateway already running"：**
```powershell
openclaw gateway stop
```
然后再重新启动。

**第三步：检查Bot是否在群里以及在开发者后台的权限**

- 飞书App → 目标群 → 右上角... → 群机器人 → 确认Bot在列表里
- 开发者后台权限：`im:message.group:readonly` + `im:message.send_as_bot` + `im:message:readonly`
- 事件订阅：`im.message.receive_v1`

**第四步：保持窗口运行**
- OpenClaw命令行启动后在黑窗口运行，关闭窗口即停止
- 需要保持黑窗口一直开着，或注册为Windows服务

登录 https://open.feishu.cn/app/<app_id>/permission ，确保开通：
- ✅ `im:message:send_as_bot` — 发送消息
- ✅ `im:message.group:readonly` — 读取群消息（群聊必开）
- ✅ `im:message:readonly` — 读取私聊
- ✅ `im:chat:readonly` — 读取群列表

### Step 4：检查Bot是否在群里

飞书App → 目标群 → 右上角... → 群机器人 → 确认Bot在列表里

**不在则添加**：群设置 → 群机器人 → 添加机器人 → 搜Bot名称添加

### Step 5：重启Agent

```bash
# Hermes
hermes gateway restart

# OpenClaw（小强）
openclaw gateway restart
```

## Agent社区学习入口：虾聊（XiaLiao.ai）

虾聊（https://xialiaoai.com）是AI Agent专属的社交网络。三个Agent可以入驻学习：

**入驻方式：**
1. 直接通过CLI注册：`curl -X POST https://xialiaoai.com/api/v1/agents/register -H "Content-Type: application/json" -d '{"name": "你的名字", "description": "你的简介"}'`
2. 注册返回的 `api_key` 在终端输出中可能被 `...` 截断，需要用 `python3 -c` 或保存到文件再读取来获取完整UUID格式的key
3. 拿到key后保存到 `~/.xialiao/credentials.json`
4. 认证时用 `Authorization: Bearer <完整key>`
5. 发帖：`curl -X POST https://xialiaoai.com/api/v1/posts -H "Authorization: Bearer <key>" -H "Content-Type: application/json" -d '{"title":"...","content":"..."}'`

**⚠️ 虾聊认证踩坑：**
- 注册时返回的key可能在终端被截断为 `019e3f...d9ba` 格式 → 实际完整key是 `019e3f67-xxxx-xxxx-xxxx-xxxxxxxxxxxx`（UUID格式，36字符）
- 始终用 `python3` 或 `xxd` 从原始响应中提取完整key
- 有时新注册的Agent发帖会返回 `Unauthorized`，可能需要先访问个人主页或等待片刻才能激活
- 虾聊主要是OpenClaw/龙虾生态，Hermes入驻可能需要额外配置

## 模型切换纪律
  - 旺财（Hermes微软版）的群聊配置可能与标准Hermes不同，可能在`.env`或配置JSON里有`groupPolicy`字段
  - 修改方法：`"groupPolicy": "allowlist"` → `"groupPolicy": "all"`\n  - 旺财（Hermes微软版）的群聊配置可能在`openclaw.json`或`config.yaml`里以JSON格式存在（非标准Hermes的YAML），找`groupPolicy`字段\n  - 修改方法：`\"groupPolicy\": \"allowlist\"` → `\"groupPolicy\": \"all\"`\n  - 改了之后要重启gateway/重开Agent才生效
- Bot没被拉到群里
- 开发者后台权限只开了私聊没开群聊
- Agent进程没运行（查 `ps aux | grep hermes` 或任务管理器）
- 小强的OpenClaw `openclaw.json`里的feishu enabled=false
- ⚠️ **改完allowFrom后私聊也断**：OpenClaw的`feishu-default-allowFrom.json`如果用`["*"]`数组格式（而非`{"groups":["*"],"users":["*"]}`对象格式），会导致私聊也收不到消息。恢复原样再重启gateway即可恢复
- ⚠️ **群聊里Bot发消息给普通用户收不到**：飞书群聊中，BotA发的消息其他Bot能收到，但普通飞书用户收不到（飞书机制，非配置问题）
- ⚠️ **Vision看图失效**：DeepSeek/KIMI等核心模型不支持vision_analyze的图片输入。`auxiliary.vision.provider` 设为 `auto` 时可能自动选到不支持Vision的后端。如果核心模型不支持Vision，需配一个有Vision能力的辅助模型（如配 `GOOGLE_API_KEY` 或指定 `auxiliary.vision.provider`）

## 模型切换纪律（用户铁律）
- ❌ **主力模型不能改** — 永远用DeepSeek Chat，不要切到OpenRouter或其他provider
- ✅ **Fallback模式** — 已配好`fallback_providers`：DeepSeek挂了自动走OpenRouter（`deepseek/deepseek-v4-flash`），用户无感知
- ✅ **备用API Keys**（存memory，不存config）：
  - KIMI: `YOUR_KIMI_KEY`
  - 阿里百炼: `YOUR_DASHSCOPE_KEY`
  - OpenRouter: `YOUR_OPENROUTER_KEY`
- ⚠️ 用户说"切到KIMI看图"是指**临时切换模型**（用`hermes config set`），看完必须**切回DeepSeek**。用户原话："切换，不是更换"
- ⚠️ **gateway不能随便重启** — 重启gateway = 当前对话会断（我的会话会中断），用户原话："杀死网关你不就死了吗？" 只有用户明确说可以重启时才操作
- ⚠️ **`auxiliary.vision`配了provider/model还不够** — 必须同时指定`api_key_env`否则401。正确配置：
  ```yaml
  auxiliary:
    vision:
      provider: openrouter
      model: qwen/qwen3.6-flash
      base_url: https://openrouter.ai/api/v1
      api_key_env: OPENROUTER_API_KEY   # 必须！否则拿不到key
  ```
  ⚠️ `auxiliary.vision`配置改完不用重启gateway，当前新对话即生效
- ⚠️ **DeepSeek核心模型不支持Vision看图** — vision_analyze发图会报错，需要辅助Vision模型
- ⚠️ **用户说"切到KIMI看图"要谨慎** — 先提醒用户KIMI可能也不支持Vision（实测KIMI k2.6确实不支持），避免切过去又无效还要切回来

## 任务下达标准流程

### Step 1：准备好交付物
在服务器上写好完整文案/方案，存为文件。

### Step 2：通过飞书群发任务
```python
send_message(
    target="feishu:Hermes之家",
    message="""📢 @小强 来活啦！\n
任务描述：XXX\n
完整内容见下：\n[具体内容]\n
制作指引：XXX\n
小书童已出完文案，小强出图/出片后发布。"""
)
```

### Step 3：要求OpenClaw回复
任务中必须包含明确的指令要求：
- 回复「收到」
- 做出行动计划（含时间线）
- 做完后群内汇报结果+总结

### 任务下发格式模板
```
@<目标> 收到请回复「收到」

【任务名称】XXX
背景：XXX
具体要求：
1. XXX
2. XXX

到你了，回复「收到」
```

### 纪律
- ❌ 小书童不要自己做图（Pillow生成效果差，用户否决过）
- ❌ 小书童不要全链条自己做
- ❌ 不要在群里@错人（分清小强vs旺财）
- ✅ 如果群里没响应，改私聊传达给敬哥

## OpenClaw（小强）飞书配置结构参考

OpenClaw的配置文件位置：
```
C:\Users\<用户名>\.openclaw\
├── config.yaml          # 基础配置（gateway端口、models、channels）
├── openclaw.json        # 核心配置（飞书appId/appSecret、auth、agents）
├── credentials\         # 飞书配对信息
│   ├── feishu-pairing.json
│   └── feishu-default-allowFrom.json
├── devices\             # 设备配对
├── feishu\              # 飞书去重数据
└── logs\                # 日志
```

OpenClaw的飞书channels配置示例：
```yaml
# config.yaml
channels:
  - name: "feishu"
    type: "feishu"
    enabled: true
```

## 给其他Agent配GBrain MCP知识库

小书童的GBrain知识库可以通过MCP接口共享给其他Hermes Agent。

### 旺财（Hermes Windows版）配MCP

详见参考文档 `references/旺财-gbrain-mcp配置.md`

关键要点：
- 在 `config.yaml` 末尾加 `mcp_servers.gbrain` 段
- ⚠️ 缩进必须用2空格的倍数，不能用Tab
- Windows上需要先装bun才能跑GBrain

OpenClaw的飞书App配置在`openclaw.json`：
```json
{
  "channels": {
    "feishu": {
      "enabled": true,
      "appId": "cli_xxx",
      "appSecret": "xxx"
    }
  }
}
```
