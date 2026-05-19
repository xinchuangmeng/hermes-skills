---
name: vibe-coding-to-agentic-engineering
title: "从Vibe Coding到Agentic Engineering——Simon Willison的反思"
description: "基于Simon Willison 2026年5月文章《Vibe coding and agentic engineering are getting closer than I'd like》的核心观点——Vibe Coding（让AI瞎写代码，人只管粘贴）和Agentic Engineering之间的距离在缩小，但这不是好事。核心洞察：AI生成代码的隐形成本（认知复杂度、技术债、安全漏洞）被严重低估，需要建立新的工程标准来弥补AI代码的质量差距。"
tags: [agent-auto, vibe-coding, agentic-engineering, code-quality, simon-willison]
trigger: |
  当讨论AI生成代码质量、评估是否用AI自动写代码、或需要建立AI代码审查标准时
---

# 从Vibe Coding到Agentic Engineering

## 🎯 核心洞察

### 什么是Vibe Coding？
- 让AI写代码，人类只管粘贴运行
- 不太理解代码逻辑也不要紧，"能跑就行"
- 典型的「盲信任」模式

### 什么是Agentic Engineering？
- AI Agent自主生成代码、修改文件、执行命令
- 比Vibe Coding更激进——Agent可以未经检查就部署
- 风险更高——错误可以快速放大

### Simon Willison的核心担忧
> "Vibe coding和Agentic engineering之间的距离越来越近了，但这让我不安。"

**2026年5月最新思考——两者已经在自己的实践中开始模糊：**

1. **Agent越来越可靠** — 请求JSON API端点+SQL查询+输出JSON，Claude Code几乎不会搞错。你可能不再review每一行代码。
2. **罪恶感悖论** — 知道应该review但不再review了。Agent太可靠反而让人松懈。
3. **"非程序员也能用Agent搭建原型"** — Vibe Coding的初衷（非程序员写代码）正在被Agentic Engineering的能力覆盖。
4. **分界线还能维持多久？** — 当Agent编码可靠到专业工程师也不review时，Vibe Coding（不review）和Agentic Engineering（应该review但实际不review）还有区别吗？

**Simon的解决方案：用自动生成测试来替代代码review。**
> "The thing that really helps me is that Claude Code generates good tests. I have it add automated tests, I have it add documentation, I know it's going to be good. But I'm not reviewing that code."
>
> 关键思路：如果你不review代码本身，至少让Agent把验证自动化——写测试、加文档、做静态分析。用自动化验证替代人工逐行review。

**问题不是AI写代码的质量，而是：**
1. 人类不再审核——信任代替了验证
2. 技术债累积——AI生成代码的可维护性低于人类代码
3. 安全盲区——AI不擅长安全编码，但人也不再检查

## 📋 应对策略

### 策略1：AI代码审查清单
每次AI生成的代码合入前，检查以下维度：

```yaml
安全审查:
  - 是否有SQL注入风险？（AI经常拼接字符串）
  - 是否有XSS风险？（AI生成的前端代码）
  - 是否有越权访问？（AI生成的API端点）
  - 是否有硬编码密钥/密码？
  - 输入验证是否完整？

质量审查:
  - 异常处理是否到位？（AI经常忽略错误路径）
  - 边界条件是否覆盖？
  - 命名是否一致性？
  - 是否有重复代码？
  - 是否有过度的抽象？（AI喜欢过度设计）

性能审查:
  - 是否在循环中调用API？
  - 是否有N+1查询问题？
  - 缓存策略是否合理？
```

### 策略2：建立AI代码的质量门槛
```yaml
# 严格模式（推荐生产使用）
quality_gates:
  complexity_threshold: 15  # 圈复杂度
  coverage_minimum: 70%     # 测试覆盖率
  security_scan: mandatory  # 必须做安全扫描
  review_required: true     # 必须人工Review

# 宽松模式（原型/实验阶段）
quality_gates:
  complexity_threshold: 25
  coverage_minimum: 30%
  review_required: false    # 可跳过Review
```

### 策略3：记住三件事
```
1. AI生成的代码 ≠ 高质量代码
2. 能跑 ≠ 正确
3. 不要因为「AI写的」就放松审查标准
```

## ⚡ 实操建议

### 关键新思路：用自动测试替代代码Review

> Simon Willison的核心洞见：当你不review AI写的代码时，至少让AI生成测试来自动验证。

```yaml
# 替代人工逐行review的自动化验证链
auto_validation_chain:
  步骤1: AI生成代码
  步骤2: AI自动生成测试（单元测试+集成测试）
  步骤3: 自动运行测试 → 全部通过？
  步骤4: 自动静态分析（复杂度/安全/风格）
  步骤5: 自动生成文档
  步骤6: 如果以上全都通过 → 可以合入（无需逐行review）
  
  核心原则: "用测试覆盖替代人工审查，但测试本身也需要review"
```

### 在Hermes工作流中的应用
```yaml
# 每次AI生成代码后，自动触发质量检查
quality_check:
  - 步骤1: AI生成代码
  - 步骤2: 自动执行静态分析（复杂度/安全扫描）
  - 步骤3: 如果复杂度>15，标记需人工Review
  - 步骤4: 如果安全扫描发现问题，拒绝合入
  - 步骤5: 只有检查全通过才能进入下一步
```

### 快速判断代码是否可信
```python
def should_trust_ai_code(code):
    red_flags = []
    if "eval(" in code:
        red_flags.append("使用了eval")
    if "exec(" in code:
        red_flags.append("使用了exec")
    if "os.system" in code:
        red_flags.append("Shell注入风险")
    if not try_except or not input_validation:
        red_flags.append("缺少异常处理或输入验证")
    return len(red_flags) == 0, red_flags
```

## ⚠️ 注意事项

1. **AI代码的维护成本**：6个月后回头看AI写的代码，理解成本比手写的高2-3倍
2. **安全是最大隐患**：AI不擅长安全编码，这已在多篇论文和实际事故中被证实
3. **信任但验证**：即使相信AI的基本能力，也要自动化检查和人工抽检
4. **Vibe Coding只适合原型**：任何上生产的东西，都必须经过Agentic Engineering的质量管控
5. **建立团队规范**：做AI开发的团队，必须有明确的「AI代码审查」流程
