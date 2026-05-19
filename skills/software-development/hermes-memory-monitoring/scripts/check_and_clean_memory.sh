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