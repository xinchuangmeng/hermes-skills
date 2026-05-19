# GBrain ↔ Hermes MCP 集成指南

> 日期：2026-05-18
> 环境：Hermes Agent 0.13.0 + GBrain v0.35.7.0
> 传输模式：STDIO（本地进程通信，无需网络）

## 架构

```
Hermes Agent (Python进程)
  ├── config.yaml 中的 mcp_servers 定义
  └── 运行时通过 mcp_tool.py 连接 stdio 子进程
        └── GBrain (Bun进程)
              └── bun run src/cli.ts serve
```

GBrain 以 **STDIO MCP Server** 模式运行，Hermes 通过子进程的方式启动 GBrain，两者通过标准输入/输出通信。无需网络端口，无需认证，同一台机器即可。

## 配置步骤

### 1. 安装 `mcp` Python 包

```bash
pip install mcp
```

Hermes 的 MCP 工具（`tools/mcp_tool.py`）依赖 `mcp` 包的 `ClientSession` 和 `StdioServerParameters`。如果没有安装，`hermes mcp test` 和运行时连接会报错：

```
name 'StdioServerParameters' is not defined
```

### 2. 安装依赖（关键！否则连接失败）

```bash
pip install mcp
```

Hermes 的 `tools/mcp_tool.py` 依赖 `mcp` 包的 `ClientSession` 和 `StdioServerParameters`。**必须先安装此包**，否则 `hermes mcp test` 和运行时连接都会报：

```
name 'StdioServerParameters' is not defined
```

注意：即使装了此包，`hermes mcp add` 命令在 v0.13.0 中仍会报同样的错（bug 在 mcp_config.py 的 probe 路径中），但**运行时的实际 MCP 连接不受影响**。

### 3. 手动写入 config.yaml（绕过 add 命令 bug）

由于 `hermes mcp add` 有 bug，**手工写入配置**是最可靠的方式。

在 `~/.hermes/config.yaml` 中添加 `mcp_servers` 节：

```yaml
mcp_servers:
  gbrain:
    command: bun
    args:
      - run
      - src/cli.ts
      - serve
    env:
      DASHSCOPE_API_KEY: sk-xxx   # embedding provider Key
    enabled: true
```

关键点：
- `args` 数组：必须拆成 `["run", "src/cli.ts", "serve"]`，不要写成字符串
- `env`：传给 GBrain 进程的环境变量
- `enabled: true`：显式启用
- **工作目录**：GBrain 需要在源码目录下启动。如果通过 gateway/cron 启动 MCP，用包装脚本确保 cwd 正确：`command: /bin/bash -c "cd /root/.bun/install/global/node_modules/gbrain && bun run src/cli.ts serve"`

### 4. 验证连接

```bash
cd /root/.bun/install/global/node_modules/gbrain
hermes mcp test gbrain
```

预期输出：
```
Testing 'gbrain'...
  Transport: stdio → bun
  Auth: none
  ✓ Connected (1267ms)
  ✓ Tools discovered: 71
```

### 4. 在会话中使用

MCP 工具在 **新会话** 中自动可用。需要通过 `/reset` 或重启 Hermes 来加载。

可用工具包括（共71个）：

| 类别 | 工具 | 用途 |
|:--|:--|:--|
| 搜索 | `query` | 混合搜索（向量+关键词+扩展） |
| 搜索 | `search` | 关键词全文搜索 |
| 搜索 | `find_experts` | 找知道某话题的页面 |
| 页面 | `get_page` | 按slug读取页面 |
| 页面 | `list_pages` | 列出页面 |
| 推理 | `think` | 多跳综合合成 |
| 推理 | `find_contradictions` | 找矛盾声明 |
| 知识 | `recall` | 从 facts 表查询个人知识 |
| 知识 | `find_trajectory` | 实体随时间的变化轨迹 |
| 代码 | `code_callers`/`code_callees` | 代码调用分析 |

## 与 GBrain CLI 的对比

| 操作 | CLI 命令 | MCP 工具 |
|:--|:--|:--|
| 语义搜索 | `gbrain query "..."` | `query` |
| 读页面 | `gbrain get <slug>` | `get_page` |
| 写页面 | `gbrain put <slug>` | `put_page` |
| 健康检查 | `gbrain doctor` | `run_doctor` / `get_health` |

MCP 工具没有 `import` 和 `embed` 命令——数据导入和 embedding 仍需通过 CLI 或 cron 脚本完成。

## 常见问题

### MCP 服务器未找到

```
No MCP servers configured.
```

检查 `config.yaml` 中 `mcp_servers` 键是否存在且格式正确。使用 `hermes mcp list` 查看。

### 连接失败：StdioServerParameters 未定义

```
Failed to connect: name 'StdioServerParameters' is not defined
```

**根本原因**：`mcp` Python 包未安装。`hermes mcp add` 和 `hermes mcp test` 子命令都报此错，但**运行时的连接是由 `tools/mcp_tool.py` 处理的**，安装 `mcp` 包后即可正常工作。这是一个缺失依赖问题，不是配置问题。

### 工具未显示在会话中

MCP 工具只在 **新会话** 中加载。在当前会话中无法使用 `/reload-mcp` 也不能立即生效。需要：
1. 输入 `/reset` 或 `/new`
2. 或重启 Hermes gateway

### GBrain 找不到模块

```
error: Could not resolve "src/cli.ts"
```

工作目录不对。GBrain 需要在源码目录下运行（`/root/.bun/install/global/node_modules/gbrain/`）。如果通过 Hermes cron 或 gateway 启动，确保环境变量 `PWD` 或 `--cwd` 指定正确。

## 技术原理

Hermes 的 MCP 实现在 `tools/mcp_tool.py` 中：

1. **启动子进程**：`_connect_server()` 解析 `mcp_servers` 配置，用 `stdio_client()` 启动子进程
2. **工具发现**：连接后调用 `list_tools()` 获取所有工具 Schema
3. **工具注册**：MCP 工具被注册为 Hermes 的工具，可在会话中直接调用
4. **调用链**：用户消息 → Hermes 选择 MCP 工具 → mcp_tool.py 通过 stdio 发送 JSON-RPC → GBrain 处理并返回结果

GBrain 的 MCP 服务实现在 `src/mcp/server.ts`，所有操作都标记为 `remote=true`（非信任调用者），有权限控制。
