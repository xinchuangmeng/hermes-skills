---
name: agent-auto-ds4-local-inference-mac
description: 基于antirez的ds4.c项目——专为Apple Silicon(Metal)设计的DeepSeek V4 Flash本地推理引擎。支持100万token上下文、磁盘KV缓存、OpenAI/Anthropic兼容API。可以将DeepSeek V4 Flash作为本地Agent后端，集成OpenCode/Claude Code等Agent工具。
tags:
  - local-inference
  - deepseek-v4
  - metal
  - apple-silicon
  - self-hosted-agent
trigger:
  - 需要在Mac本地运行Agent模型
  - 想用DeepSeek V4 Flash作为便宜的本地Agent后端
  - 需要大上下文(100万token)的本地推理
  - 部署本地API兼容的模型服务
---

# DS4: Mac上运行DeepSeek V4 Flash本地推理引擎

> **来源:** [antirez/ds4](https://github.com/antirez/ds4) — Hacker News 247 points
>
> 一个专为Apple Silicon设计的DeepSeek V4 Flash推理引擎，非通用框架，针对单一模型深度优化。

## 为什么值得关注

DeepSeek V4 Flash的特性:
- **284B参数** Mixture-of-Experts架构(实际激活远少于这个数)
- **1M token上下文窗口**
- **比例化思考** — 思维链长度随问题复杂程度自动缩放
- **高度压缩KV缓存** — 支持磁盘持久化，大上下文在本地可行
- **2bit量化运行** — 128GB MacBook即可跑

## 快速上手

### 1. 下载和构建
```shell
git clone https://github.com/antirez/ds4
cd ds4

# 下载2bit量化模型(适合128GB内存)
./download_model.sh q2

# 或者下载4bit量化(适合256GB+内存)
./download_model.sh q4

# 构建
make
```

### 2. 启动服务器
```shell
./ds4-server --ctx 100000 --kv-disk-dir /tmp/ds4-kv --kv-disk-space-mb 8192
```
默认监听 `http://127.0.0.1:8000`

### 3. 测试调用
```shell
curl http://127.0.0.1:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model":"deepseek-v4-flash",
    "messages":[{"role":"user","content":"Hello"}],
    "stream":true
  }'
```

## 集成到Agent工具

### 集成到Hermes Agent
在config.yaml中配置:
```yaml
auxiliary:
  inference:
    provider: openai-compatible
    base_url: http://127.0.0.1:8000/v1
    api_key: dsv4-local
    model: deepseek-v4-flash
```

### 集成到OpenCode
```json
{
  "provider": {
    "ds4": {
      "name": "ds4.c (local)",
      "npm": "@ai-sdk/openai-compatible",
      "options": {
        "baseURL": "http://127.0.0.1:8000/v1",
        "apiKey": "dsv4-local"
      },
      "models": {
        "deepseek-v4-flash": {
          "name": "DeepSeek V4 Flash",
          "limit": { "context": 100000, "output": 384000 }
        }
      }
    }
  },
  "agent": {
    "ds4": {
      "description": "DeepSeek V4 Flash via local ds4-server",
      "model": "ds4/deepseek-v4-flash",
      "temperature": 0
    }
  }
}
```

## 性能表现

| 机器 | prompt类型 | Prefill速度 | 生成速度 |
|------|-----------|------------|---------|
| MacBook Pro M3 Max (128GB) | 短 | 58.52 t/s | 26.68 t/s |
| MacBook Pro M3 Max (128GB) | 11709 tokens | 250.11 t/s | 21.47 t/s |
| Mac Studio M3 Ultra (512GB) | 短 | 84.43 t/s | 36.86 t/s |
| Mac Studio M3 Ultra (512GB) | 11709 tokens | 468.03 t/s | 27.39 t/s |

## 注意事项
- 仅支持Apple Silicon (Metal)，没有NVIDIA/AMD GPU支持
- 128GB RAM是q2量化的最低要求，更低内存的Mac无法运行
- 磁盘KV缓存是核心特性，利用SSD换内存，--kv-disk-dir要指向高速SSD
- CPU路径存在macOS VM Bug会导致内核崩溃，仅用于正确性验证
- Claude Code支持通过Anthropic兼容API(/v1/messages)集成
