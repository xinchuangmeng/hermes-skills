---
name: ResearchAudit 深度LLM论文审计引擎
description: 用LLM（DeepSeek API）替代关键词匹配，实现语义级别的论文深层审计，7维评分体系（研究问题价值/逻辑链条/方法可靠性/数据真实性/引用质量/创新度/结论合理性）+维度雷达图
tags: [researchaudit, llm, deep-audit, paper-analysis, deepseek, v4]
trigger: |
  当需要改进ResearchAudit的论文审计能力时使用，特别是：
  - 用户反馈审计结果太浅（只做关键词匹配）
  - 需要检测结论-实验不匹配、数据泄露等语义问题
  - 需要用LLM做深度审计且控制API费用
  - 需要双层输出（表层结构+深度语义）
  - 需要每个审计维度有可视化的雷达评分和评分解释
  - 需要在问题中找到亮点（不要只骂不夸）
---

# ResearchAudit 深度LLM论文审计引擎（v4）

## 🎯 核心思路

用 **LLM（DeepSeek）** 替代关键词匹配，对论文做7个维度的语义级别深层审计。表层扫描保留（但仅做结构/引用统计），深度审计由LLM完成。

**为什么有效**：真正的问题论文的问题不会写在表面——不是非要说"perfect"才叫过度声明，不是非要写"100 samples"才叫过拟合。LLM能理解上下文。

**v4升级要点**：
1. 7维评分体系（研究问题价值/逻辑链条完整性/方法可靠性/数据真实性/引用质量/创新度/结论合理性）
2. 每条问题带 `confidence` 置信度(0~1.0)
3. 每个维度有0-10分 + 评分依据解释
4. 正面评价（`strong_points`，解决"只骂不夸"痛点）
5. CLI输出7维雷达图可视化
6. 综合评分引入维度分调整机制

## 🏗️ 架构

```
paper_analysis.py (PaperTextAnalyzer)
│
├── analyze() 
│   ├── 原文分段（供回源匹配）
│   │   └→ _split_into_paragraphs() → self._paragraphs = [(idx, text), ...]
│   │
│   ├── 表层扫描（正则）← 轻量、100%可靠
│   │   ├── _check_structure()       — 章节完整性
│   │   ├── _check_references()      — 引用数量和自引用
│   │   ├── _check_claims()          — 绝对化语言提示（仅提醒，不扣分）
│   │   ├── _check_language()        — 句子长度、词汇去重
│   │   └── _check_ethics()          — 伦理/可复现性声明
│   │   └→ base_score = 加权平均
│   │
│   ├── 深度审计（LLM）
│   │   └→ deep_audit.py (DeepPaperAuditor)
│   │       ├── 分块（按章节分段，每块≤3000字符）
│   │       ├── 调用 DeepSeek API（7个审计维度 + 维度分 + 置信度）
│   │       ├── 多chunk summary合并（取平均值）
│   │       └── 去重合并
│   │       └→ findings[]: {issue, evidence, severity, category, fix_suggestion, confidence}
│   │       └→ summary: {dimension_scores, score_explanations, strong_points}
│   │
│   ├── 原文回源匹配
│   │   └→ _match_evidence_to_source() → 每条finding附加 source_ref（第X段）
│   │
│   └── 综合评分 = base_score − 深度扣分 + 维度分调整
│       ├── critical扣15%, major扣8%, minor扣3%, 上限扣60%
│       └── 维度分调整: (d_score - 5.0) * 0.01, 取平均, 范围[-0.05, +0.05]
│
└── cli.py
    ├── 头部：综合评分+基础分+表格数
    ├── 7维雷达图（柱子可视化 0-10/10）
    ├── ⭐ 亮点展示（来自LLM的正面评价）
    ├── 深度审计区：按严重程度分组（critical/major/minor）
    │   └── 每条带[原文段落]，原文证据，分类标签
    └── 改进建议区
```

## 🔨 关键代码

### 1. 深度审计引擎 (deep_audit.py)

核心system prompt（v4版）：

```
你是一位顶会审稿人（AC/Area Chair级别），正在对一篇论文做深度审计。
请仔细阅读论文内容，找出以下7大维度的深层问题（不是表面关键词问题）：

**审计维度：**

1. **研究问题价值**
   - 研究问题是否清晰定义？解决的问题是否真实存在/有意义？
   - 论文是否充分motivate了为什么这个问题重要？

2. **逻辑链条完整性**
   - 从引言→方法→实验→结论的推理链条是否完整？
   - 是否有未经解释的逻辑跳跃？前提到结论是否自洽？

3. **方法可靠性**
   - 方法设计是否有明显缺陷/漏洞？Baseline选择是否公平合理？
   - 评估指标是否适合任务？是否有消融实验支撑设计选择？

4. **数据真实性（初步判断）**
   - 数据集来源和规模是否明确？数据集是否适合该任务？
   - 是否有数据泄露风险（训练/测试重叠）？样本量是否足够支持结论？

5. **引用质量**
   - 关键概念/方法是否缺失引用？是否遗漏重要相关工作？
   - 是否有过度自引嫌疑？引用的时效性是否合理？

6. **创新度**
   - 声称的创新点是否真实有新意？与现有方法相比的实质性差异是什么？
   - 是"提出来一个新方法"还是"应用现有方法到新场景"？

7. **结论合理性**
   - 结论是否有充分的实验数据支撑？是否有过度声明/过度泛化？
   - 是否讨论了局限性？

额外检测：语言客观性 — 是否使用情绪化/绝对化语言

输出JSON格式（只输出JSON，不要其他文字）：
{
  "findings": [
    {
      "issue": "问题描述（中文，具体且可操作）",
      "evidence": "触发该问题的原文片段（精确摘录）",
      "severity": "critical/major/minor",
      "category": "研究问题价值/逻辑链条完整性/方法可靠性/数据真实性/引用质量/创新度/结论合理性/语言客观性",
      "fix_suggestion": "具体修改建议（中文）",
      "confidence": 0.0~1.0
    }
  ],
  "summary": {
    "strong_points": ["正面评价1", "正面评价2"],
    "dimension_scores": {
      "研究问题价值": 0~10,
      "逻辑链条完整性": 0~10,
      "方法可靠性": 0~10,
      "数据真实性": 0~10,
      "引用质量": 0~10,
      "创新度": 0~10,
      "结论合理性": 0~10
    },
    "score_explanations": {
      "研究问题价值": "具体评分依据...",
      ...
    }
  }
}
```

### 2. 关键实现细节

**分块策略**：超过**6000**字符（v5从3000增大）的论文按章节边界（`^(\\d+\\.?\\s*[A-Z])`）切割，避免token溢出。增大chunk_size减少分块数有两个好处：(1)降低多chunk合并时的分数偏差，(2)减少API调用次数节省费用。注意：如果只有摘要文本（5000-6000字符），增大后单块即可容纳整篇，不再切分，LLM评分更准确。

**JSON解析容错**（三层回退）：
1. 直接 `json.loads()`
2. 提取 `\`\`\`json ... \`\`\``
3. 提取 `{...}` 花括号块

**去重**：用 `issue[:50].lower() + "|" + evidence[:80]` 做key去重。

**无API Key时**：设置 `has_deep_audit = False`，仅展示表层扫描结果，不崩溃。

### 3. 综合评分逻辑（v5 — 经过实证调优）

**核心设计原则：** 分数主要由 LLM 专家的7维打分决定，发现扣分只做轻微标记调整。经过3轮试错得出的公式（见下方踩坑记录）。

```python
# 当前生产公式（v5 final）
dim_avg = 7个维度的平均分（0-10制）     # LLM专家意见，60%+权重
severity_scores = {"critical": 0.5, "major": 0.2, "minor": 0.05}
penalty_10 = sum(s.count * severity_scores[s] for s, count in severity_counts.items())
penalty_10 = min(3.0, penalty_10)          # 扣分上限3分（10分制）
surface_bonus = (base_score - 0.5) * 1.0   # 仅当base>0.5时，给表层完整性小奖励
score_10 = max(0.5, min(10.0, dim_avg - penalty_10 + surface_bonus))
overall_score = score_10 / 10.0            # 0-1制，前端×100得百分制
```

**为什么这样设计（踩坑记录 — 3轮试错实证）：**

- **❌ 旧方案1（v4原始）：** `base_score - deep_penalty + dim_bonus`，每个minor扣3%基础分，critical扣15%。结果：问题论文9/100，良好论文也19/100 — 完全无区分度。根本原因：LLM对任何论文都能找出6-8条问题，扣分把分数全部压到下限。
- **❌ 旧方案2：** 维度分占70%权重 + 扣分每个critical -20分（百分制）。结果：良好论文有2个critical也被打到0分，问题论文和良好论文分数完全无法区分。根本原因：扣分权重太大，抹杀了维度分的差异。
- **✅ 最终方案（v5）：** 维度分为主(60%+)，扣分只做**轻微**调整（每个critical -0.5/10而非-2/10），且设上限3分（10分制）。保持LLM专家的判断主导。

**关键教训：扣分必须设上限。** LLM的"挑刺"行为是工具本身特性——即使良好论文也有1-2个critical。扣分上限防止了critical数量多时分数崩盘，让维度分（LLM的专家评估）成为主导因素。

**实测验证：**
| 论文类型 | 维度均分 | 发现 | 综合得分 | 语义 |
|---------|---------|------|---------|------|
| 问题论文 | 0.3-1.0 | 6c+2m | **5-8/100** | 很差 ✅ |
| 良好论文 | 5.0-6.5 | 1c+3m+2mn | **40-50/100** | 有改进空间 ✅ |
| 优秀论文(模拟) | 7.5-8.5 | 0-3mn | **75-85/100** | 好 ✅ |
| 理想论文(模拟) | 9.0+ | 0 | **90+** | 优秀 ✅ |

**重要：** 分数是越高越好。前端直接 `score * 100` 展示即可，不需要翻转。

### 4. CLI双层输出（v4含雷达图+亮点）

```python
def print_paper_result(result, args=None):
    # 1. 头部：综合评分 + 基础结构分
    score_icon = "🟢" if score >= 0.7 else ("🟡" if score >= 0.5 else "🔴")
    print(f"{score_icon} 综合质量评分: {score:.2%}")
    print(f"  基础结构分: {base_score:.2%}  |  {tables_found} 个数据表格")
    
    # 2. 7维雷达图（如果LLM提供了维度分）
    deep_summary = result.get("deep_summary", {})
    dimension_scores = deep_summary.get("dimension_scores", {})
    for dim_name, dim_score in dimension_scores.items():
        bar = "█" * max(1, int(dim_score)) + "░" * (10 - int(dim_score))
        print(f"  {icon} {dim_name}: {bar} {dim_score:.1f}/10")
    
    # 3. 亮点展示
    for point in strong_points:
        print(f"    • {point}")
    
    # 4. 深度审计区块（按严重度分组）
    for severity in ["critical", "major", "minor"]:
        items = [f for f in deep_findings if f["severity"] == severity]
        # 展示：分类标签 + 问题描述 + 原文证据 + [第X段]
    
    # 5. 表层扫描
    # 6. 改进建议
```
- 严重问题带 `confidence` 显示（0~1.0）
- 每条问题带 `source_ref`（在原文的第几段）
- `-v` 模式下展示每个维度的评分依据 (`score_explanations`)

## 🧪 测试方法

```bash
# 样本3（问题论文）— 应检出8-12个深度问题
python -m researchaudit.cli --mode paper sample3_flawed_research.txt

# 样本2（数据污染）— 应有6-8个合理问题
python -m researchaudit.cli --mode paper sample2_data_contamination.txt

# 样本1（顶会摘要版）— 误报偏高（仅摘要时），完整论文则低
python -m researchaudit.cli --mode paper sample1_tree_of_thoughts.txt
```

## 💰 费用控制

- DeepSeek API：输入¥0.14/百万token，输出¥0.28/百万token
- 每篇论文（~3000词）约 **¥0.0005~0.0006**
- **1分钱能审20篇论文**
- 超过3000字符按章节自动分块

## ⚠️ 常见坑

1. **JSON解析**：LLM有时输出带markdown包裹的JSON，必须做容错解析。v4增加了带severity+evidence+fix_suggestion+confidence的结构。
2. **去重**：同一问题如果跨chunk检出，用 issue[:50] + evidence[:80] 做key去重。
3. **无API Key时**：设置 `has_deep_audit = False`，只展示表层结果，不要崩溃。
4. **长论文token溢出**：按章节边界切割，每块≤**6000**字符（v5从3000增大，减少分块数）。
5. **摘要vs完整论文误报**：用户测试时如果只传摘要而非完整论文，LLM会按完整论文标准审，产生高误报。这是预期行为，应向用户解释。
6. **summary字段合并**：多chunk时，`dimension_scores`取平均值，`strong_points`去重拼接。使用 `_merge_summaries()` 方法。
7. **4-tuple返回**：`analyze()` 现在返回 `(findings, cost, summary, error)` 4-tuple，不是之前的3-tuple。调用方需相应更新。
8. **parse_json_response也返回summary**：`_parse_json_response()` 返回 `(findings, summary)` 二元组，不只是findings列表。
9. **维度评分范围**：LLM可能输出超出0-10范围的分数（小数或整数），在显示和计算时要做 clamp/min(max())。
10. **`severity_counts`不在deep_summary里**：`deep_summary` 只包含 `dimension_scores`、`score_explanations`、`strong_points`。`severity_counts` 需要在 `run_audit()` 层自己计算。前端的 `renderPaperResults()` 读 `data.severity_counts` 作为顶层字段，确保在API返回中作为顶层字段提供。
11. **⚠️ 类变量污染（关键 Bug！）**：`_merge_summaries()` 中 `_score_accumulator` 和 `_score_count` 用 `hasattr(self, ...)` 动态创建，这导致它们成为**实例变量**，但如果在 `__init__()` 中初始化后又被 `analyze()` 中硬编码的 `hasattr` 守卫跳过，**跨 `analyze()` 调用会残留旧值**。修复方法：在 `__init__()` 中初始化为空dict，在 `analyze()` 开头显式重置为全0。示例：
    ```python
    # __init__中：
    self._score_accumulator = {}
    self._score_count = {}

    # analyze()开头（关键！）：
    dims = ["研究问题价值", "逻辑链条完整性", ...]
    self._score_accumulator = {d: 0.0 for d in dims}
    self._score_count = {d: 0 for d in dims}
    # 然后_merge_summaries()中直接用self._score_accumulator[d] += val，
    # 不再用hasattr守卫
    ```
    后果：不修复的话，第二次 `analyze()` 调用时累加器延续第一次的值，导致分数混乱。典型表现：第一次调用全正常，第二次维度分全部偏低或偏高。
12. **`patch` 工具转义破坏**：用 Hermes 的 `patch` 工具修改含 `"""` 三引号 docstring 的 Python 文件时，工具会错误转义引号为 `\"`。如果出现 `SyntaxError: unexpected character after line continuation character`，说明 docstring 被破坏了。修复方法：用 `write_file` 完整重写文件，或用 Python 脚本 `content.replace('\\\\"', '"')` 恢复。
13. **`_chunk_text` 中 section_pattern 正则被破坏后症状**：如果正则表达式中的 `\n` 被错误的全局替换破坏（如变成了字面反斜杠+n），`_chunk_text` 会把整篇论文作为一块返回，不会切分。这通常无害但会浪费token。验证方式：打印 `len(chunks)`，如果是1但论文长度>6000，说明正则已损坏。
