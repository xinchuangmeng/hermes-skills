---
name: agent-auto-producer-consumer-patterns
description: >
  多Agent编排的5种角色模式语言（Pattern Language）——Producer（生产者）、Consumer（消费者）、
  Coordinator（协调者）、Critic（批评者）、Judge（裁判）及其组合规则。
  帮助你构建可预测、可调试的多Agent系统，避免死锁、竞态、共识幻觉等常见陷阱。
tags:
  - multi-agent
  - orchestration
  - pattern-language
  - producer-consumer
  - agent-roles
  - coordinator
  - critic
  - judge
trigger:
  - "多Agent角色设计"
  - "producer consumer agent"
  - "agent pattern language"
  - "Agent编排角色"
  - "coordinator critic judge agent"
  - "多Agent死锁"
  - "agent团队角色"
---

# 多Agent编排角色模式语言（Pattern Language）

## 为什么需要模式语言

当工程师说"这里需要加个批评者循环"、另一个答"限制3轮迭代，最后加个裁判"——对话直接跳过了10分钟解释，落在正确的设计上。

这就是模式语言的价值：**共享词汇**让多Agent系统设计从"怎么搭"变成了"怎么搭对"。

## 5种Agent角色

### 1. Producer（生产者）

**职责**：接收模糊输入（目标、问题、用户意图），产出明确的工作项。

**质量检验标准**：下游Consumer能否仅凭工作项执行，不需要参考原始输入？

**适用场景**：
- 意图解析：把"在预算内优化供应链"变成具体任务清单
- 问题分解：把复杂问题拆成可执行的子问题
- 任务规划：生成结构化的工作流

**常见问题**：
- 产出太模糊 → Consumer只能猜
- 产出太细 → 不必要的开销
- 遗漏关键维度 → 下游会产生错误结果

### 2. Consumer（消费者）

**职责**：接收已加工好的工作项，用专业技能执行。

**Consumer质量检测**：接到工作项时，是否能立刻开始工作？
- 能 → 设计正确
- 需要回看原始输入 → Producer不够好

**特点**：
- 通常是专业的、细粒度高的Agent
- 可以并行运行（Fan-Out模式）
- 输出要标准化，方便下游合并

### 3. Coordinator（协调者）

**职责**：管理Producer和Consumer之间的任务分配和进度追踪。

**核心职能**：
```
输入 → Producer → [Coordinator] → Consumer A
                                   → Consumer B
                                   → Consumer C → 汇总 → 输出
```

**质量检验标准**：能否在Consumer失败时优雅降级？

**适用场景**：
- 多个Consumer需要按依赖顺序执行
- 部分执行结果需要提前释放（部分流）
- 错误需要重试或降级

### 4. Critic（批评者）

**职责**：被动审查其他人的产出，提改进意见但不能修改。

**关键规则**：
- ❌ 不能自己改东西（越界了就是审判者角色）
- ✅ 只能说"这里有问题，因为……" 
- 需要绑定迭代次数，防止死循环

**配置示例**：
```yaml
critic:
  max_iterations: 3  # 最多批评3轮
  focus_areas:       # 批评什么维度
    - 逻辑一致性
    - 数据准确性
    - 格式规范性
  escalation:        # 超过次数怎么办
    action: escalate_to_judge
```

### 5. Judge（裁判）

**职责**：在多个产出之间做最终裁决。

**裁决场景**：
- **Producer vs Critic**：Producer不认同Critic的批评，需要上级判决
- **Consumer A vs Consumer B**：两个方案都有道理，需要选最优
- **Critic vs Critic**：多个批评者意见不同

**质量检验标准**：能否给出选择的确切理由？

## 组合规则（Composition Rules）

### 规则1：Producer → Consumer
- 先分解再执行
- Producer产出物必须让Consumer无歧义理解

### 规则2：Producer → [Critic → Consumer]*
- 生产-批评-修改 循环
- **需要设置迭代次数上限**（推荐3次）
- 超过上限 → 自动调用Judge

### 规则3：Consumer → Coordinator → Consumer
- 前一个Consumer的输出通过Coordinator路由到下一个
- Coordinator做格式转换、上下文整理

### 规则4：Fan-Out → Fan-In
```
         → Consumer A
Producer → Consumer B → Coordinator/Judge
         → Consumer C
```
- 多个Consumer并行工作
- Coordinator或Judge负责汇总

## 部署模式选择指南

| 任务类型 | 推荐角色组合 | 原因 |
|---------|------------|------|
| 文档处理 | Producer → Sequential Consumers | 流水线作业，依赖明确 |
| 代码审查 | Producer → Fan-Out Critics → Judge | 多维度并行审查+裁决 |
| 内容生成 | Producer → Critic → Producer循环 | 迭代优化 |
| 多方案选优 | Producer → Fan-Out Consumers → Judge | 出多个方案，选最优 |
| 异常处理 | Producer → Coordinator → Dynamic Handoff | 动态转交给最合适的Consumer |

## ⚠️ 注意事项

1. **Critic不自己改**——批评者只提意见不改内容，防止越界
2. **迭代必须有上限**——Critic循环不设上限就是无限开销，推荐3轮
3. **Judge要能解释原因**——不能只给结论不给理由
4. **Producer的质量决定系统上限**——最模糊的地方最需要花功夫
5. **不要所有角色都上**——2-3个角色能解决的，5个角色反而更难维护
6. **角色可以复用Agent实例**——同一个模型可以兼职不同角色，只要明确当前是什么角色

## 参考来源

- https://www.digitalapplied.com/blog/multi-agent-orchestration-patterns-producer-consumer
- https://www.codebridge.tech/articles/mastering-multi-agent-orchestration-coordination-is-the-new-scale-frontier
