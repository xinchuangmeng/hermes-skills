---
name: ResearchAudit Report Generator
description: 生成带错误类型标记的HTML/JSON客户报告，包含7大错误分类系统、严重度分析、原文证据定位和修正建议
trigger: 当需要对论文审计结果生成面向客户的可读报告，或在审计结果中标记错误类型（逻辑性错误、数据问题等）
category: software-development
---

# ResearchAudit Report Generator (v3.1+)

## 前提条件
- ResearchAudit项目路径：`/home/agentuser/projects/researchaudit/`
- 审计引擎正常运行（deep_audit.py + paper_analysis.py）
- DeepSeek API已配置（环境变量DEEPSEEK_API_KEY）

## 错误分类系统（7大类型）

每条issue自动标记以下字段：

| 字段 | 说明 | 可能值 |
|------|------|--------|
| `category` | 错误类型分类 | 结论-实验不匹配 / 引用完整性 / 逻辑矛盾 / 方法问题 / 数据问题 / 过度声明 / 遗漏重要内容 |
| `severity` | 严重程度 | critical (🔴) / major (🟠) / minor (⚪) |
| `fix_suggestion` | 修正建议 | 具体可操作的修订建议文本 |
| `source_mark` | 原文段落标记 | `[第X段]` 格式，回源到原文 |

## 使用方式

```bash
cd /home/agentuser/projects/researchaudit

# 生成HTML客户报告（浏览器打开）
python3 -m researchaudit.cli --mode paper --report html paper.txt

# 生成带错误分类的JSON报告（程序读取）
python3 -m researchaudit.cli --mode paper --report json-rich paper.txt

# 终端默认输出（不变）
python3 -m researchaudit.cli --mode paper paper.txt
```

## 输出文件位置
- HTML报告：`audit_reports/report_YYYYMMDD_HHMMSS_filename.html`
- JSON报告：`audit_reports/report_YYYYMMDD_HHMMSS_filename.json`

## HTML报告功能
- **综合评分仪表盘**：大号数字显示 0-100%
- **严重度分布条**：critical/major/minor 数量 + 色条
- **错误类型热力图**：hover显示每个类型的数量
- **段落热力图**：标注哪个段落问题最多
- **问题详情卡片**：每条issue带 severity色标 + category标签 + 原文证据(段落标记) + 修正建议

## 关键实现文件

| 文件 | 作用 |
|------|------|
| `researchaudit/detectors/deep_audit.py` | LLM提示词含 `category` / `severity` / `fix_suggestion` 字段 |
| `researchaudit/detectors/paper_analysis.py` | `_collect_issue_details()` 传递新字段 |
| `researchaudit/report_generator.py` | HTML报告引擎（深色主题配色） |
| `researchaudit/cli.py` | `--report html\|json-rich` 参数入口 |

## 代价
- 每次审计调用DeepSeek API：约 ¥0.0005
- 报告生成不额外消耗API，纯本地计算
