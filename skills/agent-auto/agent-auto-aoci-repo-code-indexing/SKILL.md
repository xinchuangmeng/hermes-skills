---
name: AOCI仓库级代码索引 — 让LLM一次读取理解全仓库
description: 基于arXiv 2605.02421论文的符号-语义索引方法（AOCI）。创建结构化仓库蓝图，让LLM单次读取即可理解整个代码库架构、依赖和设计决策。比主流Agent工具节省4-130倍token消耗。
tags: [agent, code-understanding, repo-indexing, LLM-context, AOCI, context-efficiency]
trigger: 当Agent需要理解大型代码仓库（数百文件以上）、进行跨模块重构、或进行全仓库级别的代码分析时
---

# AOCI仓库级代码索引 — 符号-语义双维度

## 核心概念
AOCI（AI-Oriented Code Indexing）是一种双维度仓库表示方法：
- **符号维度（Symbolic）**：架构坐标——文件层级、模块依赖、架构角色
- **语义维度（Semantic）**：功能描述、依赖关系、约束条件

两者组合形成**结构化蓝图**，LLM可以一次读取就获得完整仓库级理解。

## 操作步骤

### 1. 创建AOCI索引（用于Hermes Agent）

在项目根目录创建 `.aoci.yaml` 或 `.repo-blueprint.md`：

```yaml
# .aoci.yaml
version: 1.0
project: "your-project-name"

encoding_rules:
  - rule: "每个文件/数据库表生成一条索引条目"
  - rule: "每对包含符号标签 + 语义内容"
  - rule: "维护协议：增量更新，仅改动文件重新生成"

entries:
  - name: "src/agents/hermes_agent.py"
    symbolic:
      layer: "core-agent"
      depends_on: ["src/utils/", "src/llm/"]
      role: "主Agent引擎"
    semantic:
      function: "管理Agent的完整生命循环"
      key_classes: ["HermesAgent", "AgentLoop"]
      constraints: "依赖 config.yaml 中的provider配置"
      key_decisions: "使用工具调用模式而非流式输出"

  - name: "src/config/config_manager.py"
    symbolic:
      layer: "infrastructure"
      depends_on: []
      role: "配置中心"
    semantic:
      function: "加载和验证 .env 和 config.yaml"
      key_classes: ["ConfigManager"]
      constraints: "必须在Agent启动前完成初始化"
```

### 2. 使用AOCI提示Agent理解仓库

在system prompt或上下文中加上：

```
## 仓库蓝图（AOCI索引）
我已提供项目的AOCI索引，包含：
- 每个代码单元的符号定位（层、依赖、角色）
- 语义描述（功能、类、约束）
- 架构设计决策记录

在开始任务前，先阅读这个索引理解项目结构。
如果任务涉及修改代码，参照索引中的约束和设计决策。
```

### 3. 增量维护
当代码变更时，仅更新变更文件的索引条目：
```bash
# 检查哪些文件变了
git diff --name-only HEAD
# 只更新这些文件的AOCI条目
# 保持索引与代码一致
```

### 4. 与现有工具对比
| 方法 | Token消耗 | 理解质量 | 可维护性 |
|------|-----------|---------|---------|
| 传统RAG | 中 | 中（结果不稳定） | 差 |
| Agent自主探索 | 高（4-130x） | 高但慢 | 差 |
| AOCI索引 | 极低 | 高（稳定） | 好（增量维护） |

## 注意事项
- ⚠️ AOCI不是自动生成的——需要人工或Agent维护
- ⚠️ 索引需要与代码保持同步，否则会误导Agent
- ⚠️ 适合100+文件的中大型项目，小项目收益不明显
- ⚠️ 符号标签的命名要一致，不要随意发明新标签
- ⚠️ 在Agent执行复杂任务前先读取AOCI，而不是边读代码边决策

## 参考
- arXiv:2605.02421 "AOCI: Symbolic-Semantic Indexing for Practical Repository-Scale Code Understanding with LLMs"
- 论文实验：4个项目 x 3个LLM x 6种上下文条件 = 2160次评估；AOCI在所有可部署baseline中排名第一
