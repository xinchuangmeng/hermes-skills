---
name: researchaudit-test-sample-preparation
description: 在腾讯云等受限网络环境中，为ResearchAudit项目准备学术论文测试样本的完整流程
version: 1.0.0
author: Hermes Agent
tags: [ResearchAudit, 测试, 学术论文, 数据集, 网络受限]
---

# ResearchAudit 测试样本准备指南

在**网络受限环境**（腾讯云服务器，GitHub/Docker/部分境外域名访问缓慢）中，为ResearchAudit项目准备学术论文测试样本。

## 问题背景

- 腾讯云服务器访问 arXiv PDF 下载非常缓慢（870KB的PDF需要60秒以上，87%后超时）
- Semantic Scholar API 容易被限流（429错误）
- PubPeer 等网站需要JS渲染，终端无法直接解析
- 但 arXiv API (查询摘要) 可以正常工作（1秒内返回）

## 测试样本需求

ResearchAudit 的5个检测器（逻辑/数据/方法/论文文本/表格验证）需要以下类型的论文：

| 测试类型 | 样本要求 | 数量建议 |
|---------|---------|---------|
| 基准测试 | 顶会高质量论文（NeurIPS/ICML/ICLR） | 2-3篇 |
| 问题检出测试 | 有已知问题的论文（撤稿/低质量） | 2-3篇 |
| 压力测试 | 超长论文（30页+） | 1篇 |
| 格式测试 | 中文论文 / 双栏排版 | 1-2篇 |
| 多领域 | 不同CS子领域 | 3-5篇 |

## 可行的方法

### 方法一：arXiv API 搜索 + 摘要文本（推荐首选）

arXiv API 能正常访问，返回论文元数据（标题、作者、摘要、分类）：

```bash
# 搜索论文（使用已有skil）
python3 ~/.hermes/skills/research/arxiv/scripts/search_arxiv.py "chain of thought" --max 5 --sort date

# 获取单篇论文完整摘要
curl -s "https://export.arxiv.org/api/query?id_list=2305.10601" -o /tmp/paper_meta.xml
python3 -c "
import sys, xml.etree.ElementTree as ET
tree = ET.parse('/tmp/paper_meta.xml')
ns = {'a': 'http://www.w3.org/2005/Atom'}
entry = tree.find('.//a:entry', ns)
title = entry.find('a:title', ns).text.strip().replace('\\n', ' ')
summary = entry.find('a:summary', ns).text.strip()
print(f'Title: {title}')
print(f'Abstract: {summary[:500]}...')
"
```

**优点**：速度快、稳定、无需翻墙
**缺点**：只有摘要文本，无法测试PDF解析、表格提取、双栏布局等

### 方法二：用户手动上传 PDF

用户自己下载论文PDF后上传到服务器：

```bash
# 推荐存放位置
mkdir -p /home/agentuser/test_papers
# 然后将PDF文件放到此目录
```

### 方法三：国内镜像站点下载PDF（不稳定，需测试）

```bash
curl -sL --connect-timeout 10 --max-time 120 -o /home/agentuser/test_papers/paper.pdf "https://arxiv.xilesou.top/pdf/2305.10601"
```

### 方法四：找已知有问题的论文

- **arXiv withdrawn papers**：搜索标题含 "withdrawn" 的论文
- **Retraction Watch 数据库**：https://retractionwatch.com/
- **PubPeer**：需浏览器访问，不适合终端操作
- **Semantic Scholar**：搜索 "retracted" 关键词（注意限流，每次间隔数秒）

## 经典参考论文

### 高质量顶会论文（适合测误报率）

| 论文 | arXiv ID |
|------|---------|
| Attention Is All You Need | 1706.03762 |
| Tree of Thoughts | 2305.10601 |
| Learning Transferable Visual Models From CLIP | 2103.00020 |

## 测试流程建议

1. 用arXiv API搜3篇论文，提取摘要文本
2. 用ResearchAudit检测器跑这些摘要文本
3. 手动下载2篇问题论文，上传到服务器
4. 用检测器跑完整PDF
5. 记录检出率、误报率、漏报率

## 坑点与注意事项

1. **Semantic Scholar 限流**：1次/秒无API Key，超出返回429
2. **arXiv PDF 下载慢**：用 `curl -L --max-time 120` 给足时间
3. **安全策略**：腾讯云对 `curl | python3` 管道命令有安全拦截，建议分两步
4. **PDF损坏**：不完整的PDF需先验证再检测
5. **双栏论文**：PDF解析可能按行读导致文字错乱

## 快速启动命令

```bash
# 1. 创建测试目录
mkdir -p /home/agentuser/test_papers

# 2. 搜索论文
python3 ~/.hermes/skills/research/arxiv/scripts/search_arxiv.py "transformer survey" --max 5

# 3. 获取摘要文本
curl -s "https://export.arxiv.org/api/query?id_list=2305.10601" -o /tmp/paper_meta.xml
python3 -c "
import sys, xml.etree.ElementTree as ET
tree = ET.parse('/tmp/paper_meta.xml')
ns = {'a': 'http://www.w3.org/2005/Atom'}
for entry in tree.findall('.//a:entry', ns):
    title = entry.find('a:title', ns).text.strip().replace('\\n', ' ')
    print(title)
"
```
