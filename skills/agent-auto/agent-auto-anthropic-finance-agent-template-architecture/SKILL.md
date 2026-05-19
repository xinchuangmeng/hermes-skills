---
name: Anthropic金融Agent模板参考架构 — 技能+连接器+子Agent模式
description: 基于Anthropic发布的10个金融Agent模板（2026年5月）。模板采用"技能+连接器+子Agent"三组件架构——每个Agent包含：领域技能（领域知识和指令）+ 连接器（受控数据访问）+ 子Agent（特定子任务委托）。可直接复用该架构设计自己的Agent。
tags: [agent, architecture, template, anthropic, finance, agent-design, subagent]
trigger: 当设计一个新Agent系统，需要参考生产级Agent架构设计模式时
---

# Anthropic金融Agent参考架构 — 技能+连接器+子Agent

## 核心架构模式

Anthropic在2026年5月发布的10个金融Agent模板采用统一的**三组件架构**：

```
┌─────────────────────────────┐
│         主Agent              │
│  ┌─────────┬─────────┬────┐ │
│  │ 技能    │ 连接器  │子Ag│ │
│  │ (领域   │ (数据   │ent │ │
│  │ 知识)   │ 访问)   │    │ │
│  └─────────┴─────────┴────┘ │
└─────────────────────────────┘
```

### 三组件详解

**1. 技能（Skills）** — 领域知识和任务指令
- 包含：业务流程、领域专业知识、任务步骤
- 示例：估值方法论、合规规则、报表模板
- 可以写为system prompt一部分或外部文件

**2. 连接器（Connectors）** — 受控数据访问
- 提供：安全的数据通道
- 支持：MCP应用（嵌入工具）、API Connector（实时数据）
- 关键：权限管控 + 审计日志

**3. 子Agent（Subagents）** — 特定子任务的委托模型
- 作用：主Agent调用子Agent执行专门子任务
- 示例：可比公司筛选、方法论合规检查
- 优势：隔离复杂度、专业化分工

## 操作步骤

### 1. 定义Agent的三组件

在创建Agent时，明确定义：

```yaml
# agent-template.yaml
agent:
  name: "金融报告生成器"
  
  skills:
    - "金融报告撰写规范"
    - "估值模型方法论"
    - "合规检查清单"
    - "数据源优先级"
  
  connectors:
    - type: "MCP"
      source: "Bloomberg数据终端"
      permissions: "只读"
    - type: "API"
      source: "内部CRM系统"
      auth: "OAuth2"
  
  subagents:
    - name: "可比公司筛选器"
      model: "claude-3-hiku"  # 便宜模型
      task: "从连接器获取数据，筛选可比公司列表"
    - name: "方法论检查器"
      model: "claude-opus-4"  # 强模型
      task: "验证估值方法是否符合公司策略"
```

### 2. Hermes中的实现方式

```python
# Hermes Agent中的三组件实现
from hermes_tools import delegate_task

class MyAgent:
    def __init__(self):
        self.skills = {
            "domain_knowledge": "领域知识库路径",
            "task_procedures": "操作流程模板",
        }
        self.connectors = {
            "api_endpoint": "https://api.example.com",
            "mcp_apps": ["数据库工具"]
        }
    
    def run_with_subagent(self, task, expertise_needed):
        """子Agent模式——委托子任务"""
        if expertise_needed == "数据筛选":
            result = delegate_task(
                goal="筛选并排序可比公司列表",
                context=f"使用以下数据源: {self.connectors}",
                toolsets=["terminal", "web"]
            )
            return result
```

### 3. 模型选择策略
- **主Agent**：使用强模型（Opus-class）处理复杂推理
- **子Agent**：使用便宜模型（Sonnet/Haiku-class）做子任务
- **连接器调用**：直接用API调用，不用Agent包装

## Anthropic已发布的10个模板（参考）

**研究与客户覆盖：**
1. 演示文稿构建器（Pitch Builder）
2. 会议准备器（Meeting Preparer）
3. 财报审阅器（Earnings Reviewer）
4. 模型构建器（Model Builder）
5. 市场研究员（Market Researcher）

**财务与运营：**
6. 估值审核器（Valuation Reviewer）
7. 总账对账器（GL Reconciler）
8. 月结管理器（Month-end Closer）
9. 报表审计器（Statement Auditor）
10. KYC筛选器（KYC Screener）

每个模板在 Claude Cowork / Claude Code 中作为插件可用，也在 Claude Managed Agents 中作为cookbook可用。

## 注意事项
- ⚠️ 子Agent的数量不是越多越好——每个子Agent增加round-trip
- ⚠️ 连接器的权限管控很重要——金融场景下审计日志必须完整
- ⚠️ 技能要写为可执行的指令，而非参考手册
- ⚠️ 子Agent的结果需要主Agent做最终校验和整合
- ⚠️ 该模式可以推广到任何专业领域（法律、医疗、工程等）

## 参考
- https://www.anthropic.com/news/finance-agents
- Anthropic Financial Services Marketplace for Claude Cowork/Code plugins
