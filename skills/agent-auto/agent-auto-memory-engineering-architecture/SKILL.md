---
name: agent-auto-memory-engineering-architecture
title: "Agent记忆工程——从无状态提示词到持久化智能"
description: "基于Dev.to文章'Engineering Agent Memory'和Memary开源项目（216 points）——大多数AI系统在架构上是无状态的（每次会话从零开始），但生产级Agent需要结构化记忆。核心架构：捕获层→摄入管道→结构化记录→索引存储→应用层。比'把历史消息追加到prompt'更好的方法是分层记忆架构。适用于构建生产级持久化Agent系统。"
tags: [agent-auto, memory, persistent, architecture, stateless, eng-agent-memory]
trigger: |
  当需要构建需要持久记忆的Agent系统、遇到对话窗口长度限制、或想从无状态Agent升级到有状态系统时
---

# Agent记忆工程——架构设计指南

## 🎯 核心洞察

### 大多数Agent的无状态困境

```yaml
常见做法（不推荐）:
  conversation_history = []
  while True:
      user_input = get_input()
      conversation_history.append(user_input)
      prompt = "\n".join(conversation_history)
      response = llm.generate(prompt)
      conversation_history.append(response)
  # 问题: 超出token限制怎么办？跨会话怎么记忆？
  # 答: 简单追加历史消息到prompt不叫架构设计
```

这之所以能工作，是因为Demo场景下token够用。但生产环境的问题：

| 问题 | 后果 |
|------|------|
| 超出token限制 | 截断早期对话，丢失上下文 |
| 检索成本过高 | 每次生成都要处理所有历史 |
| 跨会话持久化 | Session一结束记忆归零 |
| 无关历史污染 | 干扰当前推理质量 |

### 核心转变：记忆是架构，不是抄写

> 问题不是prompt大小，**而是缺乏结构化的记忆系统。**

```
无状态系统:
  Prompt + 历史消息 → 输出

有状态系统:
  捕获层 → 摄入管道 → 结构化记录 → 索引存储 → 应用层
  ↑                                      ↓
  Prompt + 检索到的相关记忆 ←←←←←←←←←←←←
```

## 📋 Memary：开源Agent记忆系统架构

Memary（HN 216 points）是一个模仿人类记忆的Agent记忆系统：

### 核心架构

```yaml
memary_architecture:
  长期记忆层:
    存储所有重要知识
    使用向量嵌入/图数据库
    定期压缩和去重
  
  工作记忆层:
    当前会话的上下文（类似人脑短期记忆）
    有限容量，最新10-15条
    超限后自动摘要压缩
  
  情景记忆层:
    特定任务/场景的记忆
    按时间线组织
    可搜索和回溯
```

### 快速使用

```bash
pip install memary

# Memory配置文件示例
setup_config = {
    "llm_model": "gpt-3.5-turbo",  # 或本地Ollama模型
    "vision_model": "llava",
    "memory_type": "longterm",  # longterm / working / episodic
    "storage": "vector_db"      # 向量数据库后端
}
```

### 适用场景
- 客服Agent（需要记住用户之前的需求）
- 教育Agent（需要记录用户学习进度）
- 研究Agent（需要跨论文保持上下文）

## 🔧 实操模板

### 分层记忆架构（生产级）

```python
class AgentMemory:
    """三层Agent记忆架构"""
    
    def __init__(self):
        # 第1层: 工作记忆——最近上下文（Redis，10-15条）
        self.working_memory = deque(maxlen=15)
        
        # 第2层: 会话记忆——结构化JSON存储
        self.session_memory = {}
        
        # 第3层: 长期记忆——向量数据库
        self.longterm_memory = VectorDB()
    
    def add_interaction(self, user_input, agent_response):
        """添加一次交互到记忆系统"""
        # 1. 写入工作记忆
        self.working_memory.append({
            "user": user_input,
            "agent": agent_response,
            "timestamp": now()
        })
        
        # 2. 压缩（如果工作记忆满了）
        if len(self.working_memory) == 15:
            summary = self.summarize(self.working_memory)
            self.session_memory[get_session_id()] = summary
            self.working_memory.clear()
        
        # 3. 提取关键信息到长期记忆
        key_points = self.extract_key_facts(agent_response)
        for point in key_points:
            self.longterm_memory.add_embedding(point)
    
    def get_context(self, user_input):
        """为当前输入构建上下文"""
        context = []
        
        # 1. 最近工作记忆（最新鲜）
        context.extend(list(self.working_memory))
        
        # 2. 当前会话摘要（结构化）
        session_summary = self.session_memory.get(get_session_id())
        if session_summary:
            context.append(session_summary)
        
        # 3. 长期记忆检索（语义相关）
        relevant = self.longterm_memory.search(user_input, top_k=3)
        context.extend(relevant)
        
        return context
```

### Oracle记忆工程模式

Oracle AI Developer Hub提供的记忆模式示例：

```yaml
memory_patterns:
  上下文工程模式:
    思路: 不是把所有历史都塞进prompt，而是精心挑选最相关的
    实现: 
      1. 用嵌入对当前输入编码
      2. 在记忆库中语义检索
      3. 只检索Top-K最相关
    
  压缩模式:
    思路: 定期将历史摘要压缩为结构化记录
    实现:
      1. 每次对话结束时生成摘要
      2. 保存结构化JSON（含关键决策、用户偏好）
      3. 下次开始用摘要重建上下文
    
  分层路由模式:
    思路: 不同类型的记忆走不同通道
    实现:
      - 短期: Redis（毫秒级访问）
      - 中期: JSON DB（秒级）
      - 长期: 向量DB（语义检索）
```

## ⚠️ 注意事项

1. **记忆不是越大越好** — 给Agent喂过多记忆会稀释注意力，反而降低质量
2. **老化机制必要** — 3个月前的旧记忆可能已不相关，需要衰减/删除
3. **记忆污染是真实问题** — Agent的一次错误推理可能污染记忆库，需要清理机制
4. **成本和性能平衡** — 向量检索快但准确度不如结构化查询，混合使用最优
5. **隐私合规** — 记录用户历史需要合规处理（GDPR等）
6. **从无状态起步** — 初期不需要完整记忆系统，等Agent跑了2周积累数据后再设计记忆架构
