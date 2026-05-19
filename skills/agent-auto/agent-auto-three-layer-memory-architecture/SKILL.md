---
name: agent-auto-three-layer-memory-architecture
description: 从WhatsApp AI语言导师的生产架构中提取的3层Agent记忆架构——即时上下文(Redis/10-15条)、会话记忆(JSON DB/2-3轮对话)、长期模式(向量嵌入/夜间抽取)。总成本仅$0.02/用户/月。适用于需要持久记忆但不想烧钱的AI Agent应用。
tags:
  - memory-architecture
  - agent-memory
  - cost-optimization
  - multi-layer-storage
  - production-patterns
trigger:
  - 设计Agent的记忆系统时不知如何分层
  - Agent应用记忆存储成本太高($0.15+/用户/月)
  - 需要记忆但无法使用前端状态或Session Cookie
  - 构建WhatsApp/Telegram等消息平台AI机器人
---

# 三层Agent记忆架构 (Three-Layer Memory Architecture)

> **来源:** [Building AI Language Tutors on WhatsApp](https://dev.to/elenarevicheva/building-ai-language-tutors-on-whatsapp-why-messaging-apps-beat-web-11ke)
>
> 生产验证的WhatsApp西班牙语AI导师，67%月留存，总成本低于$2/用户/月

## 核心架构

| 层级 | 存储技术 | 存什么 | 成本 | 检索速度 |
|------|---------|--------|------|---------|
| **L1: 即时上下文** | Redis | 最近10-15条消息 | ~$0.02/用户/月 | <100ms |
| **L2: 会话记忆** | JSON DB + 索引 | 最近2-3轮对话 | ~$0.05/用户/月 | <500ms |
| **L3: 长期模式** | 向量嵌入(夜间抽取) | 压缩后的知识图谱 | ~$0.10/用户/月 | 1-5s |

## 各层详解

### L1: 即时上下文 (Immediate Context)
- **存什么:** 当前对话的最后10-15条消息，处理修正循环、澄清、练习连续性
- **技术选型:** Redis (子100ms检索)
- **为什么够用:** 用户不会在同一次对话中引用20条前的消息
- **在Hermes中:** 可以用文件缓存最近的N条对话

### L2: 会话记忆 (Session Memory)
- **存什么:** 最近2-3次完整对话的摘要，例如"昨天学虚拟语气时卡在第3个练习"
- **技术选型:** 结构化JSON数据库，带索引查找
- **关键设计:** 不是存原始对话，而是存**压缩摘要**
- **在Hermes中:** 可以用JSON文件按日期组织

### L3: 长期模式 (Long-term Patterns)
- **存什么:** 压缩后反复出现的错误模式、成功的教学时刻、进度标记
- **技术选型:** 向量嵌入，**夜间批量抽取** (不是实时)
- **为什么夜间处理:** 不重要用户等待，白天关注实时响应就好
- **在Hermes中:** 可以写cronjob定时做memroy总结和压缩

## 补充：Memary开源长期记忆框架（2026-05-15更新）

[HN热榜 216 points] Memary (https://github.com/kingjulio8238/memary) 是一个专门为自主Agent设计的开源长期记忆系统。

### Memary的核心设计

```yaml
Memary记忆模块:
  - 记忆存储：使用图数据库（Neo4j）而非向量数据库
  - 记忆组织：实体-关系图结构，模拟人类记忆的关联网络
  - 记忆检索：结合语义检索和关系图遍历
  - 记忆衰减：模拟人类遗忘机制，不常用的记忆逐渐弱化

与三层架构的映射:
  L1 (即时上下文) → Memary: 当前对话流
  L2 (会话记忆) → Memary: 短期图记忆（带衰减）
  L3 (长期模式) → Memary: 长期图记忆（实体-关系网络）
```

### Memary vs 传统向量记忆

| 维度 | 向量嵌入记忆 | Memary图记忆 |
|------|------------|-------------|
| 数据结构 | 向量+元数据 | 实体-关系图 |
| 检索方式 | 语义相似度 | 语义+关系遍历 |
| 关联推理 | ❌ 无法直接关联 | ✅ 支持路径推理 |
| 记忆衰减 | ❌ | ✅ 内置 |
| 部署成本 | 低（文件级） | 中（需要Neo4j） |

### 在Hermes中借鉴Memary的思路

```yaml
# 不用Neo4j，用JSON文件模拟实体-关系图
memory_graph:
  实体:  # 人、事、物、概念
    - id: "user_jingge"
      type: "user"
      attributes:
        name: "敬哥"
        focus: "跨境电商+AI Agent"
        
  关系:  # 实体之间的关联
    - source: "user_jingge"
      target: "skill_hermes"
      relation: "good_at"
      strength: 0.9
      last_updated: "2026-05-15"
    
    - source: "skill_hermes"
      target: "topic_crossborder"
      relation: "used_in"
      strength: 0.8
  
  检索合并: |
    当Agent需要记忆时：
    1. 找到相关实体
    2. 沿着关系图找到关联记忆
    3. 按strength排序返回top-K
```

## 核心原则

> "用户不需要完美的每一条历史记录。他们需要AI记住自己的痛点和学习风格。"

### 记忆分层原则
1. **最贵的存储存最少的数据** — 长期记忆只存压缩后的"模式"而非原始对话
2. **逐层衰减** — L1满后压缩进L2，L2满后摘要进L3
3. **不存不需要的** — WhatsApp AI tutor不存原始语音，只存"trilled R: 60% accuracy"

## 关键补充：上下文窗口压缩（来自WhatsApp实战）

来自同一生产系统的补充技巧（详见 agent-auto-whatsapp-context-window-strategies）：

### 1. 消息超20条后自动压缩
```python
def compress_old_messages(history, max_messages=20):
    if len(history) <= max_messages:
        return history
    old = history[:-5]
    recent = history[-5:]
    summary = llm_compress(f"压缩以下对话为3句摘要：\n{old}")
    return [{"role": "system", "content": f"[摘要] {summary}"}] + recent
```

### 2. 消息缓冲（防Token爆炸）
用户可能一次性发5-10条消息（"等等还有..."），先用Redis缓冲2秒再批量处理。

### 3. 多语言Unicode处理
所有文本先做NFD规范化（unicodedata.normalize('NFD', text)），确保西班牙语重音/阿拉伯语/中文匹配正确。

### 4. 时区感知记忆
用户在东京早上7点和圣保罗晚上8点的学习模式不同，记忆系统应该感知时区并差异化调度。

## 实操: 在Hermes中实现

### 方案1: 文件系统版 (最简单)
```
project/
  memory/
    l1_immediate.json      # 最近10条消息，随时覆盖
    l2_sessions/           # 每天一个文件，存对话摘要
      2026-05-07.json
      2026-05-08.json
    l3_long_term.json      # 手动或cron更新的长期知识
```

### 方案2: 结合memory tool
```
# 每次任务结束后，调用memory保存关键洞察
memory(action='add', target='memory', content='用户对XX功能有偏好')

# 定期执行压缩
# cronjob: 每天扫描memory，合并重复知识，清理过期内容
```

### 方案3: 消息平台Agent的记忆捷径（WhatsApp实战经验）

来自WhatsApp西班牙语AI Tutor生产系统的记忆优化技巧：

1. **不要存原始对话** — 存"用户混淆ser vs estar"而非"用户说：这咖啡是冷的吗？"
2. **用压缩摘要替代全历史** — 超过20条消息后，把早期对话压缩成"学会了X，在Y上卡住了"的摘要
3. **L3夜间批量处理** — 长期模式抽取不着急，设cronjob在低峰期跑
4. **直接问用户** — 比猜更快："上次我们练到虚拟语气了，要不要继续？" 如果用户说不，也不丢人

### 实战故事：一条JSON flag省了一个微服务

WhatsApp AI Tutor不用复杂的订阅管理面板，就三字段：
```json
{
  "subscription_active": true,
  "lessons_remaining": 15,
  "next_payment_date": "2026-06-01"
}
```
用户回复 "subscription status" 直接查 —— 不需要密码、不需要邮箱、不需要支持工单。

## 成本模型（按用户/月）

| 方案 | 成本 | 说明 |
|------|------|------|
| 全量存储在热内存 | $0.15+ | 典型Web应用 |
| 三层架构(含Redis) | $0.02 | WhatsApp AI Tutor 实测 |
| 文件版三层架构 | ~$0 | 纯文件系统，仅磁盘空间 |
| 语音处理（可选） | $22/用户/月 | ⚠️ 语音是成本大头：30秒录音=Whisper转录+speechace分析+语音合成=$0.036/次，20次/天=$22/月 |

## 注意事项

- 不要试图把所有历史都喂给LLM上下文窗口，上下文窗口会被占满，成本飙升
- 每层按需压缩，"越多越好"是误区
- L3的向量嵌入可以不用向量数据库，文件+关键词搜索也能凑合用
- 消息平台的限制(无前端状态/Session Cookie)迫使架构更干净，这条在设计任何Agent记忆时都适用
- **语音处理成本爆炸**：WhatsApp语音消息用于发音练习，30秒录音的完整流水线（下载→Whisper→speechace→语音合成）=$0.036/次，高频用户可达$22/月。Agent产品在设计语音功能前必须做成本模型
