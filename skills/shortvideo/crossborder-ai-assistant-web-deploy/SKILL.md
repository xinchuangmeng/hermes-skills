---
name: crossborder-ai-assistant-web-deploy
title: 跨境AI助手Gradio网页版部署
description: 从零到一搭建跨境AI助手Gradio网页版——4个核心功能（AI对话/翻译/Listing优化/竞品分析）、必米云搜索集成、DeepSeek API调用、腾讯云部署全流程
tags: [crossborder, gradio, web-app, deepseek, bimiyun, api, deployment]
trigger: |
  当需要部署AI工具网页版时、搭建跨境外贸工具时、需要快速上线AI对话产品时
---

# 跨境AI助手Gradio网页版部署

## 架构

```
Gradio 6.x 网页界面
├── 💬 AI对话（DeepSeek + 跨境知识库）
├── 🌐 翻译（DeepSeek，中英马泰印尼越南）
├── 📝 Listing优化（DeepSeek，含标题/卖点/关键词）
└── 🔍 竞品分析（必米云搜索 + DeepSeek分析）
```

## 项目结构

```
~/sea-ecommerce/ai-assistant/
├── config.py       # 配置文件
├── ai_core.py      # AI核心（DeepSeek + 必米云）
├── app.py          # Gradio主界面（4个Tab）
├── start.sh        # 启动脚本
└── app.log         # 运行日志
```

## Gradio 6.x 关键变化（与5.x对比）

| 变更项 | 旧版写法 | 新版写法 |
|--------|---------|---------|
| theme/css | 放`gr.Blocks(theme=..., css=...)` | 放`app.launch(theme=..., css=...)` |
| Chatbot参数 | `bubble_full_width=False` | ⚠️ 已移除，会报TypeError |

## 四大功能实现模式

### 💬 AI对话
- `gr.Chatbot` + `gr.Textbox` + `msg.submit(respond, inputs, outputs)`
- 流式输出：yield 逐步返回内容

### 🌐 翻译
- `gr.Textbox`(输入) + `gr.Dropdown`(语言选择) + `gr.Button`(触发)
- 翻译prompt要带「跨境电商翻译专家」角色，指定语言习惯

### 📝 Listing优化
- 输入产品名+卖点+平台+市场 → 生成标题/5个卖点/描述/关键词/本地化建议
- 输出用Markdown格式，可在gr.Markdown中直接渲染

### 🔍 竞品分析
- 先用必米云搜索数据 → 塞进prompt让DeepSeek分析
- 关键：prompt里要加「信息不足就诚实说」

## 跨境系统提示词要点

```python
CROSSBORDER_SYSTEM_PROMPT = """你是「跨境AI助手」...

核心能力：
1. 平台运营（Shopee/Lazada/TikTok Shop/Amazon）
2. 选品建议 + Listing优化 + 广告策略
3. 翻译本地化（中英马泰印尼越南）
4. 竞品分析 + 市场调研
5. 合规与税务

风格要求：
- 专业简洁有实操建议 + 具体数字
- 不确定时诚实说「需要查证」
- 引用来源"""
```

## 部署步骤

最佳实践（推荐）：使用 Hermes `terminal(background=true)` 模式启动，Hermes 会跟踪进程生命周期：

```bash
cd ~/sea-ecommerce/ai-assistant

# 方式1（推荐）：先 ssh 到服务器，确认依赖已安装
pip3 install gradio openai httpx -i https://pypi.tuna.tsinghua.edu.cn/simple

# 然后用 Hermes terminal(background=true, notify_on_complete=true)
# 命令: cd ~/sea-ecommerce/ai-assistant && python3 app.py
```

备用方式（SSH直连场景）：
```bash
# 确保nohup输出被正确重定向
nohup python3 app.py > app.log 2>&1 &
# 验证启动成功
sleep 2 && ss -tlnp | grep 3000
```

### 端口配置

端口通过 `config.py` 中的 `PORT` 变量控制，不要硬编码在 `app.py` 中：

```python
# config.py
HOST = "0.0.0.0"
PORT = 3000  # ← 改这里
```

```python
# app.py 启动时读取 config.py 的 PORT/HOST
app.launch(server_name=HOST, server_port=PORT, ...)
```

修改后需要重启进程才能生效。先用 `kill <PID>` 停旧进程，再用上述方式启动新进程。

### 必米云搜索 API
```
POST https://search.bimiyun.com/api/web
Headers: X-API-Key: your_key, Content-Type: application/json
Body: {"query": "关键词", "num": 5}
返回: {"organic": [{"title": "...", "link": "...", "snippet": "..."}]}
```

## 已知坑

1. **nohup后台进程不继承shell环境变量** → 代码里兜底读配置文件
2. **Gradio 6.x theme/css位置变了** → 放launch()里
3. **腾讯云无代理导致SearXNG全timeout** → 改用必米云
4. **Gradio默认端口7860可能冲突** → 改成8080
