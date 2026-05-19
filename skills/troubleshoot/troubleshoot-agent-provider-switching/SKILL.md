---
name: troubleshoot-agent-provider-switching
title: "LLM Provider切换安全检查清单——换API提供商前必须检查的4件事"
description: "基于Dev.to文章《Morning notes: what I check before swapping LLM providers》——切换LLM Provider时最常见的坑：Streaming行为不一致、Tool Call格式不兼容、可观测性缺失、Fallback路径不通。提供每项的检查方法和具体验证代码。适用于所有使用付费API的Agent和LLM应用。"
tags: [troubleshoot, provider-switching, llm-api, checklist, cost-optimization]
trigger: |
  当需要切换LLM Provider（从A公司换到B公司）、添加备选Provider、或测试新Provider兼容性时
---

# LLM Provider切换安全检查清单

## 🎯 核心洞察

### "OpenAI兼容" ≠ 真的兼容

> **"OpenAI-compatible means more than accepting a chat request. For small teams, it should also mean the first failed request is easy to debug."**
>
> 大多数Provider自称"OpenAI兼容"——但实际兼容层只保证了最基本的聊天请求，关键功能（Streaming、Tool Call、可观测性）往往有细微差异。

### 最危险的假设

> 最贵的失败不是兼容失败本身，而是**失败后你完全不知道哪里出了问题**。

## 📋 4项强制检查

### ☑️ 检查1：Streaming行为一致性

**为什么重要**：不同Provider实现Streaming的方式不同——有的是Server-Sent Events(SSE)标准，有的是自定义格式。Streaming行为不一致会导致：
- 前端流式展示卡住或断断续续
- Token计数不准确
- 超时逻辑失效

**怎么检查**：
```python
"""检查新Provider的Streaming行为"""
import requests

def check_streaming(provider_url, api_key, model):
    """检查Streaming的3个关键行为"""
    
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "用5个字描述天气"}],
        "stream": True
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{provider_url}/v1/chat/completions",
        json=payload,
        headers=headers,
        stream=True
    )
    
    checks = {
        "status_code_ok": response.status_code == 200,
        "sse_format": check_sse_format(response),  # 是否标准SSE
        "chunk_consistency": check_chunks(response),  # chunk格式是否一致
        "finish_reason": check_finish_reason(response),  # 是否正确结束
    }
    
    return checks

def check_sse_format(response):
    """检查是否是标准SSE格式（data: {...}）"""
    for line in response.iter_lines():
        if line:
            decoded = line.decode('utf-8')
            if not decoded.startswith('data: ') and decoded != 'data: [DONE]':
                return False
    return True

def check_chunks(response):
    """检查每个chunk是否包含必要的字段"""
    for line in response.iter_lines():
        if line and line.startswith(b'data: ') and line != b'data: [DONE]':
            import json
            chunk = json.loads(line[6:])
            if 'choices' not in chunk:
                return False
            delta = chunk['choices'][0].get('delta', {})
            if not any(k in delta for k in ['content', 'role', 'tool_calls']):
                return False
    return True
```

**预期结果**：
| 行为 | 标准SDK兼容 | 说明 |
|------|------------|------|
| SSE格式 | 必须是`data: {...}` | Anthropic的MBX格式不兼容标准SDK |
| 结束标记 | `data: [DONE]` | 其他格式会被SDK误解 |
| Delta字段 | 必含choices[0].delta | 缺少则前端无法逐字展示 |

---

### ☑️ 检查2：Tool Call格式标准化

**为什么重要**：每个Provider的Tool Call格式略有不同——字段名、嵌套层级、参数类型都有差异。不兼容会导致Agent的Tool Calling完全失效。

**常见差异**：
| Provider | Tool Call格式差异 |
|----------|------------------|
| OpenAI | id + type: "function" + function.name/arguments |
| Anthropic | id + name + input（嵌套方式不同） |
| DeepSeek/Qwen | 基本兼容OpenAI格式，但有些字段为null |
| Google Gemini | 完全不同的结构（functionCall: {name, args}） |

**怎么检查**：
```python
"""检查Tool Call格式兼容性"""

tool_check_prompt = [
    {"role": "user", "content": "查询北京的天气，温度是多少度？"}
]

tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "获取指定城市的天气",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
            },
            "required": ["city"]
        }
    }
}]

def check_tool_calls(response):
    """检查Tool Call的格式"""
    choice = response.json()['choices'][0]
    msg = choice['message']
    
    checks = {
        "has_tool_calls": 'tool_calls' in msg,
        "tool_calls_not_null": msg.get('tool_calls') is not None,
        "has_id": all('id' in tc for tc in msg.get('tool_calls', [])),
        "has_function": all('function' in tc for tc in msg.get('tool_calls', [])),
        "function_has_name": all('name' in tc.get('function', {}) for tc in msg.get('tool_calls', [])),
        "function_has_arguments": all('arguments' in tc.get('function', {}) for tc in msg.get('tool_calls', [])),
        "arguments_is_json": check_arguments_is_json(msg.get('tool_calls', [])),
    }
    
    return checks
```

**失败场景**：
- 某些Provider的`tool_calls`返回空数组而非null → 被SDK忽略
- `arguments`是字符串（JSON string）还是对象 → Pydantic验证会报错
- 单次调用多tool_calls的排序和id规则不一致

---

### ☑️ 检查3：可观测性（Observability）

**为什么重要**：换了Provider后，如果不能看到准确的使用数据，就等于在盲飞。

**必须要能看到的信息**：
```yaml
# 每次请求必须能追踪到
observability_required:
  - requested_model: "你请求的模型名"
  - actual_model: "实际被调用的模型（可能被重定向）"
  - token_usage:
      prompt_tokens: 输入token数
      completion_tokens: 输出token数
      total_tokens: 总token数
    # 注意：有些Provider返回的token数只是「计费token」而非「实际token」
  - latency_ms: 响应延迟
  - timestamp: 请求时间
  - status: 成功/失败/超时
```

**怎么检查**：
```python
def check_observability(provider_url, api_key, model):
    """检查Provider是否返回必要可观测数据"""
    
    response = call_provider(provider_url, api_key, model)
    data = response.json()
    
    issues = []
    
    # 检查usage字段
    usage = data.get('usage', {})
    if not usage.get('prompt_tokens'):
        issues.append("缺少prompt_tokens")
    if not usage.get('completion_tokens'):
        issues.append("缺少completion_tokens")
    if not usage.get('total_tokens'):
        issues.append("缺少total_tokens")
    
    # 检查模型标识
    if data.get('model') != model and data.get('model'):
        issues.append(f"模型被重定向: {data.get('model')} != {model}")
    
    return {
        "has_issues": len(issues) > 0,
        "issues": issues,
        "raw_response_meta": {
            "has_model": 'model' in data,
            "has_usage": 'usage' in data,
            "has_created": 'created' in data,
            "has_id": 'id' in data,
        }
    }
```

---

### ☑️ 检查4：Fallback路径完整性

**为什么重要**：Provider的API可能因为网络、配额、认证等问题不可用。如果没有干净的Fallback路径，整个系统会级联崩溃。

**测试内容**：
```yaml
fallback_checklist:
  场景1: 支付失败
    操作: 使用已过期的API Key
    预期: 返回401且提供清晰的错误信息
    失败模式: 有些Provider返回500而非401
    
  场景2: 区域访问限制
    操作: 使用被限制区域的IP
    预期: 返回清晰的地域限制提示
    失败模式: 静默失败（请求看起来成功但没有内容）
    
  场景3: 配额耗尽
    操作: 超出Rate Limit
    预期: 返回429或清晰的配额提示
    失败模式: 静默降级（返回空但状态码200）
    
  场景4: 模型不存在
    操作: 请求不存在的模型名
    预期: 返回404
    失败模式: 自动回退到默认模型（用户不知道）
```

**实现干净Fallback的模式**：
```python
class ProviderManager:
    """多Provider Fallback管理器"""
    
    def __init__(self, providers: list):
        # providers = [
        #   {"name": "provider_a", "url": "...", "api_key": "...", "priority": 1},
        #   {"name": "provider_b", "url": "...", "api_key": "...", "priority": 2},
        # ]
        self.providers = sorted(providers, key=lambda p: p["priority"])
        self.failover_counts = {}  # 跟踪fallback次数
    
    def call_with_fallback(self, payload, max_retries=3):
        """按优先级尝试每个Provider"""
        for provider in self.providers:
            for attempt in range(max_retries):
                try:
                    result = self._try_call(provider, payload)
                    self._log_success(provider, result)
                    return result
                except AuthError:
                    # 认证错误 → 立即跳过这个Provider
                    break
                except RateLimitError:
                    # 限速 → 等一段时间再试
                    time.sleep(2 ** attempt)
                except TimeoutError:
                    # 超时 → 试下一个Provider
                    continue
                except Exception as e:
                    self._log_failure(provider, e)
                    self.failover_counts[provider["name"]] = \
                        self.failover_counts.get(provider["name"], 0) + 1
        
        raise AllProvidersFailed("所有Provider都不可用")
    
    def _log_success(self, provider, result):
        """记录成功调用（可观测性）"""
        print(f"✅ {provider['name']} 成功 | 模型: {result.get('model')} | Token: {result.get('usage')}")
    
    def _log_failure(self, provider, error):
        """记录失败事件"""
        print(f"❌ {provider['name']} 失败 | 错误: {error}")
```

## 🔄 Provider切换完整流程

```yaml
# 安全切换Provider的5步流程
provider_switch_workflow:
  第1天 — 评估:
    运行4项检查（Streaming/ToolCall/Observability/Fallback）
    记录兼容性差异
    决策: 是否需要适配层
    
  第2-3天 — 预发布:
    在非关键流量上启用新Provider（10%流量）
    监控: 错误率、延迟、Token差异
    比较: 新旧Provider的结果质量
    
  第4-5天 — 并行运行:
    新旧Provider各50%流量
    确保Fallback策略生效
    
  第6-7天 — 全量切换:
    新Provider全量
    观察24小时
    准备回滚方案
```

## ⚠️ 注意事项

1. **"OpenAI兼容"只是一个营销术语**——没有统一的兼容性认证标准
2. **Streaming和Tool Calling是最容易出问题的**——这两项占Agent工作流的80%
3. **Token计数差异会直接影响成本预算**——不同Provider对同一段文本的token计数可能差15-30%
4. **Provider可能在你不知情的情况下重定向模型**——检查response的model字段是否与请求一致
5. **Fallback路径必须在切换前测试**——不要在上线后发现Fallback也没配好
6. **记录每次切换的基准线**——包括延迟P50/P95、错误率、Token消耗，方便回滚决策
7. **小团队可以先用一个Provider，但至少知道Fallback方案**——不一定要立即配多Provider，但要准备好切换计划
