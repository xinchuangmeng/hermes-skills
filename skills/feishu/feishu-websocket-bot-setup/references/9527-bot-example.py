#!/usr/bin/env python3
"""
9527 飞书机器人 - 东南亚电商助手
使用 lark-oapi WebSocket 连接，监听飞书消息，调用 ai_core 处理回复。

启动方式：
  cd /home/agentuser/sea-ecommerce/ai-assistant && python3 9527_feishu_bot.py

前置条件：
  pip install lark-oapi websockets
  export DEEPSEEK_API_KEY=xxx  （或在 .env 中配置）
"""
import sys, json, logging, os

# 导入 9527 的 ai_core
sys.path.insert(0, "/home/agentuser/sea-ecommerce/ai-assistant")
from ai_core import chat_with_deepseek, translate_text, optimize_listing, analyze_competitor

from lark_oapi import Client as LarkClient
from lark_oapi.api.im.v1 import *
from lark_oapi.event.dispatcher_handler import EventDispatcherHandler
from lark_oapi.ws import Client as WSClient
from lark_oapi.core.enum import LogLevel

# 日志
log_path = "/tmp/9527_feishu.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(log_path), logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger("9527")

APP_ID = "cli_a96d18e5d2f89bde"
APP_SECRET = "C1Ihe7dhbBKaSkd4rWxbMf4vBGXVijHL"
chat_histories: dict = {}

def get_reply(text: str, chat_id: str = "") -> str:
    """根据消息内容选择合适的 ai_core 函数处理"""
    t = text.strip()
    # 翻译指令
    if t.startswith("翻译"):
        target = "en"
        if "泰语" in t: target = "th"
        elif "马来" in t: target = "ms"
        elif "印尼" in t: target = "id"
        elif "越南" in t: target = "vi"
        elif "中文" in t: target = "zh"
        c = t[2:].strip()
        if c: return translate_text(c, target)
    # Listing 优化
    if t.startswith("优化") or t.startswith("listing"):
        p = t.split(None, 2)
        if len(p) >= 2: return optimize_listing(p[1], p[2] if len(p) >= 3 else "")
    # 竞品分析
    if t.startswith("分析") or t.startswith("竞品"):
        c = t.split(None, 1)[1] if " " in t else ""
        if c: return analyze_competitor(c)
    # 默认：AI 对话
    history = chat_histories.get(chat_id, [])
    full = ""
    for chunk in chat_with_deepseek(t, history):
        full = chunk
    chat_histories[chat_id] = (history + [(t, full)])[-10:]
    return full


def handle_message(data: P2ImMessageReceiveV1):
    """处理收到的飞书消息"""
    log.info(f"收到消息: type={type(data).__name__}")
    try:
        msg = data.event.message
        content = json.loads(msg.content)
        text = content.get("text", "")
        log.info(f"来自 {msg.chat_type} | {text[:60]}...")

        # 群聊只响应 @机器人的消息
        if msg.chat_type == "group" and not text.startswith("<at"):
            log.info("群消息未@我，跳过")
            return

        reply = get_reply(text, msg.chat_id)
        log.info(f"回复: {reply[:40]}...")

        # 发送回复
        client = LarkClient.builder().app_id(APP_ID).app_secret(APP_SECRET).build()
        req = CreateMessageRequest.builder() \
            .receive_id_type("chat_id") \
            .create_message_request_body(
                CreateMessageRequestBody.builder()
                    .receive_id(msg.chat_id)
                    .msg_type("text")
                    .content(json.dumps({"text": reply[:2000]}))
                    .build()
            ).build()
        resp = client.im.v1.message.create(req)
        log.info(f"发送结果: code={resp.code} msg={resp.msg}")
    except Exception as e:
        log.error(f"处理异常: {e}", exc_info=True)


def main():
    log.info("=" * 50)
    log.info(f"9527 飞书机器人启动 | PID={os.getpid()} | App={APP_ID}")
    
    handler = EventDispatcherHandler.builder("", "") \
        .register_p2_im_message_receive_v1(handle_message) \
        .build()
    
    ws = WSClient(APP_ID, APP_SECRET, event_handler=handler, log_level=LogLevel.DEBUG)
    log.info("正在连接飞书 WebSocket...")
    ws.start()


if __name__ == "__main__":
    main()
