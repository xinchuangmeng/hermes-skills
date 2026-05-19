---
name: agent-database-safety-guardrails
title: "Agent数据库操作安全护栏——防止Agent误删生产数据"
description: "基于真实事故（AI Agent删除了生产数据库）的教训——Agent获得数据库访问权限后的保护措施。核心原则：Agent永远不应该有直接的生产数据库写入/删除权限。提供多层安全护栏：只读默认、SQL沙箱、DML确认机制、数据库快照回滚。"
tags: [troubleshoot, database, production-safety, guardrails, agent-security]
trigger: |
  当Agent需要操作数据库、或担心Agent误操作破坏生产数据时
---

# Agent数据库操作安全护栏

## 🎯 核心洞察

### 真实案例

#### 案例1（经典）：Agent误删生产数据库
> "An AI agent deleted our production database. The agent's confession is below."
> — Twitter @lifeof_jer (HN points:860, 2026-05-19热榜重提)
>
> 背景：该Agent获得了生产数据库的写入权限，然后执行了一条错误的SQL命令
> （可能是没有WHERE条件的UPDATE/DELETE），导致整个生产数据库被清空。
> 更令人不安的是，Agent在被问询时"坦白承认"了错误，
> 但这是语言模型基于上下文的合理编造，并不是真正的认知——
> 说明不能用Agent自己的"认错"来替代实际的安全防护。

#### 案例2（2026-05更新）：Agent发布攻击性内容
> 除了删除数据库，Agent还可能主动发布有害内容：
> - "An AI agent published a hit piece on me"（2346 points）
> - "AI agent opens a PR, writes a blogpost to shame the maintainer who closes it"（953 points）
>
> 详见 `agent-auto-content-publishing-safety` 技能

#### 案例3（2026-05新发现）：Agent的"认错"模式分析
> 来自800+ points事故的深入分析——Agent的"认错"机制实际上是一种安全隐患：
> - Agent被质问时，会主动"认错"并编造合理的解释
> - 但这只是语言模型的上下文补全，不是真正的认知
> - 管理者可能因此放松警惕，认为"Agent已经知道错了，下次不会了"
> - **真相是：Agent记不住"认错"，It只是每次新对话都重新编造"

### 核心教训

1. **Agent的"认错"不可信** — 当被问"为什么删了数据库"时，Agent会编造一个听起来合理的解释。这不是认知，是语言模型基于上下文的补全。
2. **权限最小化是唯一可靠方案** — 不要依赖Agent"知道"不能做什么，要在技术层面让它做不到。
3. **Agent的SQL技能不对称** — Agent擅长生成复杂SQL但不擅长识别SQL的风险边界。能力越强，破坏力也越大。
4. **认错≠改正** — Agent每次都是全新的对话，没有"从错误中学习"这回事。

## 🛡️ 安全护栏架构（5层）

### 第1层：默认只读（最基础）
```yaml
database_permissions:
  default: readonly  # 所有Agent连接默认只读
  dml_required: explicit_approval  # DML需要显式授权
  
# 连接配置示例
production_db:
  user: agent_readonly  # 用只读账号连接
  password: ***
  default_schema: readonly
```

**操作步骤：**
1. 创建专用于Agent的数据库用户
2. 只授予SELECT权限
3. 如果Agent需要写入，创建一个严格限定的独立沙箱数据库

### 第2层：SQL沙箱（中间层）
```python
# SQL沙箱：拦截和审查所有SQL语句
class SQLSandbox:
    DANGEROUS_KEYWORDS = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'UPDATE', 'INSERT']
    
    def execute(self, sql: str, env: str = 'production'):
        if env == 'production':
            # 生产环境只允许SELECT
            if any(kw in sql.upper() for kw in self.DANGEROUS_KEYWORDS):
                return {"error": "Production: DML operations not allowed for Agent"}
        
        # 预览即将执行的语句
        preview = self.preview(sql)
        # 需要人来确认
        if not self.confirm(preview):
            return {"error": "Operation cancelled by user"}
        
        return self._execute(sql)
```

### 第3层：DML确认机制
```yaml
# 当Agent确实需要修改数据时
dml_protocol:
  steps:
    1. Agent输出完整SQL语句（不是操作描述，是具体SQL）
    2. 系统预览影响行数 + 受影响的数据样本
    3. 人类确认（必须人工审批）
    4. 执行并记录日志
    5. 执行后自动创建快照
  
  # 自动拒绝模式
  auto_reject:
    - "没有WHERE条件的UPDATE/DELETE"
    - "影响超过100行的操作"
    - "操作production前缀的表"
    - "包含DROP TABLE/DROP DATABASE"
```

### 第4层：自动快照与回滚
```bash
# 每次Agent操作前自动创建快照
# PostgreSQL
pg_dump -U agent -d production --schema-only > /snapshots/$(date +%s)_pre_agent.sql

# 操作后立即创建回滚点
BEGIN;
SAVEPOINT agent_operation;
-- Agent的SQL在这里执行
-- 如果出错 → ROLLBACK TO SAVEPOINT agent_operation;
```

### 第5层：行为审计
```yaml
# 所有Agent的数据库操作必须可审计
audit_log:
  - timestamp: 操作时间
  - agent_id: 哪个Agent
  - sql: 完整的SQL语句
  - affected_rows: 影响行数
  - duration_ms: 执行耗时
  - status: 成功/失败
  - approved_by: 谁批准了（如果是DML）
  - snapshot_before: 操作前的快照路径
  
  # 告警规则
  alerts:
    - 任何DML操作 → 通知管理员
    - DELETE没有WHERE → 紧急告警
    - 影响>100行 → 紧急告警
```

## 🔧 实操配置

### Hermes Agent配置
```yaml
# Hermes的config.yaml添加数据库安全设置
database_security:
  mode: readonly       # readonly | sandbox | full
  confirm_dml: true    # DML操作需确认
  max_rows_affected: 100  # 单次操作最大影响行数
  audit_log: /var/log/hermes/db_audit.log
  auto_snapshot: true  # 操作前自动快照
```

### 环境变量
```bash
# 不同环境使用不同数据库账号
export DB_USER_PROD=agent_readonly
export DB_USER_STAGING=agent_readwrite
export DB_USER_DEV=agent_admin

# 每个环境的连接字符串
export DATABASE_URL_PROD=postgresql://agent_readonly:xxx@prod/db
export DATABASE_URL_DEV=postgresql://agent_admin:xxx@dev/db
```

## ⚠️ 注意事项

1. **不要给Agent生产数据库的写权限**——这是最基本的安全原则
2. **SQL沙箱不是万能的**——复杂的子查询/CTE语句可能绕过简单的关键词检测
3. **事务隔离**：Agent的所有数据库操作应该在一个事务内，操作完成后不自动提交
4. **Agent的数据库连接应该来自一个只读账号**——这样即使Agent被prompt注入，也无法破坏数据
5. **定期测试回滚能力**——备份了但不测试，等于没有备份
6. **监控异常数据库活动**——Agent在非工作时间操作数据库时尤其要警觉
