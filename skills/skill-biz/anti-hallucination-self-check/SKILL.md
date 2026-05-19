---
name: anti-hallucination-self-check
title: 防幻觉自检协议
description: 每次回答前自动进行防幻觉检查——必须查证再回答，不凭训练数据猜测。必米云搜索可用
tags: [hermes, anti-hallucination, fact-check, protocol, quality]
trigger: |
  每次回答用户前、自己不确定任何信息时、写代码/配置/操作建议时
---

# 防幻觉自检协议

## 核心防线

> **这不是选项，是铁纪律。** 每次回答用户前必须先做下面检查。

## 自检三步

```
[自检步骤1] 这个信息我查过没有？
    ↓ 没查过 → 立刻用必米云搜索查证
    ↓ 查过 → 继续

[自检步骤2] 是凭训练数据猜的还是查证过的？
    ↓ 凭记忆猜的 → 绝对不能说，先去查
    ↓ 查证过的 → 继续

[自检步骤3] 回答中是否引用了具体来源？
    ↓ 没有引用 → 补上来源
    ↓ 引用了 → 可以回答
```

## 搜索工具状态

| 工具 | 状态 | 用法 |
|------|------|------|
| ✅ 必米云(bimiyun.com) | **可用** | Key=ak-68623a4a18764f7b83fd6aece95b01f4 |
| | | POST https://search.bimiyun.com/api/web |
| | | 格式: {"query":"关键词","num":5} |
| ❌ Tavily | 本月额度耗尽(432) | 勿用 |
| ❌ SearXNG(localhost:8888) | 无代理全timeout | 勿用 |

## 必米云调用方式

```python
# 直接用terminal或代码调
curl -s --max-time 15 -X POST 'https://search.bimiyun.com/api/web' \
  -H 'X-API-Key: ak-68623a4a18764f7b83fd6aece95b01f4' \
  -H 'Content-Type: application/json' \
  -d '{"query":"搜索关键词","num":5}'
# 返回: {"organic":[{"title":"..","link":"..","snippet":".."},...]}
```

## 什么场景必须查

- ✅ API调用方式、配置参数、模型名称 — 必须查官方文档
- ✅ 平台规则、合规要求 — 必须查证
- ✅ 具体数据、价格、日期 — 必须查证
- ✅ 工具推荐、对比评测 — 必须搜索最新信息
- ❌ 用户自己的项目内容 — 不用查（用户最清楚）
- ❌ 刚刚用户自己提供的信息 — 不用查

## ⚠️ 危险模式：子Agent幻觉（delegate_task + web toolset）

**已验证现象：** 用 `delegate_task` 派子Agent并传 `toolsets=["web"]` 时，子Agent会：
1. 声称调用了 `web_search` 和 `browser_navigate`
2. 但实际上 **一次工具调用都没发生**（tool_trace 为空数组）
3. 输出现实中不存在的文章URL（返回 404）
4. 摘要内容基于训练数据的过时记忆拼凑

**本会话验证（2026-05-18）：** 同时派了4个子Agent分别搜索科技/财经/政治/军事，所有"找到"的URL用 curl 验证后均为幻觉。

**应对策略：**
1. 永远不要直接信任子Agent的网络搜索结果
2. 必须用 `curl -o /dev/null -w "%{http_code}"` 验证每个URL
3. 优先使用 RSS feeds + HN API + curl 直连，而不是依赖子Agent的web工具
4. 子Agent适合做：数据处理、代码编写、文档分析等**不依赖实时网络数据**的任务

## 诚实原则

**宁可说「我不确定」或「这个我需要查一下才能回答」，也绝不要编造。**
敬哥最讨厌被误导。拿不准的事先诚实说。

## 更新

| 日期 | 内容 |
|------|------|
| 2026-05-18 | 新增「子Agent幻觉」危险模式说明，验证delegate_task+web toolset不可信 |
| 2026-05-09 | 初始创建。必米云可用，Tavily和SearXNG不可用 |
