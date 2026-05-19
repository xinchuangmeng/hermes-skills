---
name: agent-auto-orchestration-patterns
description: >
  多Agent编排模式选择指南——6种经生产验证的编排模式（Orchestrator-Worker、Sequential Pipeline、
  Fan-Out/Fan-In、Multi-Agent Debate、Dynamic Handoff），每种模式的适用场景、成本对比和已知失败模式。
  用于指导Hermes Agent的delegate_task、多Profile部署、多Agent协作场景的设计决策。
tags:
  - multi-agent
  - orchestration
  - agent-coordination
  - production-patterns
  - delegate_task
  - subagent
trigger:
  - "多Agent怎么协作"
  - "编排模式选择"
  - "multi-agent orchestration"
  - "agent coordination pattern"
  - "多个agent怎么配合"
  - "orchestrator worker"
  - "fan-out fan-in"
  - "sequential pipeline agent"
---

# 多Agent编排模式选择指南（生产验证）

## 背景

据Gartner报告，多Agent系统咨询量在2024-2025年间增长了**1445%**。组织平均使用12个Agent，这一数字将在2年内增长67%。
但**40%**的多Agent项目在部署6个月内失败——通常是因为选择了错误的编排模式。

## 6种编排模式详解

### 1. Orchestrator-Worker（调度器-工作者）

**原理**：一个调度Agent分解任务 -> 委托给多个专业Worker -> 汇总结果
**调度器用强模型**，Worker用便宜模型

**适用场景**：跨功能工作流（客服分流到计费/技术/产品等专家）
**成本**：比单一Agent方案节省**40-60%**
**实际案例**：Wells Fargo让35,000名银行员工在**30秒**内查到1,700个流程（原来10分钟）

**⛔ 失败模式**：
- 调度器是单点故障——一次误分类，下游全错
- 4个Worker以上时上下文频超限制
- 成本爆炸：测试$0.50/次的任务，100K次执行可能变成**$50,000/月**

---

### 2. Sequential Pipeline（顺序流水线）

**原理**：Agent按预定义线性链依次执行，前一个的输出是后一个的输入
**顺序在设计时确定**

**适用场景**：
- 文档处理：解析 -> 提取 -> 验证 -> 汇总
- 合同生成：模板选择 -> 条款定制 -> 合规审查 -> 风险评估
- 内容审核流水线

**⛔ 失败模式**：
- **错误传播**：第一步出错，后续全错，无法回溯
- **开销膨胀**：4个Agent的流水线约**950ms协调开销**（vs 500ms实际处理）
- **token浪费**：3个Agent流水线消耗**29,000 tokens** vs 单个Agent的10,000——如果不需要专业化，花费3倍

---

### 3. Fan-Out/Fan-In（扇出/扇入）

**原理**：多个Agent同时对相同输入或独立子任务执行
- **扇出**：分配任务给多个Worker并行处理
- **扇入**：通过投票、加权合并或LLM综合汇总

**适用场景**：
- 多视角分析（基本面/技术面/情绪面Agent并行分析股票）
- 并行代码审查（安全/风格/性能三路同时审）
- **优势**：4个独立任务墙钟时间减少**75%**

**⛔ 失败模式**：
- **API频率限制**：15个并发Agent × 150 req/s，后端限制100 req/s，各自不超但合计超
- **竞态条件**：N个Agent = N(N-1)/2个潜在并发冲突。5个Agent=10个冲突，10个=45个
- **汇总幻觉**：LLM综合可能制造虚假共识（买入派vs卖出派，汇总说"市场中性"）

---

### 4. Multi-Agent Debate（多Agent辩论）

**原理**：多个Agent在同一对话中参与讨论，贡献观点、互相质疑、多轮打磨
包括**Maker-Checker循环**（一个生成、另一个验证，直到通过）

**适用场景**：
- 合规审查（需要多专家视角）
- 质量保证高要求的场景
- 研究证实：辩论比单模型查询**减少幻觉**

**成本优化**：便宜的快速模型做Maker，强模型做Checker——质量提升但成本降低**40-60%**

**⛔ 失败模式**：
- **对话循环**：Agent争论不休永无止境。微软建议**限制群聊最多3个Agent**
- **奉承级联**：Agent倾向于随大流，即使大流是错的。5轮×3个Agent=**15次LLM调用**，结果可能还是错的

---

### 5. Dynamic Handoff（动态转交）

**原理**：每个Agent评估当前任务，决定自己处理还是转交给更合适的专家
无中央调度——基于运行时上下文自判断
**同一时间只有一个Agent活跃**

**适用场景**：
- 客服场景：计费问题中暴露出技术问题，自动转交
- 事先不确定需要什么专业知识的任务

**实际案例**：HCLTech报告通过动态转交**案件解决速度提升40%**

**⛔ 失败模式**：
- **无限循环转交**：A->B->C->A。**第一大致败因**
- **上下文丢失**：要么传完整上下文（昂贵，超窗口），要么汇总（有损，累积错误）
- **非确定性路由**：同样的输入可能走不同的路径，难以调试

---

### 6. Maker-Checker（生成-验证）

**原理**：一个Agent生成内容，另一个独立验证，通过后才释放

**适用场景**：代码审查流水线、内容审核、重要决策前的复核

---

## 模式选择决策树

```
你的任务是什么？
├── 任务可以明确拆分成独立子任务
│   └── 子任务之间有序依赖 → Sequential Pipeline
│   └── 子任务可以并行执行 → Fan-Out/Fan-In
│   └── 需要统一调度分配  → Orchestrator-Worker
├── 任务需要专业判断/质量验证
│   └── 需要多视角交叉验证 → Multi-Agent Debate
│   └── 需要生成+验证双保险 → Maker-Checker
├── 任务方向会变化，不确定需要什么专家
│   └── 让Agent自己判断 → Dynamic Handoff (慎用！)
└── 简单明确的单任务 → 不需要多Agent，单个Agent搞定
```

## ⚠️ 注意事项

1. **先单后多**：能用一个Agent解决的就不要用多个。多Agent引入的是复杂度而非智能
2. **成本模拟**：部署前按预估执行量做成本模型（参考：Orchestrator-Worker $0.50测试→$50K/月的真实案例）
3. **失败模式不忽视**：每种模式都有明确失败路径，部署时需预置熔断机制
4. **60%的Agent工作其实不需要多Agent**：善用产品分析判断是否有必要
5. **Gartner警告**：截至2027年，**40%的Agent项目可能被取消**——确保你的编排模式兼顾ROI

## 最新补充（2026-05）

### Agent角色模式语言（Pattern Language）

最新的多Agent设计实践提出5种核心角色：

| 角色 | 职责 | 核心原则 |
|------|------|---------|
| **Producer（生产者）** | 把模糊输入转为明确工作项 | 产出物下游能否直接执行？ |
| **Consumer（消费者）** | 用专业技能执行工作项 | 是否需要回看原始输入？ |
| **Coordinator（协调者）** | 管理任务分配和进度 | 失败时能否优雅降级？ |
| **Critic（批评者）** | 审查产出提改进意见（不能改） | 是否设置迭代上限？ |
| **Judge（裁判）** | 多个产出间做最终裁决 | 能否给出确切理由？ |

**核心规则**：Critic不能自己改内容、迭代必须有上限（推荐3轮）、Judge要能解释裁决理由。

详情见技能 `agent-auto-producer-consumer-patterns`

### WhatsApp 5-Agent专业分工模型

最新生产验证的模式（2026-05）：将一个领域拆成5个专业Agent：

| Agent | 模型 | 成本/次 | 流量占比 |
|-------|------|---------|---------|
| 对话Agent | Groq Llama-3 | $0.0001 | 80% |
| 语法Agent | Claude 3.5 | $0.003 | 15% |
| 词汇Agent | GPT-4 | $0.01 | 3% |
| 发音Agent | Whisper+speechace | $0.036 | 1-2% |
| 进度Agent | Oracle ML | 低 | <1% |

**核心原则**：用意图分类器做路由，80%流量走便宜模型。成本$618/月(1000用户) vs 单体Agent $1500+。

详情见技能 `agent-auto-specialized-agent-fleet-pattern`

### Anthropic Agent三层架构

Anthropic金融Agent模板定义了**Skills + Connectors + Subagents**三层：
- **Skills**：指令+知识+业务规则（对应Hermes的SKILL.md）
- **Connectors**：数据源接入（MCP服务器/API）
- **Subagents**：子任务委派（对应delegate_task）

两种部署模式：Plugin/Cowork（人工协作）vs Managed Agents（无人值守+审计日志）

详情见技能 `agent-auto-agent-template-architecture` 和 `agent-auto-vision-vs-api-cost`

## 参考来源

- https://beam.ai/agentic-insights/multi-agent-orchestration-patterns-production
- https://promptengineering.org/agents-at-work-the-2026-playbook-for-building-reliable-agentic-workflows/
- https://www.digitalapplied.com/blog/multi-agent-orchestration-patterns-producer-consumer
- https://www.anthropic.com/news/finance-agents
