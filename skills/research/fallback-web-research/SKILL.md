---
name: fallback-web-research
title: 后备网络调研方法
description: 当标准搜索工具不可用时（浏览器缺Node.js、无Tavily API Key、搜索引擎不可达），使用curl下载HTML到文件+Python脚本解析的替代调研流程。两步法：先curl -o保存页面，再运行独立py脚本提取内容。
category: research
---

# 后备网络调研方法

## 适用条件

以下条件同时成立时使用：
- browser_navigate报错（缺Node.js）
- 无TAVILY_API_KEY或搜索API不可用
- Google/DuckDuckGo等搜索引擎curl超时
- 服务器在中国大陆，国际网站被防火墙屏蔽

## ⚠️ 关键陷阱：子Agent做网络搜索会幻觉

**当使用 `delegate_task` 给子Agent并传入 `toolsets=["web"]` 时，子Agent会凭空编造搜索结果。** 它们的 tool_trace 为空，URL 返回 404，摘要也是模型训练数据中的过时知识。

**已验证的事实：** 本会话中，同时派了4个子Agent分别搜索科技/财经/政治/军事新闻。每个都声称搜索并阅读了文章，但：
- TechCrunch的"GPT-5发布"文章 → 404
- VentureBeat的"Claude 4 Sonnet"文章 → 429（可能不存在）
- Reuters的参议院债务上限文章 → timeout

**规则：** 永远不要信任子Agent的"web_search + browser_navigate"结果。必须用 curl 验证每个URL的HTTP状态码。只有返回 200 的内容才算数。

## 从中国服务器获取国际新闻的可行方案

### 方案A：RSS Feeds（最可靠）

以下RSS Feed可从中国服务器直接访问（已验证 2026-05-18）：

| 来源 | Feed URL | 说明 |
|------|----------|------|
| TechCrunch | https://techcrunch.com/feed/ | 科技、AI、创业 |
| CNBC | https://www.cnbc.com/id/100003114/device/rss/rss.html | 财经、政治 |
| Wired | https://www.wired.com/feed/rss | 科技、文化、安全 |
| Ars Technica | https://feeds.arstechnica.com/arstechnica/index | 科技、科学 |
| The Verge | https://www.theverge.com/rss/index.xml | 消费科技 |

### 方案B：Hacker News API（科技新闻最佳来源）

```bash
# 获取最新首页故事
curl -sL "https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=30"
```

### 方案C：Bing中文站搜索

```bash
curl -sL "https://cn.bing.com/search?q=KEYWORD&form=QBLH" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
```

### 方案D：国内站点

| 站点 | URL | 特点 |
|------|-----|------|
| IT之家 | https://www.ithome.com/ | 消费科技新闻 |
| 百度新闻 | https://news.baidu.com/ | 综合新闻 |
| 36氪 | https://36kr.com/news | 科技创投 |

### 验证步骤（必须！）

对于任何新闻链接，先用 curl 验证是否真的可达：

```bash
curl -sL --connect-timeout 8 "ARTICLE_URL" -o /dev/null -w "%{http_code} %{size_download}\n"
# 200 + 非零大小 = 真实内容
# 404/000/大小<1KB = 可能是幻觉
```

## 工作流程

### 1. 测试可达性

```bash
curl -s --connect-timeout 5 "https://api.github.com" -o /dev/null -w "%{http_code} %{time_total}s\n"

# 测试跨境电商行业站点
curl -s --connect-timeout 8 "https://www.cifnews.com" -o /dev/null -w "%{http_code} %{time_total}s\n"
```

### 2. 下载HTML到文件

```bash
# 下载首页
curl -sL --connect-timeout 8 "https://www.cifnews.com/" -H "User-Agent: Mozilla/5.0" -o /tmp/cif_home.html

# 下载搜索页面
curl -sL --connect-timeout 8 "https://www.cifnews.com/search?keyword=KEYWORD" -H "User-Agent: Mozilla/5.0" -o /tmp/cif_search.html

# 下载具体文章
curl -sL --connect-timeout 8 "https://www.cifnews.com/article/ARTICLE_ID" -H "User-Agent: Mozilla/5.0" -o /tmp/cif_article.html
```

### 3. 编写Python解析脚本

创建独立的 `.py` 文件，不要使用 `-c` 内联参数或管道。

#### 链接提取脚本 (extract_links.py)

```python
import re, html as htmlmod, sys

filepath = sys.argv[1]
with open(filepath, 'r', errors='replace') as f:
    content = f.read()
content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
links = re.findall(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', content, re.DOTALL)
seen = set()
for href, text in links:
    clean = re.sub(r'<[^>]+>', '', text).strip()
    if clean and len(clean) > 10 and href not in seen:
        seen.add(href)
        print(f"[{clean[:80]}] -> {href}")
```

运行：`python3 /tmp/extract_links.py /tmp/cif_home.html`

#### 文章正文提取脚本 (extract_article.py)

```python
import re, html as htmlmod, sys, json

filepath = sys.argv[1]
with open(filepath, 'r', errors='replace') as f:
    content = f.read()
content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)

# 提取JSON-LD结构化数据
jsonlds = re.findall(r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>', content, re.DOTALL)
for j in jsonlds[:3]:
    try:
        data = json.loads(j)
        if isinstance(data, dict):
            if data.get('headline'): print(f"HEADLINE: {data['headline']}")
            if data.get('articleBody'): print(f"BODY: {data['articleBody'][:2000]}")
    except: pass

# 关键词过滤提取正文
text = re.sub(r'<[^>]+>', '\n', content)
text = htmlmod.unescape(text)
lines = [l.strip() for l in text.split('\n') if l.strip() and len(l.strip()) > 8]
keywords = ['海外仓', '物流', '清关', '关税', '仓库', '运费', 'FBA', '头程',
            'TikTok', 'Temu', '供应链', '履约', '备货', '跨境电商',
            '海运', '仓储', '成本', '2026', '美国', '东南亚', '合规']
for l in lines:
    if any(k in l for k in keywords):
        print(f"  {l[:300]}")
```

运行：`python3 /tmp/extract_article.py /tmp/cif_article.html`

### 4. 综合撰写报告

- 加载已有技能库（如crossborder-supply-chain-full-chain）获取基线数据
- 新发现与基线对比，标记差异

## 注意事项

- 只能获取服务端渲染的HTML，JS动态内容无法抓取
- 如果文件小于1KB，可能被反爬或重定向，检查User-Agent头
- 优先使用Tavily API，本方法仅为后备方案
