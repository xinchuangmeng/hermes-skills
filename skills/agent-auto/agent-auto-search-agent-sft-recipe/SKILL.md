---
name: agent-auto-search-agent-sft-recipe
title: "搜索Agent训练：低成本SFT超越RL流水线（OpenSeeker-v2配方）"
description: "基于OpenSeeker-v2的研究发现——仅用10.6k数据点+SFT微调，就能训练出超越资源密集型的CPT+SFT+RL流水线的搜索Agent。核心配方：扩大知识图谱规模、扩展工具集、严格低步数过滤。适用于预算有限的团队训练高性能搜索Agent。"
tags: [agent-auto, search-agent, SFT, training, LLM-agent, open-seeker]
trigger: |
  需要训练/微调搜索Agent时
  预算有限但想要SOTA搜索能力时
  学术团队/个人开发者想训练Agent时
  对比RL和SFT训练策略的性价比时
---

# 搜索Agent训练：低成本SFT超越RL流水线（OpenSeeker-v2配方）

## 🎯 核心发现

**传统行业配方：** 预训练(CPT) → 监督微调(SFT) → 强化学习(RL) = 大量计算资源
**OpenSeeker-v2配方：** 仅SFT + 10.6k高质量数据 = 超越上述流水线

| 指标 | OpenSeeker-v2 (纯SFT) | Tongyi DeepResearch (CPT+SFT+RL) |
|------|----------------------|----------------------------------|
| BrowseComp | **46.0%** | 43.4% |
| BrowseComp-ZH | **58.1%** | 46.7% |
| Humanity's Last Exam | **34.6%** | 32.9% |
| xbench | **78.0%** | 75.0% |
| 数据类型 | 30B + ReAct | (更大的模型+全流水线) |

## 🔧 核心配方三要素

### 1. 扩大知识图谱规模

不要只给Agent开放域网页搜索，提供结构化的知识图谱作为探索地图：

```python
# 数据构建：从知识图谱生成搜索轨迹
knowledge_graph = load_knowledge_graph("wiki_data/")
for query in seed_queries:
    # 让Agent在知识图谱引导下搜索
    trajectory = agent.search_with_knowledge_graph(query, knowledge_graph)
    store_as_training_data(trajectory)
```

### 2. 扩展工具集

Agent可调用的工具越丰富，搜索策略越多样：

```yaml
tool_set:
  - web_search: "通用网页搜索"
  - wikipedia_query: "结构化百科查询" 
  - arxiv_search: "学术论文搜索"
  - code_execution: "Python沙箱执行"
  - knowledge_graph_query: "知识图谱查询"
  - document_parse: "文档解析"
```

### 3. 严格低步数过滤

质量比数量重要——只保留信息密度高、步数少的成功轨迹：

```python
def filter_trajectories(trajectories):
    filtered = []
    for traj in trajectories:
        if not traj.success:
            continue  # 只保留成功轨迹
        if len(traj.steps) > 8:
            continue  # 步数太多的不要（信息密度低）
        if traj.information_density < 0.6:
            continue  # 信息密度过滤
        filtered.append(traj)
    return filtered
```

## 📋 操作步骤

### 步骤1：构建搜索轨迹数据

```bash
# 使用OpenSeeker的开源框架
git clone https://github.com/PolarSeeker/OpenSeeker
cd OpenSeeker

# 1. 准备种子查询
cat > seed_queries.txt << 'EOF'
What are the latest advances in LLM alignment?
How does retrieval-augmented generation work?
Compare transformer and state-space models
EOF

# 2. 用教师模型生成搜索轨迹
python generate_trajectories.py \
  --seeds seed_queries.txt \
  --knowledge_graph kg_data/ \
  --tools web_search,wikipedia,arxiv \
  --max_steps 8 \
  --output trajectories.jsonl
```

### 步骤2：过滤高质量轨迹

```python
import json

with open("trajectories.jsonl") as f:
    trajectories = [json.loads(line) for line in f]

filtered = [
    t for t in trajectories
    if t["success"] and len(t["steps"]) <= 8
]

print(f"原始: {len(trajectories)}, 过滤后: {len(filtered)}")
# 存为训练数据
with open("train_data.jsonl", "w") as f:
    for t in filtered:
        f.write(json.dumps(t) + "\n")
```

### 步骤3：SFT微调

```bash
# 用标准SFT框架微调
python train.py \
  --model Qwen2.5-32B-Instruct \
  --data train_data.jsonl \
  --epochs 3 \
  --lr 2e-5 \
  --output ./search-agent-v1
```

### 步骤4：评估

```bash
# 在标准benchmark上评估
python eval.py \
  --model ./search-agent-v1 \
  --benchmark BrowseComp,HumanitysLastExam \
  --agent_paradigm react
```

## 💡 最佳实践

1. **10k条高质量 > 100k条低质量** — 数据质量是唯一瓶颈
2. **知识的广度 > 搜索步数** — 8步内解决是最佳，超过15步的轨迹噪声太大
3. **ReAct范式仍是搜索Agent的最佳选择** — 不需要复杂的plan-then-execute
4. **工具集要从简到繁** — 先3个核心工具（搜索/百科/代码），再逐步扩展

## ⚠️ 注意事项

- 30B模型是当前搜索Agent的最佳性价比选择（7B不够，70B太贵）
- SFT只能学到模式，不会像RL那样学到探索策略——如果Agent需要大量试错，RL可能还是必须的
- 中文搜索数据需要额外处理——OpenSeeker-v2的ZH benchmark比英文低12%
- 知识图谱的质量直接影响搜索轨迹质量，建议用Wikidata或自己维护的领域图谱
