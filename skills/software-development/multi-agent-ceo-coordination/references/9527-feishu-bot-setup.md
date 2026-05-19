# 9527 Feishu Bot Setup (lark-oapi WebSocket)

> Created: 2026-05-17
> Purpose: Give 9527 (Gradio e-commerce assistant) its own Feishu bot identity

## Overview

9527 runs as a Gradio web app on port 3000. To let it receive/send messages in Feishu, create a standalone Python bot using `lark-oapi` WebSocket client. This is **not** a full Hermes Agent instance — it's a lightweight script that:

1. Connects to Feishu via WebSocket (using its own App ID/Secret)
2. Listens for messages in DM and group chats
3. Calls `ai_core.py` functions to process e-commerce tasks
4. Sends responses via Feishu API

## Prerequisites

```bash
pip3 install lark-oapi
# Verify: python3 -c "import lark_oapi; print('OK')"
```

## Credentials

Register a Feishu app at `https://open.feishu.cn/app`:
- App ID: `cli_xxx`
- App Secret: `xxx`
- Enable Bot capability
- Subscribe to `im.message.receive_v1` event
- Add permissions: `im:message` (send messages)

## Script Structure

The bot script lives at `/root/.hermes/scripts/9527_feishu_bot.py`:

```python
import sys, json, logging
sys.path.insert(0, "/home/agentuser/sea-ecommerce/ai-assistant")
from ai_core import chat_with_deepseek, translate_text, optimize_listing, analyze_competitor

from lark_oapi import Client as LarkClient
from lark_oapi.api.im.v1 import *
from lark_oapi.event.dispatcher_handler import EventDispatcherHandler
from lark_oapi.ws import Client as WSClient

APP_ID = "cli_xxx"
APP_SECRET = "xxx"

def handle_message(data: P2ImMessageReceiveV1):
    """Process incoming Feishu messages and reply"""
    msg = data.event.message
    if not msg or msg.msg_type != "text":
        return
    
    # Parse text content
    content = json.loads(msg.content)
    text = content.get("text", "")
    
    # Skip group messages not mentioning the bot
    if msg.chat_type == "group":
        if not text.startswith("<at") and "9527" not in text:
            return
    
    # Route to appropriate ai_core function based on text prefix
    reply = get_reply(text, msg.chat_id)
    
    # Send reply via Feishu API
    client = LarkClient.builder().app_id(APP_ID).app_secret(APP_SECRET).build()
    content = json.dumps({"text": reply[:2000]})
    req = CreateMessageRequest.builder() \
        .receive_id_type("chat_id") \
        .create_message_request_body(
            CreateMessageRequestBody.builder()
                .receive_id(msg.chat_id)
                .msg_type("text")
                .content(content).build()
        ).build()
    client.im.v1.message.create(req)

def get_reply(text, chat_id):
    """Route message text to correct ai_core function"""
    text = text.strip()
    if text.startswith("翻译"):
        # Extract target language and content
        ...
    elif text.startswith("优化") or text.startswith("listing"):
        ...
    elif text.startswith("分析") or text.startswith("竞品"):
        ...
    else:
        # Default: AI chat with history
        ...

# Build event handler
handler = EventDispatcherHandler.builder("", "") \
    .register_p2_im_message_receive_v1(handle_message) \
    .build()

# Connect via WebSocket
ws = WSClient(APP_ID, APP_SECRET, event_handler=handler)
ws.start()  # Blocking
```

## Running the Bot

```bash
cd /home/agentuser/sea-ecommerce/ai-assistant
python3 /root/.hermes/scripts/9527_feishu_bot.py
```

Run as background process:
```bash
# Via terminal(background=true) in Hermes
terminal(background=True, 
    command="cd /home/agentuser/sea-ecommerce/ai-assistant && python3 /root/.hermes/scripts/9527_feishu_bot.py")
```

## Verifying WebSocket Connection

```bash
# Check process is running
ps aux | grep 9527_feishu

# Check WebSocket connection (look for ESTAB to feishu.cn)
ss -tnp | grep python3

# Send a test message via Feishu API
python3 << 'EOF'
import httpx
resp = httpx.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    json={"app_id": APP_ID, "app_secret": APP_SECRET})
token = resp.json()["tenant_access_token"]
# Send DM to user
httpx.post("https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
    headers={"Authorization": f"Bearer {token}"},
    json={"receive_id": "oc_xxx", "msg_type": "text", "content": '{"text":"test"}'})
EOF
```

## ⚠️ Critical: Set the Bot's Identity in the Prompt (Most Commonly Missed Step)

**Without this, the bot will tell users "I'm DeepSeek" or "I'm an AI assistant" instead of its actual identity.**

Root cause: The bot's code initializes the DeepSeek API client but doesn't pass a system prompt. The LLM defaults to whatever its training data says ("I am DeepSeek, an AI model created by...").

**Fix:** Add a system prompt explicitly. The easiest way is to modify `ai_core.py`'s `chat_with_deepseek` function to accept a system prompt parameter, or hardcode it:

```python
# In the bot script, before calling chat_with_deepseek:
SYSTEM_PROMPT = """你是9527，东南亚电商助手。
你运行在腾讯云服务器(159.75.89.135)上，跟小书童（Hermes Agent）在同一台服务器。
你的核心能力：翻译（中/英/泰/马来/印尼/越南语）、商品Listing优化、竞品分析。
你不能做的事：不能执行命令、不能访问文件系统、没有记忆（每次重启都会忘记之前的对话）。
你归小书童（Hermes Agent的CEO）管。"""
```

Then pass it to the LLM call:

```python
messages = [{"role": "system", "content": SYSTEM_PROMPT}]
# + user message history
```

**Checklist:**
- [ ] Bot knows its own name and role
- [ ] Bot knows where it runs
- [ ] Bot knows its capabilities
- [ ] Bot knows its limitations (no skills/memory/tools)
- [ ] Bot knows who manages it

## Redundancy Warning: Standalone Bot in Same Group as Full Agent

If a Full Hermes Agent (小书童) and this standalone bot (9527) are both in the same Feishu group, **the standalone bot adds no value** unless it has unique capabilities the main agent lacks:

| Scenario | Value Add? |
|----------|-----------|
| Bot has unique domain knowledge (e.g. shops-specific RAG) | ✅ Maybe useful |
| Bot serves users the main agent cannot reach | ✅ Maybe useful |
| Bot just calls the same LLM API as the main agent | ❌ Redundant |
| Bot has NO tools/memory/skills while main agent has all | ❌ Redundant |

If redundant, either:
- **Remove the bot** (the main agent handles everything)
- **Give the bot a unique skill** (e.g. real-time Shopee API data feed, price monitoring, etc.)
- **Repurpose the bot** as a specialized tool (e.g. translation-only bot, or a "群公告" announcement bot)

## Common Issues

| Issue | Diagnosis | Fix |
|-------|-----------|-----|
| Bot doesn't respond in group | Bot not added to group | Add manually via group settings |
| `No module 'hermes_cli.platforms.feishu'` | Wrong import | Use lark-oapi directly, not Hermes internals |
| WebSocket connects but messages not received | Wrong event subscribed | Register `p2_im_message_receive_v1` |
| `AttributeError: module 'lark_oapi' has no attribute 'WSClient'` | Wrong API | Use `lark_oapi.ws.Client` |
| `EventDispatcherHandler.builder() missing arguments` | Need encrypt_key/verification_token | Pass empty strings `('', '')` |
| Bot responds in DM but not in group | @mention detection issue | Check `text.startswith("<at")` logic |
