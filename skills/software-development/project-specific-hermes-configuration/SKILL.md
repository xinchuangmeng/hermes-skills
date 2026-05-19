---
name: project-specific-hermes-configuration
description: 为不同项目创建独立的Hermes配置，包括飞书Webhook隔离、技能集定制和项目目录结构
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, configuration, feishu, project-isolation, skills]
    related_skills: [hermes-multi-instance-guidelines]
---

# 项目专用Hermes配置指南

本技能指导如何为不同项目创建独立的Hermes配置，实现：
1. 独立的飞书Webhook通知
2. 项目专用的技能集
3. 隔离的项目目录结构
4. 独立的模型配置

## 使用场景

### 场景1：电商项目 vs 日常助手
- **小小书童**：日常通用助手，使用主配置
- **电商助手**：专门处理东南亚电商项目，使用项目配置

### 场景2：多团队协作
- 团队A：使用独立的飞书机器人接收通知
- 团队B：使用不同的技能集和配置

## 配置步骤

### 步骤1：创建项目目录结构
```bash
# 创建项目目录
mkdir -p ~/project-name
cd ~/project-name

# 创建标准目录结构
mkdir -p {backend,frontend,database,scripts,deployment,docs,notebooks,tests}
```

### 步骤2：创建项目专用配置
创建 `~/project-name/config.yaml`：

```yaml
name: "project-name"
personality: "technical"  # 根据项目类型选择个性
model:
  default: deepseek-chat
  provider: deepseek
  base_url: https://api.deepseek.com/v1
feishu:
  webhook_url: "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK"
  secret: "YOUR_SECRET"
  verify: true
skills:
  - jupyter-live-kernel    # 数据科学分析
  - github-pr-workflow     # GitHub工作流
  - notion                 # 项目管理
  - obsidian               # 笔记系统
agent:
  max_turns: 100
toolsets:
  - hermes-cli
```

### 步骤3：启动项目专用Hermes
```bash
# 进入项目目录
cd ~/project-name

# 设置环境变量指向项目配置
export HERMES_CONFIG=$(pwd)/config.yaml

# 启动项目专用Hermes
hermes chat --skills "jupyter-live-kernel,github-pr-workflow,notion,obsidian"
```

## 配置详解

### 1. 飞书Webhook配置
```yaml
feishu:
  webhook_url: "项目专用Webhook URL"
  secret: "项目专用Secret"
  verify: true  # 启用消息验证
```

**获取Webhook**：
1. 在飞书开放平台创建机器人
2. 获取Webhook URL和Secret
3. 替换配置中的占位符

### 2. 技能集定制
根据项目类型选择技能：

| 项目类型 | 推荐技能 | 用途 |
|---------|---------|------|
| 电商项目 | `jupyter-live-kernel`, `github-pr-workflow`, `notion`, `obsidian` | 数据分析、代码管理、项目管理、知识积累 |
| 研究项目 | `arxiv`, `llm-wiki`, `obsidian`, `notion` | 文献搜索、知识管理、笔记系统 |
| 开发项目 | `github-pr-workflow`, `test-driven-development`, `systematic-debugging` | 代码开发、测试、调试 |

### 3. 个性设置选项
```yaml
personality: "technical"  # 可选值：
                          # technical - 技术分析
                          # helpful - 友好助手
                          # concise - 简洁回复
                          # creative - 创意方案
                          # teacher - 教学解释
```

### 4. 模型配置
```yaml
model:
  default: deepseek-chat    # 项目专用模型
  provider: deepseek
  base_url: https://api.deepseek.com/v1
```

## 常见问题解决

### 问题1：技能名称不匹配
**症状**：`Error: Unknown skill(s): data-science, github, productivity`

**原因**：配置中使用了类别名称而不是具体技能名称

**解决方案**：
```yaml
# 错误写法
skills:
  - data-science
  - github
  - productivity

# 正确写法（使用具体技能名称）
skills:
  - jupyter-live-kernel      # data-science类别下的具体技能
  - github-pr-workflow       # github类别下的具体技能
  - notion                   # productivity类别下的具体技能
```

### 问题2：配置不生效
**症状**：启动时仍然使用主配置

**解决方案**：
```bash
# 确保正确设置环境变量
export HERMES_CONFIG=$(pwd)/config.yaml
echo "配置文件: $HERMES_CONFIG"

# 验证配置文件存在
ls -la config.yaml
```

### 问题3：飞书通知不工作
**解决方案**：
1. 检查Webhook URL和Secret是否正确
2. 验证网络连接
3. 检查飞书机器人权限设置

## 最佳实践

### 1. 配置版本控制
```bash
# 将项目配置加入版本控制
git add config.yaml
git commit -m "feat: add project-specific Hermes configuration"
```

### 2. 创建启动脚本
创建 `start-hermes.sh`：
```bash
#!/bin/bash
cd ~/project-name
export HERMES_CONFIG=$(pwd)/config.yaml
hermes chat --skills "jupyter-live-kernel,github-pr-workflow,notion,obsidian"
```

### 3. 文档记录
在 `docs/hermes-configuration.md` 中记录：
- 飞书Webhook用途
- 技能选择理由
- 启动方式

### 4. 技能选择指南
选择技能时考虑：
1. **项目需求**：数据分析、代码开发、文档管理
2. **团队习惯**：使用的工具和流程
3. **协作需求**：是否需要共享笔记、任务管理

## 示例配置

### 电商项目配置
```yaml
name: "sea-ecommerce"
personality: "technical"
model:
  default: deepseek-chat
  provider: deepseek
  base_url: https://api.deepseek.com/v1
feishu:
  webhook_url: "https://open.feishu.cn/open-apis/bot/v2/hook/xxx2"
  secret: "secret2"
  verify: true
skills:
  - jupyter-live-kernel    # 用户行为分析
  - github-pr-workflow     # 代码协作
  - notion                 # 项目规划
  - obsidian               # 知识管理
agent:
  max_turns: 100
toolsets:
  - hermes-cli
```

### 研究项目配置
```yaml
name: "research-project"
personality: "teacher"
model:
  default: deepseek-chat
  provider: deepseek
  base_url: https://api.deepseek.com/v1
feishu:
  webhook_url: "https://open.feishu.cn/open-apis/bot/v2/hook/xxx3"
  secret: "secret3"
  verify: true
skills:
  - arxiv                  # 文献搜索
  - llm-wiki              # 知识库
  - obsidian              # 笔记系统
  - notion                # 论文管理
agent:
  max_turns: 120
toolsets:
  - hermes-cli
```

## 验证配置

启动后检查：
1. 正确的技能已加载
2. 飞书测试消息能正常接收
3. 工作目录正确设置

```bash
# 测试飞书通知
curl -X POST -H "Content-Type: application/json" \
  -d '{"msg_type":"text","content":{"text":"Hermes配置测试"}}' \
  YOUR_WEBHOOK_URL
```

## 总结

项目专用Hermes配置提供了：
- ✅ **通知隔离**：不同项目使用不同的飞书机器人
- ✅ **技能定制**：根据项目类型加载相关技能
- ✅ **配置独立**：项目配置与代码一起管理
- ✅ **易于维护**：配置变更只影响当前项目

这种方法适合需要特定工具集和通知渠道的项目开发场景。