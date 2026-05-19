# DashScope Embedding Batch 限制修复记录

> 日期：2026-05-18
> 模型：text-embedding-v3（1024维）
> 环境：gbrain v0.35.7.0，Bun 1.3.14，DashScope国内端点

## 问题现象

`gbrain embed --stale` 报错：
```
[embed(dashscope:text-embedding-v3)] <400> InternalError.Algo.InvalidParameter:
  Value error, batch size is invalid, it should not be larger than 10.: input.contents
```

大约每3-5个页面出现一次，不是全部失败。后期批次中只剩大文件时频繁触发，说明有递归减半机制但未正确触发。

## 根因分析

### 1. DashScope 的 batch 限制是「条数」不是「token」
- OpenAI/text-embedding-3-small：限制在batch总计token数（8192 tokens）
- Alibaba DashScope text-embedding-v3：限制在 **input 数组长度 ≤ 10**
- 这是两个完全不同的限制维度，gbrain的recipe用 `max_batch_tokens: 8192` 按token估算batch，遇到短文本聚合超10条时失败

### 2. Runtime halving 不触发
gbrain的AI gateway有递归减半机制：当embedding返回token-limit类错误（如429 Too Many Requests）时，自动减半batch重试。

但 DashScope 返回的是 **400 BadRequest**，内容是 `InternalError.Algo.InvalidParameter`。这不是429，所以halving逻辑**不会被触发**，只会走普通retry（最多5次）后放弃。

代码位置：`src/core/ai/recipes/dashscope.ts` 中 embed batch 的 `chars_per_token` 和 `max_batch_tokens` 参数。

### 3. 其他尝试
- text-embedding-v2：接受batch没问题但返回 **1536维**（gbrain schema要求1024维），报 `Embedding dim mismatch`
- text-embedding-v3 设定 `dimensions: 1024` 是 Matryoshka 特性，返回正确维度

## 修复过程

### 尝试1：max_batch_tokens: 4000（→仍报错）
大半页面成功embed（约80%），但大文件仍触发。

### 尝试2：max_batch_tokens: 2000（→部分改善）
从 57→36→14 个失败页面递减，仍有顽固失败。

### 尝试3：max_batch_tokens: 1000（→基本解决）
大部分成功，只剩约70个chunk报错（分散在几个超大skill文件）。

### 最终：max_batch_tokens: 500（→完全成功）
100% coverage，0 missing。

## 最终patch

文件：`src/core/ai/recipes/dashscope.ts`

```diff
-      max_batch_tokens: 8192,
+      // Alibaba doesn't publish a hard batch-token cap for the OpenAI-compat
+      // path. Actual server-side limit is 10 inputs per batch — not token-based.
+      // Max single input ~8K chars (~4000 tokens), so 10 × ~4000 = 40K tokens max.
+      // But the 400 error isn't caught by runtime halving (only 429 triggers retry).
+      // Force small batches so the 400 never fires.
+      max_batch_tokens: 500,
```

### 验证
```bash
bun run src/cli.ts doctor | grep embeddings
# → [OK] embeddings: 100% coverage, 0 missing

bun run src/cli.ts query "测试搜索"
# → 正常返回语义搜索结果
```

## 长期修复建议

1. **给gbrain提交PR**：在DashScope recipe的注释中写明batch=条数而非tokens
2. **或者升级gateway**：让halving机制对400类参数错误也做减半重试（需谨慎，可能掩盖真正的问题）
3. **重新编译时注意**：`bun run build` 后需重新打补丁

## 搜索模式配置

```bash
bun run src/cli.ts config set search.mode balanced
```
