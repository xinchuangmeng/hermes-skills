---
name: hermes-performance-diagnosis
description: 诊断Hermes Agent卡死、响应慢、资源不足问题的安全方法（仅诊断，不修改系统）
category: software-development
tags:
  - hermes
  - performance
  - troubleshooting
  - diagnosis
  - monitoring
---

# Hermes Agent性能问题诊断指南

## 何时使用
当Hermes Agent出现以下症状时使用本技能：
- 响应缓慢或卡死
- 工具调用超时
- 内存占用过高
- 进程无响应
- 网络连接频繁断开

## 安全诊断步骤（只读操作）

### 1. 检查系统资源状态
```bash
# 查看内存使用情况（安全只读）
free -h
# 查看交换空间使用
swapon --show
# 查看进程内存占用（只读）
ps aux --sort=-%mem | head -20
# 查看Hermes进程详情（只读）
ps aux | grep hermes
```

### 2. 检查网络连接状态
```bash
# 查看网络连接状态（只读）
netstat -tulpn | grep hermes
# 查看端口监听情况
ss -tulpn | grep hermes
# 测试API响应时间（只读）
time curl -s https://api.deepseek.com/v1/chat/completions
```

### 3. 查看Hermes日志
```bash
# 查看最近错误日志（只读）
journalctl -u hermes --since "10 minutes ago" -p err
# 查看完整日志（只读）
tail -100 /var/log/hermes/hermes.log 2>/dev/null || echo "日志文件不存在"
# 查找超时记录（只读）
grep -i "timeout\|timed out" /var/log/hermes/hermes.log 2>/dev/null || echo "无超时记录"
```

### 4. 检查Hermes运行状态
```bash
# 检查Hermes服务状态（只读）
systemctl status hermes --no-pager
# 检查Hermes进程树
pstree -p $(pgrep hermes) 2>/dev/null || echo "Hermes进程未找到"
# 检查Hermes打开的文件
lsof -p $(pgrep hermes) 2>/dev/null | head -20
```

## 常见问题症状识别

### 症状1：内存不足
**识别特征**：
- `free -h`显示可用内存低于100MB
- 交换空间使用率高（swap used > 0）
- Hermes进程内存占用持续增长

**安全检查命令**：
```bash
# 检查内存使用趋势
watch -n 5 "free -h | grep -E 'Mem:|Swap:'"
# 检查Hermes内存占用变化
watch -n 5 "ps aux | grep hermes | grep -v grep"
```

### 症状2：网络连接问题
**识别特征**：
- 日志中出现"WebSocket disconnected"或"connection lost"
- API调用超时错误
- 网络连接状态异常

**安全检查命令**：
```bash
# 检查网络连接数
netstat -an | grep :8080 | wc -l
# 检查连接状态
ss -t state established | grep :8080
```

### 症状3：多实例资源竞争
**识别特征**：
- 多个Hermes进程同时运行
- 端口冲突错误
- 资源使用翻倍

**安全检查命令**：
```bash
# 检查所有Hermes实例
ps aux | grep \"hermes.*--config\" | grep -v grep
# 检查端口使用情况
ss -tulpn | grep -E \"8080|8081|8082\"
```

### 症状5：delegate_task子任务卡死 + "Still working" 循环提示
**识别特征**：
- 系统持续输出 `Still working... (X min elapsed — iteration Y/90, running: terminal)`
- 子任务超过5分钟没有进展
- 用户明确表示反感这类消息——应主动中断而非等待

**根因分析**：
最常见的原因是子任务中的终端命令卡住，其中端口抢占是高频根因：
- 子任务试图启动一个Web服务（Flask/Gradio/http.server）到已被占用的端口
- 命令尝试绑定端口失败后重试或等待，导致无限卡住

**诊断流程**：
```bash
# 第1步：立即检查端口占用情况（端口抢占是最常见根因）
ss -tlnp 2>/dev/null | grep -E '808[0-9]|500[0-9]|786[0-9]|300[0-9]'

# 第2步：检查是否有后台进程残留
ps aux | grep -E 'python3.*server|flask|gradio' | grep -v grep

# 第3步：如果有占用端口的旧进程不再需要，kill释放
kill <PID>
```

**核心原则**：遇到 "Still working" 超过2分钟，不要继续等待，应主动：
1. 查进程列表（`process list`）
2. 查端口占用（`ss -tlnp`）
3. 定位是哪个命令卡住
4. 中断子任务，手动接管自行执行

### 症状4：API兼容性问题
**识别特征**：
- JSON解析错误
- 图片处理失败
- 模型响应异常

**安全检查命令**：
```bash
# 检查最近API错误
grep -i "error\|exception\|failed" /var/log/hermes/hermes.log 2>/dev/null | tail -10
# 检查模型提供商状态
curl -s https://status.deepseek.com/ | grep -i status
```

## 诊断报告模板

### 资源诊断报告
```
=== 系统资源状态 ===
总内存: [数值]
可用内存: [数值]
交换空间使用: [数值]
Hermes内存占用: [数值]
HermesCPU占用: [数值]
```

### 网络诊断报告
```
=== 网络连接状态 ===
监听端口: [端口列表]
活动连接数: [数量]
API响应时间: [时间]
飞书连接状态: [正常/断开]
```

### 日志诊断报告
```
=== 错误日志摘要 ===
最近错误: [错误类型]
超时次数: [次数]
连接断开: [次数]
API失败: [次数]
```

### 进程诊断报告
```
=== Hermes进程状态 ===
进程ID: [PID]
运行时间: [时间]
线程数: [数量]
打开文件数: [数量]
```

## 安全建议（仅建议，不执行）

### 1. 内存优化建议
- 考虑升级服务器内存到4GB以上
- 减少同时运行的Hermes实例数量
- 调整Hermes配置降低内存使用

### 2. 网络优化建议
- 检查防火墙设置是否允许必要端口
- 考虑使用更稳定的网络环境
- 调整超时设置以适应网络波动

### 3. 配置优化建议
- 降低日志级别减少IO压力
- 调整并发任务数
- 考虑使用更稳定的模型提供商

### 4. 监控建议
- 设置资源使用监控
- 定期检查日志文件大小
- 监控API响应时间

## 诊断流程图

```
开始诊断
    ↓
检查系统资源 (free -h, ps aux)
    ↓
检查网络连接 (netstat, ss)
    ↓
检查Hermes日志 (journalctl, tail)
    ↓
检查进程状态 (systemctl, pstree)
    ↓
生成诊断报告
    ↓
提供安全建议
```

## 注意事项

1. **安全第一**：所有诊断命令均为只读操作，不会修改系统
2. **权限检查**：使用普通用户权限执行诊断
3. **数据保护**：不访问敏感配置文件内容
4. **最小影响**：诊断过程对系统影响最小化

## 相关技能
- systematic-debugging
- hermes-cronjob-troubleshooting
- system-port-inspection