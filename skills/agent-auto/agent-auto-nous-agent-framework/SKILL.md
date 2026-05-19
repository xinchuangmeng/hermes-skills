---
name: agent-auto-nous-agent-framework
title: "Nous开源Agent框架——自托管SWE Agent与WebUI"
description: "基于HN当天的Nous开源项目（155 points）——TrafficGuard发布的Nous是一套开源的Agent框架，支持自主SWE Agent、WebUI界面、多Agent编排。核心特点是开源可控、可自托管、代码仓库可见。适用于不想依赖闭源Agent平台的团队。包含快速部署指南、核心架构说明和能力边界评估。"
tags: [agent-auto, opensource, framework, swe-agent, self-hosted]
trigger: |
  当评估开源Agent框架、需要自托管Agent平台、或对比Nous与其他Agent框架（如Hermes/OpenCode）时
---

# Nous开源Agent框架实战指南

## 🎯 框架概览

**Nous** 由 TrafficGuard 团队开发，是一个开源的AI Agent框架，主要特性：

- **自主SWE Agent**——能独立完成软件工程任务（读代码、写代码、调试）
- **WebUI界面**——不只有CLI，提供浏览器操作界面
- **多Agent编排**——支持多个Agent协同工作
- **完全开源**——代码可审查、可定制、可私有化部署
- **无供应商绑定**——不依赖单一LLM提供商

| 特性 | Nous | Hermes | OpenCode | Claude Code |
|------|------|--------|----------|-------------|
| 开源 | ✅ | ✅ | ✅ | ❌ |
| WebUI | ✅ | ❌ | ❌ | ❌ |
| SWE Agent | ✅ | ❌ | ✅ | ✅ |
| 多Agent编排 | ✅ | 通过delegate | ❌ | ❌ |
| 自托管 | ✅ | ✅ | ✅ | ❌ |

## 🔧 快速部署指导

### 前提条件
```bash
# 所需环境
- Python 3.10+
- Node.js 18+ (WebUI)
- 至少8GB RAM
- LLM API Key (OpenAI/Anthropic/本地模型)
```

### 安装步骤
```bash
# 1. 克隆仓库
git clone https://github.com/TrafficGuard/nous.git
cd nous

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置
cp config.example.yaml config.yaml
# 编辑config.yaml，配置LLM提供商和API Key

# 4. 启动服务
# CLI模式
python -m nous.cli

# WebUI模式
python -m nous.webui --port 8080

# 后台服务模式
docker-compose up -d
```

### 配置示例
```yaml
# config.yaml
llm:
  provider: openai  # openai | anthropic | ollama
  model: gpt-4o     # 或 claude-opus-4 / 本地模型
  temperature: 0.3
  
agents:
  swe_agent:
    enabled: true
    max_iterations: 25
    workspace: ./workspace/
    
  web_agent:
    enabled: true
    headless: true
    
multi_agent:
  enabled: false
  max_workers: 3
```

## 🤖 与传统Agent框架的异同

### 相似之处
- 都用Agent循环（Think → Act → Observe）
- 支持工具调用（文件读写、代码执行、搜索）
- 可接入多种LLM后端

### 独特之处
1. **内置WebUI**——不必每次都打开终端，适合非技术用户
2. **SWE Agent深度**——专门优化了软件工程任务的Agent循环
3. **TrafficGuard背书**——有实际生产环境的Agent运维经验
4. **多Agent协作**——支持类似Hermes delegate_task的并行工作模式

## 🎯 适合场景 vs 不适合场景

### ✅ 适合
- 团队需要一个开源自托管的Agent平台
- 需要WebUI界面管理Agent任务
- 想做多Agent协作的POC
- 不想被单一LLM供应商绑定

### ❌ 不适合
- 需要深度定制的Agent行为（提示词级控制）
- 需要与已有系统深度集成
- 高频高并发的生产环境（框架较新，稳定性待验证）

## ⚠️ 注意事项

1. **框架较新**——Nous是近期开源的项目，社区和文档还在完善中
2. **SWE Agent的质量受限于底层模型**——用本地小模型效果会明显下降
3. **多Agent编排尚不成熟**——复杂任务可能需要手动调整
4. **WebUI可能暴露在公网**——部署时加认证，防止未授权访问
5. **建议与Hermes互补使用**——Hermes做后端深度Agent，Nous做前端可视化管理
