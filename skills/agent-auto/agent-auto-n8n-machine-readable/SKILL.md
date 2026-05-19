---
name: agent-auto-n8n-machine-readable
title: "n8n节点机器可读数据集——让Agent自动构建工作流"
description: "基于Dev.to文章——作者将n8n的524个节点转为机器可读数据集（含输入/输出/触发条件/认证方式等结构化信息），使AI Agent可以自动理解并编排工作流。核心价值：传统n8n工作流构建依赖人工拖拽，现在Agent可以基于数据集理解每个节点的能力，自主组装工作流管道。适用于需要自动化工作流编排的场景。"
tags: [agent-auto, n8n, workflow-automation, machine-readable, agent-workflow]
trigger: |
  当需要让Agent自动构建n8n工作流、讨论工作流自动化方案、或评估Agent编排工作流的能力边界时
---

# n8n节点机器可读数据集——让Agent自动构建工作流

## 🎯 核心洞察

### 问题背景
传统的n8n工作流构建方式：
- 人工拖拽节点
- 逐个配置每个节点的参数
- 手动连接节点间的数据流
- 依赖人的经验来选择合适的节点组合

### 解决方案
将n8n的524个节点全部转为结构化的机器可读数据集，包含：
- 每个节点的输入/输出格式
- 触发条件和认证方式
- 节点间的兼容性关系
- 使用场景和最佳实践

这样AI Agent就能：
1. **理解所有节点的能力** — 不再需要人告诉Agent"用哪个节点"
2. **自动编排工作流** — Agent自主选择合适的节点组合
3. **参数智能填充** — 基于节点schema自动生成配置

## 📋 数据集结构

```yaml
# 每个节点的机器可读描述
node_entry:
  name: "HTTP Request"
  type: "action"
  category: "network"
  
  # 输入
  inputs:
    - type: "trigger"
      schema: 
        method: {type: "enum", values: ["GET", "POST", "PUT", "DELETE"]}
        url: {type: "string", required: true}
        headers: {type: "object", optional: true}
        body: {type: "object", optional: true}
  
  # 输出
  outputs:
    - name: "response"
      schema:
        status_code: {type: "integer"}
        headers: {type: "object"}
        body: {type: "any"}
  
  # 触发条件
  triggers:
    - type: "webhook"
    - type: "schedule"
  
  # 认证方式
  authentication:
    - type: "basic"
    - type: "apiKey"
    - type: "oauth2"
  
  # 兼容节点
  compatible_with:
    - "Webhook"
    - "Function"
    - "Set"
```

## 🔧 使用方式

### 方式1：API直接查询
```bash
# 查询某个节点的详细信息
curl https://your-n8n-dataset.com/nodes/HTTP%20Request

# 查询某类节点的列表
curl https://your-n8n-dataset.com/categories/network
```

### 方式2：加载到Agent上下文
```python
# 在Agent系统提示词中包含数据集摘要
system_prompt = """
你是一个n8n工作流构建专家。以下是可用的节点类型摘要：

核心节点（50+）：
- HTTP请求、Webhook、Schedule（触发器）
- Function、Set、IF、Switch（逻辑处理）
- Twitter、Slack、Email、Notion（平台集成）

数据库节点（30+）：
- MySQL、PostgreSQL、MongoDB、Redis

AI/ML节点（20+）：
- OpenAI、Anthropic、Hugging Face、Qdrant

每个节点的详细schema可以通过工具查询。
"""

# 让Agent查询具体节点
function get_node_details(node_name):
    # 返回节点的输入/输出/认证信息
    return dataset[node_name]
```

### 方式3：Agent自动编排
```yaml
# 用户输入："每隔1小时抓取某个API的数据，存入数据库"
# Agent的自动决策链：

agent_reasoning: |
  1. 需要定时触发 → Schedule节点
  2. 需要调用API → HTTP Request节点
  3. 需要处理响应 → Function节点
  4. 需要存入数据库 → Postgres节点

agent_workflow:
  - Schedule(cron: "0 * * * *")
  - HTTP Request(method="GET", url=user_provided)
  - Function(code: parse_response)
  - Postgres(operation="insert", table="api_data")

# 最终输出：可执行的n8n工作流JSON
```

## 💡 实操建议

### 在Hermes中使用这个模式

```yaml
# 类比：Hermes的技能系统本身就是机器可读的
# 你可以用类似思路把自己的技能/工具做成机器可读格式

skill_machine_readable:
  - name: "skill-name"
    description: "技能功能描述"
    inputs: 
      - {name: "参数1", type: "string", required: true}
      - {name: "参数2", type: "number", optional: true}
    outputs:
      - {name: "结果", type: "object"}
    trigger_conditions:
      - "当用户请求类型A时"
      - "当检测到系统状态B时"
```

### 扩展思路：自己造机器可读工具清单

```yaml
# 把你的所有工具/API做成Agent可读的清单
my_tools_registry:
  - name: "tool_1"
    machine_readable_schema:
      input: "{type: 'object', properties: {...}}"
      output: "{type: 'object', properties: {...}}"
      cost: "$0.001/调用"
      avg_latency: "200ms"
      failure_modes: ["超时", "限流"]
```

## ⚠️ 注意事项

1. **数据集需要保持更新** — n8n节点会随版本更新而增减，数据集需要同步维护
2. **Agent编排的质量取决于数据集质量** — schema描述越精确，Agent编排越准确
3. **安全限制** — Agent编排的工作流需要人工审核后再启用，特别是涉及敏感操作时
4. **不是所有工作流都适合自动化** — 复杂判断逻辑的工作流仍然需要人工设计
5. **递归风险** — Agent可能编排出循环调用的工作流，需要在编排引擎层加保护
6. **免费获取** — 该数据集是作者公开的，可以免费使用
