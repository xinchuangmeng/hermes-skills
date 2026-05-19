# 从中国服务器获取国际新闻 — 已验证方法（2026-05-18）

## 背景

腾讯云轻量应用服务器（大陆节点）无法访问 BBC、Reuters、NYT、Guardian、Google、Wikipedia 等多数国际站点。Tavily API 额度耗尽。子Agent的 `web_search` 工具无法使用。

## 已验证可达的数据源

### RSS Feeds

| 来源 | RSS URL | 实测大小 | 上次验证 |
|------|---------|---------|---------|
| TechCrunch | https://techcrunch.com/feed/ | ~17KB | 2026-05-18 ✅ |
| CNBC | https://www.cnbc.com/id/100003114/device/rss/rss.html | ~21KB | 2026-05-18 ✅ |
| Wired | https://www.wired.com/feed/rss | ~43KB | 2026-05-18 ✅ |
| Ars Technica | https://feeds.arstechnica.com/arstechnica/index | ~78KB | 2026-05-18 ✅ |
| The Verge | https://www.theverge.com/rss/index.xml | ~32KB | 2026-05-18 ✅ |

### 可直接 curl 的单篇文章（TechCrunch 示例）

```bash
curl -sL --connect-timeout 8 "https://techcrunch.com/2026/05/17/why-trust-is-a-big-question-at-the-elon-musk-openai-trial/" \
  -H "User-Agent: Mozilla/5.0" -o article.html
# → 200, 230KB ✅
```

### API

- **Hacker News Algolia**: `https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=30`
- **百度新闻**: `https://news.baidu.com/` (JS渲染，内容需从HTML解析)
- **Bing搜索**: `https://cn.bing.com/search?q=KEYWORD&form=QBLH`

## 不可达（timeout/连接被重置）

- BBC: `feeds.bbci.co.uk/news/rss.xml` ❌
- Reuters: `www.reutersagency.com/feed/` ❌
- Guardian: `www.theguardian.com/world/rss` ❌
- NYT: `rss.nytimes.com/...` ❌
- Al Jazeera: `www.aljazeera.com/xml/rss/all.xml` ❌
- Bloomberg: `www.bloomberg.com/feed/...` ❌
- Wikipedia: `en.wikipedia.org` ❌
- Google News: `news.google.com` ❌
- Reddit: `www.reddit.com` ❌
- DuckDuckGo: `lite.duckduckgo.com` ❌
- Hacker News 主站: `news.ycombinator.com` ❌

## RSS解析Python模板

```python
import re, html as htmlmod

def parse_rss_items(filepath):
    with open(filepath, 'r', errors='replace') as f:
        content = f.read()
    
    items = []
    # Standard RSS 2.0
    blocks = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
    
    for block in blocks:
        title_m = re.search(r'<title>(.*?)</title>', block)
        link_m = re.search(r'<link>(.*?)</link>', block)
        desc_m = re.search(r'<description>(.*?)</description>', block)
        pub_m = re.search(r'<pubDate>(.*?)</pubDate>', block)
        
        title = htmlmod.unescape(title_m.group(1).strip()) if title_m else ''
        link = link_m.group(1).strip() if link_m else ''
        desc = re.sub(r'<[^>]+>', '', htmlmod.unescape(desc_m.group(1))) if desc_m else ''
        desc = re.sub(r'\s+', ' ', desc).strip()[:200]
        
        items.append({'title': title, 'link': link, 'desc': desc})
    
    return items
```

## 重要发现

### 子Agent幻觉问题

当使用 `delegate_task` 并传入 `toolsets=["web"]` 时，**子Agent会虚构搜索结果**。它们的 tool_trace 为空数组，生成的 URL 返回 404。本次会话中以下内容均为幻觉（已用 curl 验证）：

1. ❌ "OpenAI 发布 GPT-5" → techcrunch URL 返回 404
2. ❌ "Anthropic 发布 Claude 4 Sonnet" → venturebeat URL 返回 429
3. ❌ "DeepSeek R1.5 发布" → theverge URL 无法验证
4. ❌ "Google Gemini 3.0 Pro" → cnbc URL timeout
5. ❌ "NVIDIA AI Agent SDK" → zdnet URL 无法验证
6. ❌ 政治新闻中的参议院债务上限、北约演习、以哈停火、英国内阁改组、俄乌无人机 → 所有链接 timeout 或无法验证

**结论：** 不能信任子Agent的"搜索"结果。必须自己用 curl/Python 从真实数据源获取。

### Bing搜索的局限

`cn.bing.com` 搜索国际新闻关键词效果很差，会返回大量无关内容（如搜索 military 出现法语医检实验室网站）。建议直接用 RSS feeds + HN API 作为第一手来源。
