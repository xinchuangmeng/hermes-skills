---
name: claude-code-wsl2-proxy-setup
description: 在WSL2 Ubuntu中配置Claude Code（龙虾）通过Clash Verge代理连接Anthropic API的完整指南。涵盖WSL2网络配置、proxychains强制代理、Clash设置、免费节点导入等踩坑经验。
version: 1.0
author: Hermes 小书童
tags: [claude-code, wsl2, proxy, clash-verge, proxychains, networking]
---

# Claude Code WSL2 代理配置指南

## 概述

Claude Code (v2.x) 是 Node.js 应用，在 WSL2 Ubuntu 中不读 `http_proxy`/`https_proxy` 等环境变量，无法通过常规代理设置访问 Anthropic API。需要用 proxychains 强制劫持其网络流量走代理。

## 前置条件

- Windows 已安装 **Clash Verge Rev**（或任何HTTP代理客户端）
- WSL2 Ubuntu 已安装 **Claude Code**
- 代理节点可用（能打开 Google 等外网）

## 步骤一：Clash Verge 配置

### 1.1 导入订阅
- Clash Verge → **订阅** 标签 → 粘贴订阅链接 → **导入** → **更新**
- 免费节点来源：FreeClashNode (https://node.freeclashnode.com/)、Pawdroid/Free-servers (GitHub)
- **只导入 YAML 格式（.yaml），不要用 .txt 格式**

### 1.2 确认设置
- **系统代理** → **开启**（绿色）
- **模式** → **「全局」**（不是「规则」）
- **局域网连接** → **开启**（Settings中，否则WSL2连不上）
- **端口** → 记下HTTP端口号（通常在Settings页面显示，如7897）
- **节点选择** → 选一个有延迟数字（ms）的节点
- 验证：Windows浏览器打开 https://www.google.com 能访问

### 1.3 ⚠️ 不要开 TUN 模式
免费节点扛不住 TUN 模式的全局流量，会导致电脑断网。
如果误开了 TUN（虚拟网卡模式），立即关掉恢复网络。

## 步骤二：WSL2 网络确认

### 2.1 获取宿主机IP
```bash
cat /etc/resolv.conf | grep nameserver
# 输出: nameserver 172.21.128.1
```

### 2.2 测试代理连通性
```bash
# 测试到Clash端口的连接
curl http://172.21.128.1:7897 -s -o /dev/null -w "%{http_code}" --connect-timeout 5
# 返回 502 = 端口通了（Clash返回的）
# 返回 000 = 没通

# 测试通过代理访问外网
curl --proxy http://172.21.128.1:7897 -s -o /dev/null -w "HTTP:%{http_code}" --connect-timeout 10 https://api.anthropic.com
# 返回 HTTP:404 = 代理通了（不带路径所以404正常）
```

## 步骤三：安装 proxychains

### 3.1 安装
```bash
sudo apt update
sudo apt install proxychains4 -y
```

### 3.2 配置
```bash
# 修改配置文件，将默认的 socks4 代理改为 http 代理
sudo sed -i 's/socks4.*/http 172.21.128.1 7897/' /etc/proxychains4.conf

# 验证配置
grep "http" /etc/proxychains4.conf | grep -v "^#"
# 应输出: http 172.21.128.1 7897
```

### 3.3 测试 proxychains
```bash
# 测试通过proxychains访问
proxychains4 -q curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 https://api.anthropic.com
# -q 是安静模式
```

## 步骤四：启动 Claude Code

```bash
proxychains4 -q claude
```

**注意：**
- 每打开一个新终端都要通过 `proxychains4 -q claude` 启动
- 不能用普通的 `claude` 命令（不走代理）
- 也可以设别名：`alias claude='proxychains4 -q claude'` 加到 `~/.bashrc`

## 常见问题

### Q: Claude Code 显示 "ERR_BAD_REQUEST"
- 通常是网络层面的请求被拒绝，不是 API Key 问题
- 确认 Clash 的节点是通的（浏览器能打开Google）
- 确认 proxychains 配置正确

### Q: WSL2 连不上 Clash 端口
- 检查 Clash 设置中 **「局域网连接」** 是否开启
- 检查 Windows 防火墙是否拦截
- 重启 Clash Verge 试试

### Q: 浏览器能打开Google但Claude Code还是连不上
- Claude Code (Node.js) 不读 `http_proxy` 环境变量
- 必须用 proxychains 强制劫持

### Q: 免费节点不稳定
- 免费节点通常几小时到几天就失效
- 节点失效时：Clash → 订阅 → 更新 → 选新节点
- 长期使用建议买付费机场（15-20元/月）

## 节点失效后恢复步骤
1. Clash Verge → **订阅** 标签 → **更新**
2. 如果订阅源已失效，删掉旧订阅，找新订阅链接导入
3. **代理** 标签 → 选新节点
4. 浏览器测试 Google 能打开
5. WSL2 重新用 `proxychains4 -q claude` 启动

## 密钥配置参考

### Kimi视觉模型（看图）
```
Base URL: https://api.moonshot.cn/v1
模型: moonshot-v1-32k-vision-preview（看图用）
API Key: sk-xxxxx
```
示例Python调用：
```python
import base64, json, urllib.request
with open('image.jpg', 'rb') as f:
    b64 = base64.b64encode(f.read()).decode()
data_url = f"data:image/jpeg;base64,{b64}"
payload = {
    "model": "moonshot-v1-32k-vision-preview",
    "messages": [{"role":"user","content":[{"type":"image_url","image_url":{"url":data_url}},{"type":"text","text":"描述这张图"}]}]
}
req = urllib.request.Request("https://api.moonshot.cn/v1/chat/completions",
    data=json.dumps(payload).encode(),
    headers={"Content-Type":"application/json","Authorization":"Bearer YOUR_KEY"})
```

## 版本历史
- 2026-05-08: 初版创建，记录Claude Code WSL2代理配置完整流程
