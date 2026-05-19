---
name: hermes-memory-monitoring
description: 监控Hermes Agent内存使用，自动清理缓存防止卡死和超时
trigger: 当Hermes出现卡死、响应慢、超时或内存紧张时使用
tags: [hermes, memory, monitoring, performance, troubleshooting]
---

# Hermes内存监控与自动清理

## 问题背景
Hermes Agent在内存有限的服务器上运行时容易出现卡死、超时问题，特别是同时运行多个实例时。

## 解决方案
部署自动内存监控系统，当可用内存低于阈值时自动清理缓存。

## 安装步骤

### 1. 创建监控脚本目录
```bash
mkdir -p ~/.hermes/scripts
mkdir -p ~/.hermes/logs
```

### 2. 创建自动监控脚本
创建 `~/.hermes/scripts/check_and_clean_memory.sh`：
```bash
#!/bin/bash

# 内存监控脚本 - 当可用内存低于100MB时自动清理缓存
LOG_FILE="$HOME/.hermes/logs/memory_check.log"
THRESHOLD_MB=100

# 确保日志目录存在
mkdir -p "$(dirname "$LOG_FILE")"

# 获取当前时间
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# 获取内存信息
MEM_INFO=$(free -m | grep "Mem:")
TOTAL_MEM=$(echo "$MEM_INFO" | awk '{print $2}')
AVAILABLE_MEM=$(echo "$MEM_INFO" | awk '{print $7}')

# 获取交换空间信息
SWAP_INFO=$(free -m | grep "Swap:")
SWAP_TOTAL=$(echo "$SWAP_INFO" | awk '{print $2}')
SWAP_USED=$(echo "$SWAP_INFO" | awk '{print $3}')

# 获取Hermes进程信息
HERMES_PROCESSES=$(ps aux | grep -E "hermes.*run" | grep -v grep | wc -l)
HERMES_MEMORY=$(ps aux | grep -E "hermes.*run" | grep -v grep | awk '{sum+=$4} END {print sum}')

echo "[$TIMESTAMP] 内存检查开始" >> "$LOG_FILE"
echo "[$TIMESTAMP] 总内存: ${TOTAL_MEM}MB, 可用内存: ${AVAILABLE_MEM}MB" >> "$LOG_FILE"
echo "[$TIMESTAMP] 交换空间: ${SWAP_USED}/${SWAP_TOTAL}MB" >> "$LOG_FILE"
echo "[$TIMESTAMP] Hermes进程数: $HERMES_PROCESSES, 占用内存: ${HERMES_MEMORY}%" >> "$LOG_FILE"

# 检查是否需要清理
if [ "$AVAILABLE_MEM" -lt "$THRESHOLD_MB" ]; then
    echo "[$TIMESTAMP] ⚠️ 警告: 可用内存低于阈值(${THRESHOLD_MB}MB)，执行缓存清理..." >> "$LOG_FILE"
    
    # 清理缓存
    sudo sync && echo 3 | sudo tee /proc/sys/vm/drop_caches
    
    # 清理后重新检查
    sleep 2
    MEM_INFO_AFTER=$(free -m | grep "Mem:")
    AVAILABLE_MEM_AFTER=$(echo "$MEM_INFO_AFTER" | awk '{print $7}')
    
    echo "[$TIMESTAMP] ✅ 缓存清理完成，清理后可用内存: ${AVAILABLE_MEM_AFTER}MB" >> "$LOG_FILE"
else
    echo "[$TIMESTAMP] ✅ 内存状态正常，无需清理" >> "$LOG_FILE"
fi

echo "[$TIMESTAMP] 内存检查结束" >> "$LOG_FILE"
echo "----------------------------------------" >> "$LOG_FILE"
```

### 3. 设置脚本权限
```bash
chmod +x ~/.hermes/scripts/check_and_clean_memory.sh
```

### 4. 设置Cron定时任务
```bash
# 编辑crontab
crontab -e

# 添加以下行（每5分钟检查一次）
*/5 * * * * /home/agentuser/.hermes/scripts/check_and_clean_memory.sh
```

### 5. 创建手动检查脚本
创建 `~/.hermes/scripts/check_memory.sh`：
```bash
#!/bin/bash

echo "=== 系统内存状态 ==="
free -h

echo -e "\n=== Hermes进程状态 ==="
ps aux | grep -E "hermes.*run" | grep -v grep

echo -e "\n=== 内存使用详情 ==="
MEM_INFO=$(free -m)
echo "$MEM_INFO"

AVAILABLE_MEM=$(echo "$MEM_INFO" | grep "Mem:" | awk '{print $7}')
echo -e "\n可用内存: ${AVAILABLE_MEM}MB"

if [ "$AVAILABLE_MEM" -lt 100 ]; then
    echo "⚠️  警告: 可用内存低于100MB，建议清理缓存"
    echo "执行: sudo sync && echo 3 | sudo tee /proc/sys/vm/drop_caches"
fi
```

### 6. 设置手动脚本权限
```bash
chmod +x ~/.hermes/scripts/check_memory.sh
```

## 使用方法

### 快速检查内存状态
```bash
~/.hermes/scripts/check_memory.sh
```

### 手动清理内存（紧急情况）
```bash
sudo sync && echo 3 | sudo tee /proc/sys/vm/drop_caches
```

### 查看监控日志
```bash
tail -f ~/.hermes/logs/memory_check.log
```

### 查看最近10条日志
```bash
tail -10 ~/.hermes/logs/memory_check.log
```

## 监控指标说明

1. **可用内存阈值**: 100MB（可调整THRESHOLD_MB变量）
2. **检查频率**: 每5分钟
3. **清理操作**: 清理页面缓存、目录项和inode缓存
4. **日志位置**: `~/.hermes/logs/memory_check.log`

## 故障排除

### 问题1: Cron任务未执行
```bash
# 检查cron服务状态
sudo systemctl status cron

# 查看cron日志
grep CRON /var/log/syslog | tail -20
```

### 问题2: 脚本权限不足
```bash
# 确保脚本有执行权限
ls -la ~/.hermes/scripts/

# 如果没有执行权限
chmod +x ~/.hermes/scripts/*.sh
```

### 问题3: 清理后内存未明显增加
- 检查是否有内存泄漏的进程
- 检查交换空间使用情况
- 考虑重启占用内存过多的服务

## 优化建议

1. **升级服务器内存**到4GB以上
2. **调整Hermes配置**减少内存占用
3. **考虑只运行一个Hermes实例**
4. **定期检查日志**分析内存使用趋势

## 相关技能
- hermes-performance-diagnosis: 诊断Hermes性能问题
- hermes-multi-agent-configuration: 配置多个Hermes实例
- systematic-debugging: 系统化调试方法