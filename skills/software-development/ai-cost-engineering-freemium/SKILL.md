---
name: ai-cost-engineering-freemium
title: AI Freemium 成本工程优化
description: 基于真实案例的 AI 功能成本优化方法——从 $0.08 压到 $0.029/次点击（64% 降幅），适用于 ResearchAudit 等产品的 LLM API 成本控制
tags: [cost-optimization, api-cost, llm-pricing, freemium, prompt-engineering]
---

# AI Freemium 成本工程优化

## 来源
Dev.to 真实案例：Cost-engineering an "AI Generate" button in a freemium product (from $0.08 to $0.029 per click)

## 核心方法论

### 1. 成本结构分析
AI 功能的核心成本 = 每次调用的 token 费用 × 调用次数
对于 Freemium 产品，免费层成本直接影响 unit economics。

### 2. 优化策略（从高到低优先级）

#### 2.1 Prompt 压缩（最大杠杆）
- **精简 system prompt**：去除不必要的指令、说明书、示例
- **减少 few-shot 示例**：能 1 个示例就不用 3 个
- **缩短 output 长度**：设置 max_tokens，只返回最必要的信息
- **结构化输出**：用 JSON 而非自然语言描述，token 减少 30-50%

#### 2.2 模型选择（次高杠杆）
- 简单任务用便宜模型（DeepSeek-V3 vs DeepSeek-R1）
- 多级模型：简单检测用轻量模型，深度审计用强模型
- latency 要求低的任务可以选更便宜的异步方案

#### 2.3 缓存策略
- **结果缓存**：相同的输入（比如同一篇论文的重复审计）直接返回缓存
- **相似度缓存**：输入相似度 > 95% 时复用缓存
- **部分缓存**：多层审计中，已计算维度的结果缓存

#### 2.4 调用频率控制
- 频率限制（rate limiting）
- 用户级配额（quota per user per day）
- 免费层差异化：免费用户只能用快速模式/简化版

#### 2.5 Batch API（如有）
- OpenAI 等支持 batch API（50% 折扣）
- 适合非实时任务（异步报告生成）

### 3. 实际优化案例（$0.08 → $0.029）

| 优化步骤 | 成本变化 | 说明 |
|---------|---------|------|
| 基线 | $0.08 | 长 system prompt + 3-shot + 长输出 |
| 精简 prompt | $0.052 | 去除冗余指令，-35% input tokens |
| 缩短输出 | $0.038 | 限制 max_tokens，结构化 JSON |
| 缓存策略 | $0.029 | 相同输入命中缓存率约 30-40% |

## 对 ResearchAudit 的应用建议

ResearchAudit 有两层审计（正则 + LLM），成本主要在 deep_audit.py 的 DeepSeek 调用：

1. **快速概览模式**：先用正则检测器筛出有明显问题的论文，深度审计只对有"可疑"信号的论文触发
2. **分层模型**：简单维度（引用质量、结构完整性）用便宜模型跑，复杂维度（逻辑链条、方法可靠性）用强模型
3. **审计结果缓存**：相同 paper_id 重复审计直接返回缓存结果
4. **输出压缩**：deep_audit 的 prompt 已优化，但可以进一步限制每个维度的输出长度

## 注意事项
- 成本优化不要牺牲用户体验 — 免费层可以延迟但不应拒绝
- 监控用户留存 vs 成本曲线 — 免费用户的 LTV 要覆盖调用成本
- 定期审计 prompt token 用量，代码变更可能导致 prompt 膨胀
