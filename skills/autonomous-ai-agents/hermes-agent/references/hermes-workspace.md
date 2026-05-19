# Hermes Workspace — Web Control Panel

## Overview
outsourc-e/hermes-workspace (4378 stars, MIT, JS/TypeScript) is a native web workspace for Hermes Agent — chat, terminal, memory, skills, and inspector in a browser UI.

## Key Features
- **Chat interface** — full Hermes session in the browser
- **Terminal** — embedded terminal
- **Memory browser** — inspect and edit persistent memory
- **Skills manager** — browse, install, update skills from the UI
- **Inspector** — debug tool calls and agent internals

## Architecture (from AGENTS.md)
The workspace uses a **semantic Hermes swarm** with 9 specialized workers:

| Worker | Purpose | Tools |
|--------|---------|-------|
| orchestrator | Planning, routing, greenlight | todo, kanban, delegation, terminal, file |
| km-agent | Knowledge management | gbrain, file, terminal, obsidian tools |
| builder | Feature implementation | terminal, file, browser, web |
| reviewer | Code review gating | terminal, file, web, gbrain |
| qa | Smoke testing | browser, terminal, file, vision |
| researcher | Quick research | gbrain, web, browser, terminal, file |
| ops-watch | Health monitoring | terminal, cronjob, file |
| maintainer | Repo maintenance | terminal, file, web, browser |
| strategist | Strategic review | gbrain, web, session_search, file |
| inbox-triage | Inbox processing | gbrain, web, file, session_search |

All workers use **gbrain** MCP server for context-aware decisions.

## Install (requires Node 22+ and pnpm)
```bash
curl -fsSL https://raw.githubusercontent.com/outsourc-e/hermes-workspace/main/install.sh | bash
# Or:
git clone https://github.com/outsourc-e/hermes-workspace.git
cd hermes-workspace
pnpm install
pnpm dev
```

## Notes
- Requires Node 22+ and pnpm — not available on the current server
- Designed for local development, not headless server deployment
- The swarm architecture is documented in `AGENTS.md` and `swarm.yaml`
- The workspace configures Hermes with API server enabled (port 8642 by default)
- Not installed on this server — would need Node/pnpm setup first
