---
name: agent-auto-agent-sandbox-transactional-fs
title: "Agent沙箱执行：事务化文件系统（Transactional Sandbox）"
description: "基于Tilde.run的设计理念——给AI Agent一个事务化的隔离沙箱环境，支持版本化文件系统、网络隔离、回滚。每次Agent运行是一个事务：提交或回滚。适用于生产级Agent部署场景，防止Agent误操作破坏生产数据。"
tags: [agent-auto, agent-sandbox, production-safety, rollback, filesystem]
trigger: |
  当需要部署/运行Agent访问真实数据/生产环境时
  当担心Agent误操作（删文件/写脏数据/泄露密钥）时
  当需要审计Agent每一次文件操作时
  设置多Agent共享工作目录的隔离策略
---

# Agent沙箱执行：事务化文件系统（Transactional Sandbox）

## 🎯 适用场景

生产级Agent部署需要考虑的核心问题——如何让Agent访问真实数据但不造成破坏？

| 痛点 | 事务化沙箱方案 |
|------|---------------|
| Agent删了重要文件 | 回滚到上一个commit |
| Agent写入了错误数据 | 整个运行事务不提交 |
| Agent向外泄露数据 | 默认拒绝所有出站连接 |
| 审计Agent操作 | 每个文件变更关联到特定Agent运行ID |

## 🔧 核心设计模式

### 1. 版本化文件系统

Agent的所有文件操作（读/写/删/改）都经过一个版本控制层：

```
Agent运行前                     Agent运行时                    Agent运行后
~/sandbox/          ───→       ~/sandbox/              ───→   ~/sandbox/
├─ code/                        ├─ code/ (版本化)              ├─ code/ (v3)
├─ data/                        ├─ data/ (版本化)              ├─ data/ (v3) 或 回滚到v2
└─ output/                      └─ output/ (版本化)            └─ output/ (v3)
```

### 2. 网络隔离（默认拒绝策略）

```yaml
# 入站：拒绝所有内部网络/云元数据访问
# 出站：白名单制
egress_policy:
  default: deny              # 默认拒绝所有出站
  allowed:                   # 手动添加允许的端点
    - api.openai.com:443
    - api.github.com:443
    - pypi.org:443
```

## 📋 操作步骤

### 方式一：使用专用工具（如 Tilde.run）

```bash
# 1. 安装
curl https://tilde.run/install

# 2. 运行Agent在沙箱中
tilde exec my-project/python:3.12 \
  -- ./agent.py --input /sandbox/data --output /sandbox/reports

# 3. 检查变更
tilde diff my-project  # 查看本次运行的所有文件变更

# 4. 提交或回滚
tilde commit my-project  # ✓ 确认变更
tilde rollback my-project  # ↺ 撤销所有变更
```

### 方式二：用 Docker + Git 自制事务化沙箱

```bash
# 1. 创建版本化工作目录
mkdir -p ~/agent-sandbox && cd ~/agent-sandbox
git init
echo "sandbox/" > .gitignore
mkdir -p sandbox/{input,output,code}

# 2. 每次运行前创建快照
git add -A && git commit -m "pre-run snapshot $(date +%s)"

# 3. 在Docker中运行Agent（只读挂载input，可写挂载output）
docker run --rm \
  -v $(pwd)/sandbox/input:/sandbox/input:ro \
  -v $(pwd)/sandbox/output:/sandbox/output:rw \
  -v $(pwd)/sandbox/code:/sandbox/code:ro \
  --network none \                     # 完全隔离网络
  -e OPENAI_API_KEY="$KEY" \
  python:3.12 python /app/agent.py

# 4. 检查变更
cd ~/agent-sandbox && git diff --stat

# 5. 不满意就回滚
git reset --hard HEAD~1
```

### 方式三：Hermes配置——每次delegate_task前做snapshot

```python
# 在Hermes的自动化工作流中
import subprocess, os

def with_sandbox(agent_task, sandbox_dir="~/agent-sandbox"):
    """包装delegate_task执行，带事务化回滚能力"""
    # 快照当前状态
    subprocess.run(["git", "add", "-A"], cwd=sandbox_dir)
    subprocess.run(["git", "commit", "-m", f"pre-task {os.urandom(4).hex()}"], cwd=sandbox_dir)
    
    try:
        # 执行Agent任务
        result = agent_task()
        return result
    except Exception as e:
        # 出错时自动回滚
        subprocess.run(["git", "reset", "--hard", "HEAD~1"], cwd=sandbox_dir)
        raise e
```

## 💡 最佳实践

1. **每次Agent运行做一次snapshot** — 而不是每个文件写入都版本化。事务粒度=Agent单次运行
2. **默认拒绝网络** — 大多数Agent不需要网络访问，即使需要也只开放特定域名
3. **输出目录定期清理** — 版本化文件系统会累积大量历史，设置保留周期（如7天）
4. **审计日志关联AgentID** — 每个文件变更都记录是哪个Agent/哪个运行导致的

## ⚠️ 注意事项

- 事务化沙箱会增加IO开销（~5-10%），Agent运行简单任务时可能不值当
- Git对大文件（>100MB）支持不好，数据文件另做处理
- 网络白名单要定期审查，防止Agent偷偷用新域名泄露数据
- 事务回滚会丢失Agent的所有工作——如果Agent跑了好几个小时的回滚，得确认值得
- 自制方案不如专用工具（Tilde.run/lakeFS）灵活，生产环境建议用专业工具
