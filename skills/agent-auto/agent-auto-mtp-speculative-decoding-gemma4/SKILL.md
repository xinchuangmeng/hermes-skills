---
name: 多Token预测推理加速 — Gemma 4 MTP Draft方案
description: 基于Google Gemma 4博客（2026年5月5日）——使用Multi-Token Prediction (MTP) Draft模型实现最高3x推理加速。介绍投机解码原理以及如何在自部署LLM中应用MTP加速。
tags: [agent, inference-acceleration, speculative-decoding, MTP, gemma, LLM-optimization]
trigger: 当自部署LLM推理速度成为瓶颈、或需要优化Agent响应延迟时
---

# 多Token预测(MTP)推理加速 — 投机解码方案

## 核心原理

传统解码：每次预测1个token → 串行，慢
MTP Draft方案：Draft模型一次预测K个token → 主模型批量验证 → 并行，快

```
传统方式：          Token1 → Token2 → Token3 → Token4 （串行）
MTP投机解码：       [Token1, Token2, Token3, Token4]  （批量验证）
                   Draft: 快速预测
                   主模型: 一次验证K个
```

Gemma 4的MTP Draft方案实现了最高**3倍推理加速**。

## 操作步骤

### 1. 在Hermes Agent中启用MTP（如果使用llama.cpp）

```bash
# 使用llama.cpp的speculative decoding功能
# 需要：主模型 + draft模型（小模型）
./build/bin/llama-speculative \
    --model models/gemma-4-9b.gguf \
    --draft-model models/gemma-4-2b.gguf \
    --draft-min-n-tokens 5 \
    --draft-max-n-tokens 15 \
    --temp 0.0
```

### 2. 在vLLM中启用MTP

```bash
# vLLM从0.6.0+支持speculative decoding
vllm serve google/gemma-4-9b \
    --speculative-model google/gemma-4-2b \
    --num-speculative-tokens 5 \
    --speculative-draft-tensor-parallel-size 1
```

### 3. 选择合适的Draft模型

| 主模型 | 推荐Draft模型 | 预期加速 |
|--------|--------------|---------|
| Gemma 4 9B | Gemma 4 2B | 2-3x |
| Gemma 4 27B | Gemma 4 9B | 2-3x |
| Llama 3 70B | Llama 3 8B | 1.5-2x |
| 任意大模型 | 同系列小模型 | 1.5-3x |

### 4. 在Hermes Config中配置

```yaml
# config.yaml for hermes agent
llm:
  provider: llama-cpp
  model: gemma-4-9b.gguf
  speculative_decoding:
    enabled: true
    draft_model: gemma-4-2b.gguf
    max_draft_tokens: 10
    acceptance_threshold: 0.9
```

## 注意事项
- ⚠️ MTP/Draft方案需要两个模型同时加载——双倍显存
- ⚠️ 不是所有场景都有3x加速——取决于Draft模型的接受率
- ⚠️ 代码生成/结构化输出场景加速效果最好（token可预测性强）
- ⚠️ 创意写作/随机性高的场景加速效果有限
- ⚠️ 需要自部署才有意义——API调用由提供商决定

## 参考
- Google Blog (2026-05-05): "Accelerating Gemma 4: faster inference with multi-token prediction drafters"
- https://blog.google/innovation-and-ai/technology/developers-tools/multi-token-prediction-gemma-4/
- llama.cpp speculative decoding文档
