---
name: claude-code-china-network-setup
description: 在国内网络环境下配置Claude Code（龙虾）联网的完整流程。涵盖Clash Verge代理配置、WSL2 proxychains强制代理、API中转站（API2D）接入、DeepSeek Anthropic兼容接口、settings.json/apiKeyHelper以及OAuth登录问题处理。解决ERR_BAD_REQUEST无法连接Anthropic服务的根本问题。
---

# Claude Code 国内网络配置完整指南

## 问题背景

Claude Code 默认直连 `api.anthropic.com`，国内网络环境下：
- 直接连：被墙（HTTP 403）
- 普通代理：某些IP被Anthropic封禁（ERR_BAD_REQUEST）
- 环境变量设置：新版Claude Code v2.1.133+ **必须先OAuth登录一次**，settings.json/env不一定被读取

## 环境准备

### 1. WSL2 安装 Claude Code

```bash
# 进入WSL2
wsl

# 安装
npm install -g @anthropic-ai/claude-code

# 验证
claude --version
```

⚠️ **注意**：要在 WSL2 里装，不是 PowerShell！Claude Code 官方推荐 Linux 环境。

### 2. Clash Verge 代理配置

Windows 端装 Clash Verge Rev：
1. 下载：[GitHub Releases](https://github.com/clash-verge-rev/clash-verge-rev/releases)
2. 导入订阅（YAML格式，Clash Verge 不认 .txt 格式）
3. **关键设置**：
   - 顶部模式选 **「全局」**（不是「规则」）
   - **「系统代理」** 开关保持绿色
   - **「允许局域网连接」** 打开（WSL2访问宿主机需要）
   - 记下 **HTTP端口**（设置里查看）
4. 免费节点网站：FreeClashNode、clashnode.org

### 3. WSL2 代理配置

推荐用 **proxychains4** 强制所有程序走代理：

```bash
# 安装
sudo apt update && sudo apt install proxychains4 -y

# 配置（指向Windows宿主机Clash端口）
sudo sed -i 's/socks4.*/http 宿主机IP 端口/' /etc/proxychains4.conf

# 测试
proxychains4 -q curl -s -o /dev/null -w "%{http_code}" https://api.anthropic.com

# 启动龙虾
proxychains4 -q claude
```

**查宿主机IP：**
```bash
cat /etc/resolv.conf | grep nameserver
# 输出类似：nameserver 172.21.128.1
```

**常见Clash端口：** 设置里查看，如 7897、7890 等。

## 核心问题：Claude Code OAuth 登录

### 现象
- 设置了 `ANTHROPIC_BASE_URL` + `ANTHROPIC_API_KEY` / `ANTHROPIC_AUTH_TOKEN`
- 设置了 `~/.claude/settings.json` 的 `env` 或 `apiKeyHelper`
- 但 Claude Code 仍然报 `Not logged in` 或依然去连 `api.anthropic.com`

### 原因
Claude Code **v2.1.x 版本必须 OAuth 登录一次**，生成本地凭证后才能使用。环境变量和 settings.json 的配置只在 OAuth 登录之后才生效。

### 解决方案

**第1步：浏览器登录 Anthropic**
1. 确保 Clash 代理开启且节点有效
2. 浏览器打开 **https://claude.ai/login**
3. 注册/登录 Anthropic 账号

**第2步：命令行授权**
```bash
proxychains4 -q claude auth login
```
会弹出浏览器授权窗口，确认即可。

**第3步：登录后使用**
之后每次直接：
```bash
proxychains4 -q claude
```

## 可选方案：API 中转站

如果不想用 OAuth 登录，或者需要定向到国内 API 中转：

### 方案A：API2D（中转Anthropic API）
```bash
ANTHROPIC_BASE_URL=https://oa.api2d.net
ANTHROPIC_API_KEY=你的API2D_Key
```
**注意：** 这种方式仍然需要先 OAuth 登录一次。

### 方案B：DeepSeek Anthropic 兼容接口
```bash
ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
ANTHROPIC_AUTH_TOKEN=你的DeepSeek_Key
ANTHROPIC_MODEL=deepseek-chat
```
**注意：** 这种方式仍然需要先 OAuth 登录一次。

### 验证API是否可用
```bash
# 测试API2D
curl -s https://oa.api2d.net/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 你的Key" \
  -d '{"model":"claude-sonnet-4-20250514","messages":[{"role":"user","content":"hi"}],"max_tokens":10}'

# 测试DeepSeek
curl -s https://api.deepseek.com/anthropic/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: 你的DeepSeek_Key" \
  -H "anthropic-version: 2023-06-01" \
  -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"hi"}],"max_tokens":10}'
```

## settings.json 配置（OAuth登录后的个性化配置）

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
    "ANTHROPIC_AUTH_TOKEN": "你的Key",
    "ANTHROPIC_MODEL": "deepseek-chat",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"
  },
  "apiKeyHelper": "echo 你的Key",
  "permissions": {
    "allow": ["Bash", "Read", "Edit", "Write"],
    "deny": []
  }
}
```

**路径：** `~/.claude/settings.json`

## 已知问题与陷阱

1. **ERR_BAD_REQUEST** ≠ 网络不通。Claude Code报了ERR_BAD_REQUEST但curl能通，说明网络已经连上了，但API层面拒绝了（IP被封、地区限制等）。
2. **免费节点IP容易被Anthropic封禁** → 用API中转站或DeepSeek兼容接口。
3. **Clash「规则」模式不走代理** → 一定要改成「全局」或确认规则放行了Anthropic。
4. **WSL2 IP会变** → 每次重启WSL2的IP可能变化，但宿主机IP（172.21.128.1）通常不变。
5. **TUN模式慎用** → 免费节点开TUN可能拖垮整个电脑的网络。
6. **settings.json的`env`字段不一定被读取** → 保险起见用`apiKeyHelper`或在启动命令前直接设环境变量。
7. **Claude Code v2.1.132+必须先OAuth登录** → 跑`claude auth login`后浏览器授权。

## 核心方案：Claude Code Router（CCR）绕过OAuth ⭐

**对于国内用户，CCR 是目前最可靠的方案**，因为 Claude Code v2.1.x 强制 OAuth 登录，而国内注册 Anthropic 账号困难（需海外手机号/信用卡）。

### CCR 的工作原理

```
用户输入 ccr code "帮我写个脚本"
    ↓
CCR 启动本地代理服务（端口3456）
    ↓
截获 Claude Code 的 API 请求
    ↓
转发到 DeepSeek / 智谱 / OpenRouter 等国内可用 API
    ↓
国内 API 返回结果 → CCR 伪装成 Claude 响应
    ↓
绕开 Anthropic OAuth 登录
```

### 安装步骤（PowerShell）

```powershell
# 1. 安装 CCR
npm install -g @musistudio/claude-code-router

# 2. 创建配置
mkdir "$env:USERPROFILE\.claude-code-router"
```

用记事本创建 `$env:USERPROFILE\.claude-code-router\config.json`：

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
      "api_key": "你的DeepSeek_API_Key",
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

### 启动和使用

**终端1（保持运行）：**
```powershell
ccr start
```

**终端2（执行任务）：**
```powershell
ccr code "你的任务描述"
```

### CCR 的 DeepSeek 替代方案

| Provider | API端点 | 说明 |
|----------|---------|------|
| **DeepSeek**（推荐） | `https://api.deepseek.com/chat/completions` | 便宜，编程能力强，国内直连 |
| **API2D**（中转Claude） | `https://oa.api2d.net` | 可以真正调用Claude模型，但贵 |
| **智谱GLM** | `https://open.bigmodel.cn/api/paas/v4/chat/completions` | 国内模型，兼容性一般 |
| **SiliconFlow** | 见CCR文档 | 支持多种开源模型 |

### 重要：终端环境问题

```
❌ Git Bash / MSYS2 → `node: not found`（找不到Node.js）
❌ WSL2 Ubuntu → 依赖proxychains4代理（但CCR可国内直连npm安装）
✅ Windows PowerShell → 推荐！Node.js路径正确，npm安装正常
```

**推荐使用 Windows PowerShell 而非 WSL2/Git Bash 运行 CCR。**

### 常见问题

1. **`ccr start` 后一直挂着没反应** → 正常，服务在后台等待请求
2. **`ccr code` 卡在欢迎页** → 按 Ctrl+C 退出，用 `ccr code -p "指令" --max-turns 1` 跳过欢迎页
3. **配置文件写错格式** → 用记事本打开 `~/.claude-code-router/config.json` 手动编辑，PowerShell 的 heredoc 容易粘贴错
4. **PowerShell 粘贴出错** → 先复制文本，在终端点右键粘贴（不要用Ctrl+V）

## 快速启动命令（打开PowerShell后）

```powershell
# 终端1：启动CCR服务
ccr start

# 终端2：用龙虾干活
ccr code "写一个Python脚本读取当前目录文件"
```

## 版本历史
- 初始创建：2026-05-08
- 更新：2026-05-08 — 补充CCR方案作为核心推荐方案，PowerShell环境说明，JSON配置方法
