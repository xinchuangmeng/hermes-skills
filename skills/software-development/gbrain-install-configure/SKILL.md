---
name: gbrain-install-configure
title: GBrain 安装配置实战指南
description: 在 Linux 服务器上安装 garrytan/gbrain（v0.35.x）的完整流程 — 从 Bun 下载到 gbrain init 到搜索模式选择到技能包安装。覆盖国内慢速网络环境下的应对策略和常见坑点。GBrain 是 AI Agent 的长期记忆与知识库系统。
tags:
  - gbrain
  - memory
  - knowledge-base
  - pglite
  - bun
  - agent-memory
  - installation
---

# GBrain 安装配置实战指南

> 最后更新：2026-05-18
> 版本：gbrain v0.35.7.0

## 概览

GBrain 是 garrytan 开源的 AI Agent **长期记忆与知识库系统**。它作为 Agent 的「第二大脑」：
- 存储跨会话的语义记忆、事实、技能映射
- 支持 PGLite（本地零配置）和 Supabase/PGVector 两种存储后端
- 提供 MCP 接口供 Agent 查询/写入
- 内置 40+ 内置技能（resolver、book-mirror、article-enrichment 等）

## 前提条件

- **Linux x86_64**（本文基于 Ubuntu 22.04）
- **curl** 可用
- **unzip** 可用（`apt install unzip`）
- **磁盘空间**：GBrain 本体~89MB，脑库文件大小取决于导入数据量
- **可选：DeepSeek/OpenAI API Key**（用于语义搜索和 LLM 扩展）

## 安装步骤（5-10 分钟）

### 第 1 步：克隆仓库

```bash
git clone https://github.com/garrytan/gbrain ~/gbrain
cd ~/gbrain
```

大小约 9.6MB。

### 第 2 步：安装 Bun 运行时

GBrain 使用 Bun 作为 JavaScript/TypeScript 运行时。2种方式：

**方式 A：直接 curl 下载（推荐，可控版本）**

```bash
# 标准 Linux x64 版 — 约 34MB ZIP 包
# 注意：一定要下正式版，不要下 bun-profile（profile/buildid 版是 Android 链接器版本，跑不了）
curl -L -o /tmp/bun-linux.zip \
  "https://github.com/oven-sh/bun/releases/download/bun-v1.3.14/bun-linux-x64.zip" \
  --connect-timeout 30 --max-time 600 --retry 3 --retry-delay 10

unzip -o /tmp/bun-linux.zip -d /tmp/bun-extract/
cp /tmp/bun-extract/bun-linux-x64/bun /usr/local/bin/
chmod +x /usr/local/bin/bun
bun --version   # 验证
```

**方式 B：官方安装脚本（如有代理更快）**

```bash
curl -fsSL https://bun.sh/install | bash
```

**⚠️ 踩坑提示：**
- ❌ 不要下 `bun-profile` 版本（ELF 链接到 Android 的 `/system/bin/linker64`）→ 下 `bun-linux-x64.zip`
- ❌ 不要下 `.deb` 包安装（可能缺依赖）
- ✅ 下完后用 `file /tmp/bun-extract/bun-linux-x64/bun` 验证：必须是 `ELF 64-bit LSB executable, ... interpreter /lib64/ld-linux-x86-64.so.2`
- 国内环境 128Kbps 网速下，34MB 文件约需 5-6 分钟

### 第 3 步：安装依赖

```bash
cd ~/gbrain
bun install
```

约 4-5 秒（271 个包）。时间极短因为 Bun 的 npm 兼容层极快。

### 第 4 步：编译二进制

```bash
cd ~/gbrain
bun run build
# 输出: bin/gbrain (~321ms bundle 1389 modules, ~431ms compile)
cp bin/gbrain /usr/local/bin/
gbrain --version   # 验证：v0.35.7.0 等
```

### 第 5 步：初始化脑库

```bash
cd ~/gbrain   # 必须在项目目录内，因此时可以读取 package.json 中的 postinstall 脚本
gbrain init
```

这一步会：
1. 在 `~/.gbrain/brain.pglite` 创建本地 PGLite 数据库
2. 运行 63+ 个数据库迁移（创建完整 schema）
3. **自动选择搜索模式**（如无 OpenAI Key 则选 `conservative`）
4. 加载 42 个内置技能
5. 输出搜索模式成本矩阵和推荐技能包列表

### 第 6 步：配置搜索模式（关键决策点 ⚠️）

`gbrain init` 完成后会输出一个 **[AGENT]** 标记的成本矩阵，你必须展示给用户决策：

```text
[AGENT] Before continuing, SHOW this matrix to your operator and
[AGENT] ask which mode they want.
```

三种搜索模式成本对比（基于 1万次查询/月，仅搜索负载，不含缓存节省）：

| 模式 | 特点 | 月费（DeepSeek 级别） | 月费（Haiku 4.5） | 月费（Sonnet 4.6） |
|:--|:--|:--:|:--:|:--:|
| **conservative** | 保守：语义缓存 + 无 LLM 扩展 | ~$10-40 | $40 | $120 |
| **balanced** | 平衡：性价比最优 | ~$25-100 | $100 | $300 |
| **tokenmax** | 最大召回：花更多 token 做扩展查询 | ~$50-200 | $200 | $600 |

> **注意：** 未配置 OpenAI Key 则只能用于语义缓存，LLM 扩展功能不可用。

切换命令：
```bash
gbrain config set search.mode <conservative|balanced|tokenmax>
```

配置 API Key（如果用 DeepSeek 兼容 API）：
```bash
gbrain config set openai.api_key "sk-xxxx"
```

### 第 7 步：安装推荐技能包（征求用户同意 ⚠️）

`gbrain init` 完成后会列出 9 个官方推荐技能包。**必须征求用户同意后安装：**

| 技能 | 用途 |
|:--|:--|
| **book-mirror** | 🏆 旗舰 — 把书/PDF 变成双栏逐章分析（左栏原文，右栏关联脑库数据） |
| **article-enrichment** | 文章结构化处理 → 摘要/引文/洞察 |
| **strategic-reading** | 针对特定问题读一本书/案例 → 输出行动手册 |
| **concept-synthesis** | 去重概念草稿 → 分层知识图谱 |
| **perplexity-research** | 结合脑库上下文的联网搜索 |
| **archive-crawler** | 个人文件归档（安全白名单机制） |
| **academic-verify** | 学术论文可复现性验证 |
| **brain-pdf** | 脑库页面→精美 PDF |
| **voice-note-ingest** | 语音笔记精确转录（不意译，保留原话） |

安装命令：
```bash
# 全装
gbrain skillpack install --all

# 选装
gbrain skillpack install <name>

# 查看所有可选
gbrain skillpack list
```

## 知识库导入

### 基本导入

```bash
gbrain import <dir>             # 导入目录
gbrain import <dir> --recursive # 递归导入子目录
gbrain import <dir> --no-embed  # 跳过向量嵌入（纯文本导入）
```

### 导入性能特征

| 数据量 | 耗时 | 说明 |
|:--|:--:|:--|
| 11 个文件 | 0.7 秒 | 小批量极快 |
| 573 文件（385 新+188 跳过） | ~127 秒 | 大部分文件 0.5-2 秒，超大文件拖慢 |
| 超大文件（如 llms-full.txt 70MB+） | 20-77 秒/个 | 含大量代码 fence 的文件特别慢 |

### ⚠️ 导入踩坑

1. **Fence Cap 限制**：GBrain 每页最多处理 100 个 markdown fence（代码块），超出部分静默截断。报 `markdown fence cap hit (100 fences/page); skipping additional fences`。大文档里的额外 fence 内容会丢失。可通过 `GBRAIN_MAX_FENCES_PER_PAGE` 环境变量覆盖。
2. **首次导入已存在内容会全部跳过**：`0 imported, 188 skipped (188 unchanged)` — 同内容不会重复处理。
3. **`--no-embed` 后的搜索**：关键词搜索（`gbrain search`）可用，但向量搜索（`gbrain query`）受限。

### 导入后的搜索

| 搜索类型 | 命令 | 是否需嵌入 | 中文支持 |
|:--|:--|:--:|:--|
| 关键词 | `gbrain search "term"` | ❌ | ⚠️ PGLite FTS 默认用英文分词，纯中文关键词可能无返回；混合英文/数字的中文内容（如 "Shopee 泰国 定价"）可搜 |
| 语义（混合） | `gbrain query "question"` | ✅ 需 embed | — |
| 直接获取 | `gbrain get <slug>` | ❌ | ✅ |

## 自定义 Embedding Provider（重要）

### 问题背景

DeepSeek API **不提供 embedding 模型**（只有 chat 模型 `deepseek-v4-flash` 和 `deepseek-v4-pro`），因此不能直接作为 GBrain 的 embedding provider。

### 方案：阿里百炼兼容 OpenAI 接口

阿里百炼的 embedding 接口兼容 OpenAI 格式，可以为 GBrain 提供向量嵌入能力：

**具体操作步骤见 `references/aliyun-embedding-setup.md`** — 里面详细记录了：
- 验证阿里百炼 embedding 可用性
- 🚨 **两层配置系统踩坑**：`gbrain config set` ≠ `~/.gbrain/config.json`（这是最容易搞错的地方）
- 正确写入 `config.json` + 环境变量 `DASHSCOPE_API_KEY` 的完整流程
- 阿里百炼国内版 vs 国际版 base_url 区别

## 常用命令速查

```bash
gbrain --version               # 查看版本
gbrain init                     # 初始化脑库（已有则跳过）
gbrain import <dir>             # 导入目录到脑库
gbrain config set search.mode   # 切换搜索模式
gbrain config set openai.api_key  # 配置 API Key
gbrain config set openai.base_url # 配置自定义 API 端点（阿里百炼等）
gbrain search modes             # 查看当前搜索模式
gbrain search "keyword"         # 关键词搜索（无需嵌入）
gbrain query "question"         # 语义搜索（需嵌入）
gbrain get <slug>               # 直接获取页面
gbrain stats                    # 查看脑库统计
gbrain doctor --fix             # 诊断并修复问题
gbrain apply-migrations --yes   # 手动执行迁移
gbrain soul-audit               # 审计 Agent 身份配置
gbrain skillpack list           # 查看技能包
gbrain skillpack install --all  # 安装所有技能包
gbrain migrate --to supabase    # 从本地 PGLite 迁移到 Supabase
```

## AGENTS.md 关键协议

GBrain 项目根目录下的 `AGENTS.md` 规定了 Agent 安装时的操作协议：

1. **Step 3.5 协议：** 搜索模式不能静默选择 — 必须展示成本矩阵并让用户决策
2. **技能包协议：** 必须展示技能列表并征得用户同意，不能静默安装
3. **信任边界：** 区分 `remote = true`（MCP 调用者，非信任）和 `remote = false`（本地 CLI 调用者，信任）
4. **隐私规则：** 不能将真实姓名/公司/基金名称提交到公开制品中

## 🚨 关键踩坑 1：PGLite WASM 编译版 Bug + 绕过方案

### 问题现象

编译后的 `gbrain` ELF 二进制（`/usr/local/bin/gbrain`）运行 `gbrain init` 或 `gbrain embed --stale` 时报错：

```
PGLite failed to initialize its WASM runtime.
  Original error: ENOENT: no such file or directory, open '/$bunfs/root/pglite.data'
```

这是 **Bun 编译版（`bun build --compile`）的已知 bug**（GitHub issue #223）：编译后的 ELF 二进制里内嵌的 Bun 运行时虚拟文件系统路径 `/$bunfs/` 无法正确解析。

### 判断是否触发

- 如果 `gbrain` 是**编译版 ELF 二进制** → 可能触发
- 如果用 `bun run src/cli.ts` 跑源码 → **不会触发**（宿主机的 Bun 文件路径正常）
- PGLite 的 `.data` 文件实际存在于 Bun 缓存中（可通过 `find / -name "pglite.data"` 确认），但 ELF 找不到它

### 绕过方案：直接用 Bun 跑源码

```bash
cd ~/gbrain          # 必须进入 gbrain 源码目录
export DASHSCOPE_API_KEY="sk-xxx"
bun run src/cli.ts <命令>
```

### 设置别名（推荐）

```bash
echo 'alias gbrain="cd /root/.bun/install/global/node_modules/gbrain && bun run src/cli.ts"' >> ~/.bashrc
source ~/.bashrc
export DASHSCOPE_API_KEY="sk-xxx"
```

### 验证绕过成功

```bash
bun run src/cli.ts doctor
# 看到 [OK] connection: Connected, N pages 说明数据库正常
```

## 🚨 关键踩坑 2：DashScope Embedding Batch 限制修复

### 问题现象

`gbrain embed --stale` 使用 DashScope `text-embedding-v3` 时批量报错：

```
[embed(dashscope:text-embedding-v3)] <400> InternalError.Algo.InvalidParameter:
  Value error, batch size is invalid, it should not be larger than 10.: input.contents
```

### 根因

1. **DashScope 限制的是 input 条数（≤10 条/批）**，不是 token 数
2. gbrain 的 DashScope recipe 默认 `max_batch_tokens: 8192`，按 token 估算时容易超出10条限制
3. gbrain 的 runtime halving 机制**只对 token-limit 类错误（429）触发递归减半**，而 DashScope 返回的是 **400 BadRequest**，减半机制不触发，走到普通 retry 后放弃

### 修复方案

编辑 DashScope recipe，把 `max_batch_tokens` 改小：

```bash
cd /root/.bun/install/global/node_modules/gbrain
```

修改 `src/core/ai/recipes/dashscope.ts` 中的 `max_batch_tokens: 8192` 改为保守值：

```typescript
// 修改前
max_batch_tokens: 8192,

// 修改后
max_batch_tokens: 500,  // 确保一次不超过3-4条，避免400错误
```

重新运行 embedding：

```bash
export DASHSCOPE_API_KEY="sk-xxx"
bun run src/cli.ts embed --stale
```

### 注意事项

- 此 patch 只影响 `bun run src/cli.ts` 运行方式
- 编译版 ELF（`/usr/local/bin/gbrain`）不会受此影响（patch 在修改前的编译版本中已固化）
- 如果后续重新编译 ELF（`bun run build`），需要重新应用此补丁
- 重新 `git clone` 后也需要重新打补丁

**详细修复记录见 `references/dashscope-batch-patch.md`。**  

## 与 Hermes MCP 集成

> 完整步骤见 `references/hermes-mcp-integration.md`

GBrain 可以作为 Hermes 的 **STDIO MCP 服务器** 运行，暴露出71个搜索/页面/推理工具给 Hermes 直接在会话中调用。

**前置条件：** 必须安装 `mcp` Python 包（`pip install mcp`），否则报 `StdioServerParameters is not defined`。

**配置方式：** `hermes mcp add` 命令在 v0.13.0 有 bug，需要**手工写入 `~/.hermes/config.yaml`**：

```yaml
mcp_servers:
  gbrain:
    command: bun
    args:
      - run
      - src/cli.ts
      - serve
    env:
      DASHSCOPE_API_KEY: sk-xxx
    enabled: true
```

**注意事项：**
- MCP 工具只在 **新会话** 中加载（`/reset` 或重启 gateway）
- `import` 和 `embed` 等数据导入操作仍需通过 CLI 或 cron 脚本
- 检查 `~/.hermes/logs/` 排查 MCP 连接问题

## 定时自动同步

> 详见 `references/cron-auto-sync-setup.md`

GBrain 导入 skills 目录后，新文件不会自动入库。配置 cron 脚本每6小时同步：导入新文件→生成 embedding。通过 `no_agent=true` 模式纯脚本运行，不消耗 LLM token。

## 故障排查

| 问题 | 原因 | 解决 |
|------|------|------|
| `gbrain` command not found | 未编译或未放到 PATH | `bun run build; cp bin/gbrain /usr/local/bin/` |
| `gbrain init` 报 schema 迁移错误 | 数据库文件损坏 | 删除 `~/.gbrain/brain.pglite` 重新 init |
| Bun 下载后跑不了 | 下错了 bun-profile 版本 | 确认 `file` 输出是 Linux x64 ELF |
| 搜索模式不可用 | 未配置 API Key | `gbrain config set openai.api_key "sk-..."` |
| 技能包安装报错 | 缺依赖或版本不匹配 | `gbrain doctor --fix` |
| PGLite WASM 初始化失败 | 编译版 ELF 的 Bun 虚拟文件系统 bug | 用 `bun run src/cli.ts` 代替直接调用 gbrain |
| Embedding 400 batchsize 错误 | DashScope 限制 ≤10条/批，max_batch_tokens 太大 | 修改 recipe 中 max_batch_tokens 为 500 |
| MCP 连接报 StdioServerParameters 未定义 | `mcp` Python 包未安装 | `pip install mcp` |
| hermes mcp test/add 报错 | 同上的依赖问题 + v0.13.0 bug | 先 `pip install mcp`，然后手工写入 config.yaml |
