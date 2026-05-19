---
name: agent-auto-ai-co-mathematician-workbench
description: AI协同数学家工作台模式——基于arXiv论文，为研究人员构建的多Agent协作系统，支持探索式研究（创意/文献/计算/证明/理论构建）。核心架构：异步有状态工作区→不确定性管理→失败假设追踪→原生数学制品输出。在FrontierMath Tier 4上达48%新纪录。
tags:
  - multi-agent
  - research
  - mathematics
  - agent-workbench
  - scientific-discovery
  - collaboration-pattern
trigger:
  - 设计AI辅助科研系统
  - 构建研究型Agent工作台
  - 多Agent协作解决复杂问题
  - 需要Agent管理不确定性和失败假设
  - "AI co-mathematician"
  - "research agent workbench"
  - "mathematical discovery agent"
---

# AI协同数学家工作台模式

> **来源:** [AI Co-Mathematician: Accelerating Mathematicians with Agentic AI](https://arxiv.org/abs/2605.06651v1) (2026年5月)
>
> 由Daniel Zheng等18位作者发表，FrontierMath Tier 4 得分48%（所有AI系统新高）

## 核心理念

**不是让AI替数学家做数学，而是让AI成为数学家的协作伙伴。** 系统模拟人类科研协作——异步、有状态、管理不确定性、追踪失败假设。

## 5大核心能力

| 能力 | 说明 | 对应Agent角色 |
|------|------|-------------|
| **构思 (Ideation)** | 生成研究方向、猜想、问题变形 | Creative Agent |
| **文献搜索 (Literature)** | 自动搜索相关论文、发现被忽视的文献 | Research Agent |
| **计算探索 (Computational)** | 数值实验、反例搜索、模式发现 | Computation Agent |
| **定理证明 (Theorem Proving)** | 形式化证明、辅助验证、证明模式匹配 | Prover Agent |
| **理论构建 (Theory Building)** | 整理结果、构建理论框架、发现联系 | Synthesis Agent |

## 工作台核心架构

### 1. 异步有状态工作区 (Asynchronous Stateful Workspace)

与ChatGPT式的"一问一答"不同，AI Co-Mathematician使用持久化工作区：

```
workspace/
  hypotheses/          # 活跃假设列表
  failed_attempts/     # 失败尝试记录（不删除，保留用于避免重复走弯路）
  progress/            # 进展追踪
  artifacts/           # 数学制品（公式、引理、证明）
  literature/          # 文献集合
```

**关键设计：** 失败假设不删除。记录"这个方向试过了，因为XX原因不行"，避免重复劳动。

### 2. 不确定性管理 (Uncertainty Management)

系统明确标示每个输出结果的置信度：

```json
{
  "claim": "This conjecture may hold for n ≤ 7",
  "confidence": 0.6,
  "evidence": ["computational verification up to n=5", "partial proof for n=3"],
  "uncertainties": ["general case unclear"],
  "next_steps": ["try n=6 computationally", "look for counterexample patterns"]
}
```

**AI Co-Mathematician告诉数学家"我不确定的地方在哪"**，而不是假装知道一切。

### 3. 用户意图精炼 (Intent Refinement)

系统不会直接回答模糊问题，而是帮助用户把问题变清晰：

```
用户: "帮我研究这个数列的性质"
系统: "你关心的是：
1. 收敛性？→ 可以试试比率测试
2. 与已知数列的关系？→ 搜索相似模式
3. 封闭形式？→ 尝试生成函数
请选择或描述更多细节"
```

### 4. 原生数学制品输出 (Native Mathematical Artifacts)

输出不是纯文本，而是数学原生格式:

```latex
\begin{theorem}
对于所有 $n \geq 1$，有 $a_n < 2^n$
\end{theorem}
\begin{proof}
通过数学归纳法...
\end{proof}
```

## 在Hermes Agent中实现

### 方案：delegate_task + 多轮迭代

```python
def ai_co_mathematician_workflow(problem_statement):
    """
    模拟AI Co-Mathematician的探索式研究流程
    """
    results = {
        "hypotheses": [],
        "failed_attempts": [],
        "literature": [],
        "computational_evidence": [],
        "proof_attempts": [],
        "synthesis": None
    }
    
    # Phase 1: 文献搜索（Research Agent）
    lit_results = delegate_task(
        goal=f"搜索与'{problem_statement}'相关的数学文献，找出可能被忽视的相关工作",
        context=f"问题描述：{problem_statement}"
    )
    results["literature"] = lit_results
    
    # Phase 2: 生成猜想（Creative Agent）
    hypotheses = delegate_task(
        goal=f"基于文献分析，生成3-5个可验证的猜想",
        context=f"问题：{problem_statement}\n文献：{lit_results}"
    )
    results["hypotheses"] = hypotheses
    
    # Phase 3: 计算验证（Computation Agent）
    for hyp in hypotheses:
        # 小规模计算验证
        evidence = delegate_task(
            goal=f"通过数值计算或小规模枚举验证猜想",
            context=f"猜想：{hyp}"
        )
        if evidence.get("verified_for_small_cases"):
            results["computational_evidence"].append(evidence)
        else:
            results["failed_attempts"].append(hyp)
    
    # Phase 4: 形式化证明尝试（Prover Agent）
    for hyp in results["computational_evidence"]:
        proof = delegate_task(
            goal=f"尝试构建形式化证明",
            context=f"猜想：{hyp}"
        )
        results["proof_attempts"].append(proof)
    
    # Phase 5: 理论综合（Synthesis Agent）
    results["synthesis"] = delegate_task(
        goal="综合所有发现，构建完整的理论框架",
        context=f"全部结果：{results}"
    )
    
    return results
```

### 核心设计原则

1. **失败假设也记录** — 告诉用户"什么方向走不通"和"为什么走不通"同样重要
2. **渐进式探索** — 先小规模验证，再尝试证明，不走回头路
3. **多Agent各司其职** — 每个Agent处理一个数学子任务（文献/猜想/计算/证明）
4. **置信度标注** — 每个输出都要说明"我有多确定"

## 与Hermes已有技能的关联

| Hermes已有技能 | 对应AI Co-Mathematician组件 |
|---------------|--------------------------|
| delegate_task | 多Agent并行探索 |
| agent-auto-producer-consumer-patterns | Research→Creative→Prover的流水线 |
| agent-auto-orchestration-patterns | 探索式编排（非确定性路径） |
| agent-auto-structured-outputs | 结构化数学制品输出 |

## 注意事项

- ⚠️ **这与"AI替你做研究"不同** — 系统设计为人类数学家的工作台，不是自动化研究机器
- ⚠️ **FrontierMath Tier 4的48%分数很高**，但要理解这是所有AI系统的新高，不是解决所有问题
- ⚠️ **长期工作区状态管理是关键** — 没有持久化状态，探索就会前后矛盾
- ⚠️ **数学领域特别需要精确输出** — LaTeX/形式化语言必不可少，纯文本表达数学不够
- ⚠️ **这个模式不限于数学** — 同样的工作台设计可以用于物理、化学、生物学等领域的AI辅助研究
