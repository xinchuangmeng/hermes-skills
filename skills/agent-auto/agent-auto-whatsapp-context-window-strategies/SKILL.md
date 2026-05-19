---
name: agent-auto-whatsapp-context-window-strategies
description: WhatsApp消息平台AI Agent的上下文窗口压缩策略——消息队列缓冲(按秒分批发)、用户消息超20条后自动压缩为摘要、表情符号替代自然语言(NFD Unicode处理)、时区感知调度。解决了消息平台并发爆发、token预算管理和多语言编码的三大生产问题。
tags:
  - context-window
  - token-optimization
  - messaging-agent
  - queuing
  - unicode
  - timezone
trigger:
  - Agent在消息平台上的上下文窗口管理
  - 用户一次性发太多消息导致token爆炸
  - 消息平台Agent的批量消息处理
  - 处理多语言消息时的编码问题
  - Agent需要按用户时区调整行为
  - "context window overflow"
  - "message buffering agent"
  - "token budget management"
---

# 消息平台Agent上下文窗口压缩策略

> **来源:** [Building AI Language Tutors on WhatsApp](https://dev.to/elenarevicheva/building-ai-language-tutors-on-whatsapp-why-messaging-apps-beat-web-11ke)
>
> WhatsApp生产系统验证的4大战术，解决了消息平台Agent特有的上下文管理问题

## 4大上下文战术

### 战术1: 消息队列缓冲 (Message Queuing)

**问题：** 消息平台用户会一次性甩出5-10条消息（"等等...还有...另外..."），直接全部喂给LLM会导致token爆炸和角色混乱。

**方案：** 用Redis队列缓冲消息，按秒分批发送给Agent。

```python
def process_whatsapp_messages(redis_queue, batch_window_ms=2000):
    """
    缓冲消息，每2秒批量处理一次
    """
    batch = []
    batch_start = time.time()
    
    while True:
        message = redis_queue.pop(timeout=batch_window_ms)
        if message:
            batch.append(message)
        
        elapsed = time.time() - batch_start
        if elapsed >= batch_window_ms / 1000 or len(batch) >= 5:
            if batch:
                # 批量处理：合并消息+压缩
                compressed = compress_message_batch(batch)
                response = llm_process(compressed)
                send_responses(response)
                batch = []
            batch_start = time.time()
```

**效果：** 将用户突发流量分散到分钟级处理，避免上下文窗口被刷爆。

### 战术2: 摘要压缩 (Conversation Summarization)

**问题：** 超过20条消息后，原始对话历史token太大。

**方案：** 不存原始对话，存压缩摘要。

```python
def compress_old_messages(conversation_history, max_messages=20):
    """
    超过20条消息后，用LLM把前面的对话压缩成摘要
    """
    if len(conversation_history) <= max_messages:
        return conversation_history
    
    # 前15条压缩成摘要
    old_messages = conversation_history[:-5]
    recent_messages = conversation_history[-5:]
    
    # 用LLM压缩：保留关键信息，扔掉废话
    summary = llm_compress(f"""
    将以下对话压缩成3句话的摘要，只保留：
    - 用户学会了什么
    - 在哪里卡住了
    - 有什么关键偏好
    ---
    {old_messages}
    """)
    
    return [
        {"role": "system", "content": f"[压缩摘要] {summary}"}
    ] + recent_messages
```

**效果：** 大量对话维持在小token预算内，不会随着时间的推移无限膨胀。

### 战术3: Unicode规范化 (NFD Normalization)

**问题：** Regex匹配对西班牙语重音、阿拉伯语RTL文本、中文汉字容易出错。

**方案：** 所有输入先NFD规范化再处理。

```python
import unicodedata

def normalize_text(text):
    """
    Unicode NFD规范化，确保文本匹配正确
    """
    # NFD: 将é分解为e + ́，使得regex匹配更准确
    return unicodedata.normalize('NFD', text)

# 应用
user_message = "cómo estás"  # 可能是多种编码
clean_message = normalize_text(user_message)  # → "como\u0301 esta\u0301s"
```

**适用场景：**
- 西班牙语重音符号（é, í, ó, ú, ñ）
- 阿拉伯语RTL文本（مرحبا）
- 中文/日文/韩文（汉字统一码）
- 任何多语言Agent的输入处理

### 战术4: 时区感知调度 (Timezone-Aware Scheduling)

**问题：** 全球用户在各自时区有不同的使用习惯，千篇一律的行为模式浪费机会。

**方案：** 根据用户时区调整提醒消息和难度。

```python
from datetime import datetime, timezone, timedelta
import pytz

def adjust_agent_behavior(user_timezone_str):
    """
    根据用户时区调整Agent行为
    """
    user_tz = pytz.timezone(user_timezone_str)
    now = datetime.now(user_tz)
    
    hour = now.hour
    weekday = now.weekday()
    
    if 6 <= hour < 10:
        # 早晨：轻松内容，鼓励性语气
        return {"tone": "encouraging", "difficulty": "easy", "type": "review"}
    elif 10 <= hour < 17:
        # 白天：正常难度，新知识
        return {"tone": "normal", "difficulty": "medium", "type": "new_material"}
    elif 17 <= hour < 22:
        # 晚上：高强度练习
        return {"tone": "challenging", "difficulty": "hard", "type": "practice"}
    else:
        # 深夜：简单复习或休息提醒
        return {"tone": "gentle", "difficulty": "easy", "type": "light_review"}
```

**效果：** 学生在东京早上7点和圣保罗晚上8点的学习体验不同，更贴合自然节奏。

## 在Hermes中集成

### 消息缓冲示例

```yaml
# config.yaml 或 Hermes任务中
cron:
  wrap_response: true  # 确保响应包装

# 终端命令：批量消息处理脚本
python -c "
from hermes_tools import web_search, terminal
import time, json
# 实现消息缓冲和压缩
"
```

### 压缩提示词模板

```
当前对话历史太长，请你执行压缩：
1. 只保留: 用户关键偏好、已学内容、当前难点
2. 压缩为2-3句话
3. 丢弃: 寒暄、重复、无关内容

历史对话:
{history_messages}

压缩摘要（3句话以内）:
```

## 数据验证

| 策略 | 效果（WhatsApp实战） |
|------|---------------------|
| 消息缓冲(2秒窗口) | 减少50%的token浪费，降低LLM角色混淆 |
| 20条后压缩 | 将长期对话维持在5K token以内 |
| NFD规范化 | 西班牙语标注匹配准确率从82%提升到99% |
| 时区感知 | 用户练习参与率提升40% |

## 注意事项

- ⚠️ **消息缓冲不要超过5秒** — 用户会以为Bot不理自己了
- ⚠️ **压缩摘要会丢失信息** — 重要细节可能在压缩中被丢弃，压缩后给用户一个确认机会
- ⚠️ **NFD规范化对已标准化的文本无副作用** — 可以安全应用于所有输入
- ⚠️ **时区感知只覆盖时间段，不覆盖个人习惯** — 有的用户就喜欢深夜学习，尊重用户选择
- ⚠️ **这些策略不仅适用于消息平台** — 任何上下文窗口容易膨胀的场景都可复用
