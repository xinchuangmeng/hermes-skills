# Feishu WebSocket 模式 — Encrypt Key 不需要！

## 问题
当创建第二个Hermes profile并使用独立飞书App时，`.env`模板包含 `FEISHU_ENCRYPT_KEY=你的加密密钥` 和 `FEISHU_VERIFICATION_TOKEN=***` 占位符。

## 关键发现
**长连接(WebSocket)模式下，Encrypt Key和Verification Token都不需要配置！**

飞书开发者后台页面明确写着「无需配置加密策略」。

## 正确配置

### `.env` 最少配置
```bash
FEISHU_APP_ID=cli_xxx              # 每个profile必须唯一
FEISHU_APP_SECRET=xxx              # 每个profile唯一
FEISHU_DOMAIN=feishu
FEISHU_CONNECTION_MODE=websocket
# Encrypt Key 和 Verification Token 不需要
```

### 飞书开发者后台操作步骤
1. 打开 https://open.feishu.cn/app → 对应App
2. 左侧菜单「事件与回调」→「事件配置」
3. 订阅方式选择「使用长连接接收事件」(WebSocket)
4. 点「添加事件」→ 至少添加 `im.message.receive_v1`
5. **Encrypt Key 和 Verification Token 不用填**
6. 启动gateway后，回后台点「重新验证」
