---
name: feishu-websocket-bot-setup
title: 飞书 WebSocket 机器人搭建
description: 使用 lark-oapi SDK 搭建飞书 WebSocket 机器人，处理私聊和群聊消息，支持自定义事件处理和自动回复。
category: feishu
tags: [飞书, WebSocket, bot, lark-oapi, 消息处理]
---

# 飞书 WebSocket 机器人搭建

## 适用场景

需要给飞书应用配备一个自动回复的机器人，监听私聊和群聊消息，并调用自定义函数处理回复。适用于：
- 自定义 AI 助手（如 9527 东南亚电商助手）
- 企业内部工具机器人
- 与现有 Python 服务集成

## 前置条件

- 飞书应用已创建并获取 App ID 和 App Secret
- 应用的"机器人"能力已启用
- 已安装 `lark-oapi`：`pip install lark-oapi`
- 已安装 `websockets`：`pip install websockets`

## 架构概览

```
飞书 WebSocket ──→ lark-oapi WSClient ──→ EventDispatcherHandler
                                                │
                                      ┌─────────┴──────────┐
                                      │                     │
                                  接收消息              处理事件
                                      │                     │
                                  自定义函数          回复消息 API
```

## 核心代码模板

```python
import json, logging
from lark_oapi import Client as LarkClient
from lark_oapi.api.im.v1 import *
from lark_oapi.event.dispatcher_handler import EventDispatcherHandler
from lark_oapi.ws import Client as WSClient
from lark_oapi.core.enum import LogLevel

APP_ID = "your_app_id"
APP_SECRET = "your_app_secret"

def handle_message(data: P2ImMessageReceiveV1):
    """处理收到的消息事件"""
    msg = data.event.message
    if not msg or not msg.content:
        return
    
    # 解析消息内容
    content = json.loads(msg.content)
    text = content.get("text", "")
    
    # 群聊中只响应 @机器人的消息
    if msg.chat_type == "group":
        if not text.startswith("<at"):
            return
    
    # 生成回复（调用自定义函数）
    reply_text = your_reply_function(text)
    
    # 发送回复（注意：必须分两步构建 body 和 request）
    client = LarkClient.builder().app_id(APP_ID).app_secret(APP_SECRET).build()
    body = CreateMessageRequestBody.builder() \
        .receive_id(msg.chat_id) \
        .msg_type("text") \
        .content(json.dumps({"text": reply_text[:2000]})) \
        .build()
    req = CreateMessageRequest.builder() \
        .receive_id_type("chat_id") \
        .request_body(body) \
        .build()
    resp = client.im.v1.message.create(req)
    if resp.code == 0:
        log.info("消息发送成功")
    else:
        log.error(f"发送失败: {resp.code} {resp.msg}")


def main():
    # 构建事件处理器 (encrypt_key和verification_token传空字符串)
    handler = EventDispatcherHandler.builder("", "") \
        .register_p2_im_message_receive_v1(handle_message) \
        .build()
    
    # 启动 WebSocket 连接
    ws = WSClient(APP_ID, APP_SECRET, 
                  event_handler=handler, 
                  log_level=LogLevel.DEBUG)
    ws.start()

if __name__ == "__main__":
    main()
```

## 各组件说明

### 1. EventDispatcherHandler

```python
EventDispatcherHandler.builder(encrypt_key, verification_token)
    .register_p2_im_message_receive_v1(handler_function)
    .build()
```

- `encrypt_key` 和 `verification_token`：如果飞书应用没有配置加密，传空字符串 `""`
- `register_p2_im_message_receive_v1`：注册消息接收事件处理函数
- 签名：`Callable[[P2ImMessageReceiveV1], None]`

### 2. P2ImMessageReceiveV1 关键字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `event.message.chat_type` | str | `"p2p"` 私聊 / `"group"` 群聊 |
| `event.message.chat_id` | str | 聊天 ID（oc_开头群聊，ou_开头私聊） |
| `event.message.message_type` | str | `"text"` 文本消息 |
| `event.message.content` | str | JSON 字符串，文本内容在 `{"text": "..."}` |
| `event.message.sender.sender_id` | dict | 发送者信息 |

### 3. WSClient 参数

```python
WSClient(
    app_id,           # 飞书应用 App ID
    app_secret,       # 飞书应用 App Secret
    event_handler=handler,     # EventDispatcherHandler 实例
    log_level=LogLevel.INFO,   # 注意：必须传 LogLevel 枚举，不是 int
    domain="https://open.feishu.cn",
    auto_reconnect=True
)
```

**注意**：`log_level` 参数必须传 `LogLevel.DEBUG` 或 `LogLevel.INFO` 等枚举值，不能传 `logging.DEBUG`（int），否则会报 `AttributeError: 'int' object has no attribute 'value'`

### 4. 发送回复消息

```python
client = LarkClient.builder().app_id(APP_ID).app_secret(APP_SECRET).build()
body = CreateMessageRequestBody.builder()
    .receive_id(target_chat_id)
    .msg_type("text")
    .content(json.dumps({"text": reply_text}))
    .build()
req = CreateMessageRequest.builder()
    .receive_id_type("chat_id")
    .request_body(body)
    .build()
resp = client.im.v1.message.create(req)
if resp.code == 0:
    # 发送成功
```

**API 陷阱**：不要用 `.create_message_request_body()` — 这个方法不存在。正确的模式是：先用 `CreateMessageRequestBody.builder()` 建 body 对象，然后用 `CreateMessageRequest.builder().request_body(body)` 注入请求。`CreateMessageRequest.builder()` 没有 `create_message_request_body` 方法。

- 私聊和群聊都用 `chat_id` 作为 `receive_id_type`
- 群聊的 chat_id 以 `oc_` 开头
- 私聊的 chat_id 以 `oc_` 开头（不是 ou_，ou_ 是 open_id）

## 验证连接

启动后查看日志确认 WebSocket 连接成功：

```
connected to wss://msg-frontier.feishu.cn/ws/v2?...
ping success
```

连接成功后，在飞书给机器人发私聊消息，日志应显示：

```
收到消息事件! type=P2ImMessageReceiveV1
消息: chat_type=p2p chat_id=oc_xxx msg_type=text
```

## 检查机器人信息

```python
import httpx
resp = httpx.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    json={"app_id": APP_ID, "app_secret": APP_SECRET}, timeout=10)
token = resp.json()["tenant_access_token"]

bot = httpx.get("https://open.feishu.cn/open-apis/bot/v3/info",
    headers={"Authorization": f"Bearer {token}"}, timeout=10)
print(bot.json())
# 返回: {"bot": {"activate_status": 2, "app_name": "...", ...}, "code": 0}
```

`activate_status: 2` 表示机器人已激活。

## 常见坑点

1. **`LogLevel` 枚举**：`WSClient(log_level=LogLevel.DEBUG)` 不能传 `logging.DEBUG`（int 值）
2. **属性名陷阱 `msg_type` vs `message_type`**：事件对象 `EventMessage` 的属性叫 `message_type` 不是 `msg_type`（很多飞书文档错误地写成 `msg_type`）。在代码中用 `msg.message_type` 而不是 `msg.msg_type`
2. **群聊@检测**：群聊中收到消息时，文本内容以 `<at user_id="...">` 开头才表示被@
3. **消息内容解析**：飞书返回的 `content` 是 JSON 字符串，需要 `json.loads()` 解析
4. **Token 管理**：每次发送消息时创建新的 Client 实例即可，SDK 内部会管理 token 刷新
5. **WebSocket 重连**：`auto_reconnect=True` 是默认值，断线会自动重连
6. **发送后无回复**：确认机器人是否已加入群聊（需要有人工添加），确认是否在飞书开发者后台开启了"消息接收"事件

## 与 Gradio 应用共存

同一个 Gradio 应用可以与飞书机器人共享同一套业务逻辑：

```
gradio_app.py ──→ ai_core.py ←── feishu_bot.py
                    │
              DeepSeek API
```

- `ai_core.py` 包含核心业务逻辑（翻译、Listing优化、对话等）
- Gradio 和飞书 bot 都调用 `ai_core`，互不干扰
- 运行两个独立进程：Gradio Web 端口和飞书 WebSocket 机器人
