---
name: agent-auto-llm-workflows-production
title: "生产环境生存的4种LLM工作流模式"
description: "基于Dev.to文章《Four LLM Workflows That Actually Survive Production》——在真实生产环境中经受考验的4种LLM工作流模式：①结构化提取(Extraction)②事实层+生成层分离(Draft Generation)③置信度路由三分类(Triage)④文档卫生优先的RAG。每种的实现代码、验证方法和常见失败模式。适用于所有在生产环境使用LLM的团队。"
tags: [agent-auto, llm-workflows, production-patterns, extraction, triage, rag, draft-generation]
trigger: |
  当需要设计生产环境的LLM工作流、遇到LLM在生产环境不稳定、或评估LLM工作流模式的可靠性时
---

# 生产环境生存的4种LLM工作流模式

## 🎯 核心洞察

### 一句话结论

> **不要问LLM做"对话"，要问LLM做"提取"——结构化输出在生产环境最可靠。**

作者引用了多个生产系统（包括WhatsApp AI Tutor等）的经验，提炼出4种经过生产验证的工作流模式。

## 🔷 模式1：结构化提取（Extraction）

### 适用场景
从非结构化文本（PDF、邮件、工单、表单、聊天记录）中提取结构化数据

### 核心代码
```yaml
# System Prompt
你是一个数据提取器。只输出JSON，不要输出解释。

提取字段：
- customer_name: string | null
- issue_type: "billing" | "technical" | "account" | "other"
- priority: "low" | "medium" | "high"
- refund_requested: boolean
- summary: string（20字内）

规则：
- 缺少字段值→用null，不要猜测
- 不要解释提取结果
- 只输出JSON，没有markdown包裹
```

```python
# 验证层
from pydantic import BaseModel

class ExtractedTicket(BaseModel):
    customer_name: str | None = None
    issue_type: str  # "billing" | "technical" | "account" | "other"
    priority: str    # "low" | "medium" | "high"
    refund_requested: bool = False
    summary: str

def extract_from_ticket(raw_text: str) -> ExtractedTicket | None:
    """提取工单信息，用Pydantic验证"""
    try:
        result = llm_call(system_prompt, raw_text)
        return ExtractedTicket.model_validate_json(result)
    except ValidationError:
        # 验证失败 → 用更窄的prompt重试
        result = llm_call(fix_prompt, raw_text)
        try:
            return ExtractedTicket.model_validate_json(result)
        except:
            return None  # 交给人工处理
```

### 成功关键
- ✅ **不解释**：不要问"告诉我你觉得是什么"，直接要JSON
- ✅ **不闲聊**：不要对话模式，要纯提取模式
- ✅ **严格验证**：Pydantic验证=第一次防线，第二次还失败就走人工
- ✅ **null比乱猜好**：强制用null表示缺失字段

### 常见失败
- LLM输出markdown包裹的JSON（```json...```）→ prompt里明确说不要
- LLM喜欢解释（"我认为..."）→ 在prompt里严厉禁止
- 字段名幻觉 → 严格用Pydantic schema限制

## 🔷 模式2：事实层+生成层分离（Draft Generation）

### 适用场景
生成邮件、报告、摘要等需要"事实准确+风格自然"的内容

### 核心原则
> **永远不要让LLM从记忆中生成事实——你的代码拥有事实，LLM只负责润色。**
>
> 不要在prompt里写「根据你的知识生成邮件」，要写「基于下面的数据生成邮件」。

### 实现方式
```python
def build_context(ticket):
    """你的代码构建事实对象，LLM不参与"""
    return {
        "customer_name": ticket.customer_name or "尊敬的客户",
        "issue_type": ticket.issue_type,
        "priority": ticket.priority,
        "refund_status": "已批准" if ticket.refund_requested else "待处理",
        "policy_reference": get_policy_text(ticket.issue_type),  # 从数据库查
        "resolution_steps": get_resolution_steps(ticket.issue_type),  # 从知识库查
    }

def generate_reply(ticket_id):
    """生成回复：你的事实 + LLM的润色"""
    context = build_context(get_ticket(ticket_id))
    
    prompt = f"""
根据以下数据生成客户回复邮件：

客户名: {context['customer_name']}
问题类型: {context['issue_type']}
优先级: {context['priority']}
退款状态: {context['refund_status']}
相关政策: {context['policy_reference']}
解决步骤: {context['resolution_steps']}

要求：
1. 只使用上面提供的事实
2. 不要发明政策细节
3. 语气专业有礼貌
4. 200字以内
"""
    return llm_call(prompt)
```

### 成功关键
- ✅ **代码拥有事实**：所有业务规则、价格、策略都在你的代码里
- ✅ **LLM只做风格**：它负责把事实写成自然语言
- ✅ **可审计**：事实层和生成层分开，方便调试
- ✅ **不改prompt可以改数据**：改数据库里的策略文本就行了

### 常见失败
- LLM忽略提供的事实，自己编造 → prompt里加强"只使用以下事实"
- LLM把数字搞错 → 用f-string直接嵌入，不要用让LLM计算的方式
- LLM风格不一致 → 提供1-2个范文作为few-shot

## 🔷 模式3：置信度路由三分类（Triage）

### 适用场景
分类/路由任务——工单分类、内容审核、意图识别

### 实现方式
```yaml
# 让模型输出分类+置信度
system_prompt: |
  任务：对以下客户请求进行分类

  输出格式（JSON）：
  {{
    "category": "billing" | "technical" | "account" | "general",
    "confidence": 0.0-1.0,
    "reasoning": "简短分类依据"
  }}

  规则：
  - 低置信度（<0.7）时尽量标记为"general"
  - 不确定的不要硬猜
```

```python
# 基于置信度的三级路由
def route_request(text: str):
    result = llm_classify(text)
    
    if result.confidence >= 0.9:
        # 高置信度 → 自动处理
        auto_handle(result.category, text)
    elif result.confidence >= 0.6:
        # 中置信度 → 带建议排队人工
        queue_for_review(result.category, text, model_suggestion=result)
    else:
        # 低置信度 → 走现有流程（不需要改）
        existing_process(text)
```

### 成功关键
- ✅ **渐进式上线**：先保守（只处理高置信度），慢慢扩大范围
- ✅ **审核确认**：每周审核误分类案例，改进prompt
- ✅ **逃生舱机制**：低置信度走老流程，不影响生产效率

### 常见失败
- 模型总是给高置信度（即使错了）→ prompt里要求校准
- 分类太粗或太细 → 调整分类粒度，保持5-7个类别
- 类间边界模糊 → 增加few-shot例子明确边界

## 🔷 模式4：文档卫生优先的RAG（Retrieval）

### 适用场景
需要从文档库检索信息辅助LLM回答

### 核心原则
> **不要问「用什么分块策略」，先问「你的文档干净吗？」**

### 实现步骤
```yaml
# 先做文档卫生，再做RAG
document_hygiene:
  步骤1: 去重 — 删除相同或高度相似的文档
  步骤2: 添加元数据 — 每个文档标记归属部门/产品线/版本
  步骤3: 标注日期 — 每个文档的创建/更新时间
  步骤4: 拆分大文档 — 将巨型页面拆成稳定的独立章节
  步骤5: 建立分区索引 — 按产品线/客户分级分区

rag_with_hygiene:
  检索策略:
    - 先限定搜索域（哪个产品线、哪个客户级别）
    - 再在限定域内搜索
    - 只返回最相关的3-5个片段

  关键指标:
    - 检索命中率（首次检索找到正确答案的比例）
    - 无结果率（LLM报告找不到信息）
    - LLM幻觉率（生成的内容与检索结果不一致的比例）
```

### 成功关键
- ✅ **小且干净的语料库 > 大而乱的**：100条干净文档好过10000条垃圾
- ✅ **分区检索**：先限定搜索域，减少噪音
- ✅ **元数据过滤**：日期过滤、版本过滤、部门过滤
- ✅ **定频清理**：每月清理过期文档

### 常见失败
- 文档没去重 → 检索到多个版本导致LLM混淆
- 过期文档还在索引里 → LLM用了旧信息
- 分块策略调了又调，但文档本身就脏

## 📊 模式选择指南

| 你的需求 | 推荐模式 | 为什么 |
|---------|---------|--------|
| 从非结构化文本取数据 | 模式1：提取 | JSON可靠、易验证 |
| 生成客服回复/报告 | 模式2：生成 | 事实和风格分离，安全 |
| 工单/内容分类 | 模式3：三分类 | 渐进式上线，风险可控 |
| 知识库问答 | 模式4：RAG | 先清洁文档，再建检索 |

## ⚙️ 生产环境必备的基础设施

```yaml
# 所有4种模式都需要的基础设施
infrastructure_stack:
  1. 消息队列 — 异步任务的基础（Celery/Redis Queue）
  2. 类型验证 — 强制LLM输出符合预期（Pydantic/Zod）
  3. Prompt版本控制 — 在Git中管理prompt模板（不在代码里硬编码）
  4. 链路追踪 — 记录每次调用的延迟/token/结果
  5. 审核UI — 低置信度和失败案例的人工审查界面
  6. 离线评估 — 换prompt前先在测试集上跑分
```

## ⚠️ 注意事项

1. **Prompt漂移是沉默杀手**——产品改名、状态调整后，prompt里的旧名称会无声失效。解法：把业务术语维护在外部文件，prompt只引用变量名
2. **不要在干净的数据上测试，要在脏数据上测试**——OCR垃圾、表情符号、中英混合、日志片段，这些都是生产里真正遇到的
3. **没有重试预算等于没有容错**——每个LLM调用都要准备重试、限速、超时处理，带上幂等键
4. **不要对LLM输出做精确匹配**——选精确的指标：字段准确率、处理时间缩减、首次回复质量、拒单率、人工接受率
5. **离线评估先于生产部署**——换模型/prompt之前，先在历史数据集上跑一遍
