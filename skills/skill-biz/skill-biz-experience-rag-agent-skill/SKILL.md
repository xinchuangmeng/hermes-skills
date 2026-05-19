---
name: skill-biz-experience-rag-agent-skill
title: "Experience-RAG: 将检索策略封装为可插拔Agent技能"
description: "基于arXiv论文: 不要让Agent从零决定怎么检索，将检索策略经验固化为可插拔技能层。技能层做4件事: 场景分析 -> 经验查询 -> 策略路由 -> 结果封装。适用于Hermes技能设计、RAG架构优化、多策略检索。"
tags: [skill-biz, RAG, retrieval, experience, agent-skill, pluggable]
trigger: |
  设计Agent技能时需要考虑检索策略选择
  多个RAG任务需要不同的检索方式
  想把检索经验固化而非每次让Agent从头决策
  优化Agent的检索效率和质量
---

# Experience-RAG: 将检索策略封装为可插拔Agent技能

## 核心理念

传统RAG: 一条固定的检索流水线处理所有任务 -> 事实问答/多跳推理/科学验证需要不同检索策略

**Experience-RAG方案**: 在Agent和检索器池之间加一个技能层

```
Agent
  | 调用 retrieve(query) <- Agent不用关心内部细节
  v
[Experience-RAG Skill] <- 可插拔技能层
  |
  +-- 1. Scene Analysis    <- 分析当前场景
  +-- 2. Experience Lookup <- 查询经验记忆
  +-- 3. Strategy Routing  <- 路由到最合适的检索器
  +-- 4. Result Packaging  <- 格式化返回
  |
  v
[Retriever Pool]  <- 多个专业检索器
  +- dense_retriever (稠密检索)
  +- sparse_retriever (稀疏检索)
  +- hybrid_retriever (混合检索)
  +- code_search (代码检索)
```

**性能**: nDCG@10 = 0.8924，在BeIR三个数据集上超越固定单检索器

## 应用到Hermes技能设计

Experience-RAG的核心启示: 检索策略选择可以封装为可复用技能，而不是硬编码在工作流中。

```yaml
# 不好的做法: 硬编码检索策略
agent_workflow:
  steps:
    - web_search(query)
    - always use google_search  # 所有任务都用相同检索

# 好的做法: 封装为Experience-RAG技能
skill_retrieve:
  name: experience-retrieval
  scene_analysis: true    # 自动分析查询类型
  strategy_routing: true  # 自动选择最优检索策略
  experience_memory: ~/.hermes/skills/retrieval_experience/
```

## 操作步骤

### 步骤1: 分析技能需要哪些检索场景

```yaml
# 在SKILL.md frontmatter中声明检索场景
retrieval_scenes:
  - type: factoid
    description: "事实问答(谁/什么/什么时候)"
    preferred_retriever: dense
    top_k: 5
  - type: multi_hop
    description: "多跳推理(A导致B，B导致C)"
    preferred_retriever: hybrid
    top_k: 10
  - type: verification
    description: "事实验证(检查声明是否正确)"
    preferred_retriever: sparse
    top_k: 3
```

### 步骤2: 建立经验记忆

```bash
# 创建经验记忆目录
mkdir -p ~/.hermes/skills/my-skill/references/experience/

# 每条经验: 场景+最佳策略
cat > ~/.hermes/skills/my-skill/references/experience/factoid.yaml << 'EOF'
scene: factoid
best_strategy: dense_retrieval
top_k: 5
notes: 事实问答用稠密检索效果最好
EOF
```

### 步骤3: 在Hermes技能中实现场景路由

```python
def select_retrieval_strategy(query: str, context: dict) -> dict:
    """场景分析 + 经验查询 + 策略路由"""
    
    # 1. 场景分析
    if any(w in query for w in ["为什么", "原因", "how", "why"]):
        scene = "multi_hop"
    elif any(w in query for w in ["谁", "什么", "what", "who"]):
        scene = "factoid"
    elif any(w in query for w in ["验证", "是否正确", "verify"]):
        scene = "verification"
    else:
        scene = "general"
    
    # 2. 查经验记忆
    experience = load_experience(scene)
    
    # 3. 返回检索参数
    return {
        "retriever": experience["best_strategy"],
        "top_k": experience["top_k"],
        "scene": scene
    }
```

## 最佳实践

1. **Agent不应该知道检索细节** - 让技能层处理，Agent只调retrieve(query)
2. **经验记忆要持续更新** - 每次检索失败/成功都记录，更新策略权重
3. **场景分类别太细** - 3-5个场景足够，太多增加路由开销
4. **结果封装标准化** - 所有场景返回相同格式的结构化证据

## 注意事项

- 场景分析本身有开销 - 简单任务不需要走完整4层
- 经验记忆要定期维护 - 过时的经验比没有经验更糟糕
- 这个模式最适合多任务Agent - 单一任务不需要这么复杂
