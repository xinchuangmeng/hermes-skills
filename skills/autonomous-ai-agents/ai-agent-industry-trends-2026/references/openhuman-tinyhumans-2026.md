# OpenHuman (tinyhumansai/openhuman) — 开源桌面AI智能体

> 来源: GitHub API (2026-05-17) + 官方README
> 仓库: https://github.com/tinyhumansai/openhuman
> 官网: https://tinyhumans.ai/openhuman

## 基本信息

| 字段 | 值 |
|------|-----|
| 全名 | tinyhumansai/openhuman |
| 星标 | 13,081（快速增长中）|
| 语言 | Rust |
| 许可 | GPL-3.0 |
| 状态 | Early Beta |
| 创建 | 2026-02-18 |
| 最后更新 | 2026-05-17 |
| 分叉数 | 1,125 |
| 打开问题 | 121 |
| 订阅者 | 66 |
| 大小 | 83 MB |
| 技术栈 | Rust + Tauri (Desktop) + pnpm (Web/Node) |

## 官方定位

> "Your Personal AI super intelligence. Private, Simple and extremely powerful."
> "一个开源智能助手，旨在融入你的日常生活。"

## 核心特性

### 1. 桌面吉祥物（Mascot）

- 有动画形象，会说话、能感知周围环境
- **可加入 Google Meet 会议作为真实参与者**
- 跨周记忆用户，后台持续思考

### 2. 118+ 第三方集成（一键 OAuth）

支持 Gmail、Notion、GitHub、Slack、Stripe、Calendar、Drive、Linear、Jira 等主流 SaaS。
集成方式是**每 20 分钟 Auto-Fetch**：自动遍历每个已激活连接，拉取新数据到记忆树。
→ Agent 早上起床已经知道你今天的会议、最新提交、未读邮件。

### 3. 记忆树 + Obsidian Wiki

- 所有连接的数据被**规范化为 ≤3k token 的 Markdown 块**
- 评分后折叠为层级摘要树，存储在 **本地 SQLite**
- 同时以 `.md` 文件落入 Obsidian 兼容的 Vault 中，人可以打开浏览和编辑
- 灵感来自 Karpathy 的 [obsidian-wiki workflow](https://x.com/karpathy/status/2039805659525644595)

### 4. TokenJuice 智能压缩

> 每个工具调用、抓取结果、邮件正文、搜索结果都经过压缩层后才进入 LLM。

- HTML → Markdown
- 长 URL 缩短
- 去除非 ASCII 字符 等
- **节省高达 80% token 费用和延迟**

### 5. 内置工具集

| 工具 | 说明 |
|------|------|
| 网页搜索 | 默认集成 |
| 网页抓取 | 内置 scraper |
| 编码工具 | 文件系统、git、lint、test、grep |
| 语音 | STT（语音转文字） + ElevenLabs TTS（文字转语音） |
| 唇形同步 | Mascot 说话时嘴型同步 |
| 会议 Agent | 实时加入 Google Meet |

### 6. 模型路由

自动按任务类型路由到不同的 LLM 模型（推理型/快速型/视觉型），**单一订阅**覆盖多种模型。

### 7. 本地 AI 支持

通过 Ollama 可选本地运行，敏感数据不上云。

## 与 Hermes Agent 的对比

| 维度 | OpenHuman | Hermes Agent（当前系统） |
|------|-----------|------------------------|
| **部署形态** | 桌面 App（macOS/Windows/Linux） | 云端服务器（CLI 网关） |
| **安装门槛** | 下载即用，UI 引导，无需终端 | 需要 Python/venv/CLI 配置 |
| **连接方式** | 桌面 Mascot + Google Meet | 飞书 WebSocket + 群聊 |
| **数据接入** | Auto-Fetch（每 20 分钟自动拉） | 手动触发 / cron 定时 |
| **知识存储** | 记忆树 + SQLite + Obsidian Vault | skill 目录 + memory 持久化 + session DB |
| **技能体系** | 118+ 内置集成（OAuth 一键） | 305 个 Skill（YAML + SKILL.md） |
| **Token 优化** | TokenJuice（节省 80%） | 无内置压缩 |
| **开源许可** | GPL-3.0 | Apache-2.0? |
| **社区输出** | 桌面吉祥物 + 视频会议集成 | 飞书消息推送 |
| **编码能力** | 内置 coder 工具集（git/lint/test/grep） | delegate_task 给子 Agent |

## 值得借鉴的设计

1. **Auto-Fetch 机制** — 不是等 Agent 问，而是主动每 20 分钟拉取已连接服务的增量数据。Hermes 可以用 cron 做类似的事（定时拉飞书/邮件/GitHub 新数据）

2. **TokenJuice 压缩层** — 在数据进入 LLM 之前做无损压缩。Hermes 的 skill 加载策略（Progressive Disclosure）已经做到了部分，但搜索/抓取结果没有压缩

3. **记忆树（Memory Tree）** — 将数据规范化为统一格式（≤3k token Markdown 块），评分后层级存储。Hermes 的 memory 是平面字符串，缺少层级组织和评分机制

4. **桌面吉祥物 + Google Meet** — 让 Agent 以「真人参与者」身份出现在视频会议中。这类具身交互在电商运营/团队协作场景中有潜力

5. **单一订阅多模型路由** — 推理/快速/视觉模型在同一订阅下自动切换，用户不用关心哪个任务用哪个模型

## 安装方式

```bash
# macOS / Linux x64
curl -fsSL https://raw.githubusercontent.com/tinyhumansai/openhuman/main/scripts/install.sh | bash

# Windows
irm https://raw.githubusercontent.com/tinyhumansai/openhuman/main/scripts/install.ps1 | iex
```

## 社区

- Discord: https://discord.tinyhumans.ai/
- Reddit: https://www.reddit.com/r/tinyhumansai/
- X/Twitter: @tinyhumansai
- 作者: @senamakel
- 文档: https://tinyhumans.gitbook.io/openhuman/
- ProductHunt: Top Post of the Day (May 2026)
