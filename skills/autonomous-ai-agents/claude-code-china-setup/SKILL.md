---
name: claude-code-china-setup
description: 在国内网络环境下，完整配置Claude Code（龙虾）的流程。涵盖WSL2安装、Clash Verge代理配置（含免费节点）、proxychains强制走代理、API2D中转站配置等全网最全的国内可用方案。
category: autonomous-ai-agents
tags: [claude-code, china, proxy, clash-verge, proxychains, api2d, wsl2, network]
---

# Claude Code 国内完整配置指南

## 概述

由于 Anthropic API 在国内被封锁，Claude Code（龙虾）在国内环境下需要经过多层网络配置才能正常运行。本指南记录了完整的配置方案和踩坑经验。

## 环境架构（二选一）

### 方案A：WSL2 + 代理（传统方案，不推荐）
```
Claude Code (WSL2 Ubuntu)
    ↓ proxychains 强制代理
Clash Verge (Windows 代理客户端, 端口 7897)
    ↓ HTTP 代理
免费节点 / 付费机场
    ↓
Anthropic API
```

### 方案B：CCR + Windows PowerShell + 国内API（推荐 ✅）
```
Claude Code (Windows PowerShell)
    ↓ CCR 劫持请求
    ↓ 国内直连（无需代理）
DeepSeek / API2D 国内API
```

**方案B的优势：**
- ✅ **无需翻墙、无需代理** — 国内直连
- ✅ **无需 Anthropic 账号** — 完全绕过 OAuth 强制登录
- ✅ **直接装在 Windows PowerShell** — 不用 WSL2，不用折腾 proxychains
- ✅ **便宜** — DeepSeek V4 编程能力与 Claude 接近，成本仅 ¥2/百万token

## 第一步：安装 Claude Code

### 在 WSL2 Ubuntu 中安装

```bash
# 确保 Node.js 20+
node --version

# 全局安装
npm install -g @anthropic-ai/claude-code

# 验证版本
claude --version
```

### 注意用户权限
- 安装/运行时要确认当前用户：`whoami` 和 `echo $HOME`
- settings.json 必须放在正确的用户目录下（`~/.claude/settings.json`）

---

## 第二步：配置 Clash Verge 代理

### 安装 Clash Verge Rev
1. 下载 [Clash Verge Rev](https://github.com/clash-verge-rev/clash-verge-rev/releases) v2.4.7+
2. Windows 选 `x64-setup.exe` 版本
3. 双击安装，一路下一步

### 获取免费节点订阅
- 推荐源：[FreeClashNode](https://www.freeclashnode.com/free-node/)（每天更新）
- 推荐源：[Pawdroid/Free-servers](https://github.com/Pawdroid/Free-servers)（每6小时更新）
- 只导入 YAML 格式（`.yaml`），Clash Verge 不认 `.txt` 格式

### Clash Verge 关键设置
| 设置项 | 建议值 | 说明 |
|--------|--------|------|
| 模式 | **全局** (Global) | 规则模式下 API 流量可能不走代理 |
| 系统代理 | **开启** (绿色) | 右上角开关 |
| 局域网连接 | **开启** | 否则 WSL2 连不上（设置页面里找） |
| HTTP 端口 | 默认 7897 | WSL2 连接时用这个端口 |
| TUN 模式 | **关闭** | 免费节点开 TUN 会导致断网 |

### 验证代理是否通
在 Windows 浏览器打开 https://www.google.com — 能打开说明代理正常。

---

## 第三步：WSL2 配置 proxychains

### 为什么需要 proxychains
- Claude Code 是 Node.js 应用，**不读** `http_proxy` 环境变量
- 设 `export https_proxy=...` 无效
- proxychains 强制劫持所有网络请求走代理

### 安装和配置

```bash
# 安装
sudo apt update && sudo apt install proxychains4 -y

# 配置代理指向 Clash（注意WSL2的IP和Clash端口）
# WSL2 中 Windows 宿主机 IP 是 172.21.128.1（查看：cat /etc/resolv.conf | grep nameserver）
sudo sed -i 's/socks4.*/http 172.21.128.1 7897/' /etc/proxychains4.conf

# 验证配置
grep -v "^#" /etc/proxychains4.conf | grep -v "^$"

# 测试代理是否通
proxychains4 -q curl -s -o /dev/null -w "%{http_code}" https://api.anthropic.com
# 返回 404 说明代理通了（403=被墙，000=不通）
```

### 启动命令
```bash
proxychains4 -q claude
```

---

## 第四步：配置国内中转站（API2D）

如果免费节点的 IP 被 Anthropic 封了（ERR_BAD_REQUEST），需要中转站。

## ⚠️ 重要：Claude Code v2.1+ 强制 OAuth 登录

**Claude Code v2.1.x 对国内用户极不友好：**
- 完全不读 `ANTHROPIC_API_KEY` / `ANTHROPIC_BASE_URL` 环境变量
- 完全不读 `settings.json` 中的 env 配置块
- 完全不读 `config.json` 中的 `primaryApiKey`
- 即使设置 `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` 也无效
- `claude auth login --console` 要求输入验证码，但仍然需要 Anthropic 账号
- **任何形式的环境变量/配置文件迂回方案都无效**

这意味着：**没有 Anthropic 账号 + 可用代理，Claude Code v2.1+ 在国内几乎无法直接使用。**

最终可行方案：**Claude Code Router（CCR）** — 见下节。

---

## 核心方案：Claude Code Router（CCR）+ Windows PowerShell 直装 ⭐

**CCR（Claude Code Router）** 是一个开源中间件（33.6k ⭐），在本地启动代理服务器，劫持 Claude Code 的所有请求并转发到第三方 API（DeepSeek/API2D/智谱等），**完全绕过 Anthropic 的 OAuth 强制登录**。

- GitHub: [musistudio/claude-code-router](https://github.com/musistudio/claude-code-router)
- 支持多 Provider 动态路由、Request/Response 转换、UI 模式
- **不要用 WSL2，直接装在 Windows PowerShell** — 国内 npm 直连

### 安装 CCR（Windows PowerShell）

```powershell
# 直接装（CCR 安装包小，国内可直连）
npm install -g @musistudio/claude-code-router

# 验证
ccr --version
```

### CCR 与 Claude Code 的区别

| 概念 | 说明 |
|------|------|
| **Claude 模型** 🧠 | Anthropic 的 AI 大脑，会思考写代码 |
| **Claude Code** 🦾 | 给这个大脑装上手和脚，能在终端读文件写文件跑命令 |
| **CCR** 🔌 | 一个转接头，把 Claude Code 的请求劫持转发到 DeepSeek 等国内 API |

**公式：你的CCR = DeepSeek 的大脑（模型） + Claude Code 的手脚（工具）**

比喻：
- 真 Claude = 米其林厨师（精致但贵、难访问）
- CCR + DeepSeek = 夜市烧烤摊老板（味道不差、便宜、随到随吃）

### 配置 Provider（DeepSeek 方案，国内直连免费）

创建 `C:\Users\<用户名>\.claude-code-router\config.json`：

```json
{
  "PORT": 3456,
  "APIKEY": "",
  "API_TIMEOUT_MS": 600000,
  "LOG": true,
  "Providers": [
    {
      "name": "deepseek",
      "api_base_url": "https://api.deepseek.com/chat/completions",
      "api_key": "sk-你的DeepSeekKey",
      "models": ["deepseek-chat"],
      "transformer": {
        "use": ["deepseek"]
      }
    }
  ],
  "Router": {
    "default": "deepseek,deepseek-chat"
  }
}
```

### ⚠️ PowerShell 粘贴注意事项

PowerShell 对 `{}` 和 `@` 有特殊解析，**不能直接粘贴多行 JSON**。以下方法任选一：

**方法A：用记事本创建（推荐 ⭐）**
```powershell
notepad "$env:USERPROFILE\.claude-code-router\config.json"
```
会弹出记事本 → 粘贴 JSON → 保存 → 关闭
⚠️ 弹窗如果提示"找不到是否重建"，选 **是/创建**

**方法B：卸载 Claude Code 本体（可选）**
```powershell
# 如果之前装过 Claude Code，可以删掉（现在用 ccr code 代替 claude）
npm uninstall -g @anthropic-ai/claude-code
```

### 💡 终端环境判断技巧

用户常分不清自己在哪个终端。快速判断方法：
- 看窗口标题栏或边框文字：
  - **"Ubuntu" / "WSL"** → WSL2 终端
  - **"Windows PowerShell"** → PowerShell（推荐装 CCR）
  - **"MINGW64" / "Git Bash"** → 不推荐在这里装（Node 路径可能不对）
- PowerShell 中 `wsl` 命令不可用，要用 `wsl` 得在 WSL2 终端
- PowerShell 中没有 `proxychains4` 命令

### ❌ 强制避免的操作

- **不要在 `ccr start` 运行时直接输入新命令** — 先 Ctrl+C 停止，或开第二个 PowerShell 窗口
- **不要试图在 `ccr start` 的运行窗口里粘贴多行 JSON** — 会被 `>` 续行提示符卡死
- PowerShell 粘贴时：光标必须在行首，右键才粘贴

### ⚠️ 正确使用 CCR 的两个 PowerShell 窗口

**误解：** 以为 `ccr start` 和 `ccr code` 可以在同一个窗口交替输入
**事实：** `ccr start` 启动后持续运行占用前台，必须开第二个窗口

**正确流程：**

**窗口1（服务端，保持运行）：**
```powershell
ccr start
```

**窗口2（干活用，新开一个 PowerShell）：**
```powershell
ccr code -p "帮我写个脚本" --max-turns 5

# 或者进入交互模式
ccr code "帮我写个Python脚本"
```

**注意：** 电脑重启后需要重新 `ccr start`

### 常见问题

| 问题 | 解决 |
|------|------|
| `ccr` 提示 `node: not found` | 在 Git Bash/MSYS2 里装的？切到 PowerShell 重装 |
| `Failed to parse config` | JSON 格式错误，用记事本创建 |
| `No providers configured` | config.json 未正确写入，检查文件内容 |
| 连接超时/卡住 | DeepSeek 响应慢，耐心等待或用 `-p` 模式限时 |

### 支持的 Provider 对比

| Provider | 端点 | 费用 | 编程能力 | 国内直连 |
|----------|------|------|---------|---------|
| **DeepSeek** ⭐推荐 | `api.deepseek.com` | ¥2/百万token | 与Claude接近 | ✅ |
| **API2D** (中转Claude) | `oa.api2d.net` | ¥21起充 | 真Claude模型 | ✅需充值 |
| **智谱 GLM** | `open.bigmodel.cn` | 免费额度多 | 中等 | ✅ |
| **硅基流动** | `api.siliconflow.cn` | 多种开源模型 | 看模型 | ✅ |
| **火山引擎** | `ark.cn-beijing.volces.com` | 豆包系列 | 中等 | ✅ |

### ⚠️ CCR 模式的已知限制（重要）

CCR 虽然解决了"能打字"的问题，但以下功能依赖 Anthropic 官方 OAuth，**CCR 模式不支持**：

| 功能 | CCR 支持？ | 原因 |
|------|-----------|------|
| CLI 对话 + 代码生成 | ✅ | 核心功能正常 |
| 读/写文件、终端命令 | ✅ | Claude Code 工具系统 |
| agent-browser | ✅ | 独立的 CLI 工具 |
| **飞书集成** | ❌ | 需要 OAuth 认证连接飞书 API |
| **`/skill` 命令** | ❌ | 需要连 Anthropic 官方技能仓库 |
| **Hooks 机制** | ❌ | 需要 OAuth 认证 |
| **`claude auth login`** | ❌ | 需要 Anthropic 账号 |

**如果用户需要飞书/微信集成，建议改用 OpenClaw（原生支持） 或 我（Hermes Agent）的飞书网关。**

### 与真实 Claude Code 的差距

| 对比项 | 真实 Claude Code | CCR + DeepSeek |
|--------|-----------------|----------------|
| 模型 | Claude Opus/Sonnet/Haiku | DeepSeek V4 |
| 编程核心能力 | 精良稳定 | 旗鼓相当（硬核任务） |
| 工程规范 | 代码更规范 | 略粗犷 |
| 多文件理解 | 超大上下文 | 稍弱 |
| 费用 | $20/月订阅 | ¥2/百万token |
| 国内可用 | ❌ 需翻墙+账号 | ✅ 直连 |
| **比喻** | 米其林厨师 | 夜市烧烤摊老板 |

---

## 常见问题与踩坑

### Q1: 代理能打开 Google，但 Claude Code 连不上
**原因**：Claude Code 不读环境变量（`http_proxy`），需要用 proxychains。
**解决**：`proxychains4 -q claude`

### Q2: 节点能打开网页，但 ERR_BAD_REQUEST
**原因**：免费节点的 IP 被 Anthropic 拉黑了。
**解决**：用 API2D 或 DeepSeek 中转站。

### Q3: WSL2 连不上 Clash 端口
**原因1**：Clash 的「局域网连接」没开 → 去 Clash 设置打开
**原因2**：Windows 防火墙拦截 → 临时关闭防火墙测试
**原因3**：WSL2 IP 变了（重启后） → 用 `cat /etc/resolv.conf | grep nameserver` 查新 IP

### Q4: TUN 模式开了但电脑断网
**原因**：免费节点扛不住 TUN 全局流量。
### Q5: settings.json 不起作用

**原因**：**Claude Code v2.1.x 完全不读环境变量配置**，无论是 `settings.json`、`config.json` 还是环境变量 `ANTHROPIC_API_KEY` — 全部忽略。

**原因2**：文件放到了错误的用户目录（如 root 用户却写到 /root/.claude/，但实际运行的是 user 用户）。

**解决**：不用折腾了，直接上 CCR。CCR 绕过 OAuth 不需要任何 settings.json。

### Q6: PowerShell 粘贴多行 JSON 卡死

**原因**：PowerShell 中直接粘贴 `{` 开头的 JSON 会被解析为脚本块，进入 `>>` 续行提示符。也可能因为光标不在行首，导致粘贴内容反序（每行按 `>>` 提示符逐行执行）。

**解决（二选一）：**
1. **用记事本创建配置文件（推荐 ⭐）：**
   ```powershell
   notepad "$env:USERPROFILE\.claude-code-router\config.json"
   ```
   弹出记事本 → 粘贴 JSON → Ctrl+S 保存 → 关闭
   ⚠️：如果提示"找不到是否重建"，选 **是/创建**
2. **单行命令**：压缩 JSON 为一行再 `Set-Content`，但注意转义

### Q7: ccr start 后无法输入新命令，按 Ctrl+C 退出了又得重开

**原因**：`ccr start` 是前台服务，占用终端。\
**解决**：永远保持 `ccr start` 在一个窗口跑，开第二个 PowerShell 窗口执行 `ccr code`。

### Q7: `wsl` 和 `sudo` 密码忘了
```powershell
# 在 PowerShell 中以 root 重置密码
wsl -u root passwd <用户名>
```

---

## 日常启动流程（Windows PowerShell + CCR 推荐方案）

```powershell
# 1. 确保 Clash Verge 已开启（可选，CCR+DeepSeek 国内直连不需要翻墙）
# 2. 打开 PowerShell

# 3. 启动 CCR 服务（窗口1，保持运行）
ccr start

# 4. 在第二个 PowerShell 窗口使用
ccr code -p "帮我写个Python脚本" --max-turns 5
```

## 🔑 关键发现：用户说的"龙虾"可能不是 Claude Code

**重要：** 国内开发者常把 **OpenClaw**（开源版 AI Agent）也叫做"龙虾"，因为它名字带 claw（爪）。OpenClaw 和 Claude Code 是完全不同的产品：

| 对比 | Claude Code | OpenClaw |
|------|-------------|----------|
| 厂商 | Anthropic 官方 | 开源社区（17万⭐） |
| 安装 | `npm i -g @anthropic-ai/claude-code` | `npm i -g openclaw` |
| 启动命令 | `claude` | `openclaw` |
| 飞书集成 | ❌ 需 Hook 配置 | ✅ 原生支持 |
| OAuth 认证 | ✅ 强制 | ❌ 不需要 |
| 国内可用 | ❌ 需翻墙 | ✅ 可配置国内模型 |
| 配置目录 | `~\.claude\` | `~\.openclaw\` |
| 端口 | 无（CLI 直连 API） | 默认 18789（HTTP 服务） |

**症状辨别法：** 如果用户说装了"龙虾"，但：
- 启动后显示 `OpenClaw` 字样 → 是 OpenClaw，不是 Claude Code
- 配置文件在 `~\.openclaw\` → 是 OpenClaw
- 飞书已经能回消息 → 是 OpenClaw（原生支持飞书）
- 启动后有 `Gateway`、`Scheduled Task`、端口监听等 → 是 OpenClaw（它是服务模式）

## 配套工具安装

### agent-browser（浏览器自动化）
```powershell
npm install -g agent-browser
# 验证
agent-browser --help
```

### jianying-editor-skill（剪映自动化）
剪映 Skill 让 AI 能通过 Python 代码自动生成和编辑剪映视频草稿。

**安装步骤：**

1. **剪映版本要求：** 实际测试 **9.5.0 版本**兼容
   - 官方 9.5.0 离线安装包（字节 CDN 链接可能已被重定向到最新版）
   - 建议从 **夸克网盘** 下载旧版：https://pan.quark.cn/s/18fa895fc8f5
   - 安装后打开剪映提示更新选"不更新"或"稍后提醒"

2. **下载 skill（GitHub 被墙时从服务器中转）：**
   ```powershell
   # 在服务器上先 git clone
   cd ~ && git clone https://github.com/luoluoluo22/jianying-editor-skill.git
   tar czf jianying-editor-skill.tar.gz jianying-editor-skill/
   
   # 从 Windows 拉取
   scp user@server:/path/to/jianying-editor-skill.tar.gz C:\\Users\\<用户名>\\Downloads\\
   tar -xzf C:\\Users\\<用户名>\\Downloads\\jianying-editor-skill.tar.gz -C $env:USERPROFILE\\.claude\\skills\\
   ```

3. **安装 Python 依赖：**
   ```powershell
   pip install uiautomation playwright pynput edge-tts pymediainfo
   ```

4. **初始化 playwright（可选，需要翻墙）：**
   ```powershell
   playwright install chromium
   ```
   ⚠️ 如果网络不通可跳过 — Chromium 只为 Web-to-Video 功能，基础剪辑用不到

5. **使用示例：**
   ```powershell
   ccr code "帮我把 assets/ 里的视频导入剪映，配 BGM，加标题"
   ```

### ⚠️ jianying-editor-skill 云端素材 403 问题

当运行示例脚本时，云端素材下载可能报 403 Forbidden：
```
[ERROR] Download error: 403 Client Error: Forbidden for url: https://...
```

**原因：** 该 skill 通过剪映的云端 API 下载素材，但未经剪映软件内的认证。即使登录了剪映账号也不行。

**解决：** 
- 在剪映软件内先**播放一次**要用的云端素材（建立本地缓存）
- 或者直接使用**本地素材**（自己录制的视频/图片/音乐），不依赖云端
- 核心功能（创建项目、TTS 配音、字幕、保存草稿）不受影响
- 测试命令（验证 skill 能否正常读取剪映草稿目录）：
  ```powershell
  python "C:\Users\<用户名>\.claude\skills\jianying-editor-skill\scripts\draft_inspector.py" list --limit 5
  ```

## 验证网络配置的测试命令

```bash
# 测试普通网页
curl -s -o /dev/null -w "%{http_code}" https://www.google.com

# 测试 Anthropic API
proxychains4 -q curl -s -o /dev/null -w "ANTHROPIC:%{http_code}" https://api.anthropic.com

# 测试中转站
curl -s -o /dev/null -w "API2D:%{http_code}" https://oa.api2d.net

# 测试 WSL2 到 Clash
curl http://172.21.128.1:7897 -s -o /dev/null -w "CLASH:%{http_code}" --connect-timeout 5
```

各返回码含义：
- `000` = 连接超时/不通
- `200/404` = 通了（正常）
- `403` = 被墙（代理没生效）
- `502` = 连上代理了但请求被拒
