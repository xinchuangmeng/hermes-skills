---
name: learning-hermes-agent
description: Complete guide to learning Hermes AI Agent from scratch - discovery methods, progressive learning path, and effective usage patterns
tags: [hermes, learning-path, ai-agent, beginners, documentation, teaching]
author: Hermes Agent
created: 2026-04-20
version: 1.0.0
---

# Learning Hermes AI Agent

## Overview

This skill provides a structured approach to learning Hermes AI Agent from zero to proficient usage. It focuses on discovery-based learning, practical application, and developing effective mental models for working with Hermes. Special attention is given to Chinese-speaking learners and entrepreneurial applications.

## When to Use

Use this skill when:
- You're new to Hermes and want to learn effectively
- You need to teach someone else how to use Hermes
- You want to discover undocumented features or capabilities
- You're stuck and need to learn how to learn the system
- You're a Chinese speaker needing English command translations
- You want to use Hermes for entrepreneurial purposes

## Core Learning Principles

### 1. Discovery-Based Learning
Hermes is best learned through exploration, not just reading documentation. The system teaches you about itself through interaction.

### 2. Error-Driven Progress
Errors are learning signals, not failures. Each error reveals system boundaries and capabilities.

### 3. Progressive Complexity
Start with simple commands, then combine tools, then create workflows, then automate processes.

### 5. Language Bridge Learning
For Chinese speakers: Learn commands by function, not translation. Create personal glossaries and use visual memory aids (✓ = 正常, ✗ = 未配置).

### 6. Entrepreneurial Focus
Learn skills in the context of startup needs: research, planning, execution, and automation.

## Learning Path (7-Day Plan)

### Day 1: Foundation & First Contact (Chinese-Friendly Version)
**Goal**: Understand what Hermes is and complete your first task

#### Phase 1: Cognitive Foundation (1 hour)
1. **System Discovery with Translation**
   ```bash
   hermes --help
   hermes version
   ```
   - Learn: Hermes是AI智能体平台，不是聊天机器人
   - Key distinction: 具有自主执行任务能力
   - Command translations:
     - `hermes chat` = 聊天模式
     - `hermes status` = 状态检查  
     - `hermes version` = 版本信息
     - `hermes skills list` = 技能列表

2. **Environment Assessment**
   ```bash
   ls ~/.hermes/
   hermes status  # 重点理解输出中的符号：✓=正常，✗=未配置
   ```
   - Discover installed components
   - Understand status symbols: ✓ (working), ✗ (not configured)

3. **Documentation Discovery**
   - Check local skill documentation: `~/.hermes/skills/*/SKILL.md`
   - Use `skills_list()` and `skill_view()` to explore
   - Read skill docs as learning material (they're use case demonstrations)

#### Phase 2: First Operations (2 hours)
1. **Complete a Real Task in Chinese**
   - Choose a simple, concrete need (文件操作, 信息搜索, etc.)
   - Let Hermes help you with it using Chinese instructions
   - Observe the process: 命令 → 工具选择 → 执行 → 响应

2. **Tool Exploration**
   - Try 3 different tool types (file, terminal, search)
   - Note patterns in how Hermes uses tools

3. **Skill System Introduction**
   ```bash
   hermes skills list
   ```
   - Understand skills as packaged expertise
   - Install and test one practical skill
   - **Entrepreneurial focus**: Start with arXiv (research) or GitHub PR (collaboration)

#### Phase 3: Integration & Reflection (1 hour)
1. **Create Learning Notes in Chinese**
   - Document what you learned
   - List questions for tomorrow
   - Create a "我的Hermes使用笔记" file

2. **Plan Next Steps**
   - Identify 3 features to explore tomorrow
   - Set specific learning goals
   - Consider entrepreneurial applications

### Day 2-7: Progressive Mastery with Entrepreneurial Focus
- **Day 2**: Tool combinations and basic workflows (创建学习计划目录)
- **Day 3**: Skill system mastery (安装测试5个创业技能)
- **Day 4**: Memory and session management (记住创业信息)
- **Day 5**: Delegation and subagent workflows (自动化研究流程)
- **Day 6**: Automation with cron jobs (定时市场分析)
- **Day 7**: Complex project implementation (完整创业工具箱)

## Entrepreneurial Skills Testing Methodology

### 5 Essential Skills for Startups

1. **Linear** (Project Management)
   - Status: Requires API key
   - Test: Check if `LINEAR_API_KEY` is set
   - Use case: Team task management, product roadmap

2. **Notion** (Knowledge Management)
   - Status: Requires API key  
   - Test: Check if `NOTION_API_KEY` is set
   - Use case: Business plans, user research, documentation

3. **arXiv** (Academic Research)
   - Status: Ready to use (no API key needed)
   - Test command:
     ```bash
     curl -s "https://export.arxiv.org/api/query?search_query=all:AI+startup&max_results=3"
     ```
   - Use case: Technology research, competitor analysis

4. **Polymarket** (Market Prediction)
   - Status: Ready to use (no API key needed)
   - Test command:
     ```bash
     curl -s "https://gamma-api.polymarket.com/public-search?text=AI&limit=3"
     ```
   - Use case: Market trend analysis, risk assessment

5. **GitHub PR Workflow** (Code Collaboration)
   - Status: Requires GitHub authentication
   - Test: Check if `gh` CLI is installed or `GITHUB_TOKEN` is set
   - Use case: Team coding, CI/CD, version control

### Creating the Entrepreneurial Toolbox

#### Step 1: Create Toolbox Document
```bash
write_file(
  path="~/ai-agent-learning/创业工具箱.md",
  content="# 🚀 My Entrepreneurial Toolbox\n\n[Full content...]"
)
```

#### Step 2: Include These Sections
1. **Skill Summary Table** - 状态,用途,配置需求
2. **Detailed Skill Guides** - 核心功能,配置步骤,应用场景  
3. **Stage-based Application** - 创意验证,产品开发,增长扩张
4. **Action Checklist** - 优先级任务列表
5. **Success Metrics** - 量化目标和定性目标

#### Step 3: Integration Workflows
Create these automated flows:
1. **Research to Execution**:
   ```
   arXiv搜索 → Notion记录 → Linear任务 → GitHub实现
   ```

2. **Market to Product Alignment**:
   ```
   Polymarket趋势 → Notion分析 → Linear规划 → GitHub开发
   ```

### Learning from the System Itself
1. **Observe Hermes' Behavior**
   - How does it choose tools?
   - What patterns emerge in its responses?
   - How does it handle errors?

2. **Reverse Engineer from Examples**
   - Look at how skills are structured
   - Analyze successful task completions
   - Identify best practices from the system's own behavior

## Teaching Methodology

### For Teaching Others
1. **Start with Their Need**
   - Don't teach features; solve their problem
   - Let them see immediate value

2. **Progressive Revelation**
   - Show one capability at a time
   - Build from simple to complex
   - Connect new learning to previous understanding

3. **Error as Teaching Moment**
   - When something fails, explore why
   - Show how to recover and learn
   - Demonstrate system boundaries

4. **Mental Model Development**
   - Teach "commander" mindset
   - Show tool combination patterns
   - Develop intuition for what Hermes can do

### Common Teaching Patterns
```python
# Pattern 1: Problem → Solution → Explanation
"帮我创建一个学习计划目录" → Hermes does it → "看，我用了文件工具和终端工具"

# Pattern 2: Exploration → Discovery → Application
"hermes tools list 能做什么？" → Discover capabilities → "现在用搜索工具试试"

# Pattern 3: Error → Analysis → Learning
"这个命令失败了" → "让我看看为什么" → "哦，需要这样用..."
```

## Common Pitfalls & Solutions

### Pitfall 1: Overwhelming with Theory
**Solution**: Start with practical tasks immediately. Theory comes after practice.

### Pitfall 2: Fear of Errors
**Solution**: Frame errors as learning opportunities. Each error reveals system capabilities.

### Pitfall 3: Isolated Learning
**Solution**: Always connect learning to real needs. Every skill learned should solve a real problem.

### Pitfall 4: Documentation Hunting
**Solution**: Use the discovery methods above. Don't search for docs; let the system reveal them.

### Pitfall 5: Messaging Platform Pairing Issues
**Solution**: Understand the pairing workflow for platforms like Feishu, Telegram, etc.

**Pairing Troubleshooting Checklist:**
1. **Check current pairing status**:
   ```bash
   hermes pairing list
   ```
   - Shows pending requests and approved users
   - If no pending requests, user needs to send `/pair` command in the messaging app first

2. **Review gateway status**:
   ```bash
   hermes gateway status
   hermes gateway start  # If not running
   hermes gateway restart  # If conflicts exist
   ```

3. **Check configuration**:
   - Use `hermes config` to view platform settings
   - Check if `GATEWAY_ALLOW_ALL_USERS` is enabled (bypasses pairing requirement)

4. **Examine logs**:
   ```bash
   hermes logs  # View recent logs
   ```
   - Look for "pairing", "unauthorized", or platform connection errors

5. **Complete pairing workflow**:
   - User sends `/pair` command in messaging app
   - System generates pairing code
   - Admin approves with: `hermes pairing approve <platform> <code>`
   - Example: `hermes pairing approve feishu ABC123`

6. **Common issues**:
   - **Gateway conflicts**: "Another gateway instance is already running" → use `hermes gateway restart`
   - **Already approved**: User appears in approved list but still unauthorized → check platform-specific allowlist settings
   - **No pending requests**: User hasn't sent `/pair` command yet
   - **Configuration issues**: Platform credentials may be missing or incorrect

## Assessment & Progress Tracking

### Daily Checkpoints
- [ ] Completed at least one real task
- [ ] Learned one new capability
- [ ] Documented findings
- [ ] Set tomorrow's learning goals

### Weekly Milestones
- **Week 1**: Can complete basic tasks independently
- **Week 2**: Can combine tools for complex tasks
- **Week 3**: Can teach someone else the basics
- **Week 4**: Can automate workflows

## Advanced Learning Strategies

### 1. Skill Reverse Engineering
- Study how existing skills work
- Identify patterns and best practices
- Create your own skill based on learnings

### 2. Tool Combination Experiments
- Try unusual tool combinations
- Discover emergent capabilities
- Document successful patterns

### 3. System Boundary Testing
- Push Hermes to its limits
- Discover what it can't do
- Understand the "why" behind limitations

### 4. Teaching as Learning
- Explain Hermes to someone else
- Create tutorials or documentation
- Solidify your own understanding

## Key Mental Models

### 1. Hermes as Colleague
Not a tool, but a team member with specific skills.

### 2. Capability-Based Thinking
Focus on what Hermes can do, not just what commands to type.

### 3. Discovery Mindset
The system will teach you if you know how to learn from it.

### 4. Error as Signal
Every failure contains information about system boundaries.

## Quick Start Commands

```bash
# First 5 commands to run
hermes --help                    # See all capabilities
hermes tools list               # See available tools
hermes skills list              # See available skills
ls ~/.hermes/skills/            # Explore skill documentation
hermes chat                     # Start interactive session
```

## Success Indicators

You're learning effectively when:
- You can anticipate which tools Hermes will use
- You recover from errors quickly
- You discover new capabilities without being told
- You can explain Hermes to someone else
- You solve real problems faster than before

## Related Skills
- `ai-agent-learning-path` - General AI agent development learning
- `writing-plans` - Creating implementation plans
- `subagent-driven-development` - Working with delegation

---

*Remember: The best way to learn Hermes is to use Hermes. Start with a real need and let the system teach you.*