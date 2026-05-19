---
name: PaperTextAnalyzer 原文证据标记（v2 - LLM回源匹配）
description: 对ResearchAudit的PaperTextAnalyzer深度审计结果做原文回源匹配——将LLM返回的每条evidence在论文原文中定位到精确段落（第X段），使用引文精确匹配+关键词重叠模糊匹配双策略
tags: [researchaudit, paper-analysis, evidence, deep-audit, llm, source-matching]
trigger: |
  当需要让PaperTextAnalyzer的深度审计结果显示问题在原文中的具体位置时使用：
  - 用户抱怨"只给分数不给具体位置"
  - 需要给客户展示问题原文出处（审计报告可追溯）
  - 审计结果需要精确段落引用而非模糊描述
  - 代码在 paper_analysis.py 的 analyze() 方法中已有 `_paragraphs` 属性但需要扩展
---

# PaperTextAnalyzer 原文证据标记（LLM回源匹配）

## 核心架构

v3双引擎架构下，深度审计（LLM）返回的 `deep_findings` 每条包含 `evidence` 字段
（LLM提取的触发原文片段）。回源匹配的目标是**将evidence映射到原文段落号**。

```
原文 → 分段编号 → LLM审计（返回evidence）→ 回源匹配 → 输出[第X段]
```

## 新增方法

### 1. `_split_into_paragraphs(text)` — 原文分段

```python
def _split_into_paragraphs(self, text):
    """按空行分割，过滤<20字符的短片段（标题等）"""
    raw_paragraphs = re.split(r'\n\s*\n+', text)
    paragraphs = []
    for i, para in enumerate(raw_paragraphs):
        para = para.strip()
        if len(para) < 20:
            continue
        paragraphs.append((i + 1, para))
    return paragraphs
```

**要点：**
- 段落编号从1开始，方便人类阅读
- 短片段过滤（标题、公式行）避免干扰匹配
- 在 `analyze()` 一开始就调用，存入 `self._paragraphs`

### 2. `_match_evidence_to_source(deep_findings)` — 回源匹配引擎

```python
def _match_evidence_to_source(self, deep_findings):
```

**双策略匹配算法：**

**策略A：引文精确匹配（优先级最高）**
1. 从evidence中提取双引号内的文本 `re.findall(r'"([^"]{15,})"', evidence)`
2. 如果无引文，提取evidence中最长句子作为备选
3. 对每个候选引文，在每个段落中做不区分大小写的子串搜索
4. 匹配得分 = `len(candidate) / len(para_text) * 100`

**策略B：关键词重叠匹配（引文匹配不充分时兜底）**
1. 提取evidence中的关键词（`re.findall(r'\w{4,}', text.lower())`）
2. 提取每个段落的关键词
3. 计算重叠比例：`overlap / len(evidence_keywords)`
4. 得分 = 重叠比例 × 50（权重减半，作为精确匹配的补充）

**匹配门槛：** 得分 ≥ 20 才算匹配成功

**不匹配的情况（正常行为）：**
- "缺少伦理声明" — LLM检测到缺失内容，evidence说的是"缺少"，原文中没有对应文字
- "方法描述太模糊" — 同样是总体判断而非具体引用
- 这类问题不标记段落号，用户自然理解"这是LLM的整体判断"

**匹配成功时，在finding中追加字段：**
```python
finding["source_ref"] = f"第{best_match_idx}段"  # 如 "第8段"
finding["source_excerpt"] = para_text[:100]  # 原文片段预览
```

## 代码集成位置

在 `paper_analysis.py` 的 `analyze()` 方法中：

```python
def analyze(self, text):
    # 1. 原文分段
    self._paragraphs = self._split_into_paragraphs(text)
    
    # 2. 表层扫描（正则）
    ...
    
    # 3. 深度审计（LLM）
    auditor = DeepPaperAuditor()
    deep_findings, cost, error = auditor.analyze(text)
    
    # 4. 回源匹配 — 核心新增
    deep_findings = self._match_evidence_to_source(deep_findings)
    
    # 5. 合并到 issue_evidence（带段落引用）
    for finding in deep_findings:
        source_ref = finding.get("source_ref", "")
        display_issue = issue_text
        if source_ref:
            display_issue = f"{issue_text} [{source_ref}]"
        self.issues.append(f"[深度] {display_issue}")
        self.issue_evidence.append((display_issue, evidence, "deep", severity, category))
```

## CLI 输出修改

在 `cli.py` 的 `print_paper_result()` 中，每个严重级别的循环：

```python
src = f.get("source_ref", "")
src_str = f" [{src}]" if src else ""
print(f"    #{idx} [{cat}] {issue}{src_str}")
```

**输出效果示例：**
```
🔴严重 (3个)
  #1 [结论-实验不匹配] 结论夸大：声称99.7%准确率... [第8段]
    原文: "We achieved 99.7% accuracy on our test dataset..."
  #2 [方法问题] 方法描述模糊... [第5段]
```

## 测试验证

**测试论文片段（10段）：**
- 包含引言、方法论、结果、结论
- 故意埋入"99.7%准确率"、"显著优于"等过度声明

**预期结果（7条全匹配到正确段落）：**
| 问题类型 | 回源段落 | 匹配依据 |
|----------|---------|---------|
| 结论-实验不匹配 | 第8段 | "99.7% accuracy" 引文 |
| 方法问题 | 第5段 | "surface scanning module" 关键词 |
| 数据问题 | 第8段 | "test dataset" 关键词 |
| 过度声明 | 第8段 | "major breakthrough" 关键词 |
| 遗漏重要内容 | 第5段 | "rule detection" 关键词 |
| 引用完整性 | 第2段 | "recent advances" 关键词 |
| 逻辑矛盾 | 第6段 | "regular expressions" 关键词 |

## ⚠️ 常见陷阱

1. **evidence中没有精确引用** — LLM有时只从整体理解中推导问题，不引用原文。此时回源匹配用关键词重叠兜底，但匹配质量取决于关键词密度
2. **段落分割粒度** — 按空行分割可能把同一段落分成多个（如公式前后有空行）。可考虑用句号分割作为备选方案
3. **中英文混合** — 论文可能中英混排，关键词匹配时需 `lower()` 处理
4. **引文提取失败** — 如果LLM的evidence中无引导或无引文，回退到完整句子提取；仍不行的，用evidence整体做关键词匹配
5. **匹配门槛调整** — 20% 门槛在短测试中有效，长论文中可能需降为15%
6. **`self._paragraphs` 生命周期** — 只在 `analyze()` 调用期间有效；如果外部直接调用 `_match_evidence_to_source()` 需先手动设置 `_paragraphs`
7. **不回源也是有效输出** — 缺失性检测（如"缺少伦理声明"）的不匹配是正常行为，不应强行标记段落

## 与旧版（v1）的区别

| 维度 | v1（技能旧内容） | v2（当前实现） |
|------|------------------|----------------|
| 证据来源 | 正则匹配上下文（前后60字符） | LLM evidence回源匹配 |
| 定位方式 | 原文文本片段 | 段落编号（第X段） |
| 匹配算法 | `re.search()` 精确匹配 | 引文精确匹配+关键词模糊匹配 |
| 分类 | 关键词规则（极限词/实验/规范） | LLM自分类（7大维度） |
| 缺失检测 | 关键词回退扫描（精准度低） | 不标记（合理保留） |
| 输出粒度 | 上下文片段截断 | 段落号+原文片段预览 |
