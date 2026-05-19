---
name: agent-auto-llms-discovery-protocol
title: LLM站点发现协议——llms.txt和agent-capabilities.md标准
description: "新兴的Web标准让网站为AI Agent和LLM提供结构化信息：/llms.txt（站点摘要给LLM）和/agent-capabilities.md（能力声明给AI Agent）以及/.well-known/ucp（统一通信协议）。Shopify已为所有商店启用。涵盖格式、配置和Agent使用策略。"
tags: [agent-auto, web-standards, discovery, llm, infrastructure]
trigger: |
  当AI Agent需要发现网站能力、或搭建Agent可消费的站点接口时
---

# LLM站点发现协议

## 核心洞察

### Web Agent能力发现标准

从2026年开始，一个新兴的Web标准正在形成——让网站通过专用端点为AI Agent和LLM提供结构化信息：

| 端点 | 用途 | 面向目标 |
|------|------|----------|
| `/llms.txt` | Markdown格式的站点摘要和关键文档 | LLM（语言模型检索） |
| `/agent-capabilities.md` | AI Agent能力声明、API端点 | AI Agent（自主智能体） |
| `/.well-known/ucp` | 统一通信协议（UCP） | 跨平台Agent通信 |

### 现实案例

> **Shopify自动启用：** Shopify已悄然为所有商店自动部署了`/llms.txt`、`/agent-capabilities.md`和`/.well-known/ucp`端点（来源：Dev.to @no7software, 2026-05-16）。
> 这意味着Shopify上的每个店铺现在都有一个AI Agent可以直接阅读的结构化接口。
>
> **开发者指南：** 商家可以通过Shopify的`theme.liquid`或Custom Data API覆盖或补充默认内容。

## 各端点详解

### 1. `/llms.txt` — 给LLM的站点摘要

**格式：** 纯Markdown

**目的：** 给LLM/搜索引擎一个站点的结构化摘要，和`robots.txt`类似但针对AI场景

```markdown
# Site Name
> Site description for LLMs

## Core Documentation
- [Getting Started](/docs/getting-started): Quick start guide
- [API Reference](/docs/api): Complete API documentation
- [FAQ](/docs/faq): Frequently asked questions

## Key Pages
- [Home](/)
- [Products](/products)
- [Blog](/blog)

## Structured Data
- Company: Acme Inc
- Founded: 2020
- Employees: 50-100
- Industry: SaaS
```

**在Agent场景中的用途：**
- LLM搜索引擎在抓取前快速了解站点结构
- Agent在访问网站前预读站点摘要，减少不必要的页面爬取
- 比AI去读HTML页面再自己总结高效得多

### 2. `/agent-capabilities.md` — 给Agent的能力声明

**格式：** Markdown + 结构化指令

**目的：** 告诉来访的AI Agent「你能帮我做什么」以及「怎么做」

```markdown
# [Site Name] Agent Capabilities

## Available Actions
- `search_products(query, limit=10)` → 搜索商品
- `get_product_details(sku)` → 获取商品详情
- `check_inventory(sku)` → 检查库存
- `get_order_status(order_id)` → 查询订单状态

## Authentication
- 所有Agent操作需要API Key: `Authorization: Bearer <key>`
- 限速: 100 req/min

## Agent Rules
1. 必须标识自己为AI Agent
2. 不要承诺价格，让用户确认当前价格
3. 不要承诺配送日期，只说"预估"
4. 确认库存后再下单
```

**在Agent场景中的用途：**
- Agent到达网站后先读能力声明，了解自己能做什么、不能做什么
- 比传统REST API文档更适合AI Agent消费
- 定义了Agent的操作权限和行为边界

### 3. `/.well-known/ucp` — 统一通信协议

**格式：** JSON

**目的：** Agent间的标准化通信接口

```json
{
  "protocol": "ucp/1.0",
  "capabilities": ["chat", "task", "notification", "payment"],
  "endpoints": {
    "chat": {
      "url": "https://example.com/ucp/chat",
      "methods": ["send", "receive", "history"]
    },
    "task": {
      "url": "https://example.com/ucp/task",
      "methods": ["create", "status", "cancel"]
    }
  },
  "auth": {
    "type": "oauth2",
    "scopes": ["agent:basic", "agent:read", "agent:write"]
  }
}
```

## 实操指南

### 检查现有站点

```bash
# 检查站点是否已支持
curl -s https://example.com/llms.txt | head -20
curl -s https://example.com/agent-capabilities.md | head -20
curl -s https://example.com/.well-known/ucp

# 检查Shopify店铺
curl -s https://any-shop.myshopify.com/llms.txt
curl -s https://any-shop.myshopify.com/agent-capabilities.md
```

### 为自己的站点添加端点

```bash
# Nginx配置：添加llms.txt
location /llms.txt {
    alias /var/www/site/llms.txt;
    default_type text/markdown;
}

# Nginx配置：添加capabilities端Point
location /agent-capabilities.md {
    alias /var/www/site/agent-capabilities.md;
    default_type text/markdown;
}
```

### 对Hermes Agent的使用策略

1. **搜索前先读`/llms.txt`** — 在爬取整个网站前先检查这个文件，能节省大量token和请求
2. **优先按能力声明交互** — 如果目标网站有`/agent-capabilities.md`，优先按它定义的操作方式来交互
3. **UCP值得关注** — 如果未来需要Hermes与其他Agent协作跨平台，这是标准化方向
4. **自己搭建站点时主动支持** — 增加这些端点能让站点对AI搜索和Agent更友好

## 注意事项

1. **这是新兴标准** — 尚未被W3C标准化，但Shopify的采用是重要信号
2. **不要依赖它的存在** — 绝大多数网站尚未支持，返回404是常态
3. **能力声明的定义权在网站方** — Agent应该遵守其中的规则，而非忽略
4. **UCP还在早期** — 目前主要是大平台Agent之间使用
5. **安全边界** — 能力声明中定义的API需要有独立的Agent认证机制
