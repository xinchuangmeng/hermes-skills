---
name: feishu-send-image-from-server
title: 从服务器发送图片到飞书群聊/私聊
description: 通过飞书HTTP API从服务器上传PNG/JPG图片并发送到飞书群聊或私聊的完整流程。包含获取tenant_access_token、multipart/form-data上传图片、发送image消息三个步骤。
category: feishu
tags: [飞书, 图片发送, API, HTTP, multipart, image]
---

# 从服务器发送图片到飞书群聊/私聊

## 适用场景

在服务器上用Python Pillow或其他方式生成了图片（如Logo、数据图表、预览图等），需要直接发送到飞书群聊或私聊。

**核心限制**：Hermes的 `send_message` 工具只支持文本消息，无法附图片。需要通过飞书HTTP API手动完成。

## 完整工作流

### 前置条件

- 飞书App ID和App Secret（在 `~/.hermes/profiles/<profile_name>/.env` 中 `FEISHU_APP_ID` 和 `FEISHU_APP_SECRET`）
- 目标群聊/私聊的 chat_id（通过 `send_message(action='list')` 获取）

### 步骤1：获取tenant_access_token

```python
import json, urllib.request

env_path = "/home/agentuser/.hermes/profiles/southeast-ecommerce/.env"
# 从.env读取FEISHU_APP_ID和FEISHU_APP_SECRET

token_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
token_data = json.dumps({
    "app_id": app_id,
    "app_secret": app_secret
}).encode("utf-8")

req = urllib.request.Request(token_url, data=token_data, headers={
    "Content-Type": "application/json"
})

with urllib.request.urlopen(req, timeout=10) as resp:
    token_json = json.loads(resp.read())
    access_token = token_json.get("tenant_access_token", "")
```

### 步骤2：上传图片（multipart/form-data）

使用 `POST https://open.feishu.cn/open-apis/im/v1/images` 上传：

```python
boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
with open(file_path, "rb") as f:
    file_data = f.read()

body_bytes = b""
body_bytes += f'--{boundary}\r\n'.encode()
body_bytes += 'Content-Disposition: form-data; name="image_type"\r\n'.encode()
body_bytes += 'Content-Type: text/plain\r\n\r\n'.encode()
body_bytes += b'message\r\n'
body_bytes += f'--{boundary}\r\n'.encode()
body_bytes += f'Content-Disposition: form-data; name="image"; filename="{file_name}"\r\n'.encode()
body_bytes += 'Content-Type: image/png\r\n\r\n'.encode()
body_bytes += file_data
body_bytes += f'\r\n--{boundary}--\r\n'.encode()

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": f"multipart/form-data; boundary={boundary}",
}

req = urllib.request.Request(
    "https://open.feishu.cn/open-apis/im/v1/images",
    data=body_bytes, headers=headers
)
with urllib.request.urlopen(req, timeout=30) as resp:
    result = json.loads(resp.read())
    image_key = result.get("data", {}).get("image_key", "")
```

**重要参数**：
- `image_type` 固定为 `"message"`（图片用于消息发送）
- `Content-Type` 根据图片格式设置（`image/png`, `image/jpeg` 等）

### 步骤3：发送图片消息

```python
msg_content = json.dumps({"image_key": image_key})
msg_body = json.dumps({
    "receive_id": chat_id,
    "msg_type": "image",
    "content": msg_content
}).encode("utf-8")

msg_req = urllib.request.Request(
    f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
    data=msg_body,
    headers={
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
)

with urllib.request.urlopen(msg_req, timeout=30) as msg_resp:
    msg_result = json.loads(msg_resp.read())
    # msg_result.get("code") == 0 表示成功
```

**注意**：
- `receive_id_type=chat_id` 用于群聊（oc_开头），如果是私聊（ou_开头）需要改为 `open_id`
- 群聊 chat_id 格式：`oc_xxxxxxxxxxxxxxxxxxxxxx`
- 私聊 open_id 格式：`ou_xxxxxxxxxxxxxxxxxxxxxx`

## 常见坑点

1. **lark_oapi的`core.file`不存在** → 不要用Python SDK的 `lark.core.file.File`，直接用原始HTTP请求更可靠
2. **429限流** → Vision API对同一账户有并发限制（默认3），发送时注意不要并发太多
3. **Token过期** → tenant_access_token有效期2小时，每次发送前重新获取
4. **图片大小限制** → 飞书图片上传限制20MB以内
5. **发送后补充文字说明** → 图片发送后可以用 `send_message` 补充文字说明

## 完整脚本模板

参考 `/home/agentuser/sea-ecommerce/send_logos_http.py`，核心函数：

```python
def send_feishu_image(access_token, chat_id, file_path):
    \"\"\"发送图片到飞书群聊。返回True/False。\"\"\"
    # 步骤2 + 步骤3 的代码合并
```

## Hermes之家群聊chat_id

当前已知：
- Hermes之家群：`oc_28767f98f032653b31955095f974fb7c`（通过 `send_message(action='list')` 确认）
