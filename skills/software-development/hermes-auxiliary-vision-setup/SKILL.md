---
name: Hermes Auxiliary Vision Setup
description: Configure Hermes Agent auxiliary.vision for image analysis when the main provider (e.g. DeepSeek) doesn't support vision
tags: [hermes, vision, auxiliary, configuration, troubleshooting]
---

# Hermes Auxiliary Vision Configuration Guide

## Background

When the Hermes main model (e.g. DeepSeek deepseek-chat) does not support image analysis, `vision_analyze` tool calls will fail. You need to configure an auxiliary multimodal vision model.

## How It Works

Hermes auxiliary vision is handled in `agent/auxiliary_client.py`:

- `resolve_vision_provider_client()` resolves vision config and creates the OpenAI client
- When `base_url` + `api_key` are explicitly set → goes through `"custom"` provider path
- When `provider: auto` → tries in order: main provider → OpenRouter → Nous Portal
- `moonshot` / `kimi` providers alias to `kimi-coding` (not a strict vision backend)

## Configuration Options

### Option A: OpenRouter (LLaMA Vision — free tier available)

```yaml
auxiliary:
  vision:
    api_key: "sk-or-v1-xxx"
    base_url: "https://openrouter.ai/api/v1"
    model: "meta-llama/llama-3.2-11b-vision-instruct"
    provider: openrouter
    timeout: 120
```

Pitfalls:
- Some models return 403 "not available in your region" (gpt-4o, gemini-2.5-flash)
- Free tier has a total usage limit; check dashboard at openrouter.ai
- LLaMA Vision generally works in all regions

### Option B: Kimi (Moonshot) Multimodal API

```yaml
auxiliary:
  vision:
    api_key: "sk-xxx"
    base_url: "https://api.moonshot.cn/v1"
    model: "kimi-k2.6"
    provider: moonshot
    timeout: 120
```

Pitfalls:
- base_url must be `https://api.moonshot.cn/v1` (NOT api.kimi.com — returns 404)
- Kimi K2.6 pricing: input ¥6.50/1M tokens, output ¥27.00/1M tokens
- Create API Key at platform.kimi.com console
- Keys from the new platform (platform.kimi.com) may return 401 on old domain (api.moonshot.cn) — verify key status in platform console
- **Platform migration issue**: If a key returns 401 on api.moonshot.cn, it may be a new-platform key that's incompatible — create a new key or check console

### Option C: MiniMax (⚠️ TRAP — accepts image_url format but does NOT process images)

```yaml
auxiliary:
  vision:
    api_key: "sk-xxx"  # MiniMax API Key from platform.minimaxi.com
    base_url: "https://api.minimaxi.com/v1"
    model: "MiniMax-M2.7"
    provider: minimax
    timeout: 120
```

⚠️ **KNOWN ISSUE**: MiniMax-M2.7 API accepts `image_url` format in messages (no error),
but the model **does not actually process images** — it responds "I don't see any image."
This is a server-side format compatibility, not true multimodal support.
Do NOT use MiniMax for vision tasks until they release a dedicated VL model.

Available models on MiniMax (text only): `MiniMax-M2.7`, `abab6.5g-chat`, `abab6.5t-chat`, `abab6.5s-chat`

## Diagnostic Steps

### Test API Key Connectivity

```python
from openai import OpenAI

api_key = "your-api-key"
base_url = "https://api.moonshot.cn/v1"

client = OpenAI(api_key=api_key, base_url=base_url)
try:
    resp = client.chat.completions.create(
        model="kimi-k2.6",
        messages=[{"role": "user", "content": "hello"}],
        max_tokens=10
    )
    print("SUCCESS:", resp.choices[0].message.content)
except Exception as e:
    print(f"ERROR: {e}")
```

### Testing If a Model Actually Processes Images

Some models accept `image_url` format in API requests but **silently ignore images**. This is a known trap.

**Test method**: Send a real image and check if the response acknowledges it using the OpenAI Python SDK with appropriate api_key and base_url. If the model responds with color/object detection → true multimodal support. If it says "I don't see any image" → image was accepted but silently ignored.

**Known models that accept but don't process**: MiniMax-M2.7

### Common Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| 400 | Bad request format | Check model name, message format |
| 401 | Invalid authentication | API Key invalid/expired — create new one |
| 403 | Region/Quota limit | Switch model or top up account |
| 429 | Rate limited | Retry after waiting |

## Verification

After changing config, just send an image to Hermes — the vision tool will use the auxiliary model automatically. No restart needed.

## Key Pitfalls Discovered

1. **OpenRouter region lock**: gpt-4o, gemini models may be blocked in China. LLaMA Vision is safest fallback
2. **OpenRouter free tier exhaustion**: Returns 403 "Key limit exceeded" — check dashboard at openrouter.ai/settings/keys
3. **Kimi platform migration**: Keys from new platform (platform.kimi.com) may not work with old API domain (api.moonshot.cn) — create key on the correct platform
4. **MiniMax image format trap**: API accepts `image_url` format but model doesn't actually process images — always verify with a real test
5. **Config hot-reload**: config changes take effect immediately — no restart needed
6. **Hermes vision auto-detect**: When provider=auto, order is: main provider → OpenRouter → Nous
7. **Hermes does NOT recursively cron**: Cron-run sessions should not schedule more cron jobs

## Architecture-Level Debugging: `_build_call_kwargs` and `base_url` Routing

This section documents a subtle architecture-level issue discovered during debugging of the auxiliary client.

### The Problem

When patching `_build_call_kwargs()` in `agent/auxiliary_client.py` to add provider-specific behavior (e.g. forcing `temperature=1.0` for Kimi K2.6), using `base_url` as the discriminator **does not work** for named providers.

### Root Cause

**`_build_call_kwargs` receives `base_url=None` for named providers (moonshot, openrouter, anthropic, etc.).**

Call chain:

```
vision_analyze_tool()
  → async_call_llm(task="vision", temperature=0.1)
    → _resolve_task_provider_model("vision", provider="moonshot", ...)
        Returns: (provider="moonshot", model="kimi-k2.6", base_url=None, ...)
           ↑ Only returns a non-None base_url when provider is "custom"
    → resolve_vision_provider_client(provider="moonshot", ...)
        Builds the client internally — the moonshot.cn base URL is embedded
        in the provider routing, not surfaced to callers
    → _build_call_kwargs(provider="kimi-coding", base_url=None, ...)
        The Kimi temperature patch checks:
          "moonshot.cn" in (None or "" or "")  →  False  ❌
```

`_resolve_task_provider_model()` only returns a non-None `base_url` when:
- An explicit `base_url` argument is passed directly to `async_call_llm`/`call_llm`
- The config has `auxiliary.{task}.base_url` set (but only if `provider` is also "auto" or unset — setting both `base_url` and a named provider causes the config parser to return `custom` provider, not the named one)

Otherwise, `base_url` is always `None` because the named provider's endpoint URL is baked into the provider-specific routing code inside `resolve_provider_client()` / `resolve_vision_provider_client()`.

### How to Fix Such Patches

Use `provider` (the already-normalized string) rather than `base_url` to identify the provider:

```python
# BROKEN — base_url is None for named providers
if temperature is not None and temperature != 1.0:
    _kimi_base = base_url or _current_custom_base_url() or ""
    if "moonshot.cn" in _kimi_base.lower() or "kimi.com" in _kimi_base.lower():
        temperature = 1.0

# FIXED — use normalized provider name
if temperature is not None and temperature != 1.0:
    if provider == "kimi-coding" or provider == "kimi-coding-cn":
        temperature = 1.0
```

The `provider` parameter is already normalized by `_normalize_aux_provider()`:
- `moonshot` → `kimi-coding`
- `kimi` → `kimi-coding`
- `moonshot-cn` → `kimi-coding-cn`
- `kimi-cn` → `kimi-coding-cn`

### Verification: Confirm Process Loaded the Change

After editing `agent/auxiliary_client.py`:

```bash
# 1. Check if .pyc is fresher than .py (auto-recompile on import)
stat agent/__pycache__/auxiliary_client.cpython-*.pyc

# 2. Verify the running gateway process started AFTER the edit
ps -p <PID> -o etime,args --no-headers     # start time
stat agent/auxiliary_client.py              # file modification time
```

Since Hermes uses lazy imports (`from agent.auxiliary_client import ...` inside functions), the running process loads the latest version at each call — no restart needed unless the process started before the edit AND uses the class-level import (check `import` location).

### Lesson for Hermes Skills

When writing patches for `_build_call_kwargs` or any auxiliary client function:
- Use the `provider` parameter (already normalized) for provider-specific logic
- Do NOT rely on `base_url` — it's `None` for all named/built-in providers
- The only case where `base_url` is non-None: explicit URL override (either via function argument or `auxiliary.{task}.base_url` in config without a named provider)
