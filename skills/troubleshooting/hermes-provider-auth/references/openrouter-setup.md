# OpenRouter 配置参考

> 适用场景：在 Hermes Agent 中配置 OpenRouter 作为 LLM Provider

## 配置方式

### 方式 A：交互式（推荐）

```bash
hermes model
```

交互选择 OpenRouter → 按提示输入 API Key → 选择模型。**这是最靠谱的方式。**

### 方式 B：手动编辑 config.yaml（非交互环境）

当 `hermes model` 报错 "requires an interactive terminal" 时（比如通过飞书/远程访问），手动改配置：

```yaml
# ~/.hermes/config.yaml
model:
  default: openrouter/<provider>/<model-id>    # 例如 openrouter/deepseek/deepseek-v4-pro
  provider: openrouter
```

同时在 `.env` 中设置 API Key：

```bash
# ~/.hermes/.env
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxx
```

或者直接写进 config.yaml（不推荐，但有 key 分隔需求的场景可用）：

```yaml
openrouter_api_key: sk-or-v1-xxxxxxxxxxxx
```

## 可用模型查询

用你的 API Key 查询 OpenRouter 支持的模型列表：

```bash
curl -s https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer $OPENROUTER_API_KEY"
```

## 推荐模型（2026年5月实测可用）

| 模型 ID | 上下文 | 特点 |
|:--|:--:|:--|
| `deepseek/deepseek-v4-pro` | 1049K | DeepSeek V4 旗舰，性价比高 |
| `deepseek/deepseek-v4-flash` | 1049K | 快速版，适合简单任务 |
| `qwen/qwen3.6-35b-a3b` | 262K | 通义千问 MOE，高效 |
| `qwen/qwen3.6-max-preview` | 262K | Qwen 最新旗舰 |
| `openai/gpt-5.5` | 1050K | OpenAI 最新 |
| `~openai/gpt-latest` | 1050K | OpenAI 最新跟随 |
| `~anthropic/claude-sonnet-latest` | 1000K | Claude Sonnet 最新 |
| `~google/gemini-pro-latest` | 1049K | Gemini Pro 跟随最新 |
| `google/gemini-2.5-pro` | 1049K | Gemini 2.5 Pro（正式版） |
| `google/gemini-3.1-pro-preview` | 1049K | Gemini 3.1 Pro（最新预览版） |

> `~` 前缀表示 OpenRouter 的 Alias 模型（自动跟踪最新版本）

## 结合 SkillClaw 使用

如果同时运行 SkillClaw（在 localhost:30001 作为 DeepSeek 代理），切换 OpenRouter 后 SkillClaw **不会自动停止**。有两种处理方式：

**方式一：保留 SkillClaw 作为备用**
- 不改动 SkillClaw 进程
- Hermes 走 OpenRouter，不冲突
- 日后如需切换回 DeepSeek，只需改 config.yaml 回 `provider: custom + base_url: http://127.0.0.1:30001/v1`

**方式二：停掉 SkillClaw 释放资源**
```bash
kill $(lsof -ti :30001) 2>/dev/null
# 然后清理 config.yaml 中的 custom provider 配置
```

## 模型命名规则（重要！）

```yaml
# ✅ 正确写法（去掉 openrouter/ 前缀）
model: google/gemini-2.5-pro

# ❌ 错误写法（带 openrouter/ 前缀 → 400 Bad Request）
model: openrouter/google/gemini-2.5-pro-preview-03-25

# ❌ 错误写法（含日期后缀 → 一旦过期就是 400）
model: openrouter/google/gemini-2.5-pro-preview-03-25
```

**两条铁律：**
1. **不要带 `openrouter/` 前缀** — 模型ID就是 `provider/model-name` 格式
2. **不要用带日期的预览版**（如 `-03-25`）— 一个月内必过期，用 `google/gemini-2.5-pro` 或 `~` 别名

## ⚠️ 国内服务器（腾讯云/阿里云）关键陷阱：Gemini/Claude 403 区域封锁

**症状：** Google Gemini 所有模型返回 HTTP 403；Claude 部分模型也 403
**根因：** 腾讯云/阿里云等国内云厂商的 IP 段被 Google/Anthropic 地毯式封锁，与 OpenRouter 无关
**验证方法：**
```bash
# Google → 403
curl -s -o /dev/null -w "%{http_code}" -X POST https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -d '{"model":"google/gemini-2.5-pro","messages":[{"role":"user","content":"hi"}],"max_tokens":5}'

# DeepSeek → 200（对比）
curl -s -o /dev/null -w "%{http_code}" -X POST https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -d '{"model":"deepseek/deepseek-chat","messages":[{"role":"user","content":"hi"}],"max_tokens":5}'
```

**国内云能用的模型：** DeepSeek、Qwen、Llama、OpenAI（大部分可用）
**被封锁的：** Google Gemini 全系列、Anthropic Claude 系列

### 方案 A：国内 API 中转站（推荐）

中转站兼容 OpenAI 协议，改 `base_url` + `api_key` 就行，代码不用动：

| 平台 | 特点 | 适合 |
|------|------|------|
| **4SAPI**（星链） | CN2 专线，全模型支持 | 稳定性优先 |
| **PoloAPI** | 老牌，0.15 折 Claude，支付宝 | 性价比优先 |
| **SiliconFlow** | 国内直连开源模型 | 已有 DeepSeek Key 的补充 |
| **NoneLinear** | 智能代理架构，99.99% 可用率 | 企业级需求 |

配置示例：
```yaml
# config.yaml
model:
  default: gemini-2.5-pro
  provider: custom
openai_base_url: https://xxx.com/v1  # 中转站地址
openai_api_key: sk-xxx               # 中转站 Key
```

### 方案 B：家用机中转

小强/旺财（Windows 本地）走家里宽带 → OpenRouter 上的 Gemini/Claude 正常可用（家庭宽带 IP 未被封锁）。

## 故障排查

| 症状 | 原因 | 修复 |
|:--|:--|:--|
| `No inference provider configured` | OpenRouter Key 未被读取 | 检查 `OPENROUTER_API_KEY` 是否在 `.env` 中 |
| 模型返回 404 | 模型 ID 拼写错误 | 用 `curl` 查模型列表确认正确 ID |
| 模型返回 403（Gemini/Claude） | 国内服务器 IP 被封锁 | 见上方「区域封锁」方案 A/B |
| 配置生效但报认证错误 | Key 无效或额度耗尽 | 检查 OpenRouter 后台额度 |
