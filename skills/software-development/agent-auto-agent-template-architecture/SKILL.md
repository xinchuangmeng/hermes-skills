---
name: agent-auto-agent-template-architecture
description: >
  Anthropic金融Agent模板架构方法论——将Agent拆为3层：Skills（领域指令+知识）、Connectors（数据源接入）、
  Subagents（子任务委派）。适用于构建企业级可复用的Agent模板，支持Claude Cowork/Code插件和Managed Agents两种部署模式。
tags:
  - agent-template
  - enterprise-agent
  - anthropic
  - agent-architecture
  - skills
  - connectors
  - subagents
  - managed-agents
trigger:
  - "Agent 模板设计"
  - "企业级 Agent 架构"
  - "Anthropic agent template"
  - "Skills Connectors Subagents"
  - "Claude Managed Agents"
  - "agent skill connector 架构"
  - "可复用的Agent"
  - "金融Agent"
---

# Anthropic Agent模板架构设计指南

## 核心架构：Skills + Connectors + Subagents

Anthropic在2026年4月发布的10个金融Agent模板，采用统一的**三层参考架构**：

```
+-- Agent Template -------------------------+
|                                            |
|  Skills（领域指令+知识）                    |
|  +-- 任务特定指令（模型规范、策略模板）     |
|  +-- 领域知识（市场术语、合规要求）         |
|  +-- 业务规则（阈值、审批流程）             |
|                                            |
|  Connectors（数据源接入）                   |
|  +-- 市场数据（S&P Capital IQ, MSCI, ...)  |
|  +-- 内部系统（数据仓库、CRM、文档库）       |
|  +-- MCP Apps（如Moody评级数据应用）         |
|                                            |
|  Subagents（子任务委派）                   |
|  +-- 同行业挑选                            |
|  +-- 方法验证                              |
|  +-- 其他专用模型                          |
+--------------------------------------------+
```

## 3层详解

### 第1层：Skills（技能层）

Skills是Agent的**大脑**——告诉Agent该怎么做、有哪些规则、用什么方法。

**包含内容**：
- **任务指令**：如"按照M&A估值三方法（DCF、可比公司、先例交易）构建模型"
- **领域知识**：金融术语、模型标准（如LBO模型、DCF模型的结构）
- **业务规则**："估值倍数不能超过行业均值30%"、"必须使用最新3年财报"

**在Hermes中怎么对应**：
每个Hermes skill的SKILL.md本身就承担了Skills层的角色——指令、知识、规则都在markdown里写清楚。

### 第2层：Connectors（连接器层）

Connectors是Agent的**感官**——从哪些数据源获取信息。

**支持的连接器类型**：
| 类型 | 示例 | 接入方式 |
|------|------|----------|
| 市场数据 | S&P Capital IQ, PitchBook, Morningstar | API Key / MCP |
| 研究数据 | MSCI, LSEG, Chronograph | 托管连接器 |
| 内部系统 | 数据仓库、CRM、文档库 | Custom Connector |
| MCP Apps | Moody MCP App（6亿+公司数据） | MCP服务器 |

### 第3层：Subagents（子Agent层）

Subagents是Agent的**双手**——做具体子任务的辅助Agent。

**典型子任务**：
- 可比公司选择：给一批候选公司，选最匹配的3-5个
- 方法验证：检查评估方法是否适用于当前场景
- 数据质量检查：核实数据源的时效性

**在Hermes中委托子任务**：
```python
# 使用delegate_task委托子任务
from hermes_tools import delegate_task
result = delegate_task(
    goal="从给定的10家公司中选出最匹配的3家作为可比公司",
    context="行业：SaaS，规模：1-5亿营收，利润：正运营利润",
    toolsets=["terminal", "file"]
)
```

## 部署模式

Anthropic提供两种部署方式：

### 模式A：作为插件（Plugin）
- **运行环境**：Claude Cowork 或 Claude Code
- **使用方式**：分析师启动后，Agent在本地桌面软件中工作
- **适用场景**：需要人工在回路中的协作场景
- **示例**："把手头所有的用户反馈整理成报告，发给整个团队"

### 模式B：作为Managed Agent
- **运行环境**：Claude Platform
- **使用方式**：预配置后自动运行（夜间任务、批量处理）
- **适用场景**：需要长时间运行、跨多笔交易的场景
- **特性**：
  - 长会话支持（多小时的交易结算）
  - 按工具设置权限
  - 托管凭据保险库
  - 完整审计日志

## 如何复用这个架构到自己的Agent

### 步骤1：定义Skills
```markdown
# Agent技能文档（对标Hermes的SKILL.md）
## 任务
[描述Agent要做的核心任务]

## 知识库
[列出该Agent需要知道的领域知识]

## 规则
[列出必须遵守的业务规则]
```

### 步骤2：配置Connectors
为每个数据源配置名称、接入方式、访问权限。

### 步骤3：设计Subagents
```
子Agent清单：
- 数据验证（用便宜模型） → 检查数据完整性
- 质量控制（用强模型） → 审查输出并修正
```

### 步骤4：选择部署模式
- **高频交互+人工监督** → Plugin模式
- **批量+无人值守** → Managed Agent模式

## 与Hermes Agent的对比

| 层次 | Anthropic模板 | Hermes对应 |
|------|--------------|-----------|
| Skills | .claude/skills/下的技能文件 | ~/.hermes/skills/下的SKILL.md |
| Connectors | MCP服务器+托管连接器 | MCP服务器配置 |
| Subagents | Claude Code subagent | delegate_task / 多Profile |
| 部署 | Cowork/Code / Managed Agents | 命令行 / 飞书/Telegram / cronjob |

## ⚠️ 注意事项

1. **Skills是核心**——Anthropic强调Agent模板的核心价值在于Skills的质量，其次才是Connectors和Subagents
2. **用户始终在回路中**——两个部署模式都强调"用户审核、迭代、批准后才对外发布"
3. **Connectors需要治理**——权限管理、数据合规、审计日志不可少
4. **Subagents不一定要用强模型**——子任务的精确度要求不同，可以用不同模型控制成本
5. **这个架构可泛化到非金融场景**——任何企业Agent都可以用这个三层结构

## 参考来源

- https://www.anthropic.com/news/finance-agents
- https://github.com/anthropics/financial-services
- https://platform.claude.com/docs/en/managed-agents/overview
