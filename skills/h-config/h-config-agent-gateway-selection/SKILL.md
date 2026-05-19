---
name: Agent网关平台选型指南
description: >
  2026年6大Agent网关平台横向对比——TrueFoundry（企业级）、AgentGateway.dev（开源标准）、
  Kagent（K8s原生）、Pragatix（合规）、Obot AI（MCP优先）、Operant AI（安全研究）。
  含选型决策树、各平台适用场景和成熟度评估。适用于多Agent架构的网关/编排层选型。
tags: [agent-gateway, mcp, a2a, platform-selection, infrastructure]
trigger: 需要选择Agent网关平台时、设计多Agent架构时、评估MCP治理方案时
---

# Agent网关平台选型指南

> 来源：dev.to - "6 Agent Gateway Platforms That Actually Exist in 2026" (May 2026)

## 什么是Agent Gateway

**Agent Gateway = Agent和基础设施之间的承重墙。**

就像API网关（Kong/Istio）之于微服务——Agent Gateway解决：
- LLM路由（请求该去哪个模型）
- MCP工具治理（谁可以用什么工具）
- Agent注册（谁部署了什么Agent）
- A2A流量管理（Agent之间的通信）
- 审计日志（谁做了什么）

## 六平台横向对比

| 平台 | LLM路由 | MCP治理 | Agent注册 | A2A支持 | 自托管 | 合规认证 | 成熟度 |
|------|---------|---------|-----------|---------|--------|---------|--------|
| **TrueFoundry** | ✅ | ✅ | ✅ | 规划中 | VPC/本地 | SOC2,HIPAA,ITAR | 生产级(10B req/mo) |
| **AgentGateway.dev** | ✅ | ✅ | 通过A2A卡片 | ✅ | ✅ | 无 | 预生产 |
| **Kagent** | 通过Envoy | ✅ | 规划中 | 规划中 | 仅K8s | 无 | 早期 |
| **Pragatix** | ❌ | ❌ | ✅ | ❌ | 本地部署 | 待定 | 早期 |
| **Obot AI** | ❌ | ✅ | 部分 | ❌ | ✅ | 无 | 早期-中期 |
| **Operant AI** | ❌ | 仅安全 | ❌ | ❌ | ❌ | 无 | 研究型 |

## 选型决策树

```
你有多少Agent？
├── 1-3个Agent
│   └── 不需要Gateway，直接用Hermes Profile管理
├── 3-10个Agent
│   ├── 在用K8s？ → Kagent（如果你深度依赖K8s+Envoy）
│   ├── MCP服务器太多？ → Obot AI
│   └── 其他 → AgentGateway.dev（开源、快速上手）
├── 10-50个Agent
│   ├── 合规要求高（金融/医疗）？ → Pragatix
│   └── 需要一站式管理？ → TrueFoundry
└── 50+个Agent
    └── TrueFoundry（唯一经大规模验证的选项）
```

## 各平台详解

### 1. TrueFoundry — 企业级一站式平台
- **Gartner认可** | 处理NVIDIA、Siemens Healthineers的10B+请求/月
- **延迟开销**：约3-4ms
- **优势**：SOC2/HIPAA/ITAR合规全内置，VPC或本地部署
- **劣势**：对小项目过于重，集成了大量自有组件
- **适用**：需要统一控制平面管理模型+工具+Agent的团队

### 2. AgentGateway.dev — 开源标准
- **背景**：Linux Foundation's Agentic AI Foundation支持
- **语言**：Rust
- **2026年4月发布**，非常新（几周前）
- **无RBAC，无合规认证，无生产案例研究**
- **适用**：想参与开放标准建设的团队；有能力在上层搭建治理机制

### 3. Kagent — K8s原生
- **构建于** KGateway（基于Envoy）
- 将Service Mesh模式扩展到Agent流量
- **非常早期**，与K8s生态深度耦合
- **适用**：已经深度使用K8s+Envoy的团队

### 4. Pragatix — 合规聚焦
- 单一目标：Agent治理和执行层控制
- 本地部署，面向受监管行业
- **功能窄**：无LLM路由，无MCP网关，无可观测性仪表板
- **适用**：昨天就需要治理的安全/合规团队

### 5. Obot AI — MCP优先
- 起步于开源MCP网关，现在增加Agent编排
- **出色的MCP服务器生命周期管理**（部署/编目/访问控制）
- 向Linux Foundation捐赠了MCP Dev Summit
- **无LLM路由，无A2A**
- **适用**：有"40台MCP服务器不知道谁部署了哪台"的团队

### 6. Operant AI — 安全研究
- **不是网关** — 是AI Agent威胁情报
- 发布了《2026 MCP安全指南》；发现"Shadow Escape"零点击攻击向量
- **只能监控/研究** — 必须配合实际网关使用
- **适用**：想在部署治理之前了解Agent攻击向量的安全团队

## 关键洞察

> "Agent Gateway领域现在正处于2015年API网关的时期。早期。碎片化。少数可信选项，一堆半成品方案，以及一个清晰的感觉：这类东西将成为未来十年的承重基础设施。"

**预测**：这个列表将在6个月内翻倍，至少有一个平台会被大型厂商收购。

## Hermes Agent如何集成

Hermes目前支持：
1. **原生MCP客户端**（native-mcp技能）——连接MCP服务器，自动发现工具
2. **mcporter** CLI——管理MCP服务器和工具调用
3. **多Profile**——管理多个Agent实例

如果需要更高级的网关能力（多Agent协作、A2A流量管理），可以考虑：
- **小规模**：Hermes多Profile + native-mcp足以
- **中规模**：引入AgentGateway.dev作为A2A通信层
- **大规模**：TrueFoundry做统一控制平面

## 注意事项
⚠️ AgentGateway.dev才几周大——不要在生产环境冒险使用
⚠️ 大多数平台不支持A2A——Agent间通信仍然需要自定义方案
⚠️ 合规认证很重要——如果处理敏感数据，选有SOC2/HIPAA的平台
⚠️ 这个赛道变化很快——6个月后选型结论可能完全不同
⚠️ 对于个人/小团队，直接用Hermes内置功能比引入网关更简单
