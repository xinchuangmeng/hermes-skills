---
name: agent-auto-specialized-agent-fleet-pattern
description: Agent不应该是全能的，而应该像专家团队一样分工。来自WhatsApp AI Tutor生产系统——5个专业Agent（对话/语法/词汇/发音/进度）+ 意图分类路由。每个Agent只做一件事，但做到最好。核心收益：成本降低、质量提升、调试更容易。
tags:
  - multi-agent
  - specialization
  - agent-design
  - production-patterns
  - cost-optimization
  - agent-fleet
trigger:
  - 设计多Agent系统时不知如何分工
  - Agent总是答错专业问题
  - 不知道要不要把Agent拆细
  - 一个模型又想便宜又想质量高
  - "specialized agent pattern"
  - "agent fleet design"
  - "multi-agent specialization"
---

# Agent专业分工模式（Specialized Agent Fleet）

> **来源:** WhatsApp西班牙语AI Tutor生产系统，每天处理数千对话
>
> 核心理念：**一个Agent不需要会所有东西，只需要精通一件事。**

## 5个专业Agent的实战案例

WhatsApp西班牙语AI Tutor没有用一个"万能Agent"，而是拆成了5个：

| Agent | 模型 | 专业领域 | 占流量 | 误判惩罚 |
|-------|------|---------|--------|---------|
| **Conversation Agent** | Groq Llama-3 | 闲聊、理解检查、"你昨天做了什么" | 80% | 低——聊错了重聊就行 |
| **Grammar Agent** | Claude 3.5 | 复杂语法解释、虚拟语气、细微纠错 | 15% | 高——教错语法用户就废了 |
| **Vocabulary Agent** | GPT-4 + 自定义嵌入 | 词汇管理、间隔重复、新词引入 | 3% | 中——选错词浪费学习时间 |
| **Pronunciation Agent** | Whisper + speechace | 语音评分、音素级纠错、发音练习 | 1-2% | 低——发不准不影响理解 |
| **Progress Agent** | Oracle ML | 跨对话分析、难度调整、建议方向 | <1% | 中——进度不准用户不信任 |

## 路由层：意图分类

每个消息先过**意图分类器**（Groq，便宜快速），分派给对应Agent：

```
用户消息 → 意图分类 → Router → 专业Agent → 回复
```

**好处：**
- 不用每个Agent都加载所有模型
- 90%的消息不到100ms就回复了
- 语法Agent虽然慢，但只有15%的用户感觉到

## 为什么拆比合好

### 对比实验（估算）

| 维度 | 单体Agent | 5个专业Agent |
|------|-----------|-------------|
| 成本/月(1000用户) | $1,500+ | $618 |
| 平均响应时间 | 800ms | 120ms (80%请求) |
| 语法错误率 | 15% (啥都学啥都不精) | <3% (专注) |
| 调试难度 | 高 — 一个系统错了不知道哪有问题 | 低 — 对应Agent独立调试 |
| 模型选择灵活度 | 低 — 只能选一个模型 | 高 — 每块用最合适的模型 |

### 拆分的黄金准则

1. **每个Agent的知识边界必须清晰** — 如果两个Agent可能回复同一个问题，设计就有问题
2. **Agent之间不共享模型** — Conversation Agent用Groq，Grammar Agent用Claude，不需要统一
3. **每个Agent有独立的失败处理** — Grammar Agent挂了不影响Conversation Agent继续工作
4. **意图分类的准确率 > Agent的质量** — 把语法问题送到对话Agent，再好的对话Agent也答不对

## 实现架构图

```
                    ┌─────────────────────┐
                    │   Intent Classifier  │
                    │   (Groq, $0.0001)    │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │          │          │          │            │
   ┌────▼───┐ ┌───▼────┐ ┌───▼───┐ ┌───▼───┐  ┌─────▼──────┐
   │Convers.│ │Grammar │ │Vocab  │ │Pronun.│  │  Progress   │
   │Groq    │ │Claude  │ │GPT-4  │ │Whisper│  │  Oracle ML  │
   │$0.0001 │ │$0.003  │ │$0.01  │ │$0.036 │  │  (nightly)  │
   └────────┘ └────────┘ └───────┘ └───────┘  └─────────────┘
```

## 在Hermes中实现

```yaml
# config.yaml — 按任务类型配置不同模型
models:
  fast: { provider: groq, model: llama3-70b }
  accurate: { provider: anthropic, model: claude-sonnet-4-20250514 }
  specialized: { provider: openai, model: gpt-4 }
```

```python
# 在代码中实现路由
def route_message(message):
    """根据消息类型路由到最佳模型"""
    intent = classify_intent(message)  # 便宜模型做分类
    
    if intent == "simple_chat":
        return fast_model(message)      # 80% - 便宜快速
    elif intent == "complex_reasoning":
        return accurate_model(message)  # 15% - 强模型
    elif intent == "specialized_task":
        return specialized_model(message)  # 5% - 领域专家
```

## 注意事项

- ⚠️ **别过早拆分** — 先从一个Agent开始，只有在发现"单个Agent不够好"时才拆
- ⚠️ **拆了不代表成本翻倍** — 5个Agent各司其职比1个Agent啥都干更便宜（因为贵的模型只处理少量请求）
- ⚠️ **意图分类是命门** — 如果分类不准，复杂任务送到便宜模型，便宜模型答错；简单任务送到贵模型，成本爆炸
- ⚠️ **不需要5个Agent就强拆** — WhatsApp有5个是因为西班牙语教学需要5种专业能力。如果你的场景只需要对话，1个Agent就够了
- ⚠️ **Agent越多，测试越难** — 每个Agent的输入输出都要有独立测试用例
