---
name: agent-auto-evolutionary-coding-agent-pattern
description: 基于Google DeepMind AlphaEvolve架构——用LLM进化式生成算法代码的模式。核心架构包括Prompt Sampler、LLM代码生成、自动验证器、进化数据库和反馈循环。
tags:
  - evolutionary-algorithm
  - coding-agent
  - code-generation
  - llm-evaluation
  - iterative-optimization
trigger:
  - 需要自动化生成和优化算法代码
  - Agent生成代码后需要自动验证质量
  - 需要多轮迭代改进代码而非一次生成
  - 构建基础设施优化脚本如性能调优
---

# 进化式编码Agent模式 (Evolutionary Coding Agent Pattern)

> **来源:** AlphaEvolve by Google DeepMind — Gemini-powered coding agent for designing advanced algorithms
>
> AlphaEvolve是Google DeepMind开发的进化式编码Agent，用Gemini模型自动发现和优化算法，已在Google数据中心、芯片设计和AI训练中生产部署。

## 核心架构

```
Prompt Sampler --> LLM (代码生成) --> Evaluator (自动验证)
      ^                                    |
      |                                    v
      +---------- Programs DB <------------+
                     (进化算法)
```

### 5个组件

| 组件 | 角色 | 在Hermes中的对应物 |
|------|------|-------------------|
| Prompt Sampler | 组装提示词，从成功案例中提取模式 | 系统提示词 + 历史记录 |
| LLM | 生成新程序/代码 | 主模型的代码生成功能 |
| Evaluator | 自动运行并评分 | 脚本验证或测试运行 |
| Programs DB | 存储结果，实现进化算法 | 文件系统 + 评分日志 |
| Feedback Loop | 最优程序反馈到提示词 | 下一轮提示词注入 |

## 关键设计决策

### 1. 多模型搭配
- 廉价模型(Gemini Flash)做广度探索 | 快速生成大量方案
- 高端模型(Gemini Pro)做深度优化 | 精调最佳方案
- 实操: 用DeepSeek/GPT-4o-mini做广域生成，Claude/GPT-4做深度优化

### 2. 自动验证是关键
AlphaEvolve的秘诀不是LLM生成代码的能力，而是自动验证器:
- 每次代码生成后自动运行测试
- 用客观指标评分(速度/准确率/资源消耗)
- 只有通过验证的代码才进入下一轮

### 3. 进化算法不是一次生成
- 需要约15次变异(mutations)才能完成复杂修改
- 每轮保留最佳方案，基于此生成变体
- 实践成果: 75%场景复现最先进方案，20%场景超越

## 实操: 在Hermes中实现简化版

### 模式: 多轮代码迭代改进
```python
from hermes_tools import terminal

def evolve_code(initial_code, evaluator_script, iterations=5):
    current_code = initial_code
    best_score = float('inf')
    
    for i in range(iterations):
        # 1. 让LLM生成改进版本(通过提示词实现)
        # 2. 保存并运行验证器
        with open("candidate.py", "w") as f:
            f.write(current_code)
        result = terminal(f"python {evaluator_script}")
        
        # 3. 如果更好则保留
        score = parse_score(result.output)
        if score < best_score:
            best_score = score
            # 保留，下轮继续改进
```

### 结合delegate_task做并行探索
```
主Agent: 拆分任务 -> 分配子任务
SubAgent 1: 探索方案A (廉价模型)
SubAgent 2: 探索方案B (廉价模型)
SubAgent 3: 探索方案C (廉价模型)
主Agent: 收集结果 -> 用高端模型精调Top-1
```

## 注意事项

- 验证器必须可靠，它自己出Bug会导致错误的进化方向，先确保验证器经过测试
- 15次迭代成本累积，先用廉价模型跑广域搜索再用高端模型精调
- 进化模式适合: 性能优化、算法发现、配置调优。不适合: 创意写作、一次性代码
- 生产部署需要人工审核，不要直接信任自动进化出的代码
