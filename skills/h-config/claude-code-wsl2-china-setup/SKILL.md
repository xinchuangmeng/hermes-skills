---
name: claude-code-wsl2-china-setup
description: 在国内网络环境下，通过WSL2安装和配置Claude Code（龙虾）的完整指南。包括PowerShell误装处理、代理配置、Clash Verge Rev免费节点获取、WSL2代理环境变量设置等全部踩坑经验。
version: 1.0
author: Hermes 小书童
---
# 代理配置关键发现（2026-05-08经验）
# Claude Code (Node.js) 不认 http_proxy 环境变量！
# 正确的做法：
#   1. Clash Verge 开「局域网连接」+ 全局模式 + 系统代理
#   2. WSL2 设置 export https_proxy/http_proxy（可验证curl走代理）
#   3. 但对于Claude Code本身，环境变量方式经常无效
#   4. 替代方案：proxychains 强制走代理，或开 TUN 模式
# 注意：免费节点不支持 TUN 模式，开了会断网
# 推荐用 proxychains4: proxychains4 claude
#
# 【2026-05-08 更新】核心踩坑：
# 1. 即使 proxychains4 + curl 能通（返回404/200），Claude Code 仍可能 ERR_BAD_REQUEST
# 2. 根本原因：免费节点的出口IP被Anthropic封禁了（公共IP多人共用）
# 3. 解决方案：改用国内API中转站（API2D等）设置 ANTHROPIC_BASE_URL
# 4. 或使用付费机场的独享IP节点
# 5. WSL2 IP会变！每次重启WSL2后需重新检查 cat /etc/resolv.conf | grep nameserver
# 6. Clash Verge端口不一定是默认7890，实际是7897（自定义端口已在设置里配好）
# 7. Kimi Moonshot API可用于备选视觉识别（国内直连不走代理）

---

# claude-code-wsl2-china-setup

## 概述

Claude Code（俗称龙虾）是Anthropic的AI编码智能体CLI。国内用户需要处理两大问题：
1. 正确安装到WSL2（非PowerShell）
2. 配置网络代理使其能访问Anthropic API

## 第一步：确认安装位置（关键坑）

⚠️ **Claude Code必须装在WSL2里，不要装在Windows PowerShell！**

### 检查是否装错位置
```powershell
# 在PowerShell里查
npm list -g @anthropic-ai/claude-code
```
如果在PowerShell里看到了，说明装错了。Claude Code的Windows原生兼容性差，文件读写、脚本执行容易出问题。

### 正确安装到WSL2
```bash
# 打开WSL2终端
wsl

# 确保Node.js 20+
node --version

# 全局安装
npm install -g @anthropic-ai/claude-code

# 验证
claude --version
```

### 清理PowerShell版（可选）
```powershell
# 在PowerShell里执行
npm uninstall -g @anthropic-ai/claude-code
```
不删也没关系，WSL2和Windows的npm全局包是独立目录，互不干扰。

## 第二步：配置网络代理

Claude Code需要直连 `api.anthropic.com`，国内需代理。

### 获取WSL2宿主IP
```bash
cat /etc/resolv.conf | grep nameserver
# 输出示例：nameserver 172.21.128.1
```

### Windows端：安装代理客户端

推荐Clash Verge Rev（社区维护，免费开源）：
- GitHub：https://github.com/clash-verge-rev/clash-verge-rev
- 下载：amd64选 `Clash.Verge_x.x.x_x64-setup.exe`

**配置步骤：**
1. 安装后打开软件
2. 点「订阅」→ 导入订阅链接
3. 推荐免费节点源：https://github.com/Pawdroid/Free-servers
   - 订阅链接：`https://proxy.v2gh.com/https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub`
4. 导入后点「更新」
5. 选一个节点（美国/英国等）
6. 模式选「全局」
7. 打开「系统代理」开关（绿色）

其他免费节点站：
- https://www.freeclashnode.com/free-node/（每日更新）
- 支持YAML格式直接导入Clash Verge

### WSL2设置代理环境变量

```bash
export https_proxy=http://172.21.128.1:7890
export http_proxy=http://172.21.128.1:7890
```

注意：7890是Clash默认端口，如果代理软件用其他端口则修改。

### 永久设置（写入~/.bashrc）
```bash
echo 'export https_proxy=http://172.21.128.1:7890' >> ~/.bashrc
echo 'export http_proxy=http://172.21.128.1:7890' >> ~/.bashrc
source ~/.bashrc
```

## 第三步：启动Claude Code

```bash
# 首次启动（会弹出浏览器登录Anthropic账号）
claude

# 登录完成后进入交互模式
# 或一次性任务模式
claude -p "你的任务" --max-turns 5

# 跳过权限确认（用于自动化）
claude --dangerously-skip-permissions
```

## 第四步：WSL2代理调试流程

```bash
# 用curl测试代理是否通（返回200=通，000=不通）
curl -x http://172.21.128.1:7897 -s -o /dev/null -w "%{http_code}" --connect-timeout 10 https://www.google.com

# 查看WSL2自身IP（排查IP变化问题）
ip addr show eth0 | grep inet
```

## 第五步：验证Claude Code是否能连接

```bash
export https_proxy=http://172.21.128.1:7897
export http_proxy=http://172.21.128.1:7897
claude
```

如果curl返回`000`+超时，按排查清单逐步检查。

## 常见问题

### Q: curl返回000，代理不通
A: 逐步排查：
1. **Clash Verge右上角开关** → 必须是**绿色**（开启）
2. **顶部模式** → 必须是**「全局」**（规则模式可能不走API流量）
3. **设置 → 局域网连接** → **必须开启**（WSL2通过局域网连接Windows）
4. **设置 → 端口设置** → 记下HTTP端口号（不一定是7890，可能是7897或其他）
5. **选中的节点** → 节点必须有延迟数字（ms），显示Error的节点是失效的
6. **用浏览器测试** → 打开 https://www.google.com，打不开说明节点已失效

### Q: 免费节点失效了怎么办？
A: 免费节点通常不稳定，几个小时后就会失效。处理方式：
1. 在Clash Verge「订阅」中删除旧订阅，导入新的免费节点
2. 免费节点站每日更新：https://node.freeclashnode.com/
3. GitHub更新源：https://github.com/Pawdroid/Free-servers
4. yaml格式直接支持Clash Verge，txt格式需转换
5. 如果频繁使用，建议买付费机场（15-20元/月，稳定得多）

### Q: 浏览器登录弹不出来
A: 确保Windows系统代理已开启（Clash Verge的"系统代理"开关为绿色）。如果还不行，手动访问 https://console.anthropic.com/ 登录后获取API Key，用环境变量方式：
```bash
export ANTHROPIC_API_KEY=你的key
claude --dangerously-skip-permissions
```

### Q: claude --version 显示版本但 claude 启动不了
A: 通常是网络问题。先确认 `curl -x http://你的宿主机IP:端口 -s -o /dev/null -w "%{http_code}" https://api.anthropic.com` 能不能通。

### Q: proxychains4+curl通了，但claude还是ERR_BAD_REQUEST？
A: 这是因为免费节点的IP被Anthropic API层面封禁了（公共IP多人共用）。解决方法：
1. **使用API中转站**（如 API2D）：设置环境变量 `export ANTHROPIC_BASE_URL=https://你的中转站地址`
2. **换付费机场**：独享IP节点，15-20元/月
3. **换DeepSeek的Anthropic兼容接口**：`export ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic`
4. 注意：ERR_BAD_REQUEST 表示网络通了但API拒绝了，ERR_CONNECTION 表示网络不通

### Q: 如何用proxychains4强制claude走代理？
```bash
# 1. 安装
sudo apt update && sudo apt install proxychains4 -y

# 2. 配置（将socks4改为http代理）
sudo sed -i 's/socks4.*/http 你的宿主机IP 你的端口/' /etc/proxychains4.conf

# 3. 验证配置
grep -v "^#" /etc/proxychains4.conf | grep "http"

# 4. 测试（返回404或200即通）
proxychains4 -q curl -s -o /dev/null -w "%{http_code}" https://api.anthropic.com

# 5. 启动claude
proxychains4 -q claude
```

### Q: 装了proxychains4后却找不到命令？
A: 可能安装不完整，重新安装：
```bash
sudo apt install --reinstall proxychains4 -y
which proxychains4  # 应显示 /usr/bin/proxychains4
```

### Q: WSL2密码忘了怎么办？
A: 在PowerShell里用root重置：
```powershell
wsl -u root passwd 你的用户名
```

### Q: Clash Verge的TUN模式开了但断网？
A: 免费节点不支持TUN模式（流量扛不住），立即关掉：
1. Clash Verge → 设置 → 虚拟网卡模式 → 关掉（灰色）
2. 只用「系统代理」+「全局」模式即可

### Q: PowerShell也装了，WSL2也装了，冲突吗？
A: 不冲突。PowerShell里的claude和WSL2里的claude是两个独立的程序，调用路径不同。建议只用WSL2版本。

### Q: 内置看图工具拦截了图片怎么办？
A: 可用Kimi/Moonshot API作为备选视觉识别方案：
- Base URL: `https://api.moonshot.cn/v1`（国内直连，不需代理）
- 模型名: `moonshot-v1-32k-vision-preview`（支持图片理解）
- Key来源: platform.kimi.ai 或 platform.moonshot.cn
- 注意：内容过滤较严格，prompt要简短精准

## Clash Verge关键设置检查清单

| 检查项 | 位置 | 正确状态 |
|--------|------|---------|
| 系统代理开关 | 主界面右上角 | 🟢 绿色（开启） |
| 代理模式 | 主界面顶部 | 🌍 全局 |
| 系统代理设置 | 设置页 | ✅ 开启（蓝色） |
| 局域网连接 | 设置页 | ✅ 开启（蓝色） |
| HTTP端口 | 设置页→端口设置 | 记下号码（如7897） |
| 选中节点 | 代理页 | 有延迟数字ms |
| Windows浏览器测试 | 打开google.com | ✅ 能正常访问 |
