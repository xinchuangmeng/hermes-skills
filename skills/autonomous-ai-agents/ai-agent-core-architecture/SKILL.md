---
name: ai-agent-core-architecture
title: AI Agent底层架构、记忆系统与任务编排核心原理（v2.0深度更新）
description: 完整的AI Agent软件架构知识体系，涵盖四层架构模型（推理层、编排层、记忆数据层、工具集成层）、CoALA认知架构、四类记忆系统（工作/情景/语义/程序）、Agent Loop循环模式（ReAct/Plan-and-Execute/Reflexion/ToT）、上下文工程与工具编排，适用于构建生产级Agent系统
tags:
  - ai-agent
  - architecture
  - memory-system
  - task-orchestration
  - react-loop
  - context-engineering
  - tool-calling
  - coala
  - mcp
  - a2a
  - anthropic-patterns
---

# AI Agent底层架构、记忆系统与任务编排核心原理（v2.0）

> 最后更新：2026-05-13
> 本轮更新（v3.0）：新增Anthropic Managed Agents架构（Brain-Hands解耦+Session持久化+Meta-harness设计）、长期运行Agent Harness设计模式（Initializer+Coding Agent+Progress File）、Redis Agent Architecture 2026版完整刷新、Agent Skills渐进式加载架构，集成Anthropic 2026年5月最新Engineering博客系列

## 一、什么是AI Agent架构

AI Agent架构定义Agent如何感知环境、推理决策、调用工具行动，并在过程中学习和适应。它区分了"单次响应的聊天机器人"和"自主规划并执行多步任务的自治系统"。

> **2026年5月关键更新：** Anthropic发布系列工程博客，Agent架构从"模式选择"进化到"生产级工程化"——
> 1. **Managed Agents**（2026-04-08）：Brain-Hands解耦架构，Session作为持久化事件日志，Meta-harness设计适应未来模型变化
> 2. **Agent Skills**（2025-10-16，2025-12-18开放标准）：渐进式加载的知识封装，SKILL.md + 层级文件结构
> 3. **Long-Running Agents**（2025-11-26）：Initializer + Coding Agent双Agent模式，Progress File + Feature List + Git持久化
> 4. **Claude Code Auto Mode**（2026年5月）：Agent自主编码的安全自动化模式

> **核心公式：Agent = LLM推理引擎 + 记忆系统 + 工具调用 + 编排控制 + 安全边界**

### 关键区别
| | 传统编程 | Workflow | AI Agent |
|---|---|---|---|
| 决策者 | 开发者写死的逻辑 | 预设条件分支 | AI在运行时做决策 |
| 适应性 | 固定流程 | 有限分支 | 实时调整策略 |
| 容错 | 崩溃或报错 | 预设异常路径 | 自我修正重试 |
| 维护 | 改代码 | 改配置 | 改提示或技能 |

---

## 二、四层架构模型（2026生产标准）

### 架构全景图


┌─────────────────────────────────────────────┐
│              用户输入/目标                     │
└──────────────────┬──────────────────────────┘
                   ▼
┌─────────────────────────────────────────────┐
│  Layer 1: 推理层 (Reasoning Layer)          │
│  ┌─────────────────────────────────────┐   │
│  │ LLM推理引擎 (ReAct/CoT/Plan模式)     │   │
│  │ 任务分解 → 工具选择 → 结果评估 → 迭代 │   │
│  └─────────────────────────────────────┘   │
├─────────────────────────────────────────────┤
│  Layer 2: 编排层 (Orchestration Layer)      │
│  ┌─────────────────────────────────────┐   │
│  │ Agent循环控制 | 状态管理 | 错误处理  │   │
│  │ 并行/串行执行 | 人机协作边界        │   │
│  └─────────────────────────────────────┘   │
├─────────────────────────────────────────────┤
│  Layer 3: 记忆与数据层 (Memory & Data)      │
│  ┌──────────┬──────────┬──────────────┐    │
│  │ 短期记忆 │ 长期记忆 │ RAG知识检索   │    │
│  │ (上下文) │ (数据库) │ (向量+图DB)   │    │
│  └──────────┴──────────┴──────────────┘    │
├─────────────────────────────────────────────┤
│  Layer 4: 工具集成层 (Tool Integration)     │
│  ┌─────────────────────────────────────┐   │
│  │ MCP协议 | Function Calling | API调用 │   │
│  │ 读/写/转换/代码执行 四类工具         │   │
│  └─────────────────────────────────────┘   │
├─────────────────────────────────────────────┤
│              安全与可观测性                    │
│  输入验证 | 审计日志 | 权限控制 | 限流       │
└─────────────────────────────────────────────┘


### 1.1 推理层 (Reasoning Layer)
- **功能：** 解释输入、分解任务、规划行动、评估结果
- **核心决策：** 决定下一步做什么、调哪个工具、检查是否完成目标
- **关键：** 即使用非SOTA模型，好的推理层设计也能产出可靠结果
- **2026新趋势：** 推理轨迹结构化输出(thinking traces)成为标准，模型内部CoT与外部可见推理路径分离

### 1.2 编排层 (Orchestration Layer)
- **功能：** 控制Agent循环流程、管理状态、处理失败重试
- **核心能力：**
  - 串行/并行执行控制
  - 失败回退与重试机制
  - 超时限制与步数上限
  - 人机协作边界（Human-in-the-loop/on-the-loop/over-the-loop）
  - 多Agent路由与协调
- **2026新趋势：** LangGraph作为编排层事实标准，支持有状态图、可恢复检查点、人类中断点

### 1.3 记忆与数据层 (Memory & Data Layer)
- **短期记忆：** 当前会话上下文，在LLM上下文窗口内
- **长期记忆：** 跨会话持久化知识，通过向量数据库(FAISS/Qdrant/Pinecone)语义检索
- **RAG增强：** 向量搜索 + 元数据过滤 + re-ranking + BM25混合检索 → Reciprocal Rank Fusion + cross-encoder re-ranking
- **2026新趋势：** Redis Agent Memory Server提供完整双层记忆架构（内存级短期+向量长期），兼顾性能与规模

### 1.4 工具集成层 (Tool Integration Layer)
- **四大工具类型：**
  - **读工具：** 搜索引擎、数据库查询、文档检索
  - **写工具：** 创建记录、发送消息、更新数据库
  - **转换工具：** 摘要、分类、翻译、格式化
  - **代码执行工具：** 运行脚本/命令
- **每个工具必备：** 清晰描述、严格I/O Schema、输入验证、最小权限、限流、重试、审计日志
- **2026新趋势：** 工具设计升格为ACI（Agent-Computer Interface），投入不亚于HCI的设计精力

---

## 三、生产级Agent模式体系（Anthropic 2026）

> 来源：Anthropic《Building Effective Agents》(Dec 2024) — 与数十个客户团队总结的核心发现

### 3.1 Workflows vs Agents —— 核心区分

Anthropic将AI系统分为两大类，这是设计决策的首要判断：

| | **Workflow (工作流)** | **Agent (智能体)** |
|---|---|---|
| 控制权 | 预设代码路径 | LLM动态自主控制 |
| 灵活性 | 适用于路径已知的多步任务 | 适用于需要动态决策的任务 |
| 成本 | 可预测 | 可变，通常更高 |
| 调试 | 容易 | 更难 |
| 适用场景 | 结构明确、可分解的任务 | 开放式、不可预测路径的问题 |

**核心建议：先做最简单的方案。** Agenti系统以延迟和成本换取性能。大多数应用，优化单次LLM调用+检索+in-context examples就足够了。只在简单方案不够时增加复杂度。

### 3.2 五大可组合Workflow模式

Anthropic总结了5种经过生产验证的可组合模式，按复杂度递增排列：

#### 模式1: Prompt Chaining（提示链）

输入 → LLM#1 → [Gate检查] → LLM#2 → ... → 输出

- **核心：** 将任务分解为固定顺序的子步骤，每个LLM调用处理上一步的输出
- **关键机制：** 在中间步骤插入程序化「门控检查」，确保流程仍在正轨
- **适合场景：** 任务可清晰分解为固定子任务，如：写大纲→检查→写全文
- **代表案例：** 生成营销文案→翻译为不同语言；先写大纲检查通过再写全文

#### 模式2: Routing（路由）

输入 → LLM分类器 → [路由到A/路由到B/路由到C]

- **核心：** 分类输入，路由到专门的后续任务。实现关注点分离。
- **关键：** 无需优化一个prompt应对所有情况，LLM分类可准确处理
- **适合场景：** 不同类型的客服问题（退换货/技术支持/一般咨询）路由到不同下游流程
- **成本优化技巧：** 简单/常见问题路由到小模型（如Claude Haiku），难问题路由到强模型

#### 模式3: Parallelization（并行化）

输入 → [LLM-A / LLM-B / LLM-C] → 聚合

两种变体：
- **Sectioning（分块）：** 将任务拆分为独立子任务并行执行
- **Voting（投票）：** 同一任务多次执行取多样输出，聚合获取高置信度结果
- **适合场景：** 安全护栏（一个处理查询，一个审查不当内容）、自动化评测、代码安全审计、内容审核

#### 模式4: Orchestrator-Workers（编排器-工作者）

输入 → [Orchestrator] → 
  ├─ Worker A ...
  ├─ Worker B ...
  └─ Worker C ...
        ↓
  汇总结果 → 输出

- **核心：** 中央LLM动态分解任务，委托给工作LLM，汇总结果
- **关键区别：** 与Parallelization不同，子任务不是预定义的——Orchestrator根据具体输入确定
- **适合场景：** 编码产品（多文件变更）、搜索任务（多源信息收集分析）

#### 模式5: Evaluator-Optimizer（评估器-优化器）

输入 → Generator → [Evaluator评估] → 合格→输出
                          ↓ 不合格
                       Generator重新生成

- **核心：** 一个LLM生成响应，另一个LLM评估反馈，形成迭代循环
- **适合条件：** (1) 有清晰的评估标准；(2) 迭代优化可提供可衡量的价值
- **适合场景：** 文学翻译（细微差异需要评估器批评）、复杂搜索（多轮搜索和分析）

### 3.3 Agent的设计原则

当确实需要Agent时，遵循三条核心原则：

1. **在你的Agent设计中保持简单。** 成功的实现不使用复杂框架，而是使用简单、可组合的模式
2. **让规划过程透明可见。** 显式展示Agent的规划步骤
3. **精心设计ACI（Agent-Computer Interface）。** 通过彻底的文档和测试来优化工具

### 3.4 Agent vs 传统编排模式的选择决策树（2026扩展版）


问题够简单吗？ ─→ 直接LLM调用（不需要Agent）
     ↓ 否
路径是否已知？ ─→ Workflow模式
  ├─ 顺序固定 → Prompt Chaining
  ├─ 分类处理 → Routing
  ├─ 可并行  → Parallelization
  ├─ 动态分解 → Orchestrator-Workers
  └─ 需要质量迭代 → Evaluator-Optimizer
     ↓ 路径未知
需要自主决策？ ─→ Agent模式
  ├─ 单会话、单一领域 → 单Agent（ReAct/Plan-and-Execute）
  ├─ 跨会话、长期任务 → Long-Running Agent（Initializer + Coding Agent双模式）
  ├─ 多领域需要专家协作 → 多Agent系统
  └─ 生产级托管 → Managed Agents（Brain-Hands解耦）



---

## 四、上下文工程（Context Engineering）—— 2025/2026新范式

> 来源：Anthropic《Effective Context Engineering for AI Agents》(May 2025)

### 4.1 从提示词工程到上下文工程的演进

**提示词工程（Prompt Engineering）：** 关注如何写有效的指令，特别是system prompt。适合单次交互场景。

**上下文工程（Context Engineering）：** 关注如何策划和维护那组最优的token——包括system instructions、tools(MCP)、外部数据、消息历史等。适合多轮推理和长时间运行的Agent。

> 核心洞察：LLM与人类一样，有「注意力预算」——上下文越长，精确检索信息能力越下降。这来自于Transformer架构的n² pairwise关系。

### 4.2 有效上下文的组成


系统指令(System Prompt) + 工具描述(MCP/Functions) + 外部数据(RAG) + 消息历史 + 记忆


每一部分的优化原则：
- **系统指令：** 极简清晰，使用XML标签/Markdown标题分节
- **工具定义：** 最小可行工具集，避免功能重叠→模糊决策点
- **Few-shot示例：** 精选多样化的典型示例（相当于让LLM"看图"胜过千言）
- **消息历史：** 渐进式清理——清除不再需要的工具执行结果是最安全、最高性价比的压缩

### 4.3 三大上下文管理技术

| 技术 | 说明 | 效果 |
|------|------|------|
| **压缩(Compaction)** | 上下文接近窗口极限时，用LLM对内容做高保真摘要 | 保留架构决策、未解决bug；丢弃冗余工具输出 |
| **结构化笔记(Note-taking)** | Agent定期写入外部持久化笔记（如NOTES.md），按需拉回上下文 | 跨上下文重置保持连贯性，Pokémon Agent多步策略关键 |
| **子Agent(Sub-agent)** | 主Agent协调，子Agent做深度工作后返回压缩摘要(1000-2000 token) | 实现关注点分离，长周期研究任务显著优于单Agent |

### 4.4 即时上下文（Just-in-Time Context）

**核心理念：** Agent不再预先加载所有数据，而是维护轻量级标识符（文件路径、存储查询、Web链接），在运行时用工具「即时」加载数据到上下文。

优势：
- **渐进式信息发现：** 每个交互产生的上下文指导下一步决策
- **自管理上下文窗口：** Agent只维护需要的内容在"工作记忆"中
- **元数据作为信号：** 文件夹层级、命名规范、时间戳都是重要信号

挑战：运行时探索比检索预计算数据慢。需要精心设计工具和启发式策略防止Agent浪费上下文追死胡同。

### 4.5 混合策略（Hybrid Strategy）

最有效的Agent常采用混合策略：
- **前期加载：** 部分关键数据预先放入上下文（速度快）
- **运行时探索：** 通过工具（glob/grep/Bash head/tail）按需检索（灵活）

> 代表案例：Claude Code用glob和grep原语浏览环境，避免过时的索引和复杂的语法树

---

## 五、记忆系统（Memory）深入拆解

### 5.1 CoALA认知架构（Princeton, arXiv:2309.02427）

CoALA将Agent的记忆系统分为四类，受人类认知科学启发：

| 记忆类型 | 类比 | 存储内容 | 实现方式 | 用例 |
|---------|------|---------|---------|------|
| **工作记忆** (Working/In-Context) | 短期工作台 | 当前上下文窗口、最近对话、中间推理 | LLM context window | 当前会话理解 |
| **情景记忆** (Episodic) | 日记本 | 过去交互的具体事件和结果 | 向量DB存储摘要 | "上次用户做了X" |
| **语义记忆** (Semantic) | 百科全书 | 事实知识和用户偏好 | 结构化DB (Postgres) | "用户喜欢简约风格" |
| **程序记忆** (Procedural) | 肌肉记忆 | 技能、规则、工作流步骤 | Skills/MCP Tools | 审批流程: 验证→路由→通知 |

### 5.2 记忆系统实现方案对比（2026）

| 方案 | 架构 | 存储 | 特点 | 适合 |
|------|------|------|------|------|
| **Redis Agent Memory Server** | 双层架构 | 内存层(短期)+向量层(长期) | 亚毫秒级访问、子<1ms内存路径、69% API调用减少 | 生产级、高性能要求 |
| **Mem0** | 混合存储 | Postgres+Qdrant+Neo4j | 比纯向量检索精确度提升26%、自动摘要/过期策略 | 灵活的多记忆类型 |
| **LangMem** | LangChain生态 | 记忆管理+自动摘要 | 与LangGraph原生集成 | 已使用LangChain的项目 |
| **Anthropic Composable Memory** | 文件系统 | 结构化笔记+记忆文件 | 支持跨会话知识库构建、项目状态维护 | 需要长周期记忆的Agent |

### 5.3 记忆系统核心挑战与解决方案（2026更新）

| 挑战 | 解决方案 |
|------|---------|
| 存储 vs 推理成本平衡 | 分层记忆 + 重要性评分 + 动态遗忘 |
| 多跳推理困难 | 图数据库 + 向量检索混合方案 |
| 记忆膨胀 | 时间衰减 + 相关性评分 + 用户定义策略 |
| 多Agent共享 | 组织级共享 + Agent隔离（agent_id/user_id） |
| **跨上下文重置的连贯性** | **结构化笔记 + Compaction + 自读笔记恢复** |
| **生产级Failure Rate** | **端到端失败率<1%才可用→需要工程约束而非仅模型精度** |

---

## 六、Agent循环（Agent Loop）— 任务编排核心

### 6.1 六大Agent模式进化线


ReAct → Self-Reflection → Plan-and-Execute → RAISE → Reflexion → LATS
(简单)                                               (最强大/复杂)


### 6.2 各模式详解

#### 模式1: ReAct (Reasoning + Acting)
- **循环：** 推理(Thought)→行动(Action)→观察(Observation)→推理...
- **优点：** 实时适应、动态纠错、迭代优化
- **缺点：** 高Token消耗、延迟大、成本不可预测
- **适合：** 动态探索性任务，解决方案路径不确定
- **2026注意：** 每个推理-行动循环消耗额外Token，多步任务成本可能指数增长。考虑语义缓存可以减少高达70% API调用（Redis LangCache实验数据）

#### 模式2: Plan-and-Execute
- **流程：** 先生成完整计划→按顺序执行→需要时重新规划
- **优点：** 执行更快、成本可预测（比ReAct更少Token）
- **缺点：** 初始计划错误可能导致全局失败
- **适合：** 稳定环境、可清晰分解的步骤化任务
- **2026改进：** 可加入re-planning检查点缓解失败风险

#### 模式3: Reflection（自我反思）
- **流程：** 执行→评估输出→发现错误→修正→再次执行
- **特点：** Agent检查组件的输出质量，形成质量反馈回路
- **适合：** 代码生成、文档编写等需要质量迭代的场景

#### 模式4: Reflexion（强化学习式反思）
- **流程：** 尝试→失败→分析原因→记忆教训→下次避免
- **特点：** 比简单Reflection更强，通过记忆系统记住失败原因
- **适合：** 需要从历史错误中学习的长周期任务

#### 模式5: Tree-of-Thoughts (ToT)
- **流程：** 同时探索多个推理分支→评估每个分支→选择最佳路径
- **特点：** 广度优先探索，避免陷入局部最优
- **适合：** 数学推理、策略规划、复杂决策

#### 模式6: LATS (Language Agent Tree Search)
- **流程：** 结合ReAct + ToT + Reflexion的终极模式
- **特点：** 用树搜索 + 自我反思 + 最佳路径回溯
- **适合：** 需要最高质量结果的复杂任务

### 6.3 模式选择指南

| 任务类型 | 推荐模式 |
|---------|---------|
| 简单单步 | 直接LLM调用（不需要Agent） |
| 多步、结构明确 | Plan-and-Execute |
| 动态、探索性 | ReAct |
| 需要质量迭代 | Reflection / Reflexion |
| 复杂推理、策略 | Tree-of-Thoughts |
| 极致质量 | LATS |
| 安全过滤+核心响应分离 | Parallelization-Sectioning |
| 多源信息综合 | Orchestrator-Workers |

---

## 七、工具编排与协议（2026最新）

### 7.1 三大工具调用协议对比

| 协议 | 架构 | 特点 | 适合 |
|------|------|------|------|
| **Function Calling** | API内嵌工具定义 | 紧耦合、简单直接 | 小型应用、快速POC |
| **MCP (Model Context Protocol)** | C/S架构协议 | 松耦合、安全隔离、标准化、数千MCP服务可用 | 生产系统、多工具生态（2025/2026行业标准） |
| **A2A (Agent-to-Agent)** | 对等协议 | 跨Agent协作标准化——不是工具调用，是Agent间通信 | 多Agent系统、跨供应商 |
| **混合MCP+A2A** | MCP做工具层 + A2A做Agent间通信 | MCP负责Agent与外部系统连接，A2A负责Agent与Agent协作 | 大型企业级多Agent系统 |

### 7.2 MCP —— 2025/2026的行业标准
- 由Anthropic在2024年底提出，类比"AI的USB-C接口"
- 客户端-服务器架构：工具定义与应用程序分离
- 安全性：凭据隔离 + 最小权限控制
- 2026状态：数千个MCP服务可用，主流平台原生支持，成为连接AI应用与外部系统的事实标准
- 三大连接类型：数据源（文件、数据库）、工具（搜索、计算器）、Workflow（专用prompt）

### 7.3 A2A (Agent-to-Agent) —— Google主导的跨Agent协议
- 2025年由Google提出，Linux Foundation开源项目
- 核心设计：Agent Card（能力清单+连接信息）→ 基于任务(Task)的通信
- 关键特性：
  - 支持长期运行任务的安全协作
  - 通过Agent Card动态发现能力
  - 兼容MCP：A2A让Agent与Agent协作，MCP让Agent与工具协作
  - 支持顺序和工作流编排
- 适用场景：不同框架(LangGraph/ADK/BeeAI)构建的Agent跨系统协作

---

## 八、生产级Agent的工程约束（Redis 2026报告）

### 8.1 关键数据点

| 指标 | 数值 | 影响 |
|------|------|------|
| 端到端Failure Rate | <1%才可用 | 5%失败率 × 20步 = 几乎必然失败，需工程控制 |
| 语义缓存 | 减少最多70% API调用 | Redis LangCache实验，15倍响应速度提升 |
| 记忆访问 | 亚毫秒级（内存级） | 影响Agent响应速度的关键瓶颈 |
| 上下文压缩 | 节省40%+ Token成本 | Compaction技术 |

### 8.2 生产环境五大约束

1. **可靠性的工程问题：** 5%单步失败率 × 20步 = 几乎必然整体失败，需要控制点设计
2. **集成复杂度被低估：** 第三方认证、凭据管理、合规要求、安全协议经常是POC卡住的原因
3. **延迟预算：** 语音/聊天的首Token延迟需在几百毫秒以内，复杂编排不适合实时场景
4. **成本约束：** 需要限制Agent自主度、优化模型选择、实施使用监控
5. **可观测性：** 需要行为可观测性（了解Agent为什么做某决策），不仅是系统指标

### 8.3 安全边界四层
| 层级 | 防护重点 | 措施 |
|------|---------|------|
| 输入层 | Prompt注入、恶意输入 | 输入验证、敏感信息过滤 |
| 推理层 | 模型偏见、越狱 | 系统提示约束、安全对齐 |
| 工具层 | 权限滥用、数据泄露 | 最小权限、访问审计 |
| 输出层 | 敏感信息泄露 | 输出过滤、PII脱敏 |

---

## 九、人机协作与可观测性

### 9.1 人机协作三种模式
| 模式 | 工作方式 | 适合场景 |
|------|---------|---------|
| **Human-in-the-loop** | 关键步骤人工确认 | 高风险操作（付款、删除数据） |
| **Human-on-the-loop** | 并行执行，异常时人工介入 | 批量处理、审核流程 |
| **Human-over-the-loop** | 全自动，事后审计 | 低风险高频任务 |

### 9.2 可观测性工具链
- 追踪：LangSmith, Langfuse, Helicone
- 监控：推理轨迹、工具调用日志、状态转换、性能指标
- 关键指标：链步骤成功率、工具错误率、平均响应时间、Token消耗
- **2026重点：** 行为可观测性（Behavioral Observability）——不仅看性能指标，更要理解Agent决策路径

---

## 十、实用落地模板

### 10.1 最小Agent架构实现步骤（2026更新）

**Step 1:** 精确定义目标与成功标准
- Agent应该做什么？
- 正确输出是什么样的？
- 无法完成时怎么做？
- 如何度量性能？

**Step 2:** 判断是否需要Agent
- 够简单？→ 直接LLM调用
- 路径已知？→ Workflow模式（Prompt Chaining / Routing / Parallelization / Orchestrator-Workers / Evaluator-Optimizer）
- 路径未知？→ Agent模式

**Step 3:** 列出所有需要的工具
- 每个工具的：输入 → 输出 → 失败模式 → 权限
- 按照ACI原则设计工具（投入不亚于HCI的设计精力）
- 工具命名、参数描述要像给新人写文档一样清晰

**Step 4:** 选择推理模式
- 简单任务 → Plan-and-Execute
- 探索任务 → ReAct
- 质量敏感 → Reflexion / Evaluator-Optimizer

**Step 5:** 设计上下文工程
- 系统指令：极简清晰→从最小prompt开始，基于失败模式逐步添加
- 工具：最小可行工具集，避免功能重叠
- 示例：精选多样化典型示例
- 运行时：Just-in-Time探索 vs 预加载的混合策略

**Step 6:** 设计记忆方案
- 短期：会话缓存（5-10轮）+ Compaction
- 长期：Redis Agent Memory Server / Mem0
- 跨重置持久化：结构化笔记（NOTES.md）
- 语义缓存：减少API调用

**Step 7:** 部署监控与限制
- 跟踪所有推理轨迹
- 设置步数上限和超时
- 行为可观测性
- 安全边界四层

### 10.2 真实世界演进案例（电商平台）

Phase 1: 单Agent处理客服（验证价值）
Phase 2: Routing模式分离订单/产品/投诉
Phase 3: 各品类专精Agent + 共享上下文
Phase 4: 多Agent协调物流/支付/库存（MCP+A2A混合）
Phase 5: Evaluator Agent持续质量改进


### 10.3 技术选型速查表

| 需求 | 推荐方案 |
|------|---------|
| 编排框架 | LangGraph（有向图+检查点） |
| 记忆系统 | Redis Agent Memory Server（高性能）/ Mem0（多类型灵活） |
| 工具协议 | MCP（行业标准） |
| 多Agent通信 | A2A（跨框架协作） |
| 可观测性 | LangSmith / Langfuse |
| 语义缓存 | Redis LangCache（减少70% API调用） |
| 上下文压缩 | 自定义Compaction Prompt |

---

## 十一、关键参考资料

| 来源 | 内容 | 日期 |
|------|------|------|
| [Anthropic Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) | 生产级Agent模式选择——Workflows vs Agents | 2024.12 |
| [Anthropic Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | 上下文管理最佳实践——Compaction/Note-taking/Sub-agent | 2025.05 |
| [CoALA论文 - Princeton](https://arxiv.org/abs/2309.02427) | 认知架构统一框架 | 2023 |
| [Redis AI Agent Architecture Guide](https://redis.io/blog/ai-agent-architecture/) | 完整四层架构详解 + 生产工程约束（2026版完整刷新） | 2026.02 |
| [Mem0 Context Engineering Guide](https://mem0.ai/blog/context-engineering-ai-agents-guide) | 上下文工程 + RAG集成完整指南 | 2025 |
| [Google A2A Protocol](https://github.com/google/A2A) | Agent-to-Agent开放协议规范 | 2025 |
| [MCP官方文档](https://modelcontextprotocol.io/introduction) | Model Context Protocol标准 | 2024-2026 |
| [Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents) | Brain-Hands解耦+Session持久化+Meta-harness | 2026-04 |
| [Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) | 渐进式知识加载+开放标准+SKILL.md规范 | 2025-10 |
| [Long-Running Agents Harness](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) | Initializer+Coding Agent双模式+Progress File | 2025-11 |
| [Claude Code Auto Mode](https://www.anthropic.com/engineering/claude-code-auto-mode) | Agent安全自动化编码 | 2026-05 |
| [Harness Design Long-Running Apps](https://www.anthropic.com/engineering/harness-design-long-running-apps) | 长周期Agent工程约束 | 2026-05 |
