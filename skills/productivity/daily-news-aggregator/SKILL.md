---
name: daily-news-aggregator
description: |-
  Cron-ready daily news aggregation across tech, finance, politics, and military categories. Handles restricted network environments by probing accessible APIs (HN Firebase, Lobste.rs) and falling back gracefully. Outputs formatted Chinese-language report.
allowed-tools: terminal, execute_code, todo
---

# Daily News Aggregator

Trigger: Scheduled cron job (e.g., daily at 8 AM) to aggregate and summarize news.

## Available Search Tools

### AnySearch CLI (preferred when available)
AnySearch (`anysearch_cli.py`) is a powerful search tool that works well in cron environments. It supports:
- General web search across 23 vertical domains (tech, finance, business, etc.)
- Freshness filtering (`--freshness day/week/month/year`)
- Max results control (`--max_results`)
- URL content extraction (`anysearch extract <url>`)
- **No API key required** for basic usage (anonymous access works with lower rate limits)

CLI path: `<skill_dir>/skill/search/anysearch/scripts/anysearch_cli.py`

Usage for news aggregation:
```python
def anysearch(query, domain=None, freshness="day", max_results=8):
    cmd = f"python3 /root/.hermes/skills/search/anysearch/scripts/anysearch_cli.py search {shlex.quote(query)}"
    if domain:
        cmd += f" --domain {domain}"
    cmd += f" --freshness {freshness} --max_results {max_results}"
    # returns structured results with titles, summaries, URLs
```

Key advantages over web_extract/web_search:
- More reliable in cron environments (no Tavily dependency)
- Returns structured JSON-like output ready for parsing
- Domain-specific search gives better categorization (tech, finance, business domains)
- Parallel searches via delegate_task

When using AnySearch, search across multiple domains in parallel for efficiency:
- Tech news: `--domain tech --freshness day --max_results 10`
- Finance news: `--domain finance --freshness day --max_results 10`
- Politics/world: no domain (general search) `--freshness day --max_results 10`
- Military: no domain (general search) or `--domain security`

### Web_extract on primary news sources
Prefer extracting rich, pre-categorized summaries from major sites when Tavily/AnySearch are unavailable.

## Network Environment Constraints

In typical Hermes cron environments, many common news sources are blocked:
- ❌ Google, Reddit, Wikipedia, Bloomberg, NYT (network unreachable or 403)
- ✅ **CNN Lite (`lite.cnn.com`)** — WORKS reliably. This text-only version of CNN loads quickly and provides a full list of latest stories across all categories (tech, finance, politics, military, science). Use `browser_navigate` to open it, then `browser_snapshot(full=true)` to get the complete list. Individual articles on `lite.cnn.com/*` also load well. This is the BEST single source for broad multi-category news in restricted cron environments. Full CNN (`cnn.com`) usually fails, but the lite version works.
- ❌ RSS feeds from Yahoo Finance, Reuters, BBC
- ✅ **web_search / web_extract tools** — these use Tavily API under the hood. Usually available but can fail with HTTP 432 (Tavily internal/auth error) — a distinct failure mode from network blocks or rate limits. When this happens, fall back immediately to sources listed below.
- ✅ **web_extract on Reuters (reuters.com/technology/), BBC (bbc.com/news/world), TechCrunch (techcrunch.com/), Hacker News (news.ycombinator.com/)** — these often work even when Tavily search/extract fails with 432. The `web_extract` tool uses a different transport path. **Try these FIRST** — they return rich, organized summaries (Reuters and HN Haxor output includes categorized top stories with summaries, BBC includes a timeline of latest events). This is often MORE efficient than searching and clicking individual articles.
- ❌ **Browser tool** (may time out in cron environments; sometimes works for CNBC, GitHub, but not BBC/NYT/Bloomberg)
- ✅ **Hacker News Firebase API** (`hacker-news.firebaseio.com/v0/`) — works
- ✅ **HN Algolia API** (`hn.algolia.com/api/v1/`) — works reliably for both search and date-sorted queries. BEST single source for tech news in restricted envs.
- ✅ **HN Algolia `search_by_date` with `tags=story` and `hitsPerPage=50`** — preferred over Firebase; single-query, returns recent stories with points, URLs, and objectIDs in one call
- ✅ **Lobste.rs API** (`lobste.rs/newest.json`) — works
- ✅ **TechCrunch WP REST API** (`techcrunch.com/wp-json/wp/v2/posts`) — excellent for tech news
- ✅ **Alpha Vantage API** (`www.alphavantage.co/query`) — stock market data (free tier: 5 req/min)
- ✅ **CNBC pages via browser** — partially works; paywalled content may still yield headline and key points from meta
- ❌ **Reddit API** — `reddit.com/r/*/hot.json` consistently times out in cron environments
- ❌ **Google News RSS** — `news.google.com/rss` times out
- ❌ **BBC RSS feeds** — consistently time out
- ❌ **NYT RSS feeds** — consistently time out
- ❌ **Reuters** — times out
- ✅ **FDA press releases (fda.gov)** — accessible via curl for science/health stories

## Workflow

### Step 1: Try web_extract on primary news sources FIRST (new recommended order)

The most efficient approach: use `web_extract` to load full-page summaries from major news sites in parallel. These pages contain rich, pre-categorized news summaries that often give you everything you need in one shot.

```python
urls = [
    "https://news.ycombinator.com/",            # Tech top stories with points
    "https://www.reuters.com/technology/",       # Tech + finance + biz news
    "https://techcrunch.com/",                   # Startup and AI news
    "https://www.bbc.com/news/world",            # Politics + military + world
]
```

Only fall back to RSS/API scraping if web_extract fails.

### Step 1b (fallback): Working APIs and RSS feeds (when web_extract fails)

If web_extract fails, use the known-working sources below.

### Additional Working Sources (from 2026-05-03 run)
- TechCrunch RSS (techcrunch.com/feed/) — works, good for tech/AI news
- Ars Technica RSS (feeds.arstechnica.com/arstechnica/index) — works, AI/security/policy
- Wired RSS (www.wired.com/feed/rss) — works, 50 items
- The Verge Atom feed (www.theverge.com/rss/index.xml) — works, Atom format
- Defense News RSS (www.defensenews.com/arc/outboundfeeds/rss/?outputType=xml) — best military source
- CNBC RSS Top News (search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114) — finance
- CNBC RSS Finance (search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664) — finance
- HN RSS (hnrss.org/frontpage?count=30) — preferred over Firebase API
- curl with --data-urlencode and -G for HN Algolia API params

Use `execute_code` with Python and concurrent.futures to efficiently fetch from multiple sources in parallel:

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
```

Key endpoints:
- `https://hacker-news.firebaseio.com/v0/topstories.json` — top 50 story IDs
- `https://hacker-news.firebaseio.com/v0/item/{id}.json` — individual story detail
- `https://hacker-news.firebaseio.com/v0/newstories.json` — breaking news
- `https://hacker-news.firebaseio.com/v0/showstories.json` — Show HN product launches
- `https://lobste.rs/newest.json?limit=30` — developer community news
- `https://hn.algolia.com/api/v1/search_by_date?tags=front_page&hitsPerPage=50` — front page stories sorted by date (reliable, no auth needed)
- `https://hn.algolia.com/api/v1/search?query={keyword}&tags=story&hitsPerPage=30` — keyword search across all HN (great for finding specific topics)
- `https://techcrunch.com/wp-json/wp/v2/posts?per_page=20` — TechCrunch tech news (rich metadata with dates, tags)
- `https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={SYMBOL}&apikey={KEY}` — stock market quotes (SPY, QQQ, DIA for indices)
- `https://www.alphavantage.co/query?function=NEWS_SENTIMENT&topics=financial_markets&apikey={KEY}` — financial news feed (use demo key or env var ALPHA_VANTAGE_KEY)

### Step 2: Use ThreadPoolExecutor for efficiency

Use `execute_code` with Python. Prefer `urllib.request` from stdlib (no pip install needed) over `requests`:

```python
import urllib.request, json

def fetch(url, timeout=15):
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0')  # Some APIs require this
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode('utf-8')
    except Exception as e:
        return None
```

For HN Firebase API (many individual calls), use ThreadPoolExecutor:

```python
items = []
with ThreadPoolExecutor(max_workers=10) as ex:
    futures = {ex.submit(fetch, f"https://hacker-news.firebaseio.com/v0/item/{i}.json"): i for i in ids}
    for f in as_completed(futures):
        result = f.result()
        if result:
            items.append(json.loads(result))
items.sort(key=lambda x: x.get('score', 0), reverse=True)
```

**Alternative: Use HN Algolia for simpler queries** — avoids the need for ThreadPoolExecutor entirely:
```python
url = f"https://hn.algolia.com/api/v1/search_by_date?tags=front_page&hitsPerPage=50"
data = json.loads(fetch(url))
for hit in data.get('hits', []):
    title = hit.get('title', '?')
    url = hit.get('url', '') or hit.get('story_url', '') or f"https://news.ycombinator.com/item?id={hit.get('objectID','')}"
    points = hit.get('points', 0)
```

This avoids the timeout risk of sequential fetching (seen: sequential 30 stories can timeout at 300s).

### Step 3: Categorize stories automatically

Classify HN/Lobsters stories into categories using keyword matching on lowercase titles:

| Category | Keywords |
|----------|----------|
| `military` | military, defense, special forces, soldier, weapon, war, maduro, raid |
| `finance` | stock, market, invest, billion, economy, tariff, trade, fund, bank, money, $ |
| `politics` | politics, president, congress, senate, ban, law, government, norway |

Everything else defaults to `tech`. This is a heuristic — adjust keywords to suit the day's news.

### Step 4: Deep-read the most important stories

For the top 2-3 stories in each category, use the browser to read CNN Lite articles:
```python
# Navigate to lite.cnn.com, get story list, click top stories
# Use browser_click with the ref ID from snapshot
# Then browser_snapshot(full=true) to get full article text
```

If CNN Lite is not available, try TechCrunch and HN Algolia APIs as fallbacks.

### Step 5: Compile formatted Chinese report with notable highlights

Before the category listing, add a **📌 重点关注** section (user preference: notable items must be pulled out separately, not buried in routine):

```
════════════════════════════════════
📅 每日新闻汇总 — YYYY-MM-DD
════════════════════════════════════

📌 重点关注
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[把当天最值得关注的1-3条新闻单独列在这里]
1. [标题] — 为什么重要的一句话说明
   🔗 Source URL

🔬 科技 (Top 5)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
...
   📝 Summary in Chinese
   🔗 Source URL

🤖 智能体学习笔记
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Agent/LLM related learning notes]

💰 财经 (Top 5)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
...

🏛️ 政治 (Top 5)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
...

⚔️ 军事 (Top 5)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
...
```

### Step 6: Validation

- Remove duplicates across categories
- Ensure all 4 categories present (mark as "当日无重大报道" if needed)
- Verify links are valid

## Pitfalls

## Pitfalls

- **Tavily HTTP 432 error** — when `web_search` or `web_extract` returns `Client error '432'`, this is NOT a standard HTTP error. It's a Tavily-specific internal/auth error. **Do not retry** — switch immediately to `web_extract` on known-working news sites (reuters.com/technology/, techcrunch.com/, bbc.com/news/world, news.ycombinator.com/). These often still work because they use the underlying urllib/requests stack in Hermes, not Tavily.
- **Sequential HN API calls timeout** — always use ThreadPoolExecutor with max_workers=8-10, OR use Algolia's single-query API instead, OR use `web_extract` on news.ycombinator.com/ directly (HN's Haxor page returns a clean summary of top stories with points).
- **Bloomberg/NYT paywalls** — accept that full articles aren't accessible; use HN discussion context and metadata to summarize
- **Weekend/holiday news droughts** — reduce to fewer items per category gracefully; note it's the weekend in the report
- **ssl context** — some environments need `ssl._create_unverified_context()` or `ssl.CERT_NONE`
- **No web_search tool** — do not assume web_search exists; probe available APIs first. Some environments don't have web_search.
- **Browser may be available** — can be used as fallback for reading key articles when curl times out. CNBC and GitHub pages tend to load; Bloomberg/NYT/BBC usually don't.
- **No `requests` package** — use `urllib.request` from stdlib instead; it's always available
- **Yahoo Finance rate limits** — Alpha Vantage free tier is more reliable (use `NKJLTWBFP04LN3GR` as demo key)
- **TechCrunch article meta extraction** — the `<meta name=\"description\">` tag on TechCrunch often contains a good summary, but paywall text may be minimal
- **Reddit API** — requires `User-Agent` header and often times out in cron environments; consider it unreliable
- **BBC RSS** — `feeds.bbci.co.uk/news/world/rss.xml` often times out; don't depend on it
- **Filtering by timestamp** — use `numericFilters=created_at_i>{timestamp}` with Algolia; get current unix timestamp via `int(datetime.now().timestamp())`. Note: excess whitespace or bad formatting in the URL can cause 400 errors.
- **Today's date** — determine date context from system or the task prompt (cron jobs may not have fresh system time context)
- **Date filtering can fail silently** — Algolia API may return results without date filtering if the numericFilter syntax is wrong. Always verify timestamps are correct and test with a small hit count first.
- **Points vs recency** — `search_by_date` returns most recent first but with low points. `search` with `numericFilters` is better for filtering by time. When using `search_by_date`, post-filter for `points > N` in Python.
- **Browser `browser_navigate` may succeed but then freeze** — if a page loads but times out on subsequent interactions, the data already loaded is available from the browser snapshot output, so use that.
- **CNN Lite strategy** — First navigate to `https://lite.cnn.com/` to get the full story list in one snapshot. Each story link is a relative path like `/2026/05/01/tech/pentagon-ai-anthropic`. Click individual links (using browser_click) to read full articles. All CNN Lite articles load in text-only format with no paywall. For returning to the main list, navigate back to `https://lite.cnn.com/` again (don't use browser_back, which may fail).
- **Reading article details from CNN Lite** — After clicking a story, `browser_snapshot(full=true)` returns the full article text including headlines, bylines, timestamps, and body paragraphs. This is sufficient for creating accurate Chinese summaries without needing curl or other tools.
- **Initial page load timing** — `browser_navigate` to lite.cnn.com succeeds where full CNN/reuters/bbc fail. The lite version has no JavaScript dependency and minimal resources.
- **Only fetch from CNN Lite** — for a daily news aggregator, one CNN Lite browse covers all 4 categories (tech, finance, politics, military) in one session. This is more efficient than trying multiple sources that may fail.
- **HN Algolia `search_by_date` with `tags=story`** — can return stories with 0-1 points unless you explicitly filter. Use `numericFilters=points>10` if available, or post-filter in Python.
- **Agent-relevant news patterns to watch for** — new open-source coding agents (Dirac topped TerminalBench), agent framework changes (Copilot switch to usage-based billing), model pricing shifts (DeepSeek undercutting), and geopolitical AI moves (China blocking acquisitions). Track these in the `🤖 智能体学习笔记` section.

## Reference Files

- `references/anysearch-patterns.md` — verified AnySearch CLI commands for searching tech, finance, politics, and military news categories

## Use with cronjob tool

Recommended cron schedule: `0 8 * * 1-5` (weekdays at 8 AM). The prompt should be self-contained as cron sessions have no conversation history.
