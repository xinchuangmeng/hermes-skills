---
name: hermes-windows-wsl2-install
description: 在Windows上安装Hermes Agent的完整教程——包括WSL2方案和Windows原生(PowerShell)方案。国内网络环境下的踩坑指南：GitHub被墙处理(代理/ZIP自动降级/手动ZIP)、winget缺失处理、py pip镜像配置、hermes model命令的坑（不支持多参数）、PATH配置、API Key设置、飞书配置等。
version: 2.0.0
author: Hermes 小书童（实战总结 v2.0）
license: MIT
metadata:
  hermes:
    tags: [hermes, windows, wsl2, installation, setup]
    related_skills: [learning-hermes-agent, hermes-multi-agent-port-configuration]
---

# Windows安装Hermes Agent教程（WSL2 + 原生双方案）

本技能包含两种安装方式：**WSL2方案**（通过Windows的Linux子系统）和 **Windows原生方案**（PowerShell直接安装，无需WSL）。

---

## 方案A：Windows原生安装（无需WSL，推荐）

Hermes官方提供了PowerShell安装脚本，支持直接在Windows上安装运行。

### 前置条件

- Windows 10/11 或 Windows Server
- 管理员身份

### 一步安装（需能直连GitHub）

```powershell
irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1 | iex
```

### 国内网络环境安装（GitHub被墙时的完整流程）

#### 前置检查：Windows Server vs Windows 桌面版

- **Windows 10/11 桌面版** — 有 `winget`，可以 `winget install Git.Git`
- **Windows Server** — ❌ 没有winget，必须去官网下载Git安装包

#### 第一步：手动安装Git（Windows Server无winget方案）

```powershell
# 检查Git是否已装
git --version

# 如果没有Git，去官网下载：
# https://git-scm.com/download/win
# 或者用腾讯软件中心：https://pc.qq.com/ 搜"Git"

# Windows Server没有winget，只能用浏览器下载
```

#### 第二步：设置代理（如果有代理工具）

```powershell
# Clash默认端口7890
$env:HTTP_PROXY="http://127.0.0.1:7890"
$env:HTTPS_PROXY="http://127.0.0.1:7890"

# v2rayN默认端口10809
$env:HTTP_PROXY="http://127.0.0.1:10809"
$env:HTTPS_PROXY="http://127.0.0.1:10809"

# 设置代理后再运行安装脚本
irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1 | iex
```

#### 第三步：如果代理不可用（Git clone/ZIP下载都失败时的终极方案）

如果你设了代理（`$env:HTTPS_PROXY`）但提示"由于目标计算机积极拒绝，无法连接"，说明**代理工具没开或端口不对**。先关掉代理再试：

```powershell
$env:HTTP_PROXY=""
$env:HTTPS_PROXY=""
```

关掉代理后，安装脚本会**自动降级为ZIP下载**（从GitHub下载源码ZIP包），这是正常的，耐心等待即可。

**如果ZIP下载也失败**（raw.githubusercontent.com被墙），手动方案：
```powershell
# 1. 打开浏览器访问 https://github.com/NousResearch/hermes-agent
# 2. 点绿色"Code"按钮 → "Download ZIP"
# 3. 解压到 %LOCALAPPDATA%\hermes\hermes-agent\
# 4. 然后跳到第四步手动pip安装
```

#### 第四步：PyPI包下载失败处理

如果安装脚本在装Python依赖时报错（`tcp connect error` / `目标计算机积极拒绝`），说明代理或网络有问题。手动安装：

```powershell
# 进入Hermes目录
cd $env:LOCALAPPDATA\hermes\hermes-agent

# 激活虚拟环境
venv\Scripts\activate

# 用清华镜像安装依赖
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -e ".[all]"

# 把hermes加到系统PATH
$hermesPath = "$env:LOCALAPPDATA\hermes\hermes-agent\venv\Scripts"
[Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path", "User") + ";" + $hermesPath, "User")
```

#### 第五步：验证安装

```powershell
# 关掉PowerShell重新打开
hermes version
```

应该输出类似 `Hermes Agent v0.13.0 (2026.5.7)`

#### 第六步：配置LLM模型

⚠️ **关键坑：`hermes model set` 命令不接受多参数**

```powershell
# ❌ 错误写法（会报 unrecognized arguments）
hermes model set deepseek deepseek-chat

# ✅ 正确做法：不带参数运行 model 命令，进入交互式菜单
hermes model
```

交互式菜单步骤：
1. 选 **16. DeepSeek**（如果默认是别的）
2. 输入你的 DeepSeek API Key
3. 模型选 **2. deepseek-chat**（不要选deepseek-v4-flash，新账号可能没开通）

或者手动配Key再用交互菜单选模型：
```powershell
hermes config set DEEPSEEK_API_KEY sk-你的key
hermes model
```

### 第七步：配置飞书

安装完后运行 `hermes setup`，选 Quick setup，一路确认DeepSeek配置后，在消息平台列表中找到 **10. 飞书/Feishu**。如果显示[✓] configured说明之前配置已导入，直接确认即可。

### 第八步：飞书配置（手动修改.env）

如果 `hermes setup` 向导配飞书失败（一直问Telegram token），可以直接手动修改配置文件：

```powershell
# 编辑 .env 文件，加入飞书配置
notepad $env:USERPROFILE\\.hermes\\.env
```

添加以下内容：
```
FEISHU_APP_ID=cli_你的AppID
FEISHU_APP_SECRET=你的AppSecret
FEISHU_VERIFICATION_TOKEN=你的验证Token（非必须）
FEISHU_HOME_CHANNEL=oc_你的群ID
FEISHU_CONNECTION_MODE=websocket
```

然后编辑 config.yaml：
```powershell
notepad $env:USERPROFILE\\.hermes\\config.yaml
```

确保 `feishu:` 部分有完整配置（注意YAML缩进）：
```yaml
feishu:
  - type: lark
    app_id: cli_你的AppID
    app_secret: 你的AppSecret
    connection_mode: websocket
    home_channel: oc_你的群ID
```

### 第九步：启动

```powershell
hermes
```

如果启动后飞书报 `No module named 'openai'`，说明虚拟环境缺包：
```powershell
# 退出Hermes后执行
cd $env:LOCALAPPDATA\\hermes\\hermes-agent
.\\venv\\Scripts\\python.exe -m pip install openai
# 如果报 pip 不存在，先装 pip
.\\venv\\Scripts\\python.exe -m ensurepip --upgrade
.\\venv\\Scripts\\python.exe -m pip install openai
```

### 卸载WSL2（可选）

如果之前装了WSL2版的Hermes，确定不用了可以删除释放空间：
```powershell
# 查看WSL实例
wsl -l -v

# 删除（注意：这会删除WSL里所有数据！）
wsl --unregister Ubuntu
```

#### 安装目录

- **源码位置**: `%LOCALAPPDATA%\hermes\hermes-agent\`
- **配置文件**: `%USERPROFILE%\.hermes\`
- **hermes命令**: `%LOCALAPPDATA%\hermes\hermes-agent\venv\Scripts\hermes.exe`

---

## 方案B：WSL2安装

## 前置条件

- Windows 10/11
- BIOS已开启虚拟化（Intel VT-x / AMD-V）

## 第一步：安装WSL2

以**管理员身份**打开PowerShell，执行：

```powershell
wsl --install
```

安装完成后重启电脑。系统会自动安装Ubuntu最新LTS版本。

如果只想装特定版本：
```powershell
wsl.exe --install Ubuntu-20.04
```

## 第二步：首次启动WSL

重启后，开始菜单搜索"Ubuntu"启动，第一次会要求设置**用户名和密码**——这是WSL独立的用户名密码，**跟Windows登录密码没关系**。

## 第三步：如果忘记WSL密码

如果在WSL里 `sudo` 时提示 `Sorry, try again`，说明密码不对，按以下步骤重置：

1. 关掉WSL窗口
2. 以管理员身份打开Windows PowerShell
3. 进入WSL root模式：

```powershell
wsl -u root
```

4. 重置密码（将 `用户名` 换成WSL的用户名）：

```bash
passwd 用户名
```

5. 输入新密码两次（输入时不显示，正常）
6. 看到 `password updated successfully` 后退出：

```bash
exit
exit
```

7. 重新打开WSL，用新密码登录

## ⚠️ 重要：两个不同的Hermes

WSL的 pip 源里有两个不同的"hermes"：
- **`hermes`**（学术版v0.9.1）—— 旧的学术研究工具，不是智能体
- **`hermes-agent`**（智能体版v0.12.0+）—— 我们要装的AI智能体框架

**不要用 `pipx install hermes`，那是旧版。** 用一键安装脚本安装 Hermes Agent。

在WSL终端里，按顺序执行：

```bash
# 1. 更新软件源
sudo apt update

# 2. 安装Python（通常WSL自带）
sudo apt install python3 python3-pip python3-venv -y

# 3. 安装pipx（Ubuntu 24.04+禁止直接用pip装系统包，必须用pipx）
sudo apt install pipx -y

# 4. 用pipx安装Hermes
pipx install hermes

# 5. 添加PATH
pipx ensurepath

# 6. 生效配置
source ~/.bashrc

# 7. 启动
hermes
```

## 启动Hermes

以后每次使用，在WSL终端里直接输入：
```bash
hermes
```

注意：**不能在Windows的CMD或PowerShell里打hermes**，必须在WSL的Linux环境里。

## 关键踩坑总结（基于多次实战）

### 1. pip vs pipx vs 一键脚本
**正确做法：** 用 `curl` 一键安装脚本（从GitHub clone），不要在系统层用pip或pipx装。

### 2. 安装卡住时怎么办
如果 `sudo apt install` 卡在配置ffmpeg等包，直接 `Ctrl+C` 中断，进入虚拟环境安装：
```bash
cd ~/.hermes/hermes-agent && source venv/bin/activate && pip install --break-system-packages -e .
```

### 3. 终端输入不显示
Linux终端输入密码和API Key时完全不显示内容，这是安全设计，正常输入后直接回车即可。
最佳做法：先在记事本复制好，在WSL终端里点鼠标右键粘贴。

### 4. 飞书Gateway连不上（错误码1000040345）
三步排查：
- 检查 `.env` 里App Secret是否被重复粘贴（常见错误）
- 检查飞书开放平台应用是否已发布（状态必须为"已启用"）
- 检查事件订阅是否配置了 `im.message.receive_v1` 且用长连接

### 5. 飞书开放平台必须手动操作的配置
Gateway配了App ID/Secret还不够，还必须在飞书开放平台手动：
- 启用机器人能力
- 添加权限（im:message等5项）
- 配置事件订阅（长连接 + im.message.receive_v1）
- 发布版本
