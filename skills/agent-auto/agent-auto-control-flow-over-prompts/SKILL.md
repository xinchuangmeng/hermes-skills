---
name: agent-auto-control-flow-over-prompts
description: 当Agent提示词写了MANDATORY/DO NOT SKIP还不管用时，应该把控制流从提示词移到代码中——确定性编排比更长的提示链可靠。核心框架：显式状态机 + 校验检查点 + LLM作为组件而非系统。
tags:
  - agent-control-flow
  - deterministic-orchestration
  - prompt-engineering-limits
  - agent-reliability
trigger:
  - 写Agent提示词时反复强调"MANDATORY"/"DO NOT SKIP"仍不生效
  - Agent部署后出现静默错误导致坏数据
  - 提示词越来越长（500+ tokens）但可靠性反而下降
  - 需要构建生产级Agent（金融/医疗/基础设施场景）
---

# Agent 控制流优先于提示词（Control Flow Over Prompts）

> **来源：** [Agents need control flow, not more prompts](https://bsuh.bearblog.dev/agents-need-control-flow/) — Hacker News 261 points
>
> **核心发现：** 可靠Agent处理复杂任务需要的是用代码实现的确定性控制流（deterministic control flow），而不是越来越长的提示链。

## 为什么要关注这个问题？

> 想象一种编程语言，其中语句只是"建议"（suggestions），函数可以返回"成功"但实际上在**幻觉**（hallucinating）。这就是纯提示词驱动的Agent现状。

- 软件可靠性来自**递归可组合性**（recursive composability）：系统由库→模块→函数构成，代码底层全是代码
- 代码有**可预测的行为**，支持**局部推理**
- 提示链（prompt chains）缺乏这些属性：非确定性、弱规范、难以验证

## 核心原则：把逻辑从"散文"移到"运行时"

### 确定性编排（Deterministic Scaffold）

**错误做法：** 在提示词里写 `MANDATORY: 必须先检查XX再执行YY，DO NOT SKIP`

**正确做法：** 在代码层面实现：
1. **显式状态机（Explicit State Transitions）** — 每一步有明确的进入条件和退出条件
2. **校验检查点（Validation Checkpoints）** — 关键步骤后自动验证输出格式/内容/业务规则
3. **LLM作为组件（LLM as a Component）** — LLM只是系统中的一块，不是整个系统

### 失败应对策略

在没有程序化验证的场景下，只有3种选项：

| 策略 | 说明 | 适用场景 |
|------|------|---------|
| **Babysitter（保姆）** | 人在环路中，每步手动检查 | 高风险任务、小规模 |
| **Auditor（审计）** | 执行完后做端到端全面验证 | 适合自动化流水线 |
| **Prayer（祈祷）** | 接受输出不去验证 | 低风险、成本敏感场景 |

## 实操步骤

### 步骤1：识别"纯提示词"瓶颈
搜索你的Agent提示词中是否有以下模式：
- `MANDATORY`, `DO NOT SKIP`, `必须` 等强调词
- 超过500tokens的单一任务指令
- 同一个提示词同时描述"做什么"和"怎么做"

### 步骤2：提取可确定性执行的部分
将提示词中的**过程性描述**（怎么做）提取出来，转为代码：
```
# 提示词原文（坏）
"搜索文件 → 读取内容 → 分析 → 输出报告。MANDATORY: 先搜索再读取"

# 代码编排（好）
def execute_analysis():
    files = search_files(pattern)
    contents = [read_file(f) for f in files]
    report = llm_analyze(contents)  # LLM只做分析
    validate_report(report)         # 校验检查点
    return report
```

### 步骤3：添加校验检查点
在关键步骤后插入程序化验证：
```python
def validate_report(report):
    assert "analysis" in report, "报告中缺少分析部分"
    assert len(report) > 100, "报告太短"
    # 更多业务规则...
```

### 步骤4：选择失败应对策略
- **生产级/高可靠性：** Auditor模式 — 写验证脚本自动审计输出
- **低风险/原型：** Prayer模式 — 接受输出，错误通过用户反馈修正
- **中间态：** Babysitter模式 — 关键步骤停住等人确认

### 步骤5：渐进式迁移
不需要一次性全改，从最频繁出错的环节开始：
1. 选1个当前经常失败的Agent任务
2. 识别其中最有规律的子步骤
3. 把这个子步骤从提示词搬进代码
4. 添加验证，持续迭代

## 注意事项

⚠️ **不要完全抛弃提示词**
- 控制流用代码，但LLM的内容生成（创意/分析/总结）仍然需要好的提示词
- 目标是把"怎么做"（过程）交给代码，"做什么"（意图）保留在提示词

⚠️ **过度工程化的风险**
- 简单任务（单步LLM调用）不需要这套框架
- 只有3步以上、有依赖关系的复杂任务才需要

⚠️ **检查点不要太多**
- 每个检查点增加延迟和复杂度
- 只在关键决策点（文件删除/数据库写入/金额确认）添加

⚠️ **Managed Agent平台的限制**
- 有些托管Agent平台（Cursor Cloud Agents, Anthropic等）不允许注入确定性控制流
- 自托管/自建Agent框架才能充分发挥这套模式
