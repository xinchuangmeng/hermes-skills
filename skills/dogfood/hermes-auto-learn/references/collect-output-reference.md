# 采集输出参考 — 2026-05-18（v2，新增连接失败模式）

本文件记录两轮真实采集输出，供后续维护者和LLM cron参考。注意同一日可能有多次执行，模式不同。

## 本轮采集概要（2026-05-19 01:00）— arXiv 空结果（模式B）

```text
=== Auto-Learn: 2026-05-19 ===
Hacker News: 30 items
Dev.to: 10 items
arXiv: 0 items
```

**arXiv诊断：模式B（查询返回0条，非连接失败）。** 今日输出中arXiv部分是空结果而非"Failed to fetch"——说明API请求成功（curl正常返回），但无匹配论文。2026-05-19是星期二，arXiv工作日正常发布，所以不是周末问题。推测3个查询条件过于严格导致匹配数为0。

**输出文件：** 今日`arxiv.md`大小仅247字节，内容为标题行+空行（无Failed to fetch）。`_summary.txt` 最后一行为重复的`0 items`（脚本bug：arXiv计数变量可能被打印了两次）。

## 本轮采集概要（2026-05-18 04:00）

```text
=== Auto-Learn: 2026-05-18 ===
Hacker News: 30 items
Dev.to: 8 items (3个标签为空)
arXiv: Failed to fetch × 3（连接失败，非空结果）
```

## 三种arXiv失败模式的真实案例

| 日期 | 模式 | 输出内容 | 根因 |
|------|------|----------|------|
| 2026-05-18 04:00 | **连接失败** | `* Failed to fetch for query: ...` × 3 | 服务器网络无法reach arXiv |
| 2026-05-17 | 空结果 | 标题行+空行，无Failed字样 | 周末无新论文 + 查询条件严格 |

## 输出文件清单

| 文件 | 大小 | 内容 |
|------|------|------|
| `hackernews.md` | 4.4 KB | 6个话题各5条，共30条HN |
| `devto.md` | 2.5 KB | 5个标签，仅 automation 和 llm 有结果 |
| `arxiv.md` | 247 B | 3条 "Failed to fetch" |
| `_summary.txt` | 186 B | 采集汇总 |

## Hacker News采集详情（2026-05-18）

使用Algolia HN Search API，6个查询词各取top 5：

1. **AI agent** — 5条，最高分2346（AI agent发表抹黑报道）, 953（AI开PR羞辱维护者）, 879（Opus 4.5 Agent体验）
2. **Hermes AI** — 5条，非同名项目为主（金融助手等），相关性低
3. **autonomous agent** — 5条，包含Nous开源框架（155分）、Betting Against Agents（427分）
4. **prompt engineering** — 5条，多个顶级指南（Brex 540分，DAIR.AI 544分，Addy Osmani 464分）
5. **LLM automation** — 5条，分数普遍低（1-3分），质量一般
6. **agentic** — 5条，高分集中：Qwen3.6（1274）、Kiro IDE（1063）、Gemini 2.0（1015）、Vibe coding（787）、Qwen3-Coder（765）

## Dev.to采集详情（2026-05-18）

| 标签 | 结果数 | 说明 |
|------|--------|------|
| `ai-agents` | 0 | ❌ 空（常见） |
| `artificial-intelligence` | 0 | ❌ 空（常见） |
| `automation` | 5 | ✅ 质量中，"4 LLM Workflows That Survive Production" 有价值 |
| `prompt-engineering` | 0 | ❌ 空（常见） |
| `llm` | 5 | ✅ 含"Distilled Gemini tool calling → 26M parameters" 亮点 |

## arXiv采集详情（2026-05-18 04:00）

3个查询，全部返回 "Failed to fetch"：

1. `cat:cs.AI+AND+(agent+OR+autonomous)` → Failed to fetch
2. `cat:cs.CL+AND+(prompt+engineering+OR+LLM+agent)` → Failed to fetch
3. `cat:cs.SE+AND+(AI+agent+OR+automation)` → Failed to fetch

**诊断（区别于"0条空结果"）：** 没有`<entry>`解析失败或parse error，而是curl自身未收到有效HTTP响应。推测为国内服务器对export.arxiv.org的网络访问受限。

## 用户路径偏差（历史遗留）

用户可能给出的脚本路径：
```text
/home/agentuser/.hermes/scripts/learn/auto_learn.sh
```
实际路径：
```text
/root/.hermes/scripts/learn/auto_learn.sh
```
这是系统从 agentuser → root 迁移后的遗留不一致。已在SKILL.md的"坑"区记录。
