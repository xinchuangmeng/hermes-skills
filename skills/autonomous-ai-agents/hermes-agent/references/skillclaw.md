# SkillClaw — Community Skill Evolution System

## Overview
SkillClaw (AMAP-ML/SkillClaw, v0.4.0, MIT) is a skill evolution system for Hermes and other claw-family agents. It runs as an API proxy that intercepts LLM requests, records session data, and evolves skills from real usage. Backed by arXiv 2604.08377 (HuggingFace #2 Paper of the Day).

## How It Works

```
Agent → SkillClaw Proxy (:30001) → LLM (deepseek-chat)
                                       ↓
                                  Records session data
                                       ↓
                                  Evolves skills (dedup, quality, version)
```

## Installation
```bash
git clone https://github.com/AMAP-ML/SkillClaw.git
cd SkillClaw
bash scripts/install_skillclaw.sh
source .venv/bin/activate
skillclaw setup    # interactive config wizard
skillclaw start --daemon
```

## Config (at ~/.skillclaw/config.yaml)
```yaml
claw_type: hermes  # or openclaw/claude/codex
llm:
  provider: custom
  api_base: https://api.deepseek.com/v1
  model_id: deepseek-chat
proxy:
  port: 30001
  served_model_name: skillclaw-model
skills:
  dir: /root/.hermes/skills  # reuses existing skill directory
  top_k: 6
prm:
  enabled: false  # needs separate scoring model
sharing:
  enabled: false
```

## Commands
```bash
skillclaw status              # Check running state
skillclaw stop / start        # Control
skillclaw skills push/pull/sync  # Share skills (sharing must be enabled)
skillclaw dashboard sync/serve   # Visualization
skillclaw doctor              # Integration diagnostics
skillclaw restore             # Restore from backups
```

## Effect on Hermes Config
When started, SkillClaw auto-modifies `~/.hermes/config.yaml` to route all LLM calls through its proxy:
- `model.provider` → `custom`
- `model.base_url` → `http://127.0.0.1:30001/v1`
- `model.default` → `skillclaw-model`
- `model.api_key` → `skillclaw`

A backup is saved to `~/.skillclaw/backups/hermes/`.

## Status on This Server
- **Running**: Yes (PID stored in SkillClaw state)
- **Port**: 30001
- **Skills loaded**: 316 (from /root/.hermes/skills)
- **Proxy verified**: ✅ Health endpoint responds, LLM calls pass through
- **PRM scoring**: Disabled (no separate scoring model configured)
- **Skill sharing**: Disabled (will enable later after accumulating session data)

## Notes
- The install script creates a separate venv at `SkillClaw/.venv/`
- The proxy can conflict with other services if run on the same port — keep it on 30001
- Sharing needs an OSS/S3 backend to be useful — local storage is single-machine only
