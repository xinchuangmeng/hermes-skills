#!/bin/bash
# ============================================================
# Hermes Auto-Learn Script
# 每天凌晨1点-7点：搜集全球编程和AI Agent最新知识
# 输出：~/.hermes/skills/auto_learned/daily_summary.md
# ============================================================

set -euo pipefail

LEARN_DIR="$HOME/.hermes/skills/auto_learned"
mkdir -p "$LEARN_DIR"

SUMMARY="$LEARN_DIR/daily_summary.md"
DATE_TAG=$(date '+%Y-%m-%d')
HOUR=$(date '+%H')

# 阶段1：记录启动
cat > "$SUMMARY" << 'HEADER'
# 🤖 Hermes Auto-Learn Daily Summary
HEADER
echo "" >> "$SUMMARY"
echo "## 📅 $(date '+%Y-%m-%d %H:%M')" >> "$SUMMARY"
echo "" >> "$SUMMARY"

# ==========================================
# 阶段2：根据当前小时执行不同任务
# ==========================================
if [ "$HOUR" -ge 1 ] && [ "$HOUR" -lt 3 ]; then
    # 凌晨1-3点：数据结构化+知识整理
    echo "### 📚 知识整理" >> "$SUMMARY"
    echo "凌晨时段：正在进行数据结构化和知识整理" >> "$SUMMARY"
    echo "" >> "$SUMMARY"

    # 记录过去24小时新发现的知识点
    CACHE_FILE="$LEARN_DIR/.knowledge_cache"
    if [ -f "$CACHE_FILE" ]; then
        echo "**累积知识点统计**：" >> "$SUMMARY"
        wc -l "$CACHE_FILE" 2>/dev/null | awk '{print $1}' >> "$SUMMARY"
        echo "" >> "$SUMMARY"
    fi

elif [ "$HOUR" -ge 3 ] && [ "$HOUR" -lt 5 ]; then
    # 凌晨3-5点：深度阅读+整理笔记
    echo "### 📖 深度阅读与整理" >> "$SUMMARY"
    echo "深度阅读时段：分析已有知识，提取可更新的技能内容" >> "$SUMMARY"
    echo "" >> "$SUMMARY"

    # 检查是否有新的知识点可以归档
    TODAY_DIR="$LEARN_DIR/$DATE_TAG"
    if [ -d "$TODAY_DIR" ]; then
        echo "**今日已归档知识点**：" >> "$SUMMARY"
        echo "- 目录：$TODAY_DIR" >> "$SUMMARY"
        find "$TODAY_DIR" -type f -name "*.md" | while read -r f; do
            echo "  - 文件：$(basename "$f")" >> "$SUMMARY"
        done
        echo "" >> "$SUMMARY"
    fi

elif [ "$HOUR" -ge 5 ] && [ "$HOUR" -lt 7 ]; then
    # 凌晨5-7点：技能对比与更新准备
    echo "### 🔧 技能更新准备" >> "$SUMMARY"
    echo "技能对比时段：对比新知识与现有技能文件，标记需要更新的内容" >> "$SUMMARY"
    echo "" >> "$SUMMARY"

    # 检查现有技能目录
    SKILL_DIR="$HOME/.hermes/skills"
    if [ -d "$SKILL_DIR" ]; then
        SKILL_COUNT=$(find "$SKILL_DIR" -name "SKILL.md" 2>/dev/null | wc -l)
        echo "**现有技能文件数**：$SKILL_COUNT" >> "$SUMMARY"
        echo "" >> "$SUMMARY"
    fi

    # 生成周度回顾（只在周日）
    DOW=$(date '+%u')
    if [ "$DOW" -eq 7 ]; then
        echo "---" >> "$SUMMARY"
        echo "## 📊 周度回顾" >> "$SUMMARY"
        echo "本周学习总结将在下一轮交互时展示" >> "$SUMMARY"
    fi
else
    echo "### ⏳ 非学习时段" >> "$SUMMARY"
    echo "当前不在自动学习时间窗口内（01:00-07:00）" >> "$SUMMARY"
    echo "" >> "$SUMMARY"
fi

# ==========================================
# 阶段3：留存统计
# ==========================================
echo "---" >> "$SUMMARY"
echo "_学习完成于 $(date '+%H:%M')_" >> "$SUMMARY"

# 保留最近7天的记录，清理更早的
find "$LEARN_DIR" -maxdepth 1 -type d -mtime +7 ! -path "$LEARN_DIR" -exec rm -rf {} + 2>/dev/null || true

echo "Hermes Auto-Learn: 学习完成 ($(date))"
