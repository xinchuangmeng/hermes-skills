# 旺财（Hermes Windows版）配GBrain MCP

## 配置文件位置
```
C:\Users\Administrator\.hermes\config.yaml
```

## 需要加的配置段
```yaml
mcp_servers:
  gbrain:
    command: bun
    args:
      - run
      - src/cli.ts
      - serve
    env:
      DASHSCOPE_API_KEY: YOUR_DASHSCOPE_KEY
    enabled: true
```

## ⚠️ 关键踩坑 - YAML缩进
- 每层缩进必须用 2 个空格（2的倍数）
- **千万不要用记事本手动敲空格**，记事本的缩进经常对不齐
- Windows 版 Hermes v0.13.0 对 YAML 缩进非常敏感，不对齐就报错

缩进对照表：
| 层级 | 内容 | 缩进空格数 |
|------|------|-----------|
| 0 | `mcp_servers:` | 0 |
| 1 | `  gbrain:` | 2 |
| 2 | `    command: bun` | 4 |
| 2 | `    args:` | 4 |
| 3 | `      - run` | 6 |
| 3 | `      - src/cli.ts` | 6 |
| 3 | `      - serve` | 6 |
| 2 | `    env:` | 4 |
| 3 | `      DASHSCOPE_API_KEY: ...` | 6 |
| 2 | `    enabled: true` | 4 |

**验证缩进是否正确：**
```powershell
Get-Content "C:\Users\Administrator\.hermes\config.yaml" | Select-Object -Last 15 | ForEach-Object { "'{0}'" -f $_ }
```
每行开头单引号内的空格数量决定了缩进层级。

## 替代方案：用 PowerShell 命令添加（避免缩进问题）
如果记事本缩进总不对，用命令行追加：
```powershell
Add-Content "C:\Users\Administrator\.hermes\config.yaml" "`nmcp_servers:"
Add-Content "C:\Users\Administrator\.hermes\config.yaml" "  gbrain:"
Add-Content "C:\Users\Administrator\.hermes\config.yaml" "    command: bun"
Add-Content "C:\Users\Administrator\.hermes\config.yaml" "    args:"
Add-Content "C:\Users\Administrator\.hermes\config.yaml" "      - run"
Add-Content "C:\Users\Administrator\.hermes\config.yaml" "      - src/cli.ts"
Add-Content "C:\Users\Administrator\.hermes\config.yaml" "      - serve"
Add-Content "C:\Users\Administrator\.hermes\config.yaml" "    env:"
Add-Content "C:\Users\Administrator\.hermes\config.yaml" "      DASHSCOPE_API_KEY: YOUR_DASHSCOPE_KEY"
Add-Content "C:\Users\Administrator\.hermes\config.yaml" "    enabled: true"
```

## 前置条件
1. 先装 Bun：`powershell -c "irm bun.sh/install.ps1 | iex"`
2. 装完关掉旧窗口，开新窗口才能用 `bun` 命令
3. 安装 GBrain：`bun install -g gbrain`
4. 改完配置重启：`hermes gateway restart`

## 验证是否生效
改完后在旺财对话里问：
> 旺财，从GBrain查跨境选品标准
如果MCP生效了，旺财能描述GBrain的功能并查询知识库。
如果还是不认识GBrain，说明MCP配置没被加载。
