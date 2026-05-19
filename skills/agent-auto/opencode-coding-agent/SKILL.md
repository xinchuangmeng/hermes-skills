---
name: opencode-coding-agent
title: "OpenCode 开源AI编码Agent使用指南"
description: "OpenCode是开源AI编码Agent，支持多语言、多LLM后端、Git集成。作为Claude Code/Codex的开源替代，可直接通过CLI调用。核心架构：Agent循环引擎 + 文件编辑 + 终端执行 + Git工作流."
tags: [agent-auto, opencode, coding-agent, open-source, cli]
trigger: |
  当需要部署开源AI编码Agent、替代Claude Code/Codex、或用OpenCode执行代码生成/重构/审查任务时
---

# OpenCode 开源AI编码Agent使用指南

## 📋 概述

OpenCode（https://opencode.ai/）是一个开源的AI编码Agent，可作为Claude Code、OpenAI Codex等商业编码Agent的开源替代方案。支持多种LLM后端（OpenAI/Anthropic/Ollama等），提供类似Codex/Claude Code的终端体验。

### 最新动态（2026-05-15更新）
- Hacker News 1274 points 热榜，社区关注度极高
- 作为Claude Code的开源替代，呼声越来越高（尤其是在Claude Code被发现存在隐私/成本问题后）
- 支持Qwen3-Coder作为后端（低成本+开源+Agent编码优化）

## 🚀 安装

### 方式1：pip安装（推荐）
```bash
pip install opencode-ai
```

### 方式2：从源码安装
```bash
git clone https://github.com/OpenCodeAI/opencode.git
cd opencode
pip install -e .
```

### 方式3：npm安装
```bash
npm install -g @opencode/cli
```

## ⚙️ 配置

### 设置LLM后端
```bash
# OpenAI
opencode config set provider openai
opencode config set api_key $OPENAI_API_KEY
export OPENAI_API_KEY=sk-...

# Anthropic Claude
opencode config set provider anthropic
opencode config set model claude-sonnet-4-20250514
export ANTHROPIC_API_KEY=sk-ant-...

# Ollama本地部署
opencode config set provider ollama
opencode config set model qwen3.6-35b-a3b
```

### 配置文件位置
```
~/.config/opencode/config.yaml
```

```yaml
provider: anthropic
model: claude-sonnet-4-20250514
max_tokens: 4096
temperature: 0.0
# 以下可选
system_prompt: "You are an expert software engineer..."
workspace: /path/to/project
```

## 🎯 核心用法

### 基础命令
```bash
# 进入交互模式（类似Claude Code）
opencode

# 单次任务
opencode "给你的任务描述"

# 指定工作目录
opencode --workspace /path/to/project "重构这个模块"

# 使用特定模型
opencode --model deepseek-chat "请解释这段代码"

# 调试模式
opencode --verbose "找到这个bug"
```

### 常用场景
```bash
# 代码审查
opencode "审查当前分支的diff，找出潜在bug"

# 重构
opencode "将utils.py中的函数按职责拆分到独立文件中"

# 测试编写
opencode "为src/目录下所有Python文件编写单元测试"

# 文档生成
opencode "为这个API生成OpenAPI 3.0文档"
```

## 🔗 与Hermes集成

### 作为delegate_task的子Agent
```
OpenCode适合作为子Agent处理编码密集型任务：
- 代码审查 → delegate_task给OpenCode
- 大规模重构 → OpenCode异步执行
- 测试生成 → OpenCode自动覆盖
```

### 在Hermes工作流中使用
```bash
# 在terminal中调用
opencode "完成xxx功能" --timeout 300
```

## ⚡ 性能对比

| Agent | 开源 | 多LLM支持 | Git集成 | 终端执行 | 文件编辑 |
|-------|------|-----------|---------|---------|---------|
| OpenCode | ✅ | ✅ (多后端) | ✅ | ✅ | ✅ |
| Claude Code | ❌ | ❌ (仅Claude) | ✅ | ✅ | ✅ |
| Codex CLI | ✅ | ❌ (仅OpenAI) | ✅ | ✅ | ✅ |

## ⚠️ 注意事项

1. **Token消耗**：OpenCode默认使用较长的上下文窗口，注意监控API费用
2. **模型兼容性**：不同LLM后端对工具调用的支持程度不同，推荐使用Claude Sonnet/Qwen3-Coder
3. **安全性**：OpenCode可以执行终端命令，在敏感环境中需控制其权限
4. **版本更新**：开源项目迭代快，定期`pip install -U opencode-ai`更新
5. **工作目录**：指定--workspace避免误操作其他项目文件
