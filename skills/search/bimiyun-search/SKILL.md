---
name: bimiyun-search
description: 必米云搜索API配置与调用指南——国内直连、免费2000次/月、中文搜索质量高。备用搜索源，当Tavily额度耗尽(432 error)时使用。支持在execute_code中用Python requests或terminal中curl调用。
category: search
---

# 必米云搜索API调用指南

## 基本信息

| 项目 | 值 |
|------|-----|
| 服务商 | bimiyun.com（比米云） |
| 免费额度 | 2000次/月 |
| 超出价格 | $0.002/次 |
| 国内直连 | ✅ 腾讯云服务器可直连 |
| 中文质量 | 优 |

## API调用方式

### 端点
```
POST https://api.bimiyun.com/v1/web
```

### 请求头
```
Authorization: Bearer ak-68623a4a18764f7b83fd6aece95b01f4
Content-Type: application/json
```

### 请求体
```json
{
  "query": "搜索关键词",
  "count": 5
}
```

### curl示例
```bash
curl -s -X POST "https://api.bimiyun.com/v1/web" \
  -H "Authorization: Bearer ak-68623a4a18764f7b83fd6aece95b01f4" \
  -H "Content-Type: application/json" \
  -d '{"query":"搜索内容","count":5}'
```

### Python示例（在execute_code中）
```python
import requests
resp = requests.post(
    "https://api.bimiyun.com/v1/web",
    headers={
        "Authorization": "Bearer ak-68623a4a18764f7b83fd6aece95b01f4",
        "Content-Type": "application/json"
    },
    json={"query": "搜索内容", "count": 5}
)
print(resp.json())
```

## 注意事项
- web_search工具默认绑定Tavily，不走必米云
- 需要在execute_code里手动调Python requests，或在terminal里curl
- 必米云返回结果结构：检查响应中的data.web数组
