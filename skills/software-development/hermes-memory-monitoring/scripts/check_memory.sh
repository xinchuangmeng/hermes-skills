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