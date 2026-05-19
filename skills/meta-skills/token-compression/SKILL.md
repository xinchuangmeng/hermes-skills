---
name: token-compression
description: Token 压缩层——将工具返回的原始数据（HTML/JSON/长文本）先压缩再送入LLM上下文，节省最多80% token。含html_to_markdown、URL缩短、去重、智能截断。参考OpenHuman TokenJuice设计。
tags: [token, compression, cost-saving, optimization, openhuman]
---

# Token 压缩层（参考 OpenHuman TokenJuice）

## 原理

不要等 token 爆了才省——每一条进入 LLM 上下文的数据都应先经过压缩层。

## 脚本位置

`/root/.hermes/scripts/token_compression.py`

## 使用方式

### Python 中调用
```python
from token_compression import compress, report, html_to_markdown

# 自动检测类型压缩
compressed = compress(html_text, max_chars=8000)

# 查看压缩效果
stats = report(long_text)
print(f"压缩率: {stats['compression_ratio']}")
```

### 终端命令行
```bash
python3 -c "
from token_compression import compress
text = open('file.html').read()
print(compress(text))
"
```

## 支持的压缩类型

| 类型 | 压缩做法 | 典型压缩率 |
|------|---------|:---------:|
| HTML | 去标签→Markdown，提取链接 | 50-80% |
| JSON | 去空字段、截断长数组、精简结构 | 30-60% |
| 长文本 | 首尾保留+中间摘要+URL缩短+去重 | 20-50% |
| 日志 | 去时间戳、去重复行、截断 | 40-70% |

## 什么时候用

- `terminal()` 返回了大量日志/HTML
- `web_search` / `web_extract` 返回了网页原文
- `read_file()` 读了大文件
- 任何工具返回了超过 2000 字符的非结构化数据

## 什么时候不用

- 结构化数据（YAML/JSON 已经是压缩格式）
- 用户指令（不要压缩用户的输入）
- 需要精确原文的场景（代码审查）
