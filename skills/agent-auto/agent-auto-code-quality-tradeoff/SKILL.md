---
name: AI生成代码质量管控 — Reasoning-Complexity Tradeoff
description: 基于arXiv论文"AI-Generated Smells"的发现——LLM越强代码越臃肿，能力增长带来架构退化。提供AI Agent生成代码时的质量检查清单，防止产生技术债。
tags: [agent, code-quality, architecture, technical-debt, reasoning-complexity-tradeoff]
trigger: 当Agent执行代码生成、代码review、重构任务，或生成长函数/复杂模块时
---

# AI生成代码质量管控 — 防止架构退化

## 核心问题
arXiv 2605.02741 论文发现了一个关键问题：
- **推理-复杂度权衡**：LLM能力增强 → 生成代码更臃肿、耦合更严重
- **体积-质量反比定律**：代码量几乎是结构退化的完美预测指标
- **功能正确 ≠ 可维护**：AI生成的代码功能测试通过但长期维护困难
- **提示词优化不能解决**：详细prompt无法阻止代码膨胀

## 操作步骤

### 1. 代码生成前的约束设置
在system prompt或任务prompt中明确添加：

```
## 代码约束
- 单函数不超过50行
- 每个函数只做一件事
- 模块间通过接口耦合，不依赖具体实现
- 生成的代码总行数预估不超过X行
- 禁止生成重复代码（DRY原则）
- 明确标注TODO和设计决策
```

### 2. 生成后质量检查清单
每次Agent生成代码后，自动执行以下检查：

```python
# 检查清单
checks = {
    "单函数长度": "是否有函数超过50行？",
    "圈复杂度": "是否有函数嵌套>4层？",
    "重复代码": "是否有明显的重复逻辑？",
    "耦合度": "模块之间是否通过抽象接口耦合？",
    "职责单一": "每个类/函数是否只做一件事？",
    "硬编码": "是否有magic number/string？",
    "测试覆盖": "关键路径是否有单元测试？",
}
```

### 3. 重构触发器
当发现以下**红灯信号**时，要求Agent先重构再继续：

- ⚠️ 单文件超过300行（立即拆分）
- ⚠️ 函数参数超过5个（改用配置对象）
- ⚠️ 出现 God Class / 万能工具类（拆分职责）
- ⚠️ 代码量比预期多2倍以上（重新设计）

### 4. 增量执行原则（结合incremental-implementation技能）
- 一次只写一个模块
- 写完立即检查质量指标
- 通过后再写下一个
- 不累积技术债

## 注意事项
- ⚠️ 功能测试通过不等同于代码质量好
- ⚠️ 更详细的prompt不能阻止代码膨胀——需要硬性约束
- ⚠️ 重构时优先保结构，再优化性能
- ⚠️ 这个规律适用于所有主流LLM（GPT-4/Claude/DeepSeek等）

## 参考
- arXiv:2605.02741 "AI-Generated Smells: An Analysis of Code and Architecture in LLM and Agent-Driven Development"
