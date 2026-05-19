---
name: agent-auto-docker-model-runner
title: "Docker Model Runner——替代本地AI全套配置的一键方案"
description: "基于Dev.to文章'Docker Model Runner Replaced My Entire Local AI Setup'。Docker Model Runner是一个Docker官方推出的工具，可以一键运行本地AI模型（LLM/Embedding/图像生成等），替代Ollama/LM Studio/llama.cpp等独立工具的复杂配置。适用于想快速体验本地AI、或简化AI开发环境的开发者。"
tags: [agent-auto, docker, local-ai, model-runner, devtools]
trigger: |
  当需要部署本地AI模型、对比Ollama/Docker Model Runner/llama.cpp、或想用Docker简化AI环境配置时
---
# Docker Model Runner——替代本地AI全套配置的一键方案

## 🎯 核心洞察

### 来源
> "Docker Model Runner Replaced My Entire Local AI Setup"
> — Dev.to @pavan_madduri

**核心观点**：如果你还在用Ollama + llama.cpp + Diffusers等一堆工具跑本地AI，Docker Model Runner用一个命令搞定全部。

### 为什么重要
| 对比项 | 传统方案（Ollama+llama.cpp+...） | Docker Model Runner |
|--------|--------------------------------|-------------------|
| 安装步骤 | 多个工具分别安装配置 | 一个Docker扩展 |
| 模型管理 | 每个工具有自己的下载方式 | 统一模型仓库 |
| API兼容 | 各不相同 | OpenAI兼容API |
| 多模态 | 需要额外配置 | 内置支持 |
| 环境隔离 | 可能污染系统 | Docker容器天然隔离 |

## 🚀 快速开始

### 安装
```bash
# 前提：Docker Desktop已安装

# 1. 安装Docker Model Runner扩展
docker extension install docker/model-runner

# 2. 启动
docker model-runner start

# 3. 下载模型
docker model-runner pull qwen3-coder:7b
docker model-runner pull nomic-embed-text:v1.5  # 向量模型

# 4. 运行模型
docker model-runner run qwen3-coder:7b
```

### 配置示例
```yaml
# docker-model-runner.yaml
models:
  - name: qwen3-coder:7b
    type: llm
    port: 11434  # 兼容Ollama端口
    
  - name: nomic-embed-text:v1.5
    type: embedding
    port: 11435
    
  - name: SDXL
    type: image-generation
    port: 11436
```

## 🔌 与Agent框架集成

### 作为OpenCode的本地后端
```bash
# Docker Model Runner启动后提供OpenAI兼容API
opencode config set provider openai
opencode config set api_base http://localhost:11434/v1
opencode config set model qwen3-coder:7b
```

### 在Hermes中使用
```bash
# 通过OpenAI兼容API调用
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-coder:7b",
    "messages": [{"role": "user", "content": "解释这段代码"}]
  }'
```

### 多模型编排
```yaml
# 用Docker Model Runner同时运行多个模型
services:
  llm:           # 对话模型
    image: qwen3-coder:7b
    port: 11434
  
  embedding:     # 向量模型
    image: nomic-embed-text:v1.5
    port: 11435
  
  vision:        # 视觉模型
    image: llava:7b
    port: 11436
```

## ⚠️ 注意事项

1. **资源消耗** — 同时运行多个模型需要大内存/显存
2. **Docker Desktop依赖** — 不能在纯服务器环境用（需要Docker Desktop）
3. **模型库有限** — 没有Ollama的模型库丰富
4. **GPU加速** — 需要配置Docker的GPU支持（nvidia-container-toolkit）
5. **适合开发环境** — 不太适合生产环境的模型部署
6. **与Ollama互补** — Ollama模型库更丰富，Docker Model Runner更方便
