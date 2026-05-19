---
name: hermes-auto-learn
title: "每日三分类自动学习系统 v4"
description: "每日循环学习跨境电商/短视频图文/AI智能体三大类实战知识，自动全网采集、整理技能、版本迭代、推送总结"
tags: [hermes, auto-learn, cron, crossborder, shortvideo, ai-agent, skills-update, daily-report]
trigger: |
  当用户说"开启每日学习"、"学习任务"、"第几轮"、"更新技能"、"学习10条"时使用
  用于管理每日三分类自动化学习系统的 cron 任务和执行
---

# 每日三分类自动学习系统 v4.1

## 🎯 目标

每日固定学习10条实战干货，三类内容循环轮学，自动全网采集、技能化归档、版本迭代、推送学习报告。

## 🏗️ 双模式架构

系统支持两种互补的运行模式：

**模式A：Script Cron（每天1-7点整点，已稳定运行）**
```
系统cron (no_agent=True)
  └→ bash /root/.hermes/scripts/learn/auto_learn.sh
     ├→ curl采集 Hacker News (Algolia API) → hackernews.md
     ├→ curl采集 Dev.to API → devto.md
     ├→ curl采集 arXiv API → arxiv.md
     └→ 生成 _summary.txt + 存入日期目录
```
- 在系统shell层执行，**不依赖Hermes终端工具链**
- 即使终端工具因venv路径问题故障，Script Cron不受影响
- 累计91次成功运行（2026-05-05 ~ 2026-05-16）

**模式B：LLM驱动（计划中，每天10:00）**
```
Hermes Agent (LLM-driven cron)
  └→ 读取进度文件 → 判断今日类别 → 全网搜索10条干货
     └→ 逐一skill_manage创建/更新技能 → 比对旧版覆盖更新
        └→ 更新进度文件 → 推送学习总结到飞书
```
- 需要web/search工具集在线
- 需要终端工具链正常（依赖venv路径）
- 适合知识深化、技能创建/更新等需要LLM推理的任务

## 📋 三类轮循顺序

| 天数 | 类别 | 内容范围 |
|------|------|---------|
| 第1天 | ① 跨境电商运营篇 | Shopee规则、泰国站选品、SLS运费、藏价定价、1688一件代发、活动报名、站外引流等 |
| 第2天 | ② 短视频图文剪辑篇 | 抖音图文爆款、竖屏排版、AI成片、字幕适配、跨境带货文案、多语种字幕、剪映出片等 |
| 第3天 | ③ 智能体落地应用篇 | Hermes优化、浏览器自动化、API对接、多模型切换、记忆优化、沙箱解除、定时任务等 |
| 第4天 | ④ 学习系统自身优化篇 | 社区生态监测、技能库盘点、旧技能淘汰/合并、学习效果复盘 |

## 📋 第四类：学习系统自身优化篇

### 监测范围

当轮到这个类别时，主动执行以下检查：

1. **Hermes社区生态监测** — 主动搜索今日头条/知乎/B站等平台关于Hermes Agent的技能推荐、使用技巧、踩坑经验。社区用户分享的实战经验可以直接转化为技能或更新现有技能。

2. **技能库健康状况普查** — 按以下标准评估每个分类下的技能：
   - 版本是否过旧（连续3轮以上无更新标记）
   - 内容是否被新技能覆盖（合并/淘汰）
   - 触发条件是否准确（description能否让Agent正确发现）
   - 引用链接是否仍然有效

3. **学习效果复盘** — 回顾过去一轮（4天）的学习成果：
   - 新建了多少技能？更新了多少旧技能？
   - 有没有重复造轮子的技能？（合并）
   - 有没有技能因内容过时而需要废弃？
   - 用户反馈了哪些偏好/纠正？→ 更新到对应技能中

4. **跨类别平衡度检查** — 确保三类内容的学习深度和频率均衡，不要偏科

### 特殊触发规则

任何时候用户分享了关于Hermes Agent本身的文章/截图/链接，**立即主动学习**：
- 提取文章中推荐的技能 → 检查是否已安装
- 提取文章中提到的技巧/方法 → 沉淀到对应技能或新建
- 不需要等待轮到第4天才处理，这是即时反馈
| 第5天 | ① 跨境电商运营篇 | (循环) |
| ... | ... | |

## 🔨 配置

### 模式A：Script Cron（已部署，每天1-7点整点）

```yaml
# 系统级shell脚本采集，不经过Hermes终端工具链
# 通过 cronjob(action='create') 的 script + no_agent=True 实现
schedule: "0 1-7 * * *"      # 每天1点到7点，每小时执行
name: "auto-learn-采集"
script: "/root/.hermes/scripts/learn/auto_learn.sh"   # curl抓取 HN/Dev.to/arXiv
no_agent: true                # 纯脚本模式，无需LLM推理
# 不设置 enabled_toolsets — 纯脚本模式不需要
```

输出目录：`~/.hermes/skills/auto_learned/YYYY-MM-DD/`
- `hackernews.md` — 30条Hacker News
- `devto.md` — 10条Dev.to
- `arxiv.md` — arXiv论文（可能为空）
- `_summary.txt` — 采集汇总

### 模式B：LLM驱动（待部署）

```yaml
schedule: "0 10 * * *"     # 每天上午10点执行
deliver: origin             # 推送到飞书当前对话
skills: ["hermes-auto-learn"]  # 加载本技能作为执行指引
enabled_toolsets: ["web", "terminal", "file", "skills"]
prompt: |
  执行每日自动学习任务：
  1. 读取 /root/.hermes/auto_learn_progress.txt 判断今日类别和当前题号
  2. 根据类别全网搜索10条最新实战干货（优先权威站点）
  3. 逐条整理为标准化技能 + 更新版本号
  4. 更新 auto_learn_progress.txt 进度
  5. 生成今日学习总结推送
```

## 📁 进度文件格式

路径：`/root/.hermes/auto_learn_progress.txt`

```
已完成题目：第一轮全30题 + 第二轮全30题 + ...
当前进度：第X轮第Y题已完成（深化更新至vZ.0，YYYY年MM月DD日第X轮深化：关键发现概要）
下次从：第X轮第Y+1题

已学题目记录：
XX. 题目名 → skill-name（已深化更新至vX.0）
```

**维护警告：不要使用 patch 工具编辑进度文件！** 该文件包含多行复杂格式化内容，patch极易导致格式错乱。正确做法：read_file读取 → 构造新内容 → write_file 一次整体写入。

## 📂 采集脚本路径

系统中有两个不同的 auto-learn 相关脚本，容易混淆：

| 脚本 | 路径 | 用途 | cron绑定 |
|------|------|------|---------|
| **主采集脚本** | `/root/.hermes/scripts/learn/auto_learn.sh` | curl抓取HN/Dev.to/arXiv → 日期目录 | `auto-learn-采集` (1-7点, no_agent=True) |
| **技能内脚本** | `/root/.hermes/skills/dogfood/hermes-auto-learn/scripts/auto_learn.sh` | 生成 daily_summary.md 元数据 | 已弃用（旧版） |

**坑（已验证 2026-05-19）：** 用户可能会说"执行 /home/agentuser/... 路径下的脚本"——这通常是迁移前的旧路径。实际脚本在 `/root/.hermes/scripts/learn/auto_learn.sh`。如果用户给的路径不存在，先 `search_files` 找到正确路径再执行。

**另一个常见陷阱（已验证 2026-05-19）：** 即使 cron job 的 task prompt 写着"执行 bash /home/agentuser/.hermes/scripts/learn/auto_learn.sh"，agent 也应该先检查文件是否存在。如果不存在，**不要直接报错返回**，而是 search_files 搜索实际路径。auto_learn.sh 实际路径是 `/root/.hermes/scripts/learn/auto_learn.sh`。

## 🐞 已知API采集问题

### Dev.to标签空返回

脚本按固定5个标签查询Dev.to：`ai-agents`, `artificial-intelligence`, `automation`, `prompt-engineering`, `llm`。部分标签（尤其是 `ai-agents`、`artificial-intelligence` 和 `prompt-engineering`）经常返回0条结果。

**原因分析：**
- Dev.to API对部分标签的匹配规则不稳定，有的标签名会被转义或重定向
- `prompt-engineering` 标签下的文章量少，且API分页策略可能导致漏采
- 非英文社区的内容使用不同标签（如中文 `人工智能`）不被匹配

**应对方案：**
- 如果发现某标签连续3天返回0（去重后），考虑替换标签：`prompt-engineering` → `machine-learning`，`ai-agents` → `webdev`（Dev.to上AI文章常挂webdev标签）
- 或增加备用标签 `generative-ai`、`chatgpt`、`tools` 提高覆盖率
- 脚本输出 `devto.md` 中只列出有结果的标签，空标签只留标题行

### arXiv查询返回0条或连接失败

arXiv API查询使用 `search_query` 参数按分类+关键词过滤。注意区分两种根本不同的失败模式：

#### 失败模式A：连接失败（curl不可达）

**症状：** 输出文件中出现 `* Failed to fetch for query: ...`，表明 `curl` 命令自身返回了非零退出码或响应体为空。

**常见原因：**
1. **服务器网络限制** — 国内服务器（腾讯云/阿里云等）可能无法直接访问 `export.arxiv.org`（arXiv在中国部分地区被限制或极慢）
2. **DNS解析失败** — 服务器DNS无法解析arXiv域名
3. **TLS/handshake超时** — 虽然查询使用HTTP（端口80），但中间网络设备可能拦截或限流

#### 失败模式B：查询返回0条（API成功但无结果）

**症状：** 没有"Failed to fetch"字样，arXiv XML解析正常但结果列表为空（`<entry>`元素数量为0）。

**常见原因：**
1. **关键词过于严格** — `cat:cs.AI+AND+(agent+OR+autonomous)` 要求文章同时属于cs.AI分类且包含agent或autonomous。arXiv分类索引有更新延迟，部分Agent相关论文可能只归入cs.LG/cs.MA而未归入cs.AI
2. **arXiv API限流** — 连续请求可能触发限流（标准限流：4次/秒，但新论文索引有时间差）
3. **查询时间窗口** — 非arXiv发布日（arXiv通常周一至周五UTC 20:00发布新提交），周末查询返回0条是正常的

#### 快速判断方法

| 输出内容 | 失败模式 | 诊断 |
|----------|----------|------|
| `* Failed to fetch for query: ...` | **连接失败** | 网络问题，curl未收到有效响应 |
| `* (parse error)` | 解析失败 | API返回了非XML内容（如429限流页或5xx错误） |
| 标题行+空行（无"Failed"字样） | 查询无结果 | API正常，但无匹配论文 |

**应对方案：**
- **连接失败型：** 在脚本中添加重试机制（3次重试，间隔5秒）或切换为HTTPS端点（`https://export.arxiv.org/api/query`）
- **查询无结果型：** 放宽arXiv查询：改用 `all:(agent+AND+(autonomous+OR+AI+OR+LLM))` 全字段搜索替代分类限定；或增加备用查询 `cat:cs.LG+AND+(agent+OR+tool+use+OR+function+calling)`
- **通用优化：** 脚本中增加API响应状态码日志、curl退出码和响应体前100字节的采样输出，精确区分三种失败模式

## 🔍 搜索策略

优先采集来源：
- 跨境电商运营：Shopee官方公告、雨果网、跨境眼、AMZ123、卖家之家
- 短视频图文：抖音创作服务平台、飞瓜数据、新榜、蝉妈妈
- 智能体落地：GitHub Trending、Hermes官方文档、HuggingFace、模型官网
- **社区生态监测：今日头条(搜索"Hermes Agent"或"智能体 技能")、知乎AI专栏、GitHub Trending(tinyhumansai等关键词)**

当 Tavily/搜索API耗尽时的备用方案：
- 百度搜索（首枪窗口策略：最重要的3个查询放在前面）
- 使用 `web_search` 或 script 方式采集
- 每个查询间隔2秒避免限流

## 📦 技能封装规范

每条知识点封装为独立Skill技能文件：
- 命名：`{category-prefix}-{topic-name}`（如 `shopee-pricing-formula`、`shortvideo-algorithm-guide`、`hermes-cron-setup`）
- 分类存储：按 business / shortvideo / agent-auto 等分类
- 版本管理：v1.0 → v2.0 → ... 每次更新升级版本号
- 头部注明：本轮新增概要、更新日期、来源
- 检测到旧版同名技能 → 自动用新内容覆盖更新
- 每周全技能库大盘点：清理无效/报错/过时技能

## 📊 每日推送模板

```
## 📚 今日学习总结 — {日期}

### 📌 重点关注
[把今天最值得关注的1-3条内容单独列在这里，而不是埋在10条速览里]
- 🔥 [最有价值的知识点] — 一句话说明为什么重要

### 🔥 10条干货速览
1. ...
2. ...

### 🔧 今日新/更新技能
- skill-name vX.0 → {新增/更新}

### ⚡ 实操执行步骤
1. ...
2. ...

### 📋 下次预告：{下一类别}
```

## ⚠️ 注意事项

1. 确保 `web` 工具集已启用（用于全网搜索）
2. 不要生成空洞内容，每条技能必须有实际操作价值
3. 优先收录2026最新有效玩法，剔除过时规则
4. 所有内容贴合无货源跨境、Shopee泰国站、图文短视频、Windows服务器智能体落地实战
5. 每周做一次全技能库大盘点

### ⛔ 重要约束：LLM驱动的Cron缺少Terminal工具

**根本原因：** LLM驱动的cron任务（`no_agent=False`，默认值）**没有 terminal 工具可用**。这是Hermes Agent的架构设计——LLM cron由调度器内部触发，不挂载完整的终端工具链。只有 `no_agent=True` 的Script Cron能直接执行shell脚本，因为它跑在OS调度器层级，完全绕过Hermes Agent工具链。

**影响：**
- 任何尝试在LLM cron中执行 `bash script.sh` 的操作都会失败
- `delegate_task` 子代理也无法绕过此限制（子代理继承父代可用的工具集）
- `cronjob(action='run')` 只是重新计算 `next_run_at`，不会立即执行脚本

**应对方案（按优先级）：**
1. ✅ **最佳：使用 Script Cron（`no_agent=True`）** — shell脚本采集任务全部用此模式，如 `auto-learn-采集`（1-7点，每小时执行）
2. ❌ **不可行：LLM cron + terminal** — 终端工具在LLM cron会话中不可用
3. ❌ **不可行：cronjob(action='run') 触发** — 不会立即执行，只重算调度
4. ⚠️ **部分可用：把任务拆分为两步** — LLM cron负责判断要不要采集，然后触发一个 `no_agent=True` 的独立脚本任务

**验证方法：** 如果在LLM cron会话中看到工具列表没有 `terminal`，说明这是正常设计，不要试图诊断"terminal工具坏了"——而是把shell脚本执行工作移到 `no_agent=True` 的Script Cron中。

## 📋 采集任务失败时报告规范

当Hermes Agent的cron任务需要执行采集脚本，但终端工具链故障导致无法运行时：

**永远不要直接返回 [SILENT]。** 即使脚本没跑起来，也要报告能找到的所有诊断信息：

1. **尝试执行脚本**并记录具体错误（不是"失败了"三个字，而是什么错误、哪个文件哪行）
2. **检查cron是否已在独立运行** — 用 `cronjob(action='list')` 查看 `auto-learn-采集` 任务的状态
3. **检查历史产出** — 用 `search_files` 查看 `~/.hermes/skills/auto_learned/` 下过去几天的目录是否存在、文件是否完整
4. **检查脚本路径是否正确** — 确认 `/root/.hermes/scripts/learn/auto_learn.sh` 存在
5. **报告下次cron执行时间** — 如果系统级cron正常运行，告知用户下次自动采集时间

报告模板：

```markdown
## 采集任务执行状态

### 脚本执行结果：❌ 无法执行
- 原因：{具体错误信息}
- 脚本路径：{实际路径，与用户给的路径对比}

### ⏲️ 系统cron状态
- 任务名：{cron name} | ID: {job_id}
- 定时：{schedule}
- 上次运行：{时间}，状态：{ok/failed}
- 累计成功：{N}次
- 下次执行：{时间}

### 📂 历史产出检查
- 最近产出日期：{最近日期}
- 文件列表：{列出文件}
- 今日是否已有产出：{是/否}
```

## 🔄 工作流

### 每日执行时间线
```
01:00 — Script Cron: 采集 HN/Dev.to/arXiv → 存日期目录
02:00 — Script Cron: 采集 HN/Dev.to/arXiv → 存日期目录
03:00 — Script Cron: 采集 HN/Dev.to/arXiv → 存日期目录
...
07:00 — Script Cron: 最后一次采集
10:00 — [计划中] LLM驱动: 读取采集数据 → 归类 → 创建/更新技能 → 推送到飞书
```

### Script Cron 工作流（已部署）
```mermaid
每天01:00-07:00整点 → 系统shell执行auto_learn.sh
  → curl抓取HN最新30条
  → curl抓取Dev.to最新10条
  → curl抓取arXiv
  → 存入 ~/.hermes/skills/auto_learned/YYYY-MM-DD/
  → 生成 _summary.txt
```

### LLM驱动 工作流（计划中）

## ⚡ 关键流程：进度文件维护规范

文件位置：`/root/.hermes/auto_learn_progress.txt`

**致命教训：不要使用patch工具修改进度文件！** 使用 `write_file` 一次整体写入。

### 技能更新流程

1. 先用 `read_file` 读取完整skill，确认版本号和已有内容
2. 使用 `patch` 更新文件头（版本号+本轮新增概要） 
3. 使用 `patch` 插入新章节 / 更新数据表格
4. 用 `read_file` 验证完整性


