---
name: search-fallback-baidu-crawl
description: >-
  当Tavily/bimiyun/SearXNG等搜索API全部不可用时(432配额耗尽/网络不通)，
  使用百度搜索直连(urllib)+HTML解析作为最后的搜索保底方案。
  国内直达、无需API Key，适合腾讯云等国内服务器环境。
trigger:
  - "Tavily 432"
  - "搜索API全部不可用"
  - "百度搜索替代方案"
  - "search fallback"
  - "web_search failed"
  - "搜索保底"
  - "首枪窗口"
  - "百度搜索限流"
  - "每日新闻汇总"
  - "新闻聚合"
  - "美股数据"
  - "财经数据采集"
  - "热榜采集"
---

# 搜索全面崩溃时的保底方案（2026-05 实战验证）

## 核心理念

当**所有搜索API + 搜索引擎**全部不可用时（不是某一个挂，是全挂），不要跟死胡同死磕。换个思路：**绕过搜索引擎，直接访问官方源头。**

> **2026-05-09实战发现：** 在腾讯云国内服务器上，Tavily 432耗尽、百度触发验证码、Bing CN被政府限制、DDG/Google网络不可达——但`urllib.request`可以直接访问 tech 公司官方博客(anthropic.com, redis.io等)和 GitHub 仓库，且质量远高于搜索引擎片段。

## 四层递减搜索策略

### 第一层（首选）：直接访问官方源头
直接阅读原始技术博客、论文、产品文档，而非通过搜索引擎间接找。

**打通队列（已验证可直达）：**
- ✅ `anthropic.com/engineering/*` — AI Agent最权威官方来源（注意：Next.js页面，但正文文本可通过 `grep/sed` 从HTML中提取，关键内容在 `<p>` 和 `<h1-3>` 标签中）。**2026-05-15验证：** 成功抓取`anthropic.com/engineering/claude-code-auto-mode`全文，包含完整的Auto Mode架构（两层防御、四类拦截场景、分类器决策标准等）。返回内容约45KB纯文本正文。
- ✅ `redis.io/blog/*` — **直接访问 `.md` 后缀获取完整Markdown原文**（2026-05-13发现！如 `redis.io/blog/ai-agent-architecture.md` 返回纯Markdown，几乎零失真的源文档）
- ✅ `mem0.ai/blog/*` — 上下文工程/Agent记忆
- ✅ `github.com/*` — 开源项目/A2A协议等
- ✅ `modelcontextprotocol.io/*` — MCP官方文档
- ✅ `arxiv.org/*` — 学术论文（PDF也可提取）
- ✅ `www.aboutamazon.com/*` — Amazon AI/电商官方新闻（**v5.13新增：跨境AI工具数据源**）

**案例（2026-05-09 + 2026-05-13 成功获取的核心资料）：**

```
2026-05-13（本次新增 — 跨境AI/电商方向）:  
  https://www.aboutamazon.com/news/retail                     → Amazon零售最新AI功能(Hear the highlights等)
  https://www.aboutamazon.com/news/small-business              → Amazon卖家政策+AI工具更新  
  https://www.aboutamazon.com/search?q=Rufus                   → Rufus AI购物助手相关文章
  https://www.cifnews.com/article/180000                       → 行业资讯（部分可达，内容质量一般）

```
https://www.anthropic.com/engineering/building-effective-agents         → 177KB 完整正文
https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents → 完整正文
https://redis.io/blog/ai-agent-architecture/                            → 585KB 2026架构指南
https://github.com/google/A2A                                            → 完整README+协议说明
https://modelcontextprotocol.io/introduction                             → 303KB 官方文档
https://mem0.ai/blog/context-engineering-ai-agents-guide                → 443KB 完整指南
```

### 第二层：百度全文提取（存在「首枪窗口」：前1-3次查询成功率高，之后限流返回空 → 必须把最高价值查询放在最前面）
### 第三层：行业站直接文章URL提取（cifnews等，成功率约30%，内容质量一般）
### 第四层：纯知识驱动（无搜索源时，依靠训练数据+已有技能做深度整合）

## 场景触发条件

当全部搜索方式不可用时：
1. ❌ Tavily API → 432 error（免费额度耗尽）
2. ❌ 必米云/Bimiyun → 未配置或额度已尽
3. ❌ SearXNG → 国内服务器无代理全部timeout
4. ❌ browser工具 → agent-browser二进制缺失或未安装
5. ❌ Google/Bing via curl → 被墙或JS渲染页面难解析
6. ❌ DuckDuckGo API → 国内网络不可达

## 方案核心A（新增主推）：直接抓取官方技术博客

当所有搜索引擎不可用时，放弃搜索思维，采用**定向抓取**模式：

```python
import urllib.request, re

def fetch_blog(url, keywords_filter=None):
    """抓取官方技术博客全文并提取高价值内容"""
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8', errors='replace')
    
    # 清理HTML
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', '\n', text)
    lines = [l.strip() for l in text.split('\n') if len(l.strip()) > 20]
    
    # 解码HTML实体
    for i, l in enumerate(lines):
        lines[i] = l.replace('&#x27;', "'").replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
    
    if keywords_filter:
        lines = [l for l in lines if any(kw in l.lower() for kw in keywords_filter)]
    
    return lines

# 使用示例：先抓取Anthropic官方博客，再从中提取Agent相关内容
lines = fetch_blog("https://www.anthropic.com/engineering/building-effective-agents")
for l in lines:
    print(l)  # 直接得到完整文章正文，比搜索引擎片段质量高10倍
```

### 可以同时抓的博客列表（已验证可达）

```python
blogs = [
    # AI Agent核心
    "https://www.anthropic.com/engineering/building-effective-agents",
    "https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents",
    # 工具协议
    "https://modelcontextprotocol.io/introduction",
    "https://github.com/google/A2A",
    # 记忆&缓存
    "https://redis.io/blog/ai-agent-architecture/",
    "https://mem0.ai/blog/context-engineering-ai-agents-guide",
]
```

## 方案核心B（备用）：百度搜索爬取

使用Python标准库`urllib.request`直接请求百度搜索，配合中文User-Agent+HTML解析提取搜索结果。

```python
import urllib.request, urllib.parse, re

def baidu_search(query, max_results=5):
    """Search Baidu and extract result snippets"""
    encoded = urllib.parse.quote(query)
    url = f"https://www.baidu.com/s?wd={encoded}&ie=utf-8"
    
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    })
    
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8', errors='replace')
    
    # 方案A: 提取搜索结果标题和URL
    title_pattern = re.findall(r'<h3[^>]*>.*?<a[^>]*href="(https?://[^"]+)"[^>]*>(.*?)</a>', html)
    for url, title in title_pattern[:max_results]:
        title_clean = re.sub(r'<[^>]+>', '', title).strip()
        # url是百度跳转链接，需要使用urllib.parse.unquote解码
        print(f"Title: {title_clean}")
    
    # 方案B: 提取所有可见文本中的关键数据片段
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    
    parts = text.split('。')
    for p in parts:
        if any(kw in p for kw in ['亿', '增长', '市场', '规模', '趋势', '目标关键词1', '目标关键词2']):
            clean = p.strip()
            if len(clean) > 20 and len(clean) < 300:
                print(f"[片段] {clean}")
```

## 具体操作流程

### Step 1: 确认环境网络可达
```python
import urllib.request
try:
    with urllib.request.urlopen("https://www.baidu.com", timeout=5) as r:
        print(f"✅ 百度可达，状态码: {r.status}")
except Exception as e:
    print(f"❌ 百度不可达: {e}")
```

### Step 2: 搜索并提取
如上方代码所示，`baidu_search()`函数一次执行即可完成搜索+提取。

### Step 3: 数据提取技巧

**提取标题和URL：**
```python
# 提取链接（百度跳转链接需解码）
links = re.findall(r'href="(https?://www\.baidu\.com/link\?[^"]+)"', html)
titles = re.findall(r'<h3[^>]*>.*?<a[^>]*href="[^"]*"[^>]*>(.*?)</a>', html)
```

**提取关键数据点：**
```python
# 用关键词锚定提取有意义的数据
for kw in ['亿', '增长', '市场', '落地', '趋势', '规模']:
    parts = text.split('。')
    for p in parts:
        if kw in p and len(p) > 15 and len(p) < 250:
            clean = p.strip()
            if not clean.startswith('// '):  # 过滤JS注释
                print(f"  [{kw}] {clean}")
```

**提取数值数据：**
```python
for pattern in [r'(\d+[.]?\d*\s*亿[^。]{0,100})', r'(增长[率速][^。]{0,80})', r'(CAGR[^。]{0,60})', r'(市场[规模][^。]{0,80})']:
    matches = re.findall(pattern, text)
    for m in matches[:3]:
        clean = m.strip()
```

## 坑和注意事项

### 2026-05-13 实战关键发现：百度搜索完全失效 + 行业站可达性分级

**0. ⚠️ `replace_all=true` 危险提醒：** 当使用 `patch` 工具的 `replace_all=true` 对 ` ``` `（代码围栏）进行批量替换时，会**删除文档中所有的代码围栏**（一个markdown文件可能20+处）。如果只是想删除一行重复的 ` ``` `，一定要使用唯一的`old_string`上下文让它精确匹配，绝不要用 `replace_all=true`。一个safe方法：先 `read_file` 看精确行号，再用 `old_string` 把上下几行一起带上确保唯一性。

**1. ⚠️ 百度搜索存在「首枪窗口」——并非完全不可用，前1-3次查询仍有高成功率**（2026-05-14实战修正）

此前2026-05-13报告百度搜索「基本0%成功率」是错误的推断——实际原因是9次密集查询触发了限流，而非搜索源失效。

修正对比：
- 2026-05-13：连续9次密集查询，全部返回空 → 误判为「搜索源完全失效」
- 2026-05-14：用3次最高价值查询作为「首枪窗口」，3次全部成功（5结果+18片段/5结果+14片段/5结果+12片段）

**结论：百度搜索是可靠的fallback，但一次会话只能最多成功3次。必须把最重要的查询放在最前面。**
- 2026-05-09：百度搜索**部分可用**（约50%成功率，能提取标题和片段）
- 2026-05-10：百度搜索**成功率下降**（约20-30%，大部分触发验证码）
- 2026-05-13：百度搜索**基本0%成功率**（所有查询返回空，未触发验证码但完全不返回结果）

**结论：百度搜索已不再是可靠的fallback方案。** 在这个服务器环境中，百度对urllib请求的屏蔽越来越严格。

**2. 行业网站「可达性」分级（2026-05-13实测）**

```yaml
✅ 完全可达（urllib/curl直连）:
  - aboutamazon.com               # Amazon官方新闻 → 跨境AI工具/卖家政策
  - 163.com (新闻)  /  tech.163.com (科技)   # ⭐新闻门户：curl可直接提取标题和新闻列表，本文每日新闻汇总任务中已验证可靠性最高
  - baidu.com（首页可达，搜索首枪窗口~2次）

⚠️ 部分可达:
  - cifnews.com（雨果网）        # 直接文章URL可达，但搜索/首页JS渲染不可用
  - zhihu.com（知乎）             # 首页可达，搜索403

❌ 完全不可达:
  - 36kr.com                       # 搜索返回空/JS渲染
  - ebrun.com（亿邦动力）         # 302无限重定向
  - sohu.com（搜狐）              # 搜索返回空
  - jianshu.com（简书）           # 编码错误
```

**3. 行业站提取的局限**

即使可达的行业站（如cifnews），提取的内容**质量参差不齐**：
- 首页内容通过JS加载，urllib只能拿到空壳
- 具体文章URL（如/article/180000）可获取，但内容以活动推广为主
- **Amazon官方站的质量远高于行业站** — 直接阅读官方公告和产品发布，零失真

**4. 更新后的搜索策略优先级（全搜索引擎失效时）**

```
第1步: 直接访问官方源头（最高优先级）
  Amazon: aboutamazon.com/search?q=关键词
  AI公司: anthropic.com/engineering/*
  GitHub: github.com/搜索
  成功率: 视具体域名，aboutamazon.com ✅

第2步: 尝试行业站直接文章URL
  雨果网: cifnews.com/article/文章ID（需要提前知道ID）
  成功率: 低，只能碰运气

第3步: 已有知识+合理推断（最后的选项）
  当所有线上搜索全部失效，利用自身训练数据和已有历史技能
  做知识驱动的深度整合，而非数据驱动的研究
  成功率: 取决于已有知识储备，但比空等好
```

**5. 对技能升级工作的影响**

当搜索全面崩溃时，技能升级策略需要从「数据驱动」切换到「知识驱动」：
- **数据驱动（正常模式）**：搜索→收集最新数据→整合更新
- **知识驱动（离线模式）**：依靠已有知识+可访问的少数源→识别新趋势→合理推断变化方向→更新技能

本次2026-05-13实战就是知识驱动模式的典型案例：仅靠aboutamazon.com的少量数据+自身知识库，完成了crossborder-ai-tools-matrix从v3.0到v4.0的深度升级（新增7个板块）。

### 2026-05-09实战关键发现

1. **不要死磕搜索——直接找源头。** 当所有搜索引擎都挂了，直接访问官博。anthropic.com、redis.io、github.com都直连可达且数据完整
2. **搜索英文关键词最好用英文User-Agent+英文搜索词**，百度效果差但官方博客本身就是英文高质量内容
3. **百度触发验证码是随机的**——同一个query第一次可能成功，第二次就要求验证。成功时尽快提取
4. **官方博客的准确率远高于搜索片段**——从Anthropic官方博客提取的Agent架构知识是零失真直接获取
5. **速度优势明显**：直接抓取官博只需1-3秒，远快于搜索引擎层层跳转
6. **已知隐患**：第二天这些URL可能被墙、公司可能改版博客URL结构，需要定期验证可达性

### 百度搜索已知问题
1. **百度搜索稳定性差** — 同一关键词多次请求结果不同，有时返回空。建议：换不同关键词重试2-3次
2. **User-Agent必须正确** — 缺失User-Agent或用错格式会导致百度返回验证页面
3. **中文结果为主** — 百度搜索英文关键词效果差，英文搜索建议换Bing（如果可达）
4. **URL是跳转链接** — 百度返回的href是`http://www.baidu.com/link?url=...`格式，需要解码才能获取真实URL
5. **反爬风险** — 短时间内频繁请求可能被限制。建议间隔2-3秒，每次最多3-5个查询
6. **HTML结构可能变化** — 百度前端会更新，正则表达式需要相应调整

### 成功案例
- **2026-05-09（主要发现）** Tavily 432耗尽、百度触发验证码、Bing被限制。改用**直接抓取官方博客**策略成功获取：
  - Anthropic《Building Effective Agents》全文（177KB）— Workflows vs Agents5种模式
  - Anthropic《Context Engineering》全文 — 注意力预算/Just-in-Time/Compaction
  - Redis《AI Agent Architecture 2026》全文（585KB）— 四层架构+Failure Rate<1%
  - Google A2A协议GitHub README — Agent Card/跨框架协作
  - MCP官方文档（303KB）— 开放标准详解
  - Mem0上下文工程指南（443KB）— RAG+记忆系统集成
  
- **2026-05-09（备用方案）** 成功使用百度搜索获取AI Agent行业最新数据（Tavily 432耗尽，browser不可用）
  - 搜索词：`AI智能体行业趋势 2026 市场规模 企业落地 最新报告`
  - 搜索结果涵盖：沃丰科技蓝皮书、多模态智能体爆发报告、43亿市场规模数据等
  - 成功提取关键数据：430亿元市场规模、300%增长率、81%企业计划更复杂场景等

- **2026-05-14（多源数据整合）** Tavily 432耗尽、Chrome sandbox不可用、web_extract不可用。改用**多源并行采集**策略成功获取：
  - **百度热搜榜** Top 40热搜词（特朗普访华、大疆降价、无人车大战等）
  - **Sina Finance** 实时美股数据（道琼斯-0.14%、纳斯达克+1.20%、英伟达+2.29%等10只）
  - **东方财富** A股指数（上证+0.67%、沪深300+1.02%）
  - **知乎热榜** 社会热点话题和热度数据
  - **多源交叉验证** 确认特朗普访华团队（马斯克、黄仁勋等十余位商界巨头）等关键信息

## 验证搜索是否成功

```python
# 简单验证：检查提取到的数据是否包含预期关键词
result_text = "..."  # 提取到的文本
expected_keywords = ['亿', '增长', '市场']
found = sum(1 for kw in expected_keywords if kw in result_text)
if found >= 2:
    print("✅ 搜索有效")
else:
    print("⚠️ 搜索可能无效，建议重试或换关键词")
```

## 2026-05-14 新增：多源数据采集方案（新闻聚合+财经数据）

### 情景：每日新闻汇总任务，需要科技/财经/政治/军事多维度信息

当所有搜索API（Tavily 432）和web_extract都挂掉时，可以用以下多源直连方案替代：

### 方案A：百度热搜榜 — `top.baidu.com/board`

```python
import urllib.request, re, json

def baidu_hot_board():
    """获取百度实时热搜榜单"""
    req = urllib.request.Request(
        "https://top.baidu.com/board?tab=realtime",
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8', errors='replace')
    
    # 提取热搜词（多个备选模式）
    titles = re.findall(r'"word":"([^"]+)"', html)
    return titles  # 返回热搜词列表
```

**特点：** 免API Key，国内直达，实时反映中文互联网热点。不返回链接，但能给出当日新闻关键词。

### 方案B：Sina Finance API（美股+全球指数）

```python
import urllib.request, re

def sina_us_stocks():
    """获取美股实时数据（需要GBK解码）"""
    url = "https://hq.sinajs.cn/list=gb_dji,gb_ixic,gb_spx,gb_nvda,gb_tsla,gb_msft,gb_aapl,gb_amzn,gb_goog,gb_meta"
    req = urllib.request.Request(url, headers={
        "Referer": "https://finance.sina.com.cn"
    })
    with urllib.request.urlopen(req, timeout=10) as resp:
        raw = resp.read()
    
    # 注意：返回GBK编码
    text = raw.decode('gbk', errors='replace')
    
    stocks = {}
    for line in text.strip().split('\n'):
        match = re.match(r'var hq_str_gb_(\w+)="([^"]+)"', line)
        if match:
            ticker = match.group(1).upper()
            parts = match.group(2).split(',')
            stocks[ticker] = {
                'name': parts[0],
                'price': parts[1],
                'change_pct': parts[2],
            }
    return stocks
```

**返回格式：** `var hq_str_gb_nvda="英伟达,225.8300,2.29,2026-05-14 07:59:59,..."`
**注意：** 必须加 `Referer: https://finance.sina.com.cn` 否则被拒。GBK编码需正确处理。

### 方案C：东方财富API（A股指数）

```python
# 上证指数 + 沪深300
url = "https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&fields=f2,f3,f12,f14&secids=1.000001,1.000300"
```

**注意：** 该端点不稳定，部分时段返回空。配合Sina Finance互为备份。

### 方案D：知乎热榜（社会热点补充）

```python
url = "https://api.zhihu.com/topstory/hot-list"
# 直接GET返回JSON（无需认证），含 title/heat/answer_count
```

**返回格式：** 结构化JSON，每条包含title、热度、链接、回答数。特别适合中文社会热点。

### 方案F（2026-05-15新增）：163.com新闻聚合（每日新闻汇总任务首选）
  
当需要做**每日新闻汇总**（科技/财经/政治/军事多维度）且所有搜索API不可用时，**163.com（网易新闻）是我们已验证的最高质量新闻源**：

**为什么163.com是首选：**
- 内容全面：覆盖科技、财经、政治、军事、社会等所有新闻类别
- 一次性抓取即可获得30-50条高质量新闻标题，覆盖所有类别
- 标题本身包含足够上下文信息（如「俄军：\"世界上最强大导弹\"试射成功 射程超35000公里」）
- 无需API Key、无频率限制（至少单次会话50次请求内无问题）
- tech.163.com 专门提供科技新闻

**2026-05-15实战验证：** 从 news.163.com 一次性提取到40+条关键新闻标题，覆盖AI（阿里AI 358亿、Anthropic 90%代码AI完成、腾讯Agent Memory开源、百川融资50亿）、政治（中美元首会晤详情）、军事（俄导弹试射）全维度。是本文每日新闻汇总任务的**核心数据源**。

**tech.163.com 专用：** 用Python urllib提取AI/科技专门新闻效果更佳，包含Anthropic、百川智能、腾讯Agent开源等细节。比百度搜索片段的质量高得多。

**推荐Python实现（用`execute_code`工具运行，安全可控）：**
```python
import urllib.request, re

# 从163.com提取新闻
def fetch_news(url, keywords_filter=None):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8', errors='replace')
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    html = re.sub(r'<[^>]+>', '\n', html)
    lines = [l.strip() for l in html.split('\n') if len(l.strip()) > 15]
    if keywords_filter:
        lines = [l for l in lines if any(kw in l for kw in keywords_filter)]
    return lines

# 使用
lines = fetch_news("https://news.163.com", ["AI", "华为", "军事", "中美"])
for l in lines:
    print(l)
```

### 方案G（2026-05-15新增）：观察者网（政治/军事深度内容）

观察者网（guancha.cn）擅长国际政治和军事深度分析，可直接用Python urllib提取标题。

### 方案E（备用）：curl直接+百度SERP通用提取

当Python urllib请求被限制或反爬时，可用系统curl配合iconv：

```bash
# 获取数据
curl -s --max-time 15 -H "User-Agent: ..." "https://top.baidu.com/board?tab=realtime" | \
  python3 -c "import sys,re; print('\n'.join(re.findall(r'\"word\":\"([^\"]+)\"', sys.stdin.read())))"

# GBK编码转换（Sina财经数据）
curl -s -H "Referer: https://finance.sina.com.cn" "https://hq.sinajs.cn/list=..." | \
  iconv -f gbk -t utf-8
```

### 多源数据整合工作流（2026-05-15升级版：新增163.com作为核心）

```
Step 1: 尝试标准web_search/web_extract（Tavily）
        如果可用 → 直接使用，最快
        如果不可用（432） → 进入Step 2

Step 2: 并行获取多个国内源
  ┌── 163.com (news.163.com + tech.163.com)   → ⭐最高优先级：一次性获取全维度新闻标题
  │   用Python urllib即可，无需curl，内容质量最高
  ├── 百度热搜 top.baidu.com → 热点关键词（补充中文互联网热度数据）
  ├── Sina Finance → 美股/全球指数价格
  ├── 观察者网 guancha.cn → 政治/军事深度文章
  ├── 百度新闻首页 news.baidu.com → 重要新闻标题（与163互补）
  └── East Money → A股指数（⚠️不稳定，可跳过）

Step 3: 使用百度搜索首枪窗口补充细节（**仅2次**，必须是最高价值的查询）
  Python urllib 请求百度搜索，注意2026-05-15窗口已收窄到约2次
  ⚠️ 今日查询1放最重要的AI/科技，查询2放第二重要的查询
  查询3+会100%返回空，不要浪费

Step 4: 用163.com + 观察者网获取更多文章详情
  对关键事件，163.com和guancha.cn的原文标题本身已包含丰富信息
  如需深度详情，尝试直接从文章的原始URL用Python urllib提取正文

Step 5: 综合多源数据，交叉验证信息准确性后输出报告
```

### 2026-05-14实战发现的关键数据点

1. **百度热搜榜可用性 ✅** — `top.baidu.com/board?tab=realtime` 可直接curl获取，正则提取 `"word":"..."` 模式，返回40+热搜词
2. **Sina Finance美股数据 ✅** — 返回完整的股票名称、价格、涨跌幅、涨跌额、开盘价、昨收、最高最低、成交量等。使用 `gb_` 前缀（港股用 `rt_hk`）
3. **知乎API热榜 ✅** — `api.zhihu.com/topstory/hot-list` 直接返回含 `title`、`heat`（热度）、`answer_count` 的JSON
4. **百度新闻首页 ✅** — `news.baidu.com` 可提取新闻标题和链接（部分）
5. **East Money波动 ⚠️** — 该API端点有时返回空（exit code 52），不可靠
6. **Baidu搜索内容页 0% ❌** — 无论是百度SERP还是百家号文章页，用Python urllib提取正文内容几乎全部返回空。只能从热搜的word/title推断事件，无法获取详情

### 关键技巧

- **Baidu热搜提取核心模式：** `re.findall(r'"word":"([^"]+)"', html)` 最简单有效
- **Sina Finance必须加Referer：** 不加返回空。Referer值：`https://finance.sina.com.cn`
- **GBK解码：** Sina和部分老站用GBK编码，`urllib.request` 默认UTF-8会报错。处理方式：
  ```python
  raw = resp.read()
  text = raw.decode('gbk', errors='replace')
  ```
- **热榜标题推断法：** 百度热搜只有标题没有详情，需要结合上下文（搜索词标题里包含多少信息）推断事件核心。例如「特朗普抵达北京」「马斯克第4个下机 黄仁勋换西装」「马斯克：只有我和黄仁勋坐上空军一号」三个热搜组合起来可以推断出访细节。
- **交叉验证：** 同一事件在不同源（知乎、百度、Sina财经）出现则可信度高

## 2026-05-10 实战修正：百度 HTML 结构解析的可靠方案

### 关键发现：`baidu_search_full()` 基于 `<div class="result">` 的块解析不可靠

在本次实战中，尝试使用正则表达式按搜索结果块分割（`re.split(r'<div[^>]*class="[^"]*result[^"]*"[^>]*>', html)`）的 `baidu_search_full()` 函数返回了0条结果——百度前端的HTML结构变化频繁，按块解析几乎不可靠。

**唯一可靠的方法**就是 `baidu_search()` 中的 **扁平正则+全文文本提取**方案。同时，本次实战发现：

1. **web_extract 同样受 Tavily 432 限制** — 不只是 web_search，web_extract 也会失败
2. **browser 工具可能也挂** — Chrome sandbox 问题导致无法启动
3. **完全备份方案只有 urllib 直连** — 当所有搜索+提取+browser工具全挂时，urllib.request + 百度是最后一层防线

### 关键词定制策略

Baidu搜索结果片段的提取质量取决于关键词的选择。不同主题需要不同的关键词集：

```python
# 跨境电商/社媒主题关键词
keywords_social_media = [
    '亿', '增长', '市场', 'AI', '社交', '电商', '流量', '算法',
    'TikTok', 'YouTube', 'Facebook', 'Instagram', 'Meta',
    'KOL', '转化', '广告', '佣金', 'ROI'
]

# AI/科技主题关键词
keywords_ai_tech = [
    '亿', '增长', '市场', '规模', '智能体', 'Agent', 'AI',
    '模型', '自动化', '落地', '部署', '开源', 'API', '生态'
]

# 短视频/内容主题关键词
keywords_short_video = [
    '流量', '算法', '播放量', '完播率', '互动', '粉丝',
    '涨粉', '爆款', '选题', '脚本', '账号', '矩阵', '变现'
]
```

### 多轮搜索策略

当需要深度研究某个主题时，不能只搜1-3次——**至少需要7次不同角度的搜索**才能收集足够的数据用于内容创作或技能升级：

```python
import time

# 策略：每轮搜索针对不同子角度，间隔2秒防封
searches = [
    # 核心关键词（必搜）
    "TikTok Shop 2026 最新算法变化",
    # 竞品平台
    "YouTube Shopping 联盟营销 2026",
    "Meta Facebook 广告 2026 最新变化",
    # 细分子话题
    "Instagram Reels 带货 2026 电商转化",
    # 新兴渠道
    "Pinterest Threads Reddit 跨境引流 2026",
    # 技术趋势
    "Google AI Overview SGE SEO变化",
    # 具体业务环节
    "WhatsApp Business 社交电商 转化",
]

for q in searches:
    result = baidu_search(q)
    # 提取和分析snippets
    time.sleep(2)  # ⚠️ 必须等待，否则被封
```

### 搜索时间估算

7次搜索 × 2秒间隔 = 约14秒搜索时间
+ 每次urllib请求1-3秒 = 约15秒
总计约 **30秒** 完成一次完整的多角度搜索。如果想要更全面的数据（14+次搜索），预算约 **60-90秒**。

### 从片段到全文的推断方法

由于百度搜索只能获得片段而非全文，需要采用**交叉验证+上下文推断**策略：

```python
# 策略1：从多个片段中提取交叉验证的数值
# 如果3个不同查询都提到"ROI 1:7"、"20%佣金"、"500订阅者"
# → 可以高置信度确认这是YouTube Shopping的实操数据

# 策略2：从搜索标题推断文章核心论点
# 标题"2026年Meta ASC广告终极指南" + 片段"手动投放正在被AI碾压"
# → 文章核心论点：Advantage+已取代手动投放

# 策略3：用web_extract尝试获取全文中最为重要的1-2篇文章
# 虽然Tavily可能限制次数，但值得一试最关键的URL
```

### 注意事项更新（2026-05-10 + 2026-05-13）

1. **❌ `baidu_search_full()` 块解析不可用** —— 百度HTML结构频繁变化，基于div class的块分割会返回0结果
2. **✅ `baidu_search()` 扁平提取是唯一可靠方案** —— 用正则提取标题+从全文中按关键词筛选片段
3. **✅ 至少7次搜索** —— 浅度搜索（1-3次）不够，必须覆盖多个子角度
4. **✅ 2秒间隔必须遵守** —— 连续快速请求会被百度封IP
5. **⚠️ 英文关键词效果差** —— 英文技术内容直接用 `fetch_blog()` 访问官方源
6. **⚠️ web_extract 同受 Tavily 432 限制** —— 不要指望web_extract作为fallback
7. **⚠️ browser 工具也可能不可用** —— Chrome sandbox问题常见于容器环境，不要依赖
**8. ⚠️ 百度搜索的「首枪窗口」策略（2026-05-14新增重要发现）** —— 百度搜索并非完全不可用，而是**存在一个「首枪窗口」：第一次查询成功率高（>80%），第2-3次开始衰减（约30-50%），第4次之后基本全部返回空**。2026-05-13报告9次全部为空，是因为连续密集查询耗尽了这个窗口。

**关键策略修正：** 不要放弃百度搜索，但要用「首枪窗口」策略：

```python
# ✅ 正确做法：把最重要的查询放在最前面，一次命中
first_batch = [
    "最重要的查询",      # #1 最可能成功 → 放这里
    "第二重要的查询",     # #2 可能成功
    "次重要的查询",       # #3 可能成功或失败
]

# ❌ 错误做法：平均分配，浪费首枪窗口
first_batch = [
    "一般查询1",         # 浪费了最宝贵的#1位
    "一般查询2",         # 浪费了#2位
    "最重要的查询",      # #3已经很可能失败了！
]
```

**实战验证（2026-05-14）：** 本次深度研究「短视频账号矩阵」主题，前3次百度搜索（查询1=成功5结果+18片段，查询2=成功5结果+14片段，查询3=成功5结果+12片段）全部成功返回有用数据（包含小红书KOS政策巨变、教培50+账号被封等关键信息）。而第4-6次查询相同的主题定向搜索全部返回0结果。这证明百度搜索的「首枪窗口」理论是有效的——**不是搜索源本身挂掉了，而是高频查询触发了限流。**

**2026-05-15实战更新（上午）：首枪窗口进一步收窄至~2次查询。** 今日查询1（AI智能体/大模型）= 5结果+15片段 ✅ 成功；查询2（AI开源框架/模型发布）= 0结果+0片段 ❌ 空。查询3-5（财经/军事/政治）= 全部0结果。统计：2次成功（5结果+15片段 / 5结果+15片段 → 实际上第二次返回了空），窗口从约3次收窄到约2次。结论：**百度搜索的窗口在持续收窄，最多依赖2次高质量查询，之后必须切换数据源。**

**2026-05-15实战更新（下午——最新数据点）：首枪窗口进一步收窄到仅1次有效查询。** 今日执行「AI工具矩阵v7.0」技能升级：
- 查询1（`AI工具 2026年5月 最新发布 新功能 大模型`）= HTML 1.2MB ✅ 11条结果 + 3个片段（含商汤DSA稀疏注意力机制等有效内容，但片段数量少说明提取精度下降）
- 查询2（`Claude Cursor Midjourney Suno AI工具 2026年5月 更新`）= HTML 877KB ✅ 5条结果 + 16个片段（以2025年旧内容为主，陈旧度高）
- 查询3（`Claude Code auto mode Cursor Perplexity NotebookLM 2026年5月 新功能`）= HTML 仅227字符 ❌ 0结果

**关键发现：** 并非百度完全封禁——第1次仍有1.2MB完整HTML返回，说明百度网页版返回正常。真正的问题是**百度搜索对AI/AI工具这类高频话题的限流更严格了**。第2次能返回但内容陈旧（多数是2025年聚合站的过时内容），第3次直接空页。

**修正策略：** 
1. 把**唯一的1次有效搜索**用于最关键、最窄的关键词（如具体公司名+事件）
2. 搜索2作为备用但不报期望
3. 将更多依赖从「百度搜索」转向「直连官方源+163.com新闻聚合」的混合策略
4. 对于AI工具/技术类话题，anthropic.com/engineering/* 直连抓取的效果远好于百度搜索

8. **⚠️ 百度搜索存在「首枪窗口」**（2026-05-14实战关键修正）—— 不是搜索源完全失效，而是限流机制。前1-3次查询成功率高（>80%），之后返回空。战略调整：**把最重要的查询放在#1，不要浪费在次要关键词上**
9. ✅ 知识驱动模式（所有搜索全挂时）—— 依靠已有知识+可访问的有限源做深度整合，而非死等搜索恢复
**10. ✅ aboutamazon.com 是新的可靠源** —— 跨境AI/电商方向，直接urllib可达，提取Amazon官方产品发布
10. **✅ 当所有搜索全挂时，进入「知识驱动」模式** —— 依靠已有知识+可访问的有限源做深度整合，而非死等搜索恢复
11. **⚠️ cifnews等行业站可达但内容质量一般** —— 文章内容多为活动推广，不如官方源有价值
