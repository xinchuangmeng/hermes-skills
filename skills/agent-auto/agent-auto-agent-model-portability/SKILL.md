---
name: agent-auto-agent-model-portability
title: "跨模型Agent架构——为最差模型设计，让最好模型提速"
description: "基于Opus 4.5 Agent体验文章的核心教训——不要为你最好的模型设计Agent系统。Opus 4.5表现出色，但如果你的系统只依赖它的出众能力，切换回GPT-4o或其他中等模型就会崩溃。核心原则：为最差模型设计（median-model architecture），让最好模型提速。含多模型测试流程、分级提示词设计、容错恢复策略。"
tags: [agent-auto, model-portability, architecture, multi-model, resilience]
trigger: |
  设计Agent系统架构时
  评估使用哪个LLM作为Agent后端时
  需要保障Agent在不同模型间迁移的稳定性时
  遇到"换模型后Agent能力断崖下降"问题时
---

# 跨模型Agent架构——为最差模型设计，让最好模型提速

## 🎯 核心洞察

> "Opus 4.5 is not the normal AI agent experience."
> 如果你只依赖最好的模型设计系统，那你的系统是脆弱的。

### 错误 vs 正确做法

```yaml
# ❌ 错误：为最佳模型设计
prompt: 简短、模糊（因为Opus能理解）
错误处理: 无（因为Opus很少出错）
重试逻辑: 无（因为Opus一次就对）
结果: 换个模型就崩了

# ✅ 正确：为最差模型设计
prompt: 详细、结构化
错误处理: 每步都有
重试逻辑: 内置（最多3次）
fallback: 降级到简单模式
结果: 任何模型都能跑，好模型跑得快
```

### 对比

| 维度 | 为最佳模型设计 | 为最差模型设计 |
|------|--------------|--------------|
| 提示词 | 简短、依赖模型理解力 | 结构化、步骤化、示例化 |
| 工具调用 | 假设模型会主动调用 | 明确指示何时调用什么 |
| 错误恢复 | 无或少 | 每步都有重试和回退 |
| 输出格式 | 自由文本 | 严格Schema+校验 |
| 模型依赖 | 紧耦合（换模型降级） | 松耦合（换模型无感） |

## 📋 架构设计指南

### 第1步：定义你的「最差模型」

```yaml
# 确定Agent系统必须支持的最弱模型
minimum_model:
  name: "GPT-4o mini 或同级"
  context_window: "至少32K"
  tool_calling: "支持基本function calling"

# 模型能力分级
model_tiers:
  tier_s: [Claude Opus 4.5, DeepSeek R1, GPT-5]
  tier_a: [Claude Sonnet 4, GPT-4o, DeepSeek V3]
  tier_b: [GPT-4o mini, Qwen3-Coder-14B, Claude Haiku]
```

### 第2步：分级提示词设计

```python
class PromptSelector:
    """根据模型能力选择提示词级别"""
    
    MODEL_TIERS = {
        "claude-opus-4": "minimal",
        "claude-sonnet-4": "standard",
        "gpt-4o": "standard",
        "gpt-4o-mini": "detailed",
        "deepseek-chat": "standard",
    }
    
    def get_prompt(self, model: str) -> str:
        tier = self.MODEL_TIERS.get(model, "standard")
        if tier == "minimal":
            return "完成以下任务，需要时调用工具。"
        elif tier == "detailed":
            return self._detailed_prompt()
        else:
            return self._standard_prompt()
```

### 第3步：容错恢复架构

```yaml
# 降级执行策略
graceful_degradation:
  步骤:
    1. 尝试完整执行（用当前模型）
    2. 如果失败 → 降级到更简单模式
       - 完整模式 → 分步模式 → 单步
    3. 仍然失败 → 寻求人类帮助

# 自动重试+模型切换
auto_retry_with_swap:
  尝试1: 当前模型，重试最多2次
  尝试2: 备用更强模型，重试1次
  尝试3: 人类介入

# 验证并重生成
verify_and_regenerate:
  生成 → 验证输出质量 → 
  不通过则用更详细prompt重生成 → 
  最多3次 → 返回最佳结果+警告
```

## 🔧 Hermes Agent配置示例

### 混合模型后端

```yaml
# config.yaml
model_providers:
  primary:     # 主力（强）
    provider: anthropic
    model: claude-sonnet-4-20250514
    temperature: 0.3
  
  fallback:    # 备用
    provider: deepseek
    model: deepseek-chat
    temperature: 0.3
  
  degraded:    # 降级（便宜快）
    provider: openai
    model: gpt-4o-mini
    temperature: 0.3

# 按任务复杂度选模型
model_selection:
  by_complexity:
    high: primary
    medium: fallback
    low: degraded
```

## 💡 多模型测试流程

```bash
# 1. 用最强模型测试
HERMES_MODEL=claude-opus-4-5 hermes run "任务"

# 2. 用中等模型测试
HERMES_MODEL=gpt-4o hermes run "任务"

# 3. 用最弱模型测试
HERMES_MODEL=gpt-4o-mini hermes run "任务"

# 目标：所有模型通过率>80%
```

## ⚠️ 常见陷阱

1. **不要依赖模型的隐性理解** — 显式说出所有步骤
2. **越长越差的模型** — 对开源模型（Qwen/LLaMA），长提示词可能降低性能
3. **格式一致性不能假设** — 用schema enforcement强制JSON输出
4. **成本管理** — 简单任务用强模型是浪费（贵5-10倍）
5. **模型更新后重新测试** — prompt老化现象真实存在
