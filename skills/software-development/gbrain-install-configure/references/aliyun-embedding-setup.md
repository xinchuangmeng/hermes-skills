# 阿里百炼 Embedding 配置参考

> 实测时间：2026-05-18（v1.0）
> 修正时间：2026-05-18（v1.1 — 发现两层配置系统问题）
> 环境：腾讯云 Ubuntu 22.04, gbrain v0.35.7.0

## 背景

GBrain 默认使用 OpenAI `text-embedding-3-large`（3072维）作为 embedding provider。但我们使用的是：

- **DeepSeek API** — 只有 chat 模型，无 embedding
- **阿里百炼（DashScope）** — 有 embedding 模型且兼容 OpenAI 格式

## 验证步骤

### 1. 检查阿里百炼 embedding 可用性

```bash
curl -s https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings \
  -H "Authorization: Bearer sk-xxx" \
  -H "Content-Type: application/json" \
  -d '{"model":"text-embedding-v3","input":"test query","encoding_format":"float"}'
```

返回值示例：
```json
{"data":[{"embedding":[-0.056...,...], ...}]}
```

### 2. 确认维度

阿里百炼 `text-embedding-v3` 返回 **1024 维**向量。

## 🚨 关键踩坑：两层配置系统

这是最容易踩的坑——**GBrain 有两层独立的配置系统：**

### 配置层对比

| 层级 | 存储位置 | 读取方 | 写入方式 | 用途 |
|:--|:--|:--|:--|:--|
| **文件级** | `~/.gbrain/config.json` | `buildGatewayConfig()` → `AIGatewayConfig` | `vim` 或 `python3` 直接编辑 | 模型选择、维度、base_url 等 gateway 配置 |
| **引擎KV** | 数据库内部（PGLite） | `engine.getConfig()` | `gbrain config set` | 引擎内部配置（不影响 gateway） |

**关键发现：** `gbrain config set embedding_model dashscope:text-embedding-v3` 虽然输出 "Set embedding_model = dashscope:text-embedding-v3"，但对 `gbrain embed --stale` **毫无效果**。因为 `buildGatewayConfig()`（在 `src/cli.ts:1313`）从 `loadConfig()` 读 JSON 文件，而 `gbrain config set` 调用的是 `engine.setConfig()` 写入 PGLite 数据库。

**源码证据（`src/cli.ts`）：**
```
function buildGatewayConfig(c: GBrainConfig): AIGatewayConfig {
  ...
  env: { ...envFromConfig, ...process.env }, // process.env wins
};
```

### 正确做法

#### 步骤 1：直接编辑 `~/.gbrain/config.json`

```bash
python3 -c "
import json
with open('/root/.gbrain/config.json') as f:
    cfg = json.load(f)
cfg['embedding_model'] = 'dashscope:text-embedding-v3'
cfg['embedding_dimensions'] = 1024
cfg['provider_base_urls'] = {'dashscope': 'https://dashscope.aliyuncs.com/compatible-mode/v1'}
with open('/root/.gbrain/config.json', 'w') as f:
    json.dump(cfg, f, indent=2)
"
```

最终的 `config.json` 结构：
```json
{
  "engine": "pglite",
  "database_path": "/root/.gbrain/brain.pglite",
  "embedding_model": "dashscope:text-embedding-v3",
  "embedding_dimensions": 1024,
  "provider_base_urls": {
    "dashscope": "https://dashscope.aliyuncs.com/compatible-mode/v1"
  }
}
```

#### 步骤 2：导出环境变量

`buildGatewayConfig()` 在 `src/cli.ts:1343` 做的 `env: { ...envFromConfig, ...process.env }` **只折叠了 OPENAI_API_KEY 和 ANTHROPIC_API_KEY**，不认 `DASHSCOPE_API_KEY`。所以必须用进程环境变量：

```bash
export DASHSCOPE_API_KEY="sk-阿里百炼Key"
```

**即使配了文件 config，DASHSCOPE_API_KEY 环境变量仍是必需的。** 因为 DashScope recipe（`src/core/ai/recipes/dashscope.ts`）声明了 `auth_env: { required: ['DASHSCOPE_API_KEY'] }`，而 gateway 的 `defaultResolveAuth()` 函数用 `recipe.auth_env.required[0]` 去读环境变量。

#### 步骤 3：持久化 DASHSCOPE_API_KEY

```bash
grep -q "DASHSCOPE_API_KEY" ~/.bashrc || \
  echo 'export DASHSCOPE_API_KEY="sk-阿里百炼Key"' >> ~/.bashrc
```

#### 步骤 4：修复 DashScope batch 限制（如运行 embed --stale 报400错误）

如遇到 `batch size is invalid, it should not be larger than 10` 错误，需要修改 gbrain 的 DashScope recipe：

```bash
cd /root/.bun/install/global/node_modules/gbrain
```

修改 `src/core/ai/recipes/dashscope.ts` 第31行，将 `max_batch_tokens: 8192` 改为 `max_batch_tokens: 500`。

**根因**：DashScope 限制 embed 请求的 input 条数 ≤10，但 gbrain 的 runtime halving 只对 429 错误触发，DashScope 返回的是 400，所以不会自动减半。

#### 步骤 5：绕过 PGLite WASM 编译版 bug（如 init 报 `/[$]bunfs/` 错误）

```bash
# 不要直接调 /usr/local/bin/gbrain，用 bun run 跑源码
cd /root/.bun/install/global/node_modules/gbrain
bun run src/cli.ts embed --stale

# 或设置别名
echo 'alias gbrain="cd /root/.bun/install/global/node_modules/gbrain && bun run src/cli.ts"' >> ~/.bashrc
source ~/.bashrc
```

### ⚠️ 注意点

1. **额度问题**：阿里百炼的 embedding 需要账户有余额/配额。无额度时 API 返回错误，`gbrain embed --stale` 会失败
2. **国际版 vs 国内版**：`dashscope-intl.aliyuncs.com`（国际版默认）vs `dashscope.aliyuncs.com`（国内版）。国内版需在 `provider_base_urls` 中显式指定
3. **维度验证**：embedding 后需确认返回向量确实是 1024 维，否则后续语义搜索可能异常

## 替代方案

如果 DashScope embedding 不可行（额度/配置问题），有几条路：

1. **只用关键词搜索**（`gbrain search`）— 不需 embedding，PGLite FTS 默认工作。中文关键词在设了 `fts.lang = zh-CN` 后可用，但中文空格分隔的多词查询可能无返回
2. **切换 Supabase + pgvector** — 可能有更多 embedding 模型选项
3. **使用其他兼容 OpenAI 的 embedding API**（如 SiliconFlow）

## 临时做法

技能库 385 页 / 5885 块已用 `--no-embed` 导入，关键词搜索正常工作。后续等解决额度/配置问题后再 `gbrain embed --stale`。
