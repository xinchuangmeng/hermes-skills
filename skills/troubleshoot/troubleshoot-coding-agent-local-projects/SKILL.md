---
name: troubleshoot-coding-agent-local-projects
title: "本地AI编码Agent项目排障——9个真实项目的实战教训"
description: "基于Dev.to文章《The Bug Wasn't in the Model: Lessons from 9 Local AI Coding Agent Projects》——9个本地AI编码Agent项目中发现的19种失败模式，全部都不是模型能力问题，而是编排/信息/基础设施层的问题。核心方法：Crystallization Loop（每次失败沉淀为可测试规则）+ 3阶段诊断流水线 + 19种失败模式速查表。适用于所有使用本地LLM做编码Agent的项目。"
tags: [troubleshoot, coding-agent, local-agent, debugging, crystallization-loop]
trigger: |
  当本地AI编码Agent项目遇到失败、测试不通过、或需要系统化排查Agent编码失败原因时
---

# 本地AI编码Agent项目排障实战指南

## 🎯 核心洞察

### 核心发现：19个失败模式，0个是模型问题

> 作者用**同一个45GB Qwen3模型**跑了9个API项目（Apple Silicon M5 Max），自主通过率从0%提升到100%。
> **但模型从来没换过。** 所有失败都是编排/信息/基础设施层的问题。

### 三变量可靠性模型

```
System Reliability ≈ DCR × Information Quality × Engine Quality
```

- **DCR（确定性覆盖率）**：有多少规则/约束被明确编码而非依赖模型理解
- **信息质量**：Context文件、设计文档、API规范的质量
- **引擎质量**：编排器（Orchestrator）本身是否有bug

## 📋 9个关键失败模式及解决方案

### 模式1：没有设计规则 → 0%通过率
**问题**：没有任何确定性脚手架或上下文设计规则时，模型什么也做不了
**解决**：建立**Crystallization Loop（晶体化循环）**——每次失败都沉淀为一个具体、可测试的**Crystallized Lesson (CL) 规则**
```
Project 1: 0条规则 → 0%
Project 9: 43条规则 → 100%
```

### 模式2：模型覆盖共享基础设施文件
**问题**：模型不断覆盖它不该碰的conftest.py、database.py等共享文件
**解决**：基础设施文件（conftest.py, database.py等）**永远不能出现在任务的目标文件列表中**
```
# CL-005: 任务文件白名单
task_targets:
  exclude_patterns:
    - "conftest.py"
    - "database.py"
    - "test_fixtures/*"
  allow_only: ["src/**", "app/**", "tests/**"]
```

### 模式3：DateTime字段静默失败
**问题**：`created_at`使用SQLAlchemy的`default=`设置，但在flush前为None导致测试失败
**解决**：DateTime字段必须在Python的`__init__`中设置，不依赖数据库写入时自动填充
```python
# ❌ 依赖DB默认值
created_at = Column(DateTime, default=datetime.utcnow)

# ✅ 在__init__中手动设置
def __init__(self):
    self.created_at = datetime.utcnow()
```

### 模式4：多Endpoint路由任务导致模型超时
**问题**：一个任务要求添加多个端点时，模型在理解累积的代码上下文时超时
**解决**：每个任务**只包含一个端点**（CL-043）
```
# ❌ 一个任务加3个端点
task: "为User资源添加CRUD端点（list/create/delete）"

# ✅ 拆成3个独立任务
task1: "添加User列表端点 (GET /users)"
task2: "添加User创建端点 (POST /users)"
task3: "添加User删除端点 (DELETE /users/:id)"
```

### 模式5：Pytest告警被误判为失败
**问题**：pytest配置告警被编排器判定为测试失败，但代码本身正确
**解决**：编排器的**门控分类系统**需要区分告警（Warning）和实际失败（Failure）
```
# 测试输出分级处理
test_results:
  pass: ✅ 通过
  warning: ⚠️ 配置告警（不阻赛，记录日志）
  failure: ❌ 实际失败（需要修复）
  error: 🚨 运行时错误（需要修复）
```

### 模式6：非幂等修正——重复应用补丁
**问题**：`client.post(` → `await client.post(` 的替换被应用两次，产生 `await await client.post(` 语法错误
**解决**：**行级幂等性守卫**——如果替换文本已存在于该行，跳过替换（FC-015）
```python
def apply_patch(line, old, new):
    """带幂等检查的补丁应用"""
    if new in line:
        return line  # ✅ 已应用，跳过
    return line.replace(old, new)
```
长期方案：用AST（LibCST）做替换，而非字符串替换。

### 模式7：RED阶段实现泄漏
**问题**：在TDD的Red阶段（只写测试），模型把实现文件也写到了磁盘，导致测试立即通过
**解决**：限制Red阶段的文件写入范围——**只能写测试文件**
```
# RED阶段文件白名单
red_phase_allowed:
  file_patterns: ["test_*.py", "*_test.py", "tests/**"]
  reject_if_not_match: true  # 写非测试文件 → 拒绝/隔离
```

### 模式8：Router注册在重试时丢失
**问题**：`git reset --hard` 重试时，编排器的自动注册修改（main.py的router import）被回滚
**解决**：Router注册放在**初始设置脚本**中完成，不放在TDD循环内
```
# ✅ 正确流程
setup_script:
  - 创建项目骨架
  - 注册router到main.py ← 在这里完成
  - 提交git

tdd_cycle:
  - RED: 写测试
  - GREEN: 写实现
  - REFACTOR: 重构
  # router注册不在TDD内
```

### 模式9：架构复杂度超出引擎能力
**问题**：项目需要多模型外键设置脚本，但编排器当时的架构无法处理
**解决**：**知道什么时候你的引擎架构处理不了项目的复杂度**——直接重新设计基线脚本，不硬撑
```
# 重新设计 vs 硬撑的决策标准
try_to_fix:
  - 如果同一个问题出现3次 → 重新设计基线脚本
  - 如果修复成本 > 重写成本的50% → 重写
  - 如果修复引入了3个以上新条件判断 → 重新设计
```

## 🔧 19种失败模式分类速查

| 类别 | 数量 | 解决方向 |
|------|------|---------|
| PRD设计缺口 | 10 | Crystallized Lesson规则加入设计检查清单 |
| 引擎Bug | 5 | 修复编排器代码+添加测试 |
| 基础设施/安装 | 3 | 标准化安装脚本 |
| 超时/性能 | 1 | 调整超时配置 |

## 🏗️ 三阶段诊断流水线

```yaml
# 遇到Agent编码失败时的诊断流程
diagnosis_pipeline:
  阶段1 — 模式匹配:
    操作: 将失败状态与19种失败模式（CL规则库）匹配
    工具: 不需要LLM，确定性匹配
    结果: 如果匹配 → 应用对应修复
    
  阶段2 — 本地LLM诊断（阶段1无匹配时）:
    操作: 用本地模型分析失败日志，识别新颖失败模式
    输入: 失败上下文 + CL规则库
    输出: 新的失败模式描述 + 修复建议
    
  阶段3 — 人工升级（阶段2失败时）:
    操作: 通知人类审查
    输出: 新的Crystallized Lesson规则，加入规则库
```

## 💡 Crystallization Loop（晶体化循环）实操

```yaml
# 每次Agent编码失败后执行
crystallization_loop:
  步骤1: 分析失败根因 → 不是"模型不够聪明"，而是"缺少了什么规则"
  步骤2: 提炼为CL规则（Crystallized Lesson）
  步骤3: 将CL规则加入设计检查清单或编排器逻辑
  步骤4: 验证新规则可以防止同类失败
  步骤5: 重试被修复的任务
  
  最终状态: 43条CL规则 → 100%通过率（从0%开始）
```

## ⚠️ 注意事项

1. **不要先怪模型**——本地Agent项目90%的失败都不是模型问题，检查编排逻辑/信息质量/基础设施
2. **Crystallization Loop是核心能力**——每次失败都是规则库的补充机会
3. **One-Endpoint-Per-Task是黄金规则**——复杂任务切片到单端点粒度
4. **RED阶段必须隔离**——TDD的Red阶段绝对不要写实现文件
5. **基础设施文件是禁区**——conftest.py、database.py等永远不能出现在任务目标中
6. **幂等性守卫不可少**——字符串替换必须检查是否已应用
7. **Router注册在Setup中完成**——不要放在TDD循环中，否则被git reset会丢失
8. **备份设计是引擎设计的必要条件**——如果编排器架构处理不了项目复杂度，果断重新设计基线
