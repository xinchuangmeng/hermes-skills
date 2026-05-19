---
name: agent-auto-deepclaude
description: >
  DeepClaude方案：用Claude Code的Agent循环引擎 + DeepSeek V4 Pro（或其他廉价后端）替代Anthropic原始API，
  实现同样的自主编码Agent体验，成本降低60-90%。适用于预算有限但仍需Claude Code强大Agent能力的场景。
  也适用于多Agent并行部署时控制API成本。支持DeepSeek、OpenRouter、Fireworks等多种后端。
tags:
  - claude-code
  - deepseek
  - cost-saving
  - agent-loop
  - coding-agent
trigger:
  - "claude code 太贵"
  - "deepclaude"
  - "deepseek替代claude"
  - "省钱agent方案"
  - "降低agent运行成本"
  - "cheaper agent backend"
  - "Claude Code cost optimization"
---

# DeepClaude：用DeepSeek跑Claude Code，17倍省钱

## 背景

Claude Code是最强的自主编码Agent，但Anthropic API价格是$\$15/M$ output tokens。
DeepSeek V4 Pro在LiveCodeBench上达96.4%，价格仅$\$0.87/M$ output tokens。
**deepclaude** 交换Claude Code的"大脑"（API后端），保留"身体"（工具循环、文件编辑、bash执行、subagent），实现同等体验但大幅降低费用。

## 快速安装（2分钟）

### 1. 获取DeepSeek API Key

```bash
# 注册: https://platform.deepseek.com/
# 充值$5，复制API Key
export DEEPSEEK_API_KEY="sk-your-key-here"
# 可选：持久化到bashrc
echo 'export DEEPSEEK_API_KEY="sk-your-key-here"' >> ~/.bashrc
```

### 2. 安装deepclaude脚本

```bash
git clone https://github.com/aattaran/deepclaude.git
cd deepclaude
chmod +x deepclaude.sh
sudo ln -s "$(pwd)/deepclaude.sh" /usr/local/bin/deepclaude
```

### 3. 使用

```bash
# 默认使用DeepSeek后端
deepclaude

# 查看可用后端和状态
deepclaude --status

# 使用OpenRouter（美国服务器，延迟更低）
deepclaude --backend or

# 使用Fireworks AI（最快推理）
deepclaude --backend fw

# 还原为原生Claude Code（处理复杂问题）
deepclaude --backend anthropic

# 查看价格对比
deepclaude --cost

# 延迟测试
deepclaude --benchmark
```

## 工作原理

Claude Code通过环境变量决定API调用目标。deepclaude临时设置这些变量，启动Claude Code，退出后自动恢复：

| 环境变量 | 作用 |
|---------|------|
| `ANTHROPIC_BASE_URL` | API端点地址 |
| `ANTHROPIC_AUTH_TOKEN` | API密钥 |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | Opus级别任务模型 |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | Sonnet级别任务模型 |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | Haiku级别任务（subagent）模型 |
| `CLAUDE_CODE_SUBAGENT_MODEL` | 子Agent模型 |

## 成本对比

| 使用场景 | Anthropic Max | deepclaude (DeepSeek) | 节省 |
|---------|--------------|----------------------|------|
| 轻度使用（10天/月） | $200/月（封顶） | ~$20/月 | 90% |
| 重度使用（25天/月） | $200/月（封顶） | ~$50/月 | 75% |
| 自动循环场景 | $200/月（封顶） | ~$80/月 | 60% |

DeepSeek自动上下文缓存（automatic context caching）使agent循环特别便宜：首次请求后，system prompt和文件上下文被缓存，价格从$\$0.44/M$降至$\$0.004/M$。

## 支持的后端

| 后端 | 标志 | 输入/M | 输出/M | 服务器位置 | 备注 |
|------|------|--------|--------|-----------|------|
| **DeepSeek** (默认) | `--backend ds` | $0.44 | $0.87 | 中国 | 自动上下文缓存 |
| **OpenRouter** | `--backend or` | $0.44 | $0.87 | 美国 | 最低延迟(美/欧) |
| **Fireworks AI** | `--backend fw` | $1.74 | $3.48 | 美国 | 最快推理 |
| **Anthropic** | `--backend anthropic` | $3.00 | $15.00 | 美国 | 原始Claude Opus |

## ✅ 可用功能
- 文件读取/写入/编辑（Read/Write/Edit工具）
- Bash/PowerShell执行
- Glob和Grep搜索
- 多步骤自主工具循环
- Subagent生成
- Git操作
- 项目初始化（`/init`）
- Thinking模式（默认开启）

## ❌ 不支持/降级功能

| 功能 | 原因 |
|------|------|
| 图片/视觉输入 | DeepSeek的Anthropic端点不支持图像 |
| 并行工具调用 | 已禁用——工具逐个执行 |
| MCP服务器工具 | 不兼容 |
| Prompt缓存节省 | DeepSeek有自己的自动缓存，忽略Anthropic的`cache_control` |

## ⚠️ 注意事项

1. **首次安装需要git clone**：确保本地有git环境
2. **DeepSeek API需要科学上网**：中国大陆用户不需要，但海外用户可能延迟高
3. **视觉功能不可用**：如需分析图片，配合Hermes的auxiliary.vision配置使用
4. **频繁切换可能触发频率限制**：代理环境中建议使用`--backend or`（OpenRouter）
5. **Subagent也会使用DeepSeek**：通过`CLAUDE_CODE_SUBAGENT_MODEL`可单独控制
