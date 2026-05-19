---
name: AI输出不盲目信任原则 — 验证即信任
description: 基于Susam Pal的"Inverse Laws of Robotics"（2026年1月）——三个反定律：不拟人化、不盲信、不放任责任。提供AI Agent使用者和开发者的安全使用清单，防止过度依赖AI输出。
tags: [prompt, safety, ai-literacy, responsible-ai, verification, guardrails]
trigger: 当设计AI Agent的产品交互、构建安全护栏、或用户可能依赖AI输出做重大决策时
---

# AI输出验证原则 — 不拟人、不盲信、不放任

## 三条核心原则（Inverse Laws of Robotics）

### 第1条：不拟人化（Non-Anthropomorphism）
**人类不能将AI系统拟人化。**
- 不能赋予AI情感、意图或道德主体性
- 拟人化扭曲判断力，极端情况导致情感依赖
- 聊天系统的礼貌用语 ≠ AI有同理心

### 第2条：不盲信（Non-Deference）
**人类不能盲目信任AI输出。**
- AI可能输出事实错误、误导性或不完整的内容
- 搜索引擎把AI答案放在结果顶部不意味着它正确
- 需要"验证即信任"（Verify-Then-Trust）而非"信任即验证"

### 第3条：不放任责任（Non-Abdication of Responsibility）
**人类必须对AI使用的后果负全责。**
- 使用AI不豁免责任
- 最终决策者永远是人类

## 操作步骤

### 1. 在System Prompt中加入安全提示

```markdown
## 输出验证原则
- 本AI不具情感或意图——所有输出都是概率计算的结果
- 请用户始终验证关键信息
- 任何重要决策应在使用AI输出后由人类审核
```

### 2. 构建验证护栏（针对Agent开发者）

```python
# Agent输出验证函数
def verify_agent_output(output, task_type):
    checks = []
    
    if task_type == "financial":
        checks.append("数值是否在合理范围内？")
        checks.append("是否有计算过程可以追溯？")
        checks.append("是否标注了数据来源？")
    
    if task_type == "code":
        checks.append("代码是否能编译/运行？")
        checks.append("是否有单元测试覆盖？")
        checks.append("是否引入外部依赖？")
    
    if task_type == "factual":
        checks.append("是否有引用的原始数据源？")
        checks.append("是否存在矛盾断言？")
        checks.append("是否有置信度评估？")
    
    return checks
```

### 3. 用户交互设计（前端展示时）

```html
<!-- AI输出的免责提示 -->
<div class="ai-disclaimer">
  <p>⚠️ 此内容由AI生成，仅供参考。 
     在做出决策前，请验证关键信息。</p>
</div>
```

### 4. Agent内部的自我约束提示词（可选）

在Agent的system prompt中加入：

```
## 诚实性原则
1. 不要猜测——如果不知道就说不知道
2. 标注置信度——低/中/高
3. 提供信息来源——让用户可以验证
4. 不要生成看似权威的错误内容
```

## 注意事项
- ⚠️ 即使LLM的准确性提高到99.9%，对于关键决策系统，那0.1%仍然致命
- ⚠️ 搜索结果顶部的AI答案会产生"权威光环"效应
- ⚠️ Agent自主操作（如自动发邮件、执行交易）需要额外安全层
- ⚠️ 核心矛盾：AI越好用→越容易被信任→风险越大

## 参考
- Susam Pal (2026-01-12): "Three Inverse Laws of AI" 
- https://susam.net/inverse-laws-of-robotics.html
