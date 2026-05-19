---
name: auto-silent-learning
description: >
  全自动无人静默自学系统 — Hermes空闲5分钟后后台启动，
  自动学习跨境/短视频/Hermes运维公开干货，精简生成skill并入库GBrain。
  30个固定选题轮转，每日9点精简总结汇报。
tags:
  - auto-learn
  - silent-learning
  - crossborder
  - short-video
  - hermes-ops
  - cron
  - gbrain
trigger:
  - "静默自学"
  - "自动学习"
  - "silent learn"
  - "自动自学"
  - "无人自学"
  - "后台学习"
---

# auto-silent-learning

全自动无人静默自学系统 — Hermes空闲5分钟后后台启动自动学习。

## 核心逻辑

1. **每5分钟采集** → 30个固定选题轮换，必米云搜索公开干货（免API免登录）
2. **每15分钟提炼入库** → DeepSeek API精简 → 生成skill → 自动导入GBrain
3. **每日9点总结** → 前一天学习内容精简汇报到飞书

## Cron Jobs

| cron | 用途 | 模式 | 脚本 |
|------|------|------|------|
| `every 5m` | 搜索采集公开干货 | `no_agent=true` | `silent_learn_collect.sh` |
| `every 15m` | 提炼→生成skill→入库GBrain | `no_agent=true` | `silent_learn_refine.sh` |
| `0 9 * * *` | 前一日自学总结汇报 | agent | — |

## 30个选题覆盖

**跨境电商（1-18）：** 泰马市场调研/爆款筛选/1688选品/成本核算/定价/货源上架
**短视频图文（19-24）：** 素材采集/剪辑/字幕/配音/成片优化/文案
**Hermes运维（25-30）：** 配置优化/定时任务/MCP/GBrain/飞书/多智能体

## 手动指令

说关键词对应操作（详见 `~/.hermes/scripts/learn_commands.md`）

## 文件结构

- 采集脚本：`~/.hermes/scripts/silent_learn_collect.sh`
- 提炼脚本：`~/.hermes/scripts/silent_learn_refine.sh`
- 学习日志：`~/.hermes/logs/silent_learn.log`
- 学习状态：`~/.hermes/logs/silent_learn_state.json`
- 每日汇总：`~/.hermes/logs/learn_summaries/`
- 自动skill：`~/.hermes/skills/auto_learned/`
