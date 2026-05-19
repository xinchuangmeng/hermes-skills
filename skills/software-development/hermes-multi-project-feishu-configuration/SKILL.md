---
name: Hermes Multi-Project Feishu Configuration
description: Configure and run multiple Hermes Agent instances for different projects with independent Feishu applications
tags: [hermes, multi-agent, feishu, systemd, profile-management]
---

# Hermes多项目飞书配置指南

## 问题背景
当需要为不同项目（如ResearchAudit和东南亚电商）运行独立的Hermes Agent实例时，需要：
1. 每个项目有独立的飞书应用配置
2. 多个Agent同时运行且互不干扰
3. 独立的配置、内存和会话隔离

## 解决方案
使用Hermes Profile和系统服务隔离，为每个项目创建独立的运行环境。

## 操作步骤

### 1. 检查现有Profile状态
```bash
# 查看所有Profile及其状态
hermes profile list

# 示例输出：
# Profile          Model            Gateway      Alias
# default         deepseek-chat    running      —
# southeast-ecommerce deepseek-chat    stopped      southeast-ecommerce
```

### 2. 创建或配置Profile
```bash
# 如果Profile不存在，创建新Profile
hermes profile create <project-name> --clone

# 例如
hermes profile create southeast-ecommerce --clone
```

### 3. 配置Profile的飞书设置
编辑Profile的配置文件：
```bash
# 编辑config.yaml设置端口（可选）
nano ~/.hermes/profiles/<project-name>/config.yaml
```

在文件末尾添加：
```yaml
gateway:
  host: "0.0.0.0"
  port: <unique-port>  # 例如3001、3002等
```

编辑环境变量文件：
```bash
# 编辑.env设置飞书应用
nano ~/.hermes/profiles/<project-name>/.env
```

添加飞书配置：
```bash
# 项目特定的飞书应用
FEISHU_APP_ID=cli_xxxxxxxxxxxxxxx  # 新的App ID
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxx
FEISHU_ENCRYPT_KEY=你的加密密钥
FEISHU_VERIFICATION_TOKEN=验证Token
FEISHU_DOMAIN=feishu
FEISHU_CONNECTION_MODE=websocket
```

### 4. 创建独立的系统服务
为每个Profile创建独立的systemd服务文件：

```bash
# 创建服务文件
nano ~/.config/systemd/user/hermes-<project-name>.service
```

服务文件内容：
```ini
[Unit]
Description=Hermes Agent Gateway - <Project Name> Project
After=network.target
StartLimitIntervalSec=600
StartLimitBurst=5

[Service]
Type=simple
ExecStart=/home/agentuser/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main gateway run --replace -p <project-name>
WorkingDirectory=/home/agentuser/.hermes/hermes-agent
Environment="PATH=/home/agentuser/.hermes/hermes-agent/venv/bin:/home/agentuser/.hermes/hermes-agent/node_modules/.bin:/home/agentuser/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="VIRTUAL_ENV=/home/agentuser/.hermes/hermes-agent/venv"
Environment="HERMES_HOME=/home/agentuser/.hermes/profiles/<project-name>"
Restart=on-failure
RestartSec=30
RestartForceExitStatus=75
KillMode=mixed
KillSignal=SIGTERM
ExecReload=/bin/kill -USR1 $MAINPID
TimeoutStopSec=60
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
```

### 5. 启动和管理服务
```bash
# 重新加载systemd配置
systemctl --user daemon-reload

# 启动项目服务
systemctl --user start hermes-<project-name>.service

# 检查服务状态
systemctl --user status hermes-<project-name>.service

# 启用开机自启
systemctl --user enable hermes-<project-name>.service
```

### 6. 验证配置
```bash
# 检查所有Hermes进程
ps aux | grep "hermes.*gateway" | grep -v grep

# 检查Profile状态
hermes profile list

# 检查服务状态
systemctl --user list-units --type=service --state=running | grep -i hermes
```

## 示例配置

### ResearchAudit项目（默认）
- **Profile**: default
- **服务文件**: `hermes-gateway.service`
- **飞书App ID**: `cli_a96ef9bf23b8dbb4`
- **配置目录**: `~/.hermes/`
- **启动命令**: 使用默认服务

### 东南亚电商项目
- **Profile**: southeast-ecommerce
- **服务文件**: `hermes-southeast-ecommerce.service`
- **飞书App ID**: `cli_a96d18e5d2f89bde`
- **配置目录**: `~/.hermes/profiles/southeast-ecommerce/`
- **端口**: 3001（配置文件中）

## 关键发现与注意事项

### 发现1：WebSocket连接模式
- Hermes网关使用WebSocket直接连接飞书，而不是监听HTTP端口
- 端口配置（如3001）在配置文件中，但实际连接是WebSocket
- 验证方法：检查服务日志中的WebSocket连接信息

### 发现2：进程冲突检测
- Hermes有内置安全检测，防止多个实例冲突
- 直接运行`hermes -p <profile> gateway run`会检测到其他进程并退出
- 解决方案：使用系统服务隔离，每个服务有独立的执行环境

### 发现3：HERMES_HOME环境变量
- 关键配置：每个服务需要设置`HERMES_HOME`指向Profile目录
- 这确保每个Agent使用独立的配置、内存和会话
- 格式：`HERMES_HOME=/home/agentuser/.hermes/profiles/<project-name>`

### 发现4：飞书应用隔离
- 每个项目必须使用不同的飞书App ID
- 在飞书开放平台为每个项目创建独立的应用
- 确保每个Profile的`.env`文件中有正确的App ID和Secret

## 常见问题

### Q1：启动失败，提示"other hermes processes running"
**原因**：Hermes检测到其他实例正在运行。
**解决**：
1. 使用系统服务方式启动，而不是直接命令行
2. 确保每个服务有独立的`HERMES_HOME`环境变量
3. 使用`-p <profile-name>`参数指定Profile

### Q2：飞书消息无法接收
**原因**：飞书App ID配置错误或事件订阅未配置。
**解决**：
1. 确认`.env`中的FEISHU_APP_ID与飞书平台一致
2. 在飞书开放平台配置事件订阅
3. 检查服务日志中的WebSocket连接状态

### Q3：Profile显示"stopped"但进程在运行
**原因**：`hermes profile list`可能不同步。
**解决**：
1. 检查实际进程：`ps aux | grep "hermes.*gateway"`
2. 检查系统服务状态：`systemctl --user status hermes-<project>.service`
3. 进程存在即表示Agent在运行

### Q4：资源占用过高
**原因**：多个Agent同时运行增加资源使用。
**解决**：
1. 监控内存和CPU使用：`htop`或`ps aux`
2. 考虑优化模型配置或减少并发任务
3. 非活跃时段可以停止部分服务

## 最佳实践

1. **命名规范**：Profile和服务名称使用小写字母和连字符
2. **配置备份**：修改前备份重要配置文件
3. **逐步验证**：每步完成后验证，避免问题累积
4. **日志监控**：启动后立即查看日志，快速定位问题
5. **飞书平台配置**：提前在飞书开放平台创建应用和配置事件订阅

## 维护命令参考

```bash
# 查看所有项目状态
hermes profile list
systemctl --user list-units --type=service --state=running | grep hermes

# 重启特定项目
systemctl --user restart hermes-<project-name>.service

# 停止特定项目（保留其他项目运行）
systemctl --user stop hermes-<project-name>.service

# 查看项目日志
journalctl --user -u hermes-<project-name>.service -n 50 --no-pager

# 禁用项目开机自启
systemctl --user disable hermes-<project-name>.service
```

## 注意事项

1. **资源隔离**：每个Profile独立运行，注意服务器资源分配
2. **飞书配额**：每个飞书应用有独立的API调用配额
3. **配置同步**：修改配置后需要重启服务生效
4. **网络要求**：确保服务器可以访问飞书WebSocket服务
5. **安全考虑**：每个项目使用独立的飞书应用，避免权限交叉