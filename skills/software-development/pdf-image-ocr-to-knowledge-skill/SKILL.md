---
name: pdf-image-ocr-to-knowledge-skill
title: 图片型PDF批量OCR并沉淀为技能的完整工作流
description: 当收到扫描件/图片型PDF（文字不可直接提取）时，用pdftoppm转PNG→delegate_task并行vision_analyze批量OCR→结构化整理数据→创建skill+存memory的完整流水线。解决pdftotext失效、单次vision超时、上下文溢出三大问题。
category: software-development
---

# 图片型PDF批量OCR并沉淀为技能的完整工作流

## 适用场景

用户发来一份PDF文档（Shopee市场报告/行业研报/产品目录等），要求：
1. ✅ 提取内容
2. ✅ 沉淀为可复用技能
3. ✅ 关键数据存记忆

**前提**：PDF为扫描件/图片型（pdftotext只抓到碎片则判断为图片型PDF）。

## 工作流

### Step 1：诊断PDF类型

```bash
pdftotext -layout input.pdf /tmp/output.txt
wc -l /tmp/output.txt
```

- 输出<200行且多为乱码/空白 → **图片型PDF**，走本流程
- 输出>200行且内容完整 → 文字型PDF，直接走 `read_file` + 结构化

### Step 2：转PNG图片

```bash
mkdir -p /tmp/pdf_pages
pdftoppm -png -r 200 input.pdf /tmp/pdf_pages/page
ls /tmp/pdf_pages/ | wc -l  # 确认页数
```

**参数说明**：
- `-r 200`：分辨率200dpi（够用又不太大，约2-3MB/页）
- 文件名格式：`page-01.png`、`page-02.png`...

### Step 3：delegate_task 并行OCR

**关键设计**：不要自己在主上下文中一个个调用vision_analyze（23页会超时+爆上下文）。使用delegate_task将所有页面传给子agent，让子agent独立完成逐页OCR。

```python
# 传给子agent的context格式
context = f"""
图片文件路径格式：/tmp/pdf_pages/page-01.png 到 /tmp/pdf_pages/page-NN.png
PDF是中文的XXX报告
第1页是封面，实际内容从第2页开始
每页用 vision_analyze 分析，输出完整文本
"""
```

**toolsets**：只传 `["vision"]`（子agent不需要终端或搜索）

**注意事项**：
- 子agent有可能遇到429限流（vision有调用频率限制），需要重试机制
- 部分页面可能OCR失败（如纯图表/纯图片页），子agent会自行处理
- 设置 `max_iterations=50` 或更高（23页至少需要23次vision调用）

### Step 4：整理结构化数据

从OCR结果中提取关键字段，按以下模板组织：

```markdown
## 一、XXXX（章节）

### 核心数据

| 指标 | 数值 | 来源 |
|------|------|------|
| ... | ... | ... |

### 关键洞察
- ...
```

### Step 5：创建技能

```bash
skill_manage(action='create', 
  name='市场/项目名-ecommerce-market-guide', 
  category='business',
  content='...完整SKILL.md内容...')
```

**技能结构**（参考thailand-ecommerce-market-guide）：
- 源信息（出品方、日期、页数）
- 核心数据速查表（方便快速查阅）
- 按章节组织（基础信息→市场规模→基础设施→人口特征→品类→竞争格局→营销节点→实操指南）
- 数据来源说明

### Step 6：存记忆

关键数据压缩成一条记忆（控制在300字内），替换旧/不重要的条目。

## 常见陷阱

| 问题 | 现象 | 解决方法 |
|------|------|---------|
| **记忆空间满**（2,200上限） | memory()返回超过上限错误 | 先replace删除过时/不重要的旧条目，再add新的 |
| **vision 429限流** | vision_analyze返回429 | delegate_task子agent可以自动重试，或在主上下文分批进行（每次5-10页） |
| **PDF页数多** | 23页以上，单次处理超时 | delegate_task并行是唯一可行方案，不要在主上下文里逐页调 |
| **pdftoppm Syntax Warning** | "Invalid Font Weight"等 | 不影响转换结果，忽略 |
| **OCR结果不全** | 某些页只有图表无文字 | vision可能漏识别图表数据，可在整理时标注"图表数据未完整识别" |

## 成功案例

- **泰国电商市场概览（Shopee官方报告2024.4）**：23页PDF，OCR耗时约14分钟，成功提取70+数据点，创建 `thailand-ecommerce-market-guide` 技能（10大章节+速查表）
