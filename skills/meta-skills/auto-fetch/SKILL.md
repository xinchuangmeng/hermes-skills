---
name: auto-fetch
description: Auto-Fetch 定时汇聚上下文到本地知识库——每20分钟自动扫描技能库/系统状态，生成上下文快照供Agent使用。参考OpenHuman Auto-Fetch设计。
tags: [auto-fetch, context, knowledge-base, openhuman, cron]
---

# Auto-Fetch（参考 OpenHuman Auto-Fetch）

## 原理

每 20 分钟自动汇聚服务器上的上下文数据，存储在本地知识库，
让 Agent 在不问用户的情况下就知道当前状态。

## 数据源

| 来源 | 说明 |
|------|------|
| 技能库 | 扫描所有 SKILL.md，记录新增/更新的技能 |
| 系统状态 | 磁盘用量、技能总数、环境变量 |

## 存储位置

| 文件 | 说明 |
|------|------|
| `~/.hermes/auto-fetch/knowledge.jsonl` | 原始知识库（JSONL 格式） |
| `~/.hermes/auto-fetch/latest_summary.md` | 最新上下文快照 |
| `~/.hermes/auto-fetch/.cursor.json` | 上次运行时间戳 |

## 定时任务

- **频率**：每 20 分钟
- **名称**：Auto-Fetch 定时汇聚上下文
- **代码**：`/root/.hermes/scripts/auto_fetch.py`

## 手动执行

```bash
python3 ~/.hermes/scripts/auto_fetch.py
```

## 阅读最新快照

```bash
cat ~/.hermes/auto-fetch/latest_summary.md
```
