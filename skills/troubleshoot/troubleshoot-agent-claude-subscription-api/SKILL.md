---
name: troubleshoot-agent-claude-subscription-api
title: Claude订阅当API用——省钱的替代方案
description: "基于Dev.to文章《Stop Paying Twice for Claude: Use Your Subscription Like an API》。核心技巧：如果你有Claude Pro/Max订阅（$20/$200/月），可以利用Claude Code的--acp模式和本地CLI来调用Claude，而不是额外支付API费用（API费用可能到$14,502/月）。这样订阅费和API费可以二选一，不用双倍支付。"
tags: [troubleshoot, cost-saving, claude, api, subscription, agent-cost]
trigger: |
  当Claude API费用过高、想降低Agent编码成本、或需要评估Claude订阅模式vs API模式的成本时
---

# Claude订阅当API用

## 核心洞察

### 问题：双重支付

很多人既付Claude Pro/Max订阅费（$20/$200/月），又通过API调用Claude模型——这就双倍花钱了。

真实案例：有人在2026年5月的Claude Code账单为$14,502/月（见troubleshoot-agent-cost-overrun技能）。

### 解决方案

如果你已经有Claude Pro/Max订阅，可以直接通过Claude Code的CLI来调用Claude模型，不需要再走API付费。

```yaml
# 两种模式对比
API模式:
  费用: 按token计费（$3/M input tokens for Sonnet）
  月费: 可能到$1000-$14502/月
  优点: 无限调用、高并发
  缺点: 费用不稳定、容易超支

订阅模式 (Claude Code CLI):
  费用: $20/月（Pro）或$200/月（Max）
  月费: 固定
  优点: 费用可控、够个人开发者使用
  缺点: 有限速、不能高并发
```

## 实操指南

### 方式1：Hermes通过Claude Code ACP模式调用

```yaml
# Hermes配置：使用订阅模式调用Claude
# 在delegate_task中设置acp_command为claude命令
delegate_task:
  acp_command: claude
  acp_args: ["--acp", "--stdio"]

# 这样子Agent会通过本地的Claude Code（用你的订阅）来运作
# 而不是通过API调用
```

### 方式2：直接在终端用Claude Code

```bash
# 用订阅模式
claude --acp --stdio

# 指定模型（Pro订阅可用Sonnet, Max订阅可用Opus）
claude --model claude-sonnet-4-20250514 --acp --stdio
claude --model claude-opus-4-20250514 --acp --stdio
```

### 方式3：在acp_args中控制模型

```yaml
# 在多Agent编排中使用订阅模式
tasks:
  - goal: "审查这段代码"
    acp_command: claude
    acp_args: ["--acp", "--stdio", "--model", "claude-sonnet-4-20250514"]

  - goal: "生成测试用例"
    acp_command: claude
    acp_args: ["--acp", "--stdio", "--model", "claude-sonnet-4-20250514"]
```

## 谁适合用订阅模式

| 场景 | 推荐模式 | 原因 |
|------|----------|------|
| 个人开发 | 订阅模式 | 固定费用可控 |
| 小团队（2-5人） | 1个Max订阅共享 | 够用且省钱 |
| 团队（5人+） | API模式 | 需要独立配额和并发 |
| 生产环境Agent | API模式 | 需要可靠性和稳定性 |
| 学习和实验 | 订阅模式 | 成本最低 |

## 注意事项

1. **订阅模式有限速** — Claude Code CLI调用Claude有速率限制，不适合高并发
2. **Pro和Max的可用模型不同** — Pro只能调用Sonnet, Max可以调用Opus+Sonnet
3. **订阅流量优先** — Claude会给Claude Code的订阅用户提供优先排队
4. **不能用于商业重分发** — 订阅模式的使用条款不允许你将Claude能力作为服务转售
5. **最好两者结合** — 高频简单任务用本地模型（Qwen3-Coder等），复杂任务用订阅Claude
