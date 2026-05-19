# 全流程管线：从需求到上线的12步

源自 Claude Code 三大 Skill（Superpowers + gstack + OpenSpec）的组合工作流。
每步对应一个技能或角色视角。**一人一天干完以前团队一周的活。**

## 12步管线

```
1. 模糊需求 → /office-hours（gstack）         → 需求澄清
2. 思路成型 → /plan-ceo-review（gstack）       → 战略评审
3. 战略通了 → /plan-eng-review（gstack）       → 架构评审
4. 方案需要 → /superpowers:brainstorming       → 头脑风暴
5. 方案定了 → /openspec:propose               → 输出规格
6. UI相关   → /plan-design-review（gstack）    → 设计评审
7. 生成代码 → /openspec:apply                 → 按规格生成
8. 代码审查 → /review（gstack）               → 代码审查
9. 安全检查 → /cso（gstack）                  → 安全审计
10. QA测试  → /qa（gstack）                   → 质量测试
11. 发布    → /ship（gstack）                 → 打包发布
12. 复盘    → /retro（gstack）                → 迭代复盘
```

## Hermes 技能映射

| 步骤 | 原版 | Hermes 等价技能 | 说明 |
|------|------|----------------|------|
| 1 | /office-hours | structured-thinking | 用追问榨干需求，搞清楚到底要解决什么问题 |
| 2 | /plan-ceo-review | structured-thinking + spec-driven-development | CEO视角：核+0心指标是什么？第一版砍50%行不行？ |
| 3 | /plan-eng-review | writing-plans | 工程经理：架构设计、技术方案 |
| 4 | /superpowers:brainstorming | structured-thinking | 多方案对比、边界条件梳理 |
| 5 | /openspec:propose | spec-driven-development（Propose） | API契约、数据模型、异常矩阵、测试用例 |
| 6 | /plan-design-review | structured-thinking | 设计视角：AI生成的UI通常很丑，需要纠偏 |
| 7 | /openspec:apply | subagent-driven-development | 按规格生成代码 |
| 8 | /review | requesting-code-review | 逻辑、命名、测试覆盖、安全 |
| 9 | /cso | requesting-code-review（安全维度） | OWASP + STRIDE 安全审计 |
| 10 | /qa | delegate_task + 测试 | 环境测试 |
| 11 | /ship | terminal | 打包、打tag、推PR |
| 12 | /retro | memory + skill_manage | 每周回顾：什么做对了，流程哪里改进 |

## 核心原则

> **AI不会替你思考流程，它只会执行你定义的流程。你定义得越清楚，它执行得越精准。**

- **不要跳过步骤** — 每个步骤都有存在的理由
- **不是每步都需要** — 改个typo不需要跑12步，但新功能需要
- **顺序不能乱** — 规格没审就写代码=开盲盒
- **先确认再前进** — 每步做完要用户点头才进下一步
