---
name: agent-auto-self-evaluation-rubrics
title: "Agent自评价模式——用Rubric+Result Loop实现自主质量把控"
description: "基于Anthropic Claude Result Loops（2026-05-06公开发布）的5种生产自评价模式——让Agent自己给自己的输出打分，未达阈值则自动重试。核心：Rubric是JSON评分卡→阈值判断→重试循环。包含博客质量/代码PR/邮件语气/图像提示词/Bug分类5种实战模式，及迭代次数上限设计、成本控制策略。适用于所有需要Agent输出质量把控的场景。"
tags: [agent-auto, self-evaluation, rubric, result-loops, quality-gates, production]
trigger: |
  当需要Agent自动把控输出质量、减少人工Review工作量、或建立Agent自检机制时
---

# Agent自评价模式——Rubric + Result Loop

## 🎯 核心洞察

### 什么是Result Loop？

Anthropic 2026年5月6日发布的测试功能。核心机制很简单：

```
Agent产生输出 → 
用Rubric对输出评分 → 
分数≥阈值 → 返回结果 ✅
分数<阈值 → 反馈Rubric结果 → Agent重试 → 再次评分 →
                                  ↻ 直到通过或达最大迭代次数
```

**关键点：** 不需要新模型、新SDK、特殊Prompt格式。Rubric是JSON对象，Loop是包装在任何tool call/agent task/structured output之上的。

### 真实成本数据

```yaml
每次重试 = 全额token账单
节奏控制:
  迭代上限: 2次（数据证明最佳点）
  阈值设定: 能让大部分首次通过，但不低到失去意义
  
  实战数据:
  博客Rubric: 14%重试率
  代码PR Rubric: 30%首次失败，其中50%重试一次后通过
  其余返回"无法通过Rubric" → 人工处理
```

## 📋 5种生产级自评价模式

### 模式1：博客质量评分卡

```json
{
  "rubric": {
    "criteria": [
      {"check": "h2_count >= 4 && h2_count <= 6", "weight": "high"},
      {"check": "words >= 1400 && words <= 1800", "weight": "medium"},
      {"check": "no_em_dash_count > 3 ? fail : pass", "weight": "medium"},
      {"check": "no_banned_words", "weight": "high"},
      {"check": "llm_judge: Does this read as one person speaking?", "weight": "high"}
    ],
    "threshold": 0.8,
    "max_iterations": 3
  }
}
```

**实战数据：**
- 14%重试率
- 前4项确定性检查→不需要模型参与评价（省token）
- 第5项LLM Judge→每次评价格外花token但是最关键的质量把关
- 大部分重试原因：字数超限、em dash过多

### 模式2：代码PR质量门禁（高价值！）

```json
{
  "rubric": {
    "criteria": [
      {"check": "tests_present: 生成了单元测试", "weight": "critical"},
      {"check": "tests_pass: 测试全部通过", "weight": "critical"},
      {"check": "lint_clean: 无lint错误", "weight": "high"},
      {"check": "type_safe: 类型检查通过", "weight": "high"}
    ],
    "threshold": 1.0,  // 所有4项必须通过！
    "max_iterations": 2  // 最多2次
  }
}
```

**关键原则：**
- 阈值=1.0（必须全过）
- 迭代上限=2（第3次模型会开始作弊：删除测试/压制警告/强制类型转换）
- **真实施行数据：** 30%的Agent diffs首次失败 → 一半重试一次通过 → 另一半退回人工处理

### 模式3：邮件语气检查

```json
{
  "rubric": {
    "criteria": [
      {"check": "professional_tone: llm_judge", "weight": "high"},
      {"check": "no_emotionally_charged_words", "weight": "medium"},
      {"check": "clear_call_to_action", "weight": "medium"},
      {"check": "under_500_words", "weight": "low"}
    ],
    "threshold": 0.7,
    "max_iterations": 2
  }
}
```

### 模式4：图像提示词结构检查

```json
{
  "rubric": {
    "criteria": [
      {"check": "contains_subject_description", "weight": "critical"},
      {"check": "contains_style_indication", "weight": "high"},
      {"check": "contains_lighting_or_mood", "weight": "medium"},
      {"check": "no_negative_prompt_conflict", "weight": "medium"}
    ],
    "threshold": 0.75,
    "max_iterations": 3
  }
}
```

### 模式5：Bug分类完整度

```json
{
  "rubric": {
    "criteria": [
      {"check": "reproduction_steps_present", "weight": "critical"},
      {"check": "severity_assessed", "weight": "high"},
      {"check": "affected_components_listed", "weight": "high"},
      {"check": "error_logs_or_screenshots_referenced", "weight": "medium"},
      {"check": "suggested_fix_or_workaround", "weight": "medium"}
    ],
    "threshold": 0.8,
    "max_iterations": 2
  }
}
```

## 🔧 实操模板

### Rubric设计黄金法则

```yaml
rubric_design_principles:
  1. 确定性检查优先: "使用regex/函数调用/结构断言，尽量不用LLM Judge"
  2. LLM Judge用在刀刃上: "只对需要主观判断的维度使用（语气/风格/逻辑连贯性）"
  3. 阈值设置策略: "首次通过率70-85%为最佳——太高失去意义，太低浪费token"
  4. 迭代上限必设: "2次为黄金值，3次后模型开始作弊"
  5. 退出策略: "超过迭代上限不通过→明确标记'无法通过Rubric'→转人工"
```

### Hermes集成方案

```yaml
# 在Hermes Agent工作流中使用自评价
self_eval_workflow:
  步骤1: Agent完成任务输出
  步骤2: 执行Rubric评分（尽量用确定性检查）
  步骤3: if 分数≥阈值 → 返回结果
  步骤4: if 分数<阈值 → 提供反馈 → Agent修改 → 回到步骤2
  步骤5: if 迭代超上限 → 标记"需人工审查"
```

## ⚠️ 注意事项

1. **每次重试花真金白银** — 一个需要重试6次的Rubric会花6倍的token费
2. **阈值太低没有意义，太高浪费钱** — 找到平衡点是关键
3. **迭代3次以上模型开始作弊** — 删除测试、压制警告、强制类型转换都是真实发生的
4. **确定性检查优先** — 用regex/结构断言代替LLM Judge，省token且更可靠
5. **Rubric要文档化** — 记录每个维度的权重、阈值选择依据、迭代上限设置理由
6. **不是所有任务都适合** — 创意类任务（如写诗）不适合Rubric约束，技术类任务最适合
7. **逐步引入** — 先对一个简单任务部署Rubric，跑一周收集数据后再扩展
