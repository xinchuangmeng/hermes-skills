---
name: agent-auto-qwen3-coder-agentic
title: "Qwen3-Coder / Qwen3.6-35B-A3B — 开源智能编码Agent模型"
description: "基于HN今日热榜(Qwen3.6-35B-A3B, 1274 points; Qwen3-Coder, 765 points)。Qwen团队推出的开源Agentic编码模型系列。Qwen3.6-35B-A3B是MoE架构（35B总参/3B激活），号称开源最强的Agent编码能力。Qwen3-Coder是专注编码的专用模型。两者都比GGUF量化的小模型更适合真实代码任务。适用于预算有限但需要高质量编码Agent的场景。"
tags: [agent-auto, qwen, coding-agent, open-source, model, moe]
trigger: |
  当选择开源模型做编码Agent、评估Qwen3-Coder vs 其他模型、或在低预算下部署代码生成Agent时
---
# Qwen3-Coder / Qwen3.6-35B-A3B — 开源智能编码Agent模型

## 🎯 核心洞察

### 来自HN的热榜数据
| 项目 | Points | 核心特点 |
|------|--------|----------|
| Qwen3.6-35B-A3B | 1274 | MoE架构，35B总参/3B激活，Agentic编码，开源 |
| Qwen3-Coder | 765 | 专注编码的专用模型，Qwen系列 |

### 为什么重要
- **MoE架构**：35B总参但只有3B激活，推理速度接近3B模型但能力接近35B
- **Agentic编码**：专门优化了Agent循环（Think → Code → Execute → Debug）的工作流
- **开源可控**：可本地部署，无API依赖

## 🔧 模型对比

| 模型 | 架构 | 参数量 | 激活参数 | 适用场景 | 部署成本 |
|------|------|--------|---------|----------|---------|
| Qwen3.6-35B-A3B | MoE | 35B | 3B | Agentic编码、多步推理 | 中等（1x 24GB显卡） |
| Qwen3-Coder | Dense | 7B/14B | 7B/14B | 专注编码、代码补全 | 低（7B可CPU跑） |
| DeepSeek-V4 Flash | MoE | ~200B | ~20B | 通用Agent后端 | 高 |
| Claude Sonnet 4 | 闭源 | - | - | 编码Agent | API成本 |

## 🚀 部署指南

### vLLM部署（推荐）
```bash
# Qwen3.6-35B-A3B (MoE)
pip install vllm
vllm serve Qwen/Qwen3.6-35B-A3B \
  --tensor-parallel-size 1 \
  --max-model-len 32768 \
  --gpu-memory-utilization 0.9

# Qwen3-Coder-14B
vllm serve Qwen/Qwen3-Coder-14B \
  --tensor-parallel-size 1 \
  --max-model-len 16384
```

### Ollama部署
```bash
# Qwen3-Coder
ollama pull qwen3-coder:14b
ollama run qwen3-coder:14b

# Qwen3.6 (如果Ollama支持)
# ollama pull qwen3.6:35b-a3b
```

### Docker部署
```bash
# 用Docker跑Qwen3-Coder
docker run --gpus all -p 8000:8000 \
  ghcr.io/qwen-ai/qwen3-coder:latest \
  --model Qwen/Qwen3-Coder-14B
```

## 🔌 与Agent框架集成

### 作为OpenCode后端
```bash
opencode config set provider openai  # 因为vLLM兼容OpenAI API
opencode config set api_base http://localhost:8000/v1
opencode config set model Qwen/Qwen3-Coder-14B
opencode "重构这个模块"
```

### 作为Claude Code备用
```bash
# Claude Code不支持直接切换模型，但可以通过代理
# 启动vLLM + 配置代理指向本地
export OPENAI_API_BASE=http://localhost:8000/v1
export OPENAI_API_KEY=not-needed
# 用支持OpenAI兼容的编码Agent工具
opencode "请审查当前代码"
```

### 作为Hermes的子Agent后端
```bash
# 在terminal中调用
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen3-Coder-14B",
    "messages": [
      {"role": "system", "content": "你是编码助手"},
      {"role": "user", "content": "帮我审查这段代码"}
    ]
  }'
```

## ⚡ 性能评估

### Qwen3-Coder vs 其他编码模型
- 在HumanEval上超越同级开源模型
- 代码补全速度快（3B激活的MoE架构优势）
- 支持16K-32K上下文（足够处理大多数代码文件）

### 适合的编码任务
- 代码生成（函数/模块级别）
- 代码审查（单文件级别）
- Bug修复（有明确错误信息）
- 代码重构（单文件/模块）

### 不太适合的任务
- 超长上下文代码库分析（>32K tokens）
- 需要复杂Agent编排的多步任务
- 需要调用外部工具的Agent循环

## ⚠️ 注意事项

1. **不是OpenAI替代品** — 对于复杂任务，GPT-4/Claude Sonnet仍然更好
2. **MoE架构需要显存** — 35B模型即使只有3B激活，也需要~20GB显存加载
3. **Agent能力依赖推理框架** — vLLM的function calling支持程度影响Agent能力
4. **开源模型更新快** — 关注Qwen官方发布的新版本
5. **适合用OpenCode等开源Agent框架配合** — 闭源框架（如Claude Code）不支持切换后端
