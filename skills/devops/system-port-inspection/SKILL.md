---
name: system-port-inspection
description: 系统性端口检查方法 - 检查服务器上的端口监听情况，识别服务，关联进程信息
tags: [devops, networking, ports, monitoring, security]
author: Hermes Agent
created: 2026-04-23
---

# 系统端口检查方法

## 适用场景

当用户需要：
- 检查服务器上哪些端口正在监听
- 识别未知服务或gateway
- 排查端口冲突问题
- 安全审计和监控

## 核心发现

1. **Hermes Gateway不监听外部端口** - 它是一个内部消息转发服务，通过systemd服务状态检查
2. **分层检查方法** - 从宏观到微观，逐步深入
3. **进程-端口关联** - 关键信息关联分析

## 检查步骤

### 第1步：快速概览
```bash
# 查看所有监听端口
sudo netstat -tulpn | grep LISTEN

# 使用ss命令（更现代）
sudo ss -tulpn
```

### 第2步：检查常见gateway端口
```bash
# 检查80、443、3000、8000-8010、8080、9000等常见端口
sudo ss -tulpn | grep -E ":(80|443|3000|800[0-9]|8010|8080|9000)"
```

### 第3步：检查本地服务端口
```bash
# 检查本地回环地址上的服务
sudo ss -tulpn | grep -E "127.0.0.1|localhost"
```

### 第4步：进程详细信息检查
```bash
# 通过PID查看进程详情
ps -fp <PID>

# 检查进程工作目录
sudo ls -la /proc/<PID>/cwd

# 检查进程打开的文件
sudo ls -la /proc/<PID>/fd/ 2>/dev/null | head -10
```

### 第5步：使用lsof进行深度检查
```bash
# 查看进程的网络连接
sudo lsof -p <PID> -i 2>/dev/null | grep -E "LISTEN|ESTABLISHED"

# 查看特定端口的进程
sudo lsof -i :<端口号>
```

### 第6步：服务状态检查（对于systemd服务）
```bash
# 检查服务状态
systemctl status <服务名>

# 对于用户服务
systemctl --user status <服务名>
```

## 特定服务检查

### Hermes Gateway检查
```bash
# 检查gateway状态
cd ~/.hermes/hermes-agent && python3 -m hermes_cli.main gateway status

# 检查gateway进程
ps aux | grep "gateway run" | grep -v grep

# 检查gateway状态文件
cat ~/.hermes/gateway_state.json
```

### 数据库服务检查
```bash
# MySQL/MariaDB
sudo ss -tulpn | grep :3306
sudo systemctl status mariadb  # 或 mysql
```

### Web服务检查
```bash
# Nginx/Apache
sudo ss -tulpn | grep -E ":80|:443"
sudo systemctl status nginx
sudo systemctl status apache2
```

## 常见发现模式

### 1. Node.js应用
- 通常在3000、8000、8080等端口
- 进程：`node app.js` 或 `node server.js`
- 检查工作目录了解项目类型

### 2. 数据库服务
- MySQL/MariaDB: 3306
- PostgreSQL: 5432
- Redis: 6379
- MongoDB: 27017

### 3. 消息队列/缓存
- Redis: 6379
- RabbitMQ: 5672
- Memcached: 11211

### 4. 容器服务
- Docker: 2375/2376
- Containerd: 动态端口

## 输出解析技巧

### netstat/ss输出字段
```
State      Recv-Q Send-Q Local Address:Port  Peer Address:Port  Process
LISTEN     0      128    0.0.0.0:22          0.0.0.0:*          users:(("sshd",pid=1234,fd=3))
```

### 关键信息提取
1. **Local Address:Port** - 监听地址和端口
2. **Process** - 进程名称和PID
3. **State** - 连接状态（LISTEN为监听中）

## 安全注意事项

1. **未知端口** - 检查是否有未授权的服务
2. **外部暴露** - 0.0.0.0表示对所有IP开放
3. **高危端口** - 如22(SSH)、3306(MySQL)等是否安全配置

## 故障排查流程

1. **端口被占用但找不到进程** - 使用`sudo lsof -i :端口`深度检查
2. **服务启动失败** - 检查端口是否已被占用
3. **连接拒绝** - 检查防火墙和SELinux设置
4. **权限问题** - 低于1024的端口需要root权限

## 自动化检查脚本

```bash
#!/bin/bash
echo "=== 系统端口检查报告 ==="
echo "生成时间: $(date)"
echo ""

echo "1. 所有监听端口:"
sudo ss -tulpn | head -20

echo ""
echo "2. 常见服务端口:"
for port in 22 80 443 3306 5432 6379 8000 8080 9000; do
    result=$(sudo ss -tulpn | grep ":$port ")
    if [ -n "$result" ]; then
        echo "端口 $port: 正在监听"
        echo "  详情: $result"
    else
        echo "端口 $port: 未监听"
    fi
done

echo ""
echo "3. 检查Hermes Gateway:"
if systemctl --user is-active hermes-gateway >/dev/null 2>&1; then
    echo "Hermes Gateway: 运行中"
else
    echo "Hermes Gateway: 未运行"
fi
```

## 经验总结

1. **Hermes Gateway特殊性** - 不监听外部端口，通过systemd服务状态检查
2. **分层检查** - 先宏观后微观，避免信息过载
3. **关联分析** - 端口+进程+工作目录+配置文件
4. **用户项目识别** - 通过工作目录识别用户正在运行的项目

## 相关技能

- [webhook-subscriptions](../webhook-subscriptions/SKILL.md) - 事件驱动服务配置
- [hermes-multi-agent-port-configuration](../../software-development/hermes-multi-agent-port-configuration/SKILL.md) - 多Agent端口配置