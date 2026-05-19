# 9527 飞书机器人 — 实际部署案例

## 概览

9527（东南亚电商助手）的飞书机器人使用本技能提供的模板搭建。
飞书应用名：`hermes 9527`，App ID: `cli_a96d18e5d2f89bde`

## 系统架构

```
用户发消息 → 飞书 WebSocket → lark-oapi WSClient → handle_message()
                                                          |
                                                    ┌─────┴──────┐
                                                    |            |
                                              get_reply()   发送回复
                                                    |
                                              ai_core.py
                                           (DeepSeek API)
```

## 关键代码路径

### 消息处理函数 (handle_message)

```python
def handle_message(data):
    msg = data.event.message
    content = json.loads(msg.content)
    text = content.get("text", "")

    # 注意：用 message_type 不是 msg_type
    log.info(f"chat_type={msg.chat_type} type={msg.message_type}")

    if msg.chat_type == "group" and not text.startswith("<at"):
        return  # 群聊未@跳过

    reply = get_reply(text, msg.chat_id)

    # 发送回复 — 必须分两步构建
    body = CreateMessageRequestBody.builder()
        .receive_id(msg.chat_id)
        .msg_type("text")
        .content(json.dumps({"text": reply[:2000]}))
        .build()
    req = CreateMessageRequest.builder()
        .receive_id_type("chat_id")
        .request_body(body)     # 不是 create_message_request_body()
        .build()
    resp = client.im.v1.message.create(req)
```

### 命令路由 (get_reply)

| 指令 | 功能 | 调用函数 |
|------|------|---------|
| 翻译 [泰语/马来/印尼/越南] 内容 | 翻译 | translate_text() |
| 优化/listing 产品名 卖点 | 生成Listing | optimize_listing() |
| 分析/竞品 品类名 | 竞品分析 | analyze_competitor() |
| 其他文本 | AI对话 | chat_with_deepseek() |

## 调试要点

1. 启动后看日志：tail -f /tmp/9527_feishu.log
2. 连接成功标志：connected to wss://msg-frontier.feishu.cn/ws/v2
3. 消息接收：receive message, event_type: im.message.receive_v1
4. 飞书应用需在开发者后台开启 im.message.receive_v1 事件

## 注意事项

- 机器人必须被手动拉入群聊才能接收群消息
- 运行在 /home/agentuser/sea-ecommerce/ai-assistant/ 目录下
- 使用 ai_core.py 作为业务逻辑层，与 Gradio Web 应用共享
- PID 管理：ps aux | grep 9527_feishu
- 日志路径：/tmp/9527_feishu.log
