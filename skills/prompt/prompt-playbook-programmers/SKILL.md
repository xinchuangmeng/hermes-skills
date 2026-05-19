---
name: prompt-playbook-programmers
title: "程序员的提示词工程实战手册——Addy Osmani版"
description: "基于Addy Osmani的'The Prompt Engineering Playbook for Programmers' (HN 464 points)。专为程序员设计的提示词工程实战指南——不是理论，而是可以直接用在代码生成、审查、重构、调试中的提示词模板和技巧。核心原则：用代码思维写提示词（精确、可测试、分模块）。适用于所有用AI辅助编码的开发者。"
tags: [prompt, programmers, code-generation, prompt-templates, addy-osmani]
trigger: |
  当用AI辅助编码、需要写代码相关的提示词、或想系统化提升AI编码效率时
---
# 程序员的提示词工程实战手册

## 🎯 核心洞察

> 来源: Addy Osmani's "The Prompt Engineering Playbook for Programmers" (HN 464 points)

### 程序员写提示词的独特优势
程序员天然适合写好的提示词——因为编程的核心就是把需求精确地、结构化地表达出来。

### 核心原则
程序员写提示词应该像写代码一样：
1. **精确** — 每个词都有意义，不要说废话
2. **可测试** — 能验证输出是否符合预期
3. **分模块** — 复杂任务拆成小步骤
4. **可复用** — 建立自己的prompt模板库
5. **可调试** — 输出不对时能定位问题

## 🔧 编码场景提示词模板

### 1️⃣ 代码生成
```markdown
# 坏写法（大而全）
"帮我写一个用户登录API"

# 好写法（精确、分步骤）
"用Python Flask实现一个用户登录API端点。

## 需求
- 方法：POST /api/login
- 输入：{username: str, password: str}
- 成功返回：{token: str, user: {id, name}}
- 失败返回：{error: string}

## 安全要求
- 密码使用bcrypt验证
- Token使用JWT，有效期24小时
- 限制登录尝试（5次失败后锁定15分钟）

## 约束
- 使用Flask-RESTful作为框架
- 错误信息不要暴露内部实现细节
- 加上类型提示
- 写单元测试"
```

### 2️⃣ 代码审查
```markdown
"请审查以下Python代码的pull request diff。

## 审查维度
1. 正确性 — 逻辑有没有bug
2. 安全性 — 有没有SQL注入/XSS/路径遍历风险
3. 性能 — 有没有不必要的循环、冗余查询
4. 可维护性 — 命名是否清晰、函数是否过长
5. 测试 — 是否有足够的测试覆盖

## 输出格式
- 严重问题：[CRITICAL] 描述（必须修复）
- 一般问题：[WARNING] 描述（建议修复）
- 风格问题：[STYLE] 描述（可选项）

## 严格规则
- 如果完全没问题，只输出："PASS | 未发现明显问题"
- 不要为了找问题而编造问题
- 不确认的标记为 [UNSURE] 

代码diff:
```diff
{diff_content}
```"
```

### 3️⃣ 调试助手
```markdown
"我遇到以下错误，请帮我调试。

## 错误信息
{error_message}

## 相关代码
```python
{relevant_code}
```

## 我已经试过的方案
1. {attempt_1}
2. {attempt_2}

## 请按以下步骤分析
1. 先分析错误根因（不要直接给解决方案）
2. 如果是常见错误，给出标准修复方案
3. 如果根因不明确，列出需要进一步排查的步骤
4. 给出修复后的代码示例
```

### 4️⃣ 重构建议
```markdown
"请帮我重构以下代码。

## 原始代码
```python
{code}
```

## 重构目标
- 主要目标：{extract_method | rename | simplify | split | ...}
- 次要目标：保持向后兼容
- 约束：不能引入新的依赖

## 输出格式
1. 重构计划（要改哪些地方，为什么）
2. 重构后的完整代码
3. 变更摘要（改了哪些文件，改了什么）
```

### 5️⃣ 测试编写
```markdown
"请为以下函数编写单元测试。

## 函数
```python
{function_code}
```

## 测试要求
- 框架：pytest
- 覆盖：正常路径 + 边界情况 + 异常路径
- 不要mock外部依赖（使用真实实例或fixture）
- 每个测试函数有清晰的docstring说明测试场景
- 覆盖率目标：行覆盖率>90%

## 输入输出示例
- 输入：{example_input}
- 预期输出：{example_output}
```

## 📦 提示词模板库管理

### 目录结构
```bash
my-prompts/
├── code-generation/
│   ├── api-endpoint.md
│   ├── database-schema.md
│   └── test-case.md
├── code-review/
│   ├── general-review.md
│   ├── security-review.md
│   └── performance-review.md
├── debug/
│   ├── error-analysis.md
│   └── crash-debug.md
└── refactor/
    ├── extract-method.md
    └── simplify-complexity.md
```

### 提示词模板的版本管理
```yaml
# 每个模板文件头部包含元数据
---
name: api-endpoint
version: v1.2.0
author: your-name
last_updated: 2026-05-14
success_rate: 0.85  # 生成代码可用的比例
known_issues:
  - "有时漏掉错误处理的类型注解"
  - "JWT相关的代码偶尔不遵循最佳实践"
---
```

## 💡 程序员特有的Prompt技巧

### 技巧1：用伪代码描述需求
```markdown
# 用伪代码让AI理解你的需求
需求：
function validate_email(email):
  if email 为空 → 返回 "邮箱不能为空"
  if email 不包含 @ → 返回 "邮箱格式不正确"
  if email 长度 > 100 → 返回 "邮箱太长"
  else → 发送验证邮件

请用Python实现以上逻辑。
```

### 技巧2：给定输入输出示例
```markdown
# 给示例比给描述更有效
输入: {"users": [{"name": "A", "score": 85}, {"name": "B", "score": 92}]}
输出: {"top": "B", "average": 88.5}

请写一个函数实现以上输入输出逻辑。
```

### 技巧3：用代码思维写约束
```markdown
# 像写断言一样写约束
约束：
  assert output is not None
  assert len(output) > 0
  assert all(item.has_key('id') for item in output)
  # 不允许输出中的日期格式不一致
```

### 技巧4：渐进式构建
```markdown
# 不要一次性要求AI做太复杂的事情
第1步: "帮我定义数据模型" → 确认
第2步: "基于上面模型，帮我实现CRUD API" → 确认  
第3步: "给API加上认证和授权" → 确认
第4步: "写以上功能的测试" → 确认
```

## ⚠️ 注意事项

1. **不要过度"编程化"提示词** — 自然语言仍然是AI理解最好的方式，代码只是辅助
2. **太长/太结构的prompt可能效果反而不好** — 找到精确和简洁的平衡点
3. **不同模型对结构化prompt的响应不同** — 在一个模型上好用的模板，换模型可能效果下降
4. **模板需要持续迭代** — 像代码一样，prompt模板需要持续优化和更新
5. **保存成功案例** — 记录哪些提示词模板效果好，哪些需要改进
6. **不只在编码时用** — 代码审查、CI/CD集成、文档生成等场景也需要专门模板
