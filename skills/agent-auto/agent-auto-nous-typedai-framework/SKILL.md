---
name: agent-auto-nous-typedai-framework
title: "Nous/TypedAI开源Agent框架部署与使用指南"
description: "基于Hacker News 155 points的Nous开源项目——TrafficGuard推出的TypedAI是一个TypeScript-first的开源Agent平台，支持自主SWE Agent、多模型（Anthropic/OpenAI/Gemini/DeepSeek etc.）、WebUI、CLI、Slack集成、代码审查Agent、Human-in-the-loop。核心价值：开源可控、可自托管、代码可见。提供快速部署、核心架构、能力边界说明。适用于不想依赖闭源Agent平台的团队和个人开发者。"
tags: [agent-auto, nous, typedai, open-source, agent-framework, self-hosted]
trigger: |
  当需要选择开源Agent框架、评估自托管Agent平台、或对比Nous/TypedAI与其他Agent框架时
---

# Nous/TypedAI开源Agent框架

## 🎯 核心洞察

### 什么是TypedAI（原名Nous）？

TrafficGuard推出的**TypeScript-first开源AI Agent平台**，2026年5月HN当日155 points。

**核心特性：**
- 自主SWE Agent（软件工程Agent）
- 多Agent编排（内置extend-reasoning多Agent实现）
- WebUI + CLI双界面
- 多模型支持：OpenAI、Anthropic（原生&Vertex）、Gemini、Groq、Fireworks、Together.ai、DeepSeek、Ollama、Cerebras、SambaNova、OpenRouter、X.ai
- 内置工具集成：Filesystem、Jira、Slack、Perplexity、Google Cloud、GitLab、GitHub等
- 代码审查Agent（自动PR审查）
- Slack聊天机器人
- Human-in-the-loop配置
- SSO/多用户支持
- 可本地运行或云端部署

### 与Hermes Agent的对比

```yaml
▸ 共同点:
  - 都是Agent框架
  - 都支持多模型
  - 都有CLI/WebUI
  - 都支持工具调用

▸ 差异:
  Hermes: Python栈、轻量级CLI、强于技能(SKILL.md)系统、可嵌入其他项目
  TypedAI: TypeScript栈、功能全面、内置SWE Agent、企业级功能更丰富（SSO/多用户）

▸ 适用场景:
  - 追求轻量级+技能系统 → Hermes
  - 需要开箱即用的全功能Agent平台 → TypedAI
  - 不想依赖闭源平台 → 两者都可
```

## 📋 快速部署指南

```bash
# 1. 克隆仓库
git clone https://github.com/TrafficGuard/typedai.git
cd typedai

# 2. 安装依赖
npm install

# 3. 配置环境
cp .env.example .env
# 在.env中配置至少一个LLM API Key

# 4. 启动
npm run dev    # 开发模式
npm run build  # 生产构建
```

### 配置示例

```yaml
# LLM服务配置（支持多种）
llm_providers:
  - provider: anthropic
    api_key: ${ANTHROPIC_API_KEY}
    model: claude-sonnet-4-20250514
  
  - provider: openai
    api_key: ${OPENAI_API_KEY} 
    model: gpt-4o
  
  - provider: deepseek
    api_key: ${DEEPSEEK_API_KEY}
    model: deepseek-chat

# Agent配置
agent_settings:
  human_in_loop: true      # 人类确认门
  max_turns: 50            # 最大轮次
  temperature: 0.3         # 低温度提高确定性
```

## 🔧 核心功能使用

### 自主SWE Agent
```bash
# CLI模式
npx typedai agent "重构这个函数，使其支持异步"

# WebUI模式
# 访问 http://localhost:3000 → 创建Agent会话
```

### 代码审查Agent
```yaml
# 自动PR审查
pr_review:
  auto_trigger: true
  review_depth: full  # 或: summary/security_only
  comment_style: inline  # 代码行内评论
```

### 多Agent编排
```typescript
// extend-reasoning多Agent实现示例
import { MultiAgent } from 'typedai/multi-agent';

const agents = new MultiAgent({
  agents: [
    { role: "researcher", model: "deepseek-chat" },
    { role: "critic", model: "claude-sonnet-4" },
    { role: "writer", model: "gpt-4o" }
  ],
  orchestration: "debate" // debate/sequential/fan-out
});
```

## ⚠️ 注意事项

1. **TypedAI是TypeScript栈** — 需要Node.js环境，不是Python
2. **功能丰富但学习曲线较陡** — 文档站：https://typedai.dev/
3. **开源可控是最大优势** — 代码完全可见，可审计、可修改
4. **注意与OpenCode（已迁移到Crush）区分** — OpenCode已改名Crush由Charm团队维护
5. **免费额度用完记得关** — 多Agent编排token消耗快
6. **建议先跑WebUI试用** — 比CLI更直观了解全部功能
