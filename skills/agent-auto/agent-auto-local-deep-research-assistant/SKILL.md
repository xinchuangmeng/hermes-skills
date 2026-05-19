---
name: agent-auto-local-deep-research-assistant
title: "本地部署AI深度研究助手（Local Deep Research）"
description: "用Docker一键部署自托管AI研究助手——给Agent一个问题，自动搜索多源（网页/arXiv/PubMed/Wikipedia/GitHub/本地文档）、迭代分析、生成带引用的结构化报告。完全本地运行，数据隐私有保障。支持Ollama本地模型或OpenAI/Anthropic云模型。"
tags: [agent-auto, research, local, self-hosted, docker, RAG, privacy]
trigger: |
  需要自动化研究/调研时
  需要带引用的深度研究报告时
  关注数据隐私，不想把数据发给云服务时
  搭建Agent的研究能力时
---

# 本地部署AI深度研究助手（Local Deep Research）

## 概述

Local Deep Research (LDR) 让你可以搭建自己的AI研究助手，功能类似OpenAI Deep Research但完全本地运行。

```
输入: "比较FAISS和Hnswlib在大规模向量搜索中的性能"
       |
       v
   [Local Deep Research]
       | 搜索: 网页 + arXiv + 代码库
       | 迭代: 分析 -> 搜索 -> 综合
       | 引用: 所有来源自动标注
       |
       v
输出: 结构化报告（含引用的PDF/HTML/Markdown）
```

## 快速部署

### Docker一键部署（推荐）

```bash
# 标准版（CPU）
curl -O https://raw.githubusercontent.com/LearningCircuit/local-deep-research/main/docker-compose.yml
docker compose up -d
# 等待30秒后访问 http://localhost:5000

# GPU加速版（Linux + NVIDIA GPU）
curl -O https://raw.githubusercontent.com/LearningCircuit/local-deep-research/main/docker-compose.yml
curl -O https://raw.githubusercontent.com/LearningCircuit/local-deep-research/main/docker-compose.gpu.override.yml
# 先装NVIDIA Container Toolkit
sudo apt-get update && sudo apt-get install nvidia-container-toolkit -y
sudo systemctl restart docker
docker compose -f docker-compose.yml -f docker-compose.gpu.override.yml up -d
```

### pip安装（开发用）

```bash
pip install local-deep-research

# 需要额外启动:
# 1. SearXNG元搜索引擎
docker run -d -p 8080:8080 --name searxng searxng/searxng
# 2. Ollama本地模型
ollama pull gemma3:12b

# 启动Web UI
export LDR_ALLOW_UNENCRYPTED=true
python -m local_deep_research.web.app
```

## 配置模型

### 本地模型（Ollama）

```yaml
# config.yaml
llm:
  provider: ollama
  model: gemma3:12b  # 或 llama3:70b / deepseek-r1:32b
  base_url: http://localhost:11434
```

### 云模型

```yaml
# config.yaml
llm:
  provider: openai
  model: gpt-4o
  api_key: ${OPENAI_API_KEY}
```

## 用Python API做自动化

```python
from local_deep_research.api import LDRClient, quick_query

# 一键研究
summary = quick_query("admin", "password", 
    "What is the current state of Rust async runtimes?")
print(summary)

# 或更精细的控制
client = LDRClient()
client.login("admin", "password")
result = client.quick_research(
    "Compare FAISS vs Hnswlib for vector search at scale"
)
print(result["summary"])
print(result["sources"])  # 所有引用来源
```

## 在Hermes工作流中集成

```python
def research_with_ldr(query: str) -> str:
    """用LDR做深度研究，返回结构化报告"""
    result = quick_query("admin", "password", query)
    
    # 提取关键信息
    report = {
        "summary": result["summary"],
        "sources": result["sources"], 
        "key_findings": extract_findings(result["summary"])
    }
    return report

# 在delegate_task中使用
delegate_task(
    goal="研究对比方案",
    context=research_with_ldr("对比方案X和Y")
)
```

## 知识库管理

LDR的每个研究会下载来源到本地库 -> 索引 -> 后续查询可同时搜索历史数据:

```bash
# 知识库位置: ~/.local_deep_research/library/
ls ~/.local_deep_research/library/

# 手动导入已有文档
cp my_documents/*.pdf ~/.local_deep_research/library/
```

## 注意事项

- Docker版最简单 - 1条命令启动，包含Ollama + SearXNG + LDR
- 纯本地运行不泄露数据 - 但也可以配置云模型混合使用
- 首次启动需要下载模型（根据模型大小，3-30GB不等）
- 如果使用Ollama本地模型，CPU推理较慢（12B模型建议16GB+内存）
- pip版需要手动处理SQLCipher加密 - 开发环境设LDR_ALLOW_UNENCRYPTED=true即可
