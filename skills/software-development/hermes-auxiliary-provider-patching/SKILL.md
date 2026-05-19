---
name: hermes-auxiliary-provider-patching
description: Pattern for writing provider-specific patches in Hermes Agent's auxiliary_client.py — using `provider` instead of `base_url` for conditional logic, since base_url is None for named providers
tags: [hermes, auxiliary, patching, provider, temperature, bugfix, vision, config]
version: 1.1
---

# Hermes Auxiliary Provider Patching

Trigger: when you need to add a model/provider-specific workaround in `agent/auxiliary_client.py` (e.g., forcing temperature, disabling max_tokens, adjusting parameters for a specific LLM).

## The Key Insight

In `_build_call_kwargs()` and related functions, **`base_url` is `None` for named providers** (e.g., `moonshot`, `deepseek`, `openai`). It only has a value when:

- `provider="custom"` and a `base_url` was explicitly passed
- A user configured `auxiliary.{task}.base_url` in config.yaml (which maps to `provider="custom"`)

This means **you cannot rely on matching `base_url` to detect named providers**.

## How Providers Flow Through the System

```
_config.yaml_
  auxiliary.vision.provider: moonshot   → normalized to "kimi-coding"
  auxiliary.vision.base_url: "https://api.moonshot.cn/v1"  → handled internally by resolve_vision_provider_client()

_call chain_
  async_call_llm()
    → _resolve_task_provider_model()
       returns: provider="kimi-coding", base_url=None
    → resolve_vision_provider_client()  ← base_url used internally here, NOT passed to _build_call_kwargs
    → _build_call_kwargs(provider="kimi-coding", base_url=None)  ← base_url is None!
```

## Correct Pattern

### ❌ Wrong (won't fire for named providers)
```python
if temperature is not None and temperature != 1.0:
    _kimi_base = base_url or _current_custom_base_url() or ""
    if "moonshot.cn" in _kimi_base.lower():
        temperature = 1.0
```

### ✅ Correct (use the already-normalized provider name)
```python
if temperature is not None and temperature != 1.0:
    _kimi_prov = (provider or "").lower()
    if _kimi_prov in ("kimi-coding", "kimi-coding-cn"):
        temperature = 1.0
```

## Provider Name Reference

The provider name in `_build_call_kwargs` is already normalized by `_resolve_task_provider_model` using `_PROVIDER_ALIASES` dict (around line 60-80 in auxiliary_client.py):

| Config value | Normalized provider |
|--------------|-------------------|
| `moonshot`, `kimi` | `kimi-coding` |
| `moonshot-cn`, `kimi-cn` | `kimi-coding-cn` |
| `google`, `google-gemini` | `gemini` |
| `x-ai`, `grok` | `xai` |
| `zhipu`, `glm` | `zai` |
| `minimax-china` | `minimax-cn` |
| `claude` | `anthropic` |
| `codex` | `openai-codex` |

## Configuring auxiliary.vision (important)

When you add an auxiliary vision provider (e.g. for image analysis when main model doesn't support vision):

**Do NOT use `api_key_env`** — Hermes does NOT support this parameter in `auxiliary.vision`. Using it causes 401 errors at runtime.

**Use `api_key` directly** to fill in the key:

```yaml
auxiliary:
  vision:
    provider: openrouter              # or kimi-coding, bailian, google, etc.
    model: qwen/qwen3.6-flash         # model that supports vision
    base_url: https://openrouter.ai/api/v1
    api_key: sk-or-v1-xxxxxxxxxxxxx   # ← DO NOT use api_key_env, fill the actual key
```

**Important caveats:**
- Changing `auxiliary.vision` config does NOT require gateway restart — changes apply to new vision calls immediately
- Authentication error (401) usually means `api_key_env` was used instead of `api_key`, or the provider model doesn't support vision
- The vision provider is independent from the main model provider — you can use DeepSeek for text + OpenRouter for vision simultaneously

## Where to Add Patches

The main entry point for parameter adjustments is `_build_call_kwargs()` (around line 2278 in auxiliary_client.py). This function builds the kwargs dict that's passed to `client.chat.completions.create()`. Patches here affect **all** auxiliary call types (vision, compression, web_extract, session_search, etc.).

For provider-specific patches, place them **after** the Anthropic `_forbids_sampling_params` check and **before** the final `if temperature is not None: kwargs["temperature"] = temperature` line.

## Verification

After patching, verify by:
1. Check the file is syntactically valid: `python3 -c "import ast; ast.parse(open('agent/auxiliary_client.py').read())"`
2. The `.pyc` cache will auto-rebuild on next import — no restart needed if the process started after the file was last modified.
3. For runtime testing, add a `logger.info(...)` to confirm the branch is hit.

## Real-World Example

The Kimi K2.6 temperature fix in this repo's `auxiliary_client.py` was initially written to match `base_url` containing `moonshot.cn`, which never fired because `base_url` was `None`. Fixed by matching `provider` against the normalized name `"kimi-coding"` instead.
