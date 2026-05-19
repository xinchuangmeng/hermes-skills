# AnySearch Patterns for Daily News Aggregation

## Verified Working Commands (2026-05-19)

### Tech / AI News
```
python3 /root/.hermes/skills/search/anysearch/scripts/anysearch_cli.py search "AI news today May 19 2026" --domain tech --freshness day --max_results 10

python3 /root/.hermes/skills/search/anysearch/scripts/anysearch_cli.py search "AI agent LLM framework release 2026" --domain tech --freshness week --max_results 10

python3 /root/.hermes/skills/search/anysearch/scripts/anysearch_cli.py search "technology news Google Apple OpenAI Anthropic" --domain tech --freshness day --max_results 10
```

### Finance News
```
python3 /root/.hermes/skills/search/anysearch/scripts/anysearch_cli.py search "stock market financial news today May 19 2026" --domain finance --freshness day --max_results 10

python3 /root/.hermes/skills/search/anysearch/scripts/anysearch_cli.py search "business economy news today" --domain business --freshness day --max_results 10
```

Note: `--domain business` tends to return more HR/career content; use `--domain finance` for market news.

### Politics / International
```
python3 /root/.hermes/skills/search/anysearch/scripts/anysearch_cli.py search "world politics news international affairs May 19 2026" --freshness day --max_results 10

python3 /root/.hermes/skills/search/anysearch/scripts/anysearch_cli.py search "US China politics diplomacy news May 2026" --freshness week --max_results 10
```

### Military / Defense
```
python3 /root/.hermes/skills/search/anysearch/scripts/anysearch_cli.py search "military defense news technology May 19 2026" --freshness day --max_results 8

python3 /root/.hermes/skills/search/anysearch/scripts/anysearch_cli.py search "defense military technology news May 2026" --freshness week --max_results 8
```

## Efficiency Tips

1. **Run searches in parallel** using `delegate_task` with 3 concurrent tasks (max_concurrent_children=3)
2. **Use delegate_task with toolsets=["terminal"]** to keep subagent context lean
3. **The anysearch CLI returns results inline** — no need for a separate extract step unless you need full article text
4. **Freshness filtering** is critical: use `--freshness day` for breaking news, `--freshness week` for broader context/trends
5. **Domain tags help filter**: tech domain eliminates finance noise, finance domain filters for market-specific content

## Result Parsing

Each search result includes:
- Title (markdown heading)
- URL link
- Content summary (usually 3-5 paragraphs covering key events)
- No explicit timestamp — rely on freshness filter

## API Key Status

As of 2026-05-19: `ak-68623a4a18764f7b83fd6aece95b01f4` (bimiyun) was returning 401 Unauthorized. AnySearch anonymous access worked without any key.
