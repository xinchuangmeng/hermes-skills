---
name: skill-biz-skill-description
description: >
  Hermes Agent技能（SKILL.md）描述优化技巧——关键发现：description字段的质量直接影响Hermes
  能否在正确时机自动加载技能。包含多触发短语策略、跨Agent兼容性说明、描述写法最佳实践。
  适用于技能作者和技能库搭建者。
tags:
  - skill-management
  - SKILL.md
  - description-optimization
  - skill-trigger
  - skill-discovery
trigger:
  - "技能描述怎么优化"
  - "skill description怎么写"
  - "技能触发不准确"
  - "skill not loading"
  - "describe skill properly"
  - "技能识别不准"
  - "heuristic matching skill"
---

# Hermes技能描述（description）优化技巧

## 核心发现

Hermes Agent通过**description字段的模糊匹配**来决定何时加载某个技能。
**description的质量直接决定了技能是否能被正确触发。**

## 最佳实践

### 1. 多触发短语策略

**不推荐（太少触发词）：**
```yaml
---
name: code-reviewer
description: Use when the user asks to review code
---
```

**推荐（覆盖多种表达方式）：**
```yaml
---
name: code-reviewer
description: >
  Use when the user asks to review code, check for bugs,
  audit security, or evaluate code quality. Also activate
  for PR reviews and merge request feedback.
---
```

**关键点**：你包含的表达方式越多，Hermes越能可靠地选中正确的技能。

### 2. 中英文混合策略

对于中国用户/双语环境：
```yaml
description: >
  代码审查技能。Use when reviewing code, checking for bugs,
  auditing security. 适用于PR review、代码质量评估、
  bug扫描、安全检查。
```

### 3. 技能名命名规范

```yaml
# ✅ 好名字：描述性强，一眼知道干什么
name: agent-auto-deepclaude
name: prompt-agent-system-prompt
name: h-config-skill-directory

# ❌ 差名字：太通用，不易识别
name: helper
name: test
name: my-skill
```

### 4. 面向场景而非面向功能

```yaml
# ❌ 面向功能
description: Use for generating HTML from markdown

# ✅ 面向场景（更容易被用户需求匹配）
description: >
  Convert markdown documents to HTML pages. Use when the user
  wants to publish a blog post, create a documentation site,
  or convert notes to web format.
```

## 跨Agent兼容性

Hermes兼容**所有SKILL.md规范的技能**——Claude Code、Cursor、Codex CLI的技能都能直接用。

**但Hermes忽略其他Agent的专属字段：**
- Claude Code的 `context: fork` → Hermes忽略
- Cursor的 `globs` → Hermes忽略
- Hermes只读 `name`, `description`, `tags`, 和markdown正文

**这意味着**：你写的技能对其他Agent也友好。但其他Agent的技能可能有Hermes不支持的配置字段。

## 目录结构最佳实践

```
~/.hermes/skills/
├── code-reviewer/
│   ├── SKILL.md
│   └── references/
│       └── checklist.md
└── test-generator/
    ├── SKILL.md
    └── examples/
        └── expected-output.md
```

## 验证技能是否被正确识别

```bash
# 重启Hermes让技能重新扫描
hermes reload

# 或者检查技能目录
ls ~/.hermes/skills/*/SKILL.md
```

## ⚠️ 注意事项

1. **description字段是触发核心**：不要写太笼统（"一个有用的技能"），不要写太长让关键内容淹没
2. **不要依赖"精准匹配"**：Hermes使用的是模糊匹配，所以要用尽量多的同义词覆盖
3. **Project-level > Global**：同名技能，项目级`skills/`优先级高于`~/.hermes/skills/`
4. **纯文本SKILL.md即可**：不需要JSON、YAML外的特殊格式，cross-agent兼容
5. **技能描述中include使用场景**：用户在真实对话中怎么描述这个需求，就把这些描述放进trigger/description

## 参考来源

- https://www.agensi.io/learn/how-to-use-skill-md-with-hermes-agent
- https://hermes-agent.nousresearch.com/docs/guides/work-with-skills
