---
name: configure-bimiyun-search
description: >
  Bimiyun(必米云)搜索API配置与调用指南——国内直连、免费2000次/月、
  中文搜索质量高、速度快(平均0.8s)。配置Hermes作为Tavily的备用搜索源。
  替代SearXNG(需代理)和Tavily(有额度限制)的搜索需求。
tags:
  - bimiyun
  - search-api
  - chinese-search
  - free-tier
  - web-search
  - primary
  - 必米云
  - 搜索API
  - 中文搜索
  - 免费搜索
trigger:
  - "bimiyun"
  - "比米云"
  - "Bimiyun"
  - "必米云"
  - "搜索"
  - "bimiyun search"
  - "中文搜索"
---

# Bimiyun(必米云)搜索API配置指南

## 基本信息

| 项目 | 值 |
|------|-----|
| 服务商 | bimiyun.com（比米云） |
| **状态** | **✅ 当前主用搜索（2026/5/9起）** |
| 免费额度 | 2000次/月 |
| 超出价格 | $0.002/次 |
| 国内直连 | ✅ 腾讯云服务器可直连 |
| 响应速度 | ~0.8s |
| 中文质量 | 优（85%中文结果） |
| API方式 | **POST**（不是GET） |

## ⚠️ 重要发现：web_search默认不走必米云

**web_search工具默认绑定Tavily！** 即使配了必米云Key，`web_search()`仍然是调Tavily。

**必米云只能在以下方式使用：**
1. `execute_code` 里手动调curl或Python
2. `terminal` 里直接curl

**不能通过web_search使用。**

---

## API调用方式

### 端点（POST）

```bash
POST https://search.bimiyun.com/api/web
Content-Type: application/json
X-API-Key: ak-68623a4a18764f7b83fd6aece95b01f4

{"query":"搜索关键词","num":结果数}
```

### 响应格式

```json
{
  "organic": [
    {
      "title": "标题",
      "link": "https://...",
      "snippet": "摘要...",
      "position": 1,
      "date": "",
      "site_name": ""
    }
  ]
}
```

### curl 示例（已验证可用 ✅）

```bash
curl -s --max-time 15 -X POST 'https://search.bimiyun.com/api/web' \
  -H 'X-API-Key: ak-68623a4a18764f7b83fd6aece95b01f4' \
  -H 'Content-Type: application/json' \
  -d '{"query":"跨境电商 2026","num":5}'
```

### Python execute_code 调用方式

```python
import urllib.request, json

def bimiyun_search(query, num=5):
    data = json.dumps({"query": query, "num": num}).encode()
    req = urllib.request.Request(
        'https://search.bimiyun.com/api/web',
        data=data,
        headers={
            'X-API-Key': 'ak-68623a4a18764f7b83fd6aece95b01f4',
            'Content-Type': 'application/json'
        }
    )
    resp = urllib.request.urlopen(req, timeout=15)
    return json.loads(resp.read().decode())
```

## ⚠️ 必米云和web_search的区别（重要！）

```python
# ✅ 正确方式：手动调Python/curl调用必米云
import requests
resp = requests.post(
    "https://search.bimiyun.com/api/web",
    headers={"X-API-Key": "ak-68623a4a18764f7b83fd6aece95b01f4", "Content-Type": "application/json"},
    json={"query": "搜索关键词", "num": 5},
    timeout=15
)
results = resp.json().get("organic", [])

# ❌ 错误方式：web_search走的是Tavily，不管Key
# web_search(query="关键词")  # 这个走Tavily，不是必米云！
```

**重要提醒：** 每次使用必米云时，**必须先加载本技能查看正确端点**。本技能的API调用方式在2026/5/11已验证为正确（POST + X-API-Key + search.bimiyun.com/api/web）。

## 何时使用

**必米云是目前主力搜索，Tavily和SearXNG暂不可用时优先使用。**

| 场景 | 推荐 |
|------|------|
| 中文内容搜索 | ✅ 必米云（85%中文结果） |
| 需要稳定国内直连 | ✅ 必米云 |
| web_search工具调用 | ❌ 走Tavily，无法用必米云 |
| execute_code里搜索 | ✅ 手动调必米云 |
| terminal里curl | ✅ 直接用 |

## 其他搜索工具当前状态

| 工具 | 状态 | 原因 |
|------|------|------|
| ✅ **必米云** | **主力可用** | 国内直连，2000次/月免费 |
| ❌ Tavily | 额度耗尽(432) | 免费1000次/月用完了，需充值或新号 |
| ❌ SearXNG | 全timeout | 腾讯云无出海代理，93个引擎全挂 |

## 当前项目中的Key

```
X-API-Key: ak-68623a4a18764f7b83fd6aece95b01f4
```

**注意：这个Key只存在技能和记忆里，没有配到任何.env文件中。**
所以每次在execute_code或terminal中使用时，必须手动传入Key。
