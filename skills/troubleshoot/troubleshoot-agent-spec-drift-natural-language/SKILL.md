---
name: troubleshoot-agent-spec-drift-natural-language
title: "自然语言规范(Spec)漂移: 提示词不够精确导致Agent幻觉"
description: "基于AI vs Non-AI实验中发现的关键问题——自然语言本质上是模糊的。给Agent写Spec时如果不够精确，Agent会'填空'（幻觉）。解法: 用结构化Spec（步骤化/示例化/约束化）替代纯自然语言描述。适用于所有向Agent描述任务/需求的场景。"
tags: [troubleshoot, spec, NLP, agent-hallucination, prompt-engineering]
trigger: |
  Agent生成的代码/结果与预期不符时
  发现Agent在"自行发挥"而不是按Spec执行时
  用自然语言描述需求给Agent效果不好时
  需要精确控制Agent行为时
---

# 自然语言规范(Spec)漂移: 提示词不够精确导致Agent幻觉

## 问题

来自真实实验: 开发者用自然语言写Spec -> Agent自行发挥 -> 结果不符合预期

> "Natural language is imprecise by nature. A real developer can fill the gaps of a specification document applying their own judgment and knowledge about the domain. AI will just hallucinate."
> -- Fernando Fornieles (AI vs Non-AI实验作者)

## 具体症状

| 问题 | 自然语言Spec | Agent行为 | 修复方法 |
|------|-------------|-----------|---------|
| 温度偏移 | "读取传感器温度" | 读取后做偏移 | 明确说"先偏移再读取" |
| 认证问题 | "实现用户认证" | 用各种方法实现 | 指定具体认证协议 |
| 数据格式 | "返回JSON" | 自己决定JSON结构 | 提供JSON Schema |
| 错误处理 | "处理异常情况" | 忽略或简单处理 | 列出所有异常+响应方式 |

## 修复方案: 结构化Spec框架

### 方法1: 步骤化Spec (Step-by-Step)

```markdown
# 不好的Spec
实现一个天气数据读取器，读取传感器数据并以JSON格式输出。

# 好的Spec (步骤化)
实现天气数据读取器，按以下步骤执行:
1. 调用sensor.read_temperature() -> 获取温度值(单位: 摄氏度)
2. 调用sensor.read_humidity() -> 获取湿度值(单位: 百分比)
3. 计算露点: 用Magnus公式，温度用step1的值，湿度用step2的值
4. 组装JSON: {"temperature": <step1值>, "humidity": <step2值>, "dew_point": <step3值>}
5. 写入文件: /output/weather_{timestamp}.json
```

### 方法2: 示例化Spec (Example-Driven)

```markdown
# 用输入输出示例替代模糊描述

输入: sensor读取返回 {"temp_raw": 23.5, "humidity_raw": 65}
预期输出:
{
  "temperature": 23.5,
  "humidity": 65,
  "dew_point": 16.2,
  "unit": "celsius"
}

输入: sensor读取返回 {"temp_raw": 0, "humidity_raw": 50}
预期输出:
{
  "temperature": 0,
  "humidity": 50,
  "dew_point": -9.3,
  "unit": "celsius"
}
```

### 方法3: 约束化Spec (Constraint-Driven)

```markdown
# 不是: "确保数据安全"
# 而是具体约束:

约束:
  - 不要在日志中打印API密钥
  - 不要在响应中包含密码字段
  - 所有网络请求必须使用HTTPS
  - 请求头必须包含Authorization: Bearer {token}
  - 如果认证失败，返回401而不是重定向到登录页

# 不是: "做基本的错误处理"
# 而是:

错误处理规则:
  - 网络超时: 重试3次，间隔2秒
  - 传感器无响应: 记录错误，返回空值(null)
  - 数据格式错误: 抛出ValueError + 附带原始数据
  - 任何未预期异常: catch后写入error.log
```

### 方法4: 分步执行模式 (Step-by-Step, 替代一次性Spec)

从实验中总结的最佳实践:

```
错误的做法:
  写完整Spec -> 让Agent一次实现 -> 发现不对 -> 重写Spec

正确的做法:
  写第1步Spec -> Agent执行 -> 验证 -> 写第2步Spec -> Agent执行 -> ...
```

## 操作步骤

### 步骤1: 识别Spec模糊点

```markdown
# 在写Spec时，问自己:
# 1. 这个描述有没有歧义?
# 2. Agent会不会有多种理解?
# 3. 如果让另一个人做，会不会做不一样?

# 有问题的模糊词:
- "适当的" -> 什么算适当?
- "基本的" -> 基本到什么程度?
- "友好的" -> 怎样算友好?
- "合理的" -> 合理范围是多少?
```

### 步骤2: 用结构化模板写Spec

```markdown
## Spec模板

### 输入
- 格式: [JSON/CSV/文本]
- 示例: [至少2个输入示例]
- 边界值: [空/NULL/最大值]

### 处理步骤 (按顺序)
1. [具体操作]
2. [具体操作]
3. [具体操作]

### 输出
- 格式: [JSON/CSV/文本]
- Schema: [输出结构示例]
- 错误输出: [异常时返回什么]

### 约束
- [约束1]
- [约束2]

### 验证条件
- [如何验证结果正确]
```

### 步骤3: 用Agent验证Spec

```markdown
# 在给Agent执行Spec前，先用另一个Agent检查Spec:
"请检查以下Spec的模糊点，标记每一条可能被'自行发挥'的地方:"
[你的Spec]
```

## 注意事项

- 写精确Spec比写代码更难吗? 实验作者说"是"——他最终放弃了Spec模式，改用逐步骤指导
- 但逐步骤指导也有代价——你需要同时理解要解决的问题和Agent的能力边界
- 如果你的Spec需要5步以上，建议拆成多个子任务，每个子任务单独delegate
- 最危险的Spec: 看起来精确但遗漏了关键细节（如温度偏移顺序）
