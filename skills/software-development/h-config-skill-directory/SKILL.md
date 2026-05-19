---
name: h-config-skill-directory
description: >
  Hermes技能目录结构与安装配置指南——技能存放位置（project-level vs global）、目录组织最佳实践、
  安装步骤、跨Agent兼容性说明、技能发现和加载机制。适用于首次搭建Hermes技能库的用户。
tags:
  - hermes-config
  - skill-directory
  - skill-installation
  - project-structure
trigger:
  - "技能放在哪个目录"
  - "技能安装"
  - "skill directory"
  - "hermes skills folder"
  - "技能目录结构"
  - "skill installation guide"
  - "hermes reload"
  - "技能不生效"
---

# Hermes技能目录结构与安装指南

## 技能存放位置

Hermes按优先级顺序检查两个位置：

### 1. 项目级技能（Project-level）
```
skills/
```
- 位于当前工作目录根目录
- 可以用git提交，团队成员共享
- **优先级高于全局技能**

### 2. 全局技能（Global-level）
```
~/.hermes/skills/          # macOS/Linux
%USERPROFILE%\.hermes\skills\  # Windows
```
- 所有项目都能访问
- 个人工具类技能放在这里

## 目录组织最佳实践

```
~/.hermes/skills/
├── agent-auto-deepclaude/           # Agent自动化类
│   ├── SKILL.md
│   └── references/
│       └── cost-comparison.md
├── prompt-agent-system-prompt/      # 提示词类
│   └── SKILL.md
├── skill-biz-skill-description/     # 技能搭建类
│   └── SKILL.md
├── troubleshooting-something/       # 排障类
│   └── SKILL.md
└── h-config-multi-instance/         # Hermes配置类
    └── SKILL.md
```

### 命名规范建议

| 类别前缀 | 用途 | 示例 |
|---------|------|------|
| `h-config-` | Hermes配置类 | `h-config-multi-instance` |
| `prompt-` | 提示词优化类 | `prompt-agent-system-prompt` |
| `skill-biz-` | 技能库搭建类 | `skill-biz-skill-description` |
| `agent-auto-` | Agent自动化类 | `agent-auto-orchestration-patterns` |
| `troubleshoot-` | 报错排障类 | `troubleshoot-api-429` |

## 安装技能

### 从文件夹安装

```bash
# 全局安装
mkdir -p ~/.hermes/skills && cd ~/.hermes/skills
# 直接复制技能文件夹
cp -r /path/to/code-reviewer ./

# 项目级安装
mkdir -p skills && cd skills
cp -r /path/to/code-reviewer ./
```

### 从压缩包安装

```bash
cd ~/.hermes/skills
unzip /path/to/code-reviewer.zip
# 验证安装
ls code-reviewer/SKILL.md
```

### 从Skills Hub安装

```bash
# 在Hermes对话中使用
/skills install https://example.com/SKILL.md --name my-skill
```

## 技能加载机制

1. Hermes**启动时**扫描所有`SKILL.md`文件
2. 读取YAML frontmatter的`description`字段
3. 使用**模糊匹配**比对用户请求
4. 匹配到最佳技能后通过`skill_view`工具加载
5. 匹配失败则回退到默认行为

### 手动刷新技能

```bash
# 重启Hermes
hermes reload
# 或直接在对话中
/reload
```

### 手动加载技能

在Hermes对话中：
```
使用[技能名]技能帮我做X
```

或在CLI中：
```
hermes --load-skill code-reviewer --goal "review this PR"
```

## ⚠️ 注意事项

1. **优先级规则**：同名技能Project-level > Global，方便按项目覆盖
2. **安装后需reload**：新增技能需要重启或`hermes reload`才能被发现
3. **不支持嵌套子目录**：Hermes不会递归扫描深处的SKILL.md，技能文件夹必须直接在`skills/`或`~/.hermes/skills/`下
4. **每个技能一个文件夹**：不要在同一个文件夹放多个SKILL.md，只会加载第一个
5. **跨Agent兼容**：Claude Code/Cursor/Codex的技能文件可直接使用，无需修改
6. **配置文件目录**：在config.yaml中可修改`skills_dir`参数自定义技能路径

## 参考来源

- https://www.agensi.io/learn/how-to-use-skill-md-with-hermes-agent
- https://hermes-agent.nousresearch.com/docs/guides/work-with-skills
