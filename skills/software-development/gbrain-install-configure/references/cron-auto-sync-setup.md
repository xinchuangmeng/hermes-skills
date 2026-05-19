# Cron Auto-Sync Setup

## SYNOPSIS
Configure GBrain to automatically re-import and re-embed new/modified skill files on a schedule.

## The Problem
GBrain's `gbrain import` and `gbrain embed` are one-shot CLIs. New skills added to ~/.hermes/skills/ are invisible to GBrain until manually re-imported. Without periodic sync, the MCP server serves stale data.

## Solution: no_agent Cron + Shell Script

### Script: `~/.hermes/scripts/gbrain_auto_sync.sh`

```bash
#!/bin/bash
# GBrain Auto Sync: re-import skills dir + embed stale pages
export DASHSCOPE_API_KEY="sk-xxx"
GBRAIN_DIR="/root/.bun/install/global/node_modules/gbrain"
SKILLS_DIR="/root/.hermes/skills"
LOG_FILE="/root/.hermes/logs/gbrain_sync.log"
mkdir -p "$(dirname "$LOG_FILE")"

cd "$GBRAIN_DIR"
echo "[$(date)] === GBrain Sync Start ===" >> "$LOG_FILE"

bun run src/cli.ts import "$SKILLS_DIR" --no-embed 2>&1 | tail -5 >> "$LOG_FILE"
bun run src/cli.ts embed --stale 2>&1 | tail -5 >> "$LOG_FILE"

PAGES=$(bun run src/cli.ts doctor 2>&1 | grep -oP 'Connected, \K\d+')
echo "Total pages: $PAGES" >> "$LOG_FILE"
```

### Cron Registration

```bash
# Via hermes cron (recommended — managed lifecycle):
hermes cron create \
  --name gbrain-sync \
  --schedule "0 */6 * * *" \
  --script gbrain_auto_sync.sh \
  --no-agent
```

### Workflow

```
cron tick (every 6h)
  └→ gbrain_auto_sync.sh (no_agent=true — no LLM cost)
      ├→ import new/changed skills (dedup by slug, skips unchanged)
      └→ embed --stale (only pages without vectors)
          └→ MCP tools see fresh data immediately
```

### Schedule Rationale

| Frequency | Pros | Cons | Use Case |
|-----------|------|------|----------|
| `every 1h` | Max freshness | More API calls for embed | Rapid iteration |
| `*/6 * * *` | Economy + freshness | 6h lag | Production/stabilized skill set |
| `0 0 * * *` | Minimal API cost | Can miss daily skill additions | Rarely-changing knowledge |

## DashScope Embedding Batch Limit Fix

`text-embedding-v3` limits batches to ≤10 inputs. GBrain's recipe uses `max_batch_tokens: 8192` which causes 400 errors on large chunks. Fix:

In `src/core/ai/recipes/dashscope.ts`:
```diff
- max_batch_tokens: 8192,
+ max_batch_tokens: 500,  // Hard cap to avoid DashScope ≤10-input limit
```

This is a **persistent patch** — re-`git clone` or re-compile ELF loses it.

## Logs

The script writes to `~/.hermes/logs/gbrain_sync.log`. Format:
```
[2026-05-18 20:33:23] === GBrain Sync Start ===
[20:33:23] Importing skills...
Import complete: 0 new, 190 unchanged
[20:34:00] Embedding...
Embedded 0 chunks across 0 pages
Total pages: 190
```

## Verifying

```bash
gbrain doctor | grep embedding  # should say "100% coverage, 0 missing"
```
