---
name: Hermes Multi-Agent Port Configuration
description: 配置多个Hermes Agent使用不同端口，避免端口冲突，实现并行运行
tags: [hermes, multi-agent, port-configuration, gateway]
---

# Hermes多Agent端口配置指南

## 问题背景
当需要运行多个Hermes Agent实例时，会遇到端口冲突问题。默认情况下，所有Agent都尝试监听3000端口，导致只有一个能成功启动。

## 解决方案
为每个Agent配置不同的端口，实现并行运行。

## 操作步骤

### 1. 检查当前端口占用
```bash
# 查看3000端口是否被占用
ss -tlnp | grep :3000

# 查看3001端口是否可用
ss -tlnp | grep :3001
```

### 2. 创建新Profile（如果尚未创建）
```bash
# 使用官方推荐方法创建新Profile
hermes profile create <profile-name> --clone

# 例如
hermes profile create southeast-ecommerce --clone
```

### 3. 修改Profile的端口配置
```bash
# 编辑Profile的config.yaml
nano ~/.hermes/profiles/<profile-name>/config.yaml
```

在文件末尾添加：
```yaml
gateway:
  host: "0.0.0.0"
  port: <unique-port-number>  # 例如3001、3002等
```

### 4. 配置独立的飞书应用
```bash
# 编辑Profile的.env文件
nano ~/.hermes/profiles/<profile-name>/.env
```

修改飞书配置：
```bash
FEISHU_APP_ID=新的AppID
FEISHU_APP_SECRET=新的AppSecret
# 可选：如果飞书平台生成
FEISHU_ENCRYPT_KEY=加密密钥
FEISHU_VERIFICATION_TOKEN=验证Token
```

### 5. 启动新Agent
```bash
# 方法1：使用Profile命令
<profile-name> gateway run

# 方法2：使用-p参数
hermes -p <profile-name> gateway run
```

### 6. 验证启动成功
```bash
# 检查端口监听
ss -tlnp | grep :<port-number>

# 检查进程
ps aux | grep "hermes.*gateway" | grep -v grep

# 检查Profile状态
hermes profile list
```

### 7. 配置飞书事件订阅
在飞书开放平台配置事件订阅：
- **请求地址URL**：`https://<服务器IP>:<端口>/webhook/feishu`
- **加密密钥**：在飞书平台生成
- **验证Token**：在飞书平台生成
- **订阅事件**：`im.message.receive_v1`

## 示例配置

### Profile A（默认）
- **名称**：default
- **端口**：3000
- **飞书App ID**：cli_a96ef9bf23b8dbb4
- **事件订阅URL**：`https://42.193.201.6:3000/webhook/feishu`

### Profile B（东南亚电商助手）
- **名称**：southeast-ecommerce
- **端口**：3001
- **飞书App ID**：cli_a96d18e5d2f89bde
- **事件订阅URL**：`https://42.193.201.6:3001/webhook/feishu`

## 诊断检查清单

在配置多Agent时，使用以下系统化检查步骤：

### 1. 进程状态检查
```bash
# 检查所有Hermes相关进程
ps aux | grep -E "(hermes|python.*hermes)" | grep -v grep

# 检查系统服务状态
systemctl --user list-units --type=service --state=running | grep -i hermes
systemctl --user status hermes-gateway.service
```

### 2. 端口监听检查
```bash
# 检查常见端口
ss -tlnp | grep -E "(3000|3001|3002|3003)"

# 注意：Hermes网关可能使用WebSocket连接，不一定监听HTTP端口
# 检查网关日志确认连接方式
journalctl --user -u hermes-gateway.service -n 20 --no-pager
```

### 3. Profile状态检查
```bash
# 查看所有Profile状态
hermes profile list

# 检查Profile配置
ls -la ~/.hermes/profiles/
```

### 4. 配置一致性检查
```bash
# 检查项目特定配置
find ~/projects -name "*config*.yaml" -o -name "*config*.yml" 2>/dev/null

# 检查配置目录结构
ls -la ~/ | grep -E "(hermes|project)"
```

## 关键发现与注意事项

### 发现1：WebSocket连接模式
- Hermes网关可能使用WebSocket直接连接飞书，而不是监听HTTP端口
- 这意味着端口检查可能显示"无监听"，但网关实际上在工作
- 验证方法：检查网关日志中的WebSocket连接信息

### 发现2：Profile状态与实际运行可能不一致
- `hermes profile list`可能显示Profile为"running"，但实际没有进程在运行
- 需要结合进程检查(`ps aux`)和端口检查确认实际状态

### 发现3：配置分散问题
- 配置可能分布在：项目目录、Profile目录、主配置文件
- 这可能导致配置不一致和难以诊断的问题
- 建议：统一使用Profile配置，避免分散配置

### 发现4：端口3001常见问题
- 多个项目可能配置使用3001端口
- 但实际可能没有服务在监听该端口
- 需要检查：Profile是否启动、端口是否被占用、配置是否正确

## 常见问题

### Q1：启动失败，提示"address already in use"
**原因**：端口被其他进程占用。
**解决**：
1. 检查端口占用：`ss -tlnp | grep :<端口>`
2. 停止占用进程或更换端口
3. 修改config.yaml中的端口号

### Q2：飞书消息路由错误
**原因**：飞书App ID配置错误或事件订阅URL端口不对。
**解决**：
1. 确认.env中的FEISHU_APP_ID与飞书平台一致
2. 确认事件订阅URL端口与config.yaml中的端口一致
3. 重启gateway：`systemctl --user restart hermes-gateway`

### Q3：Profile显示"running"但端口无监听
**原因**：Hermes网关可能使用WebSocket连接飞书，而不是监听HTTP端口。
**诊断**：
1. 检查网关日志：`journalctl --user -u hermes-gateway.service`
2. 查找WebSocket连接信息（如"connected to wss://"）
3. 确认飞书连接状态

### Q4：配置分散在不同位置
**现象**：配置在项目目录、Profile目录和主配置文件中都有。
**解决**：
1. 统一配置位置，优先使用Profile配置
2. 检查配置优先级：Profile > 项目配置 > 主配置
3. 使用环境变量或配置文件引用统一配置路径

## 最佳实践

1. **端口规划**：提前规划端口号，避免冲突
2. **命名规范**：Profile名称使用小写字母和连字符
3. **配置备份**：修改前备份重要配置文件
4. **逐步验证**：每步完成后验证，避免问题累积
5. **日志监控**：启动后立即查看日志，快速定位问题

## 注意事项

1. **防火墙**：确保服务器防火墙开放对应端口
2. **HTTPS**：飞书事件订阅要求HTTPS，需要配置SSL证书或使用反向代理
3. **资源占用**：每个Agent独立运行，注意服务器资源
4. **内存隔离**：每个Profile有独立的内存和会话，不会相互干扰