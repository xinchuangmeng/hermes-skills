---
name: prompt-agent-system-prompt
description: >
  AI Agent系统提示词（System Prompt）工程最佳实践——包含角色定义、任务规范、行为围栏、输出格式约束和ReAct推理模式的完整模板。
  适用于为Hermes Agent、Claude Code、GPT等LLM编写高质量的system prompt/sys prompt/SOUL.md。
  帮助将不可预测的LLM转化为可靠的生产级Agent。
tags:
  - prompt-engineering
  - system-prompt
  - sys-prompt
  - agent-prompt
  - chain-of-thought
  - react-pattern
  - SOUL.md
trigger:
  - "怎么写system prompt"
  - "提示词工程"
  - "agent提示词"
  - "sys prompt写作"
  - "prompt engineering agent"
  - "写Agent的角色定义"
  - "system prompt模板"
  - "behavioral guardrails"
---

# AI Agent系统提示词（System Prompt）工程最佳实践

## 核心原则

> "把提示词当成API设计：清晰、无歧义、可预测。好的API设计=好的prompt设计。"
> "最好的生产级AI系统不是有更好的模型——而是有更好的提示词工程。"

## System Prompt的6个关键组件

### 1. 角色/人格定义（Role/Persona）

**错误示范：**
```
You are a helpful assistant.
```

**正确示范：**
```
你是TechCorp的B2B SaaS客服Agent。你的职责是：
- 回答产品功能、定价和账户管理相关问题
- 排查常见技术问题
- 将复杂问题升级到人工客服

你有以下权限：知识库搜索、客户账户信息查阅。
禁止：透露其他客户信息、猜测未发布功能。
```

### 2. 任务规范（Task Specification）

```markdown
你的任务是分类客户咨询。输出格式必须为JSON：
{
  "category": "billing|technical|account|product",
  "confidence": "high|medium|low",
  "escalate": true|false,
  "follow_up_needed": true|false
}
```

### 3. 上下文/知识边界（Context）

```markdown
## 知识范围
- 产品文档：v2.0-v3.1版本
- 定价方案：Starter($50/月) / Pro($100/月) / Enterprise(定制)
- 常见问题：FAQ数据库
- 超出范围的问题：回复"我没有这个信息"而非猜测
```

### 4. 行为围栏（Behavioral Guardrails）

```markdown
## 关键规则（必须遵守）
1. 不知道就说不知道，不要编造
2. 不要承诺未确认的时间线和功能
3. 客户激动时先共情再解决问题
4. 涉及法律问题/退款>$500/客户要求时，必须升级人工
5. 不要使用行业黑话或空洞的商务用语
```

### 5. 输出格式规范（Format Specification）

```markdown
## 输出格式
- 技术问题：分步说明（1. 2. 3.）
- 账户问题：先用表格展示信息，再说明操作
- 疑难问题：先提供方案A（快速），再提供方案B（深度）

## 语气风格
专业但友好，避免：
- ❌ "根据公司政策，我们不得不通知您..."
- ✅ "我来帮您查看！"
- ❌ "利用我们的协同平台能力..."
- ✅ 用大白话解释
```

### 6. 示例（Few-Shot Examples）

```markdown
## 示例

用户："我忘记密码了"
输出：{"category": "account", "confidence": "high", "escalate": false, "follow_up_needed": false}

用户："这个功能不好使"
输出：{"category": "technical", "confidence": "medium", ...}
```

## 高级技巧

### Chain-of-Thought（思维链）

```markdown
回答技术问题时，按以下步骤思考（思考过程不输出给用户）：
1. 理解用户目标：他们想达成什么？
2. 识别相关产品功能/设置
3. 检查该场景的常见问题
4. 提供分步操作指引
5. 询问是否理解
```

### ReAct模式（推理+行动）

```markdown
你有以下工具可供调用：
- search_knowledge_base(query)
- get_account_info(user_id)
- create_support_ticket(description, priority)

处理用户问题时的思考模式：
THOUGHT: 我需要什么信息来回答？
ACTION: 调用相关函数
OBSERVATION: 检查函数返回结果
ANSWER: 基于观察结果给出回答
```

### Few-Shot最佳实践

- 包含**3-10个**示例（复杂任务更多）
- 覆盖**边界情况**和歧义输入
- 展示**精确的期望输出格式**
- 好的few-shot示例能提升准确率**15-25%**

## ⚠️ 常见陷阱

1. **提示词太长** → 超过800 tokens的prompt开始出现注意力衰减。关键指令放在开头
2. **角色定义太模糊** → "You are helpful" vs "你是具备X权限、Y职责、Z约束的客服Agent"
3. **缺少负例** → 只说要什么，没说不该要什么
4. **格式不强制** → 纯文本prompt vs Schema-enforced JSON（用Structured Outputs等框架）
5. **一次塞太多** → 一个Agent一个角色，不要试图让一个Agent做所有事
6. **未做版本控制** → prompt应该像代码一样：版本管理、测试、评审、持续改进

## 在生产中使用

```bash
# 提示词即代码(prompts-as-code)工作流
# 1. 写入文件，版本控制
git add system_prompt_v3.md
# 2. 写测试用例
# 3. 对比版本间的输出质量
# 4. 灰度切换（10%→50%→100%）
```

## 文档参考来源

- https://www.ai-agentsplus.com/blog/prompt-engineering-techniques-ai-agents-2026
- https://platform.openai.com/docs/guides/structured-outputs
- https://docs.anthropic.com/en/docs/build-with-claude/structured-outputs
