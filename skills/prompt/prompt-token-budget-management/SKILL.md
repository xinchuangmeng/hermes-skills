---
name: prompt-token-budget-management
title: LLM Token预算管理和计数策略
description: "基于Dev.to《I built a client-side LLM token counter because I kept guessing at prompt costs》。核心方法：在发送给LLM前预先计算token数量，控制prompt长度和成本。提供客户端token计数方法、常见模型的token率速查、长上下文处理时的预算分配策略。适用于所有使用付费API的Agent场景。"
tags: [prompt, token, cost-control, budget, optimization]
trigger: |
  当需要控制token消耗、预估API成本或优化prompt长度时
---

# LLM Token预算管理和计数策略

## 核心洞察

很多开发者「凭感觉猜」prompt用了多少token，等到账单来了才后悔。

**核心方法：在发送给LLM之前预先计算token数，主动控制成本。**

### Token消费的大头在哪

```yaml
# Agent场景下的token消耗分布
System Prompt:   500-2000 tokens
用户输入:        200-1000 tokens
工具调用结果:    1000-10000+ tokens  ← 这里最大
Agent思考过程:   100-500 tokens
模型输出:         200-2000 tokens

总量:           2000-15000+ tokens/次调用
```

### 各模型token单价速查

| 模型 | 输入 (per 1K) | 输出 (per 1K) | 特点 |
|------|--------------|---------------|------|
| GPT-4o | $0.0025 | $0.01 | 平衡型 |
| Claude Sonnet 4 | $0.003 | $0.015 | 编码强 |
| Claude Opus 4 | $0.015 | $0.075 | 能力强但贵 |
| DeepSeek V4 | $0.0002 | $0.001 | 很便宜 |
| Qwen3-Coder | 免费（本地） | 免费（本地） | 本地部署 |

## 实操指南

### 方法1：客户端token计数

```python
# 方法1：用tiktoken（OpenAI模型）
import tiktoken

def count_tokens(text: str, model: str = "gpt-4") -> int:
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except:
        # fallback到cl100k_base
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))

# 使用示例
prompt = "你的系统提示词+用户输入+工具结果"
tokens = count_tokens(prompt)
print(f"预计token: {tokens}")
print(f"预估费用: ${tokens/1000 * 0.003:.4f}")
```

```python
# 方法2：任意文本的token估算（不需要模型特定编码）
import re

def estimate_tokens(text: str) -> int:
    """快速估算token数（约1 token = 0.75个英文单词或1.5个中文词）"""
    # 英文：1 token ≈ 4 chars
    # 中文：1 token ≈ 2 chars
    # 代码：1 token ≈ 3 chars
    return len(text) // 4  # 粗略估算
```

### 方法2：Agent上下文预算分配

```yaml
# 给Agent的上下文分配预算
context_budget:
  total_budget: 128000  # DeepSeek V4的窗口大小
  
  # 预算分配策略
  allocation:
    system_prompt: 2000  # 固定不变的部分
    conversation_history: 10000
    current_task: 5000
    tool_results: 30000  # 代码/搜索结果
    model_output: 8000
    
  # 超过预算时怎么办
  overflow_strategy:
    - 优先压缩：对工具结果做摘要而不是原样塞入
    - 次选截断：丢弃最早的历史消息
    - 最后选择：启用长窗口（128K）但注意成本
```

### 方法3：Agent工具的token审计

```python
class TokenAwareTool:
    """感知token消耗的工具包装器"""
    
    def __init__(self, max_tokens=10000):
        self.max_tokens = max_tokens
        self.total_used = 0
    
    def execute(self, func, *args, **kwargs):
        result = func(*args, **kwargs)
        # 估算token消耗
        result_str = str(result)
        tokens_used = len(result_str) // 4
        self.total_used += tokens_used
        
        if tokens_used > self.max_tokens:
            print(f"⚠️ 工具返回了{tokens_used} tokens，超出预算")
            # 自动压缩
            return self._compress(result, self.max_tokens)
        return result
    
    def _compress(self, data, limit):
        """压缩返回结果"""
        text = str(data)
        if len(text) // 4 > limit:
            return text[:limit*4] + "...[已压缩]"
        return data
```

### 方法4：Hermes中的token控制

```yaml
# Hermes config.yaml中的token控制
agent:
  max_tokens_per_step: 4000  # 每次工具调用的最大输出
  max_context_tokens: 32000  # 上下文窗口上限
  compress_threshold: 20000  # 超过此值自动压缩
  
  # 工具结果控制
  tools:
    max_result_tokens: 5000  # 单个工具结果上限
    web_search_result_length: 3  # 每个搜索最多返回3条
```

## 避坑要点

1. **不要用字符数估算token** — 中文、代码、特殊字符的token率差异很大
2. **Agent循环消耗比想象的大** — 每次工具调用都会把之前的结果重新塞入上下文
3. **System Prompt是沉没成本** — 每个请求都要带，所以不要塞太多不常用内容
4. **压缩比删除好** — 对历史做摘要比直接丢弃更好，保留关键信息
5. **花钱最多的不是输出，是输入** — 工具返回的大块数据才是真正吞token的地方
6. **本地模型做高频任务** — 用Qwen3-Coder/DeepSeek V4做高频低难度任务，付费API做复杂任务
