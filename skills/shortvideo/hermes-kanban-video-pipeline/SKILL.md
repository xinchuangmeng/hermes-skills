---
name: hermes-kanban-video-pipeline
description: 基于Hermes Agent Kanban看板系统的短视频自动化生产线架构。核心模式：Hermes=导演（调度编排），Profile=工种（planner/copywriter/storyboarder等8个角色），Skill=工具（FFmpeg/Whisper/TTS），Kanban=传送带（8状态自动流转），DAG=事件驱动任务依赖链。含完整的看板设计、Profile分工、Prompt模板和MVP路径。
category: shortvideo
---

# Hermes Kanban 短视频自动化生产线

> 来源：AI实战派老陈文章《Hermes Agent 官方看板实战：我用它搭了一套短视频自动生产线》（2026/5/15）
> 核心理念：让大模型当导演，不当工人。

## 一、核心架构：三层分工

```
Hermes Agent（导演/调度）
    ↓
Profile（工种——planner/copywriter/editor等）
    ↓
Skill（工具——FFmpeg/Whisper/TTS/ComfyUI等）
```

### 三层职责

| 层级 | 角色 | 职责 | 类比 |
|------|------|------|------|
| 调度层 | Hermes Agent | 理解需求、拆解任务、分配Profile、推进状态、失败重试 | 导演 |
| 执行层 | Profile（工种） | 每个Profile固定能力：写脚本、分镜、素材、剪辑等 | 工厂工位 |
| 工具层 | Skill（执行器） | 真正干活：TTS、图片生成、视频剪辑、字幕等 | 工具 |

**设计原则**：Hermes只负责编排，不直接执行复杂任务。复杂任务交给专业的Skill工具。

## 二、看板设计：8状态自动流转

| 状态 | 含义 | 谁处理 | 输出物 |
|------|------|--------|--------|
| Inbox | 用户需求进入 | planner | 结构化需求JSON |
| Planning | AI自动拆解任务 | planner | 任务清单+依赖关系 |
| Script | 脚本生成 | copywriter | 结构化脚本JSON |
| Storyboard | 分镜设计 | storyboarder | 分镜JSON |
| Assets | 素材生成 | image-artist/voice-maker | 图片+音频素材 |
| Editing | 自动剪辑 | editor | 初剪视频 |
| Review | 人工审核 | 人 | 通过/重生成/修改 |
| Done | 完成 | - | 最终视频 |
| Failed | 失败（重试） | 对应Profile | 错误日志+重试原因 |

**失败处理**：每个Failed任务记录失败原因，由对应Profile重新领取执行。

## 三、Profile分工（8个工种）

| Profile | 职责 | 输出物 |
|---------|------|--------|
| planner | 理解需求、拆解任务 | 任务清单+依赖图 |
| copywriter | 撰写视频脚本 | 结构化脚本JSON |
| storyboarder | 设计分镜 | 分镜JSON |
| image-artist | 生成图片素材 | PNG/JPG素材 |
| voice-maker | 生成配音 | WAV/MP3音频 |
| editor | 视频剪辑合成 | MP4视频 |
| subtitle-maker | 生成字幕 | SRT/ASS字幕 |
| publisher | 发布文案撰写 | 发布文案+标签 |

### 创建看板和Profile

```bash
# 创建工种 Profile
hermes profile create planner --description "任务规划师"
hermes profile create copywriter --description "脚本撰写师"
hermes profile create storyboarder --description "分镜设计师"
hermes profile create image-artist --description "素材生成师"
hermes profile create voice-maker --description "配音制作师"
hermes profile create editor --description "视频剪辑师"

# 创建短视频看板
hermes kanban boards create video-production \
  --name "短视频生产线" \
  --icon 🎬 \
  --description "自动化视频制作流水线"

# 切换到视频看板
hermes kanban boards switch video-production

# 创建一条视频任务
hermes kanban create "《AI Agent入门》抖音短视频，时长2分钟" \
  --body "平台：抖音；风格：科普；受众：小白；时长：120秒" \
  --assignee planner \
  --priority high
```

## 四、核心Prompt模板

### 需求分析（Planner）
用户输入需求后转为结构化JSON：
```json
{
  "topic": "ETF网格交易",
  "platform": "douyin",
  "duration": 120,
  "style": "科普",
  "audience": "小白",
  "key_points": ["什么是ETF", "什么是网格交易"]
}
```

### 脚本生成（Copywriter）— 强制JSON输出
```
请根据以下需求生成结构化脚本（JSON格式）：
- 主题：{topic}
- 平台：{platform}
- 时长：{duration}秒
要求：
1. 每个场景包含：scene编号、speech文案、duration预估
2. 设计开头钩子：吸引眼球的前3秒
3. 输出JSON，不要输出纯文案
```

### 分镜生成（Storyboarder）
```json
{
  "scenes": [
    {"scene": 1, "prompt": "...", "camera": "medium shot", "duration": 5}
  ]
}
```

## 五、DAG任务依赖链（事件驱动）

**核心原则**：不要轮询，要事件驱动。

```bash
# 建立任务依赖链
hermes kanban link <script_task_id> <storyboard_task_id>
hermes kanban link <storyboard_task_id> <image_task_id>
hermes kanban link <storyboard_task_id> <voice_task_id>
hermes kanban link <image_task_id> <editing_task_id>
hermes kanban link <voice_task_id> <editing_task_id>
hermes kanban link <editing_task_id> <review_task_id>
```

**完整DAG流程**：
```
需求输入 → [Planning] → [Script] → [Storyboard] → [Image] + [Voice]（并行）
→ [Editing]（依赖Image+Voice都完成）→ [Review] → [Done]
```

## 六、MVP路径：最小可行链路

**第一阶段（MVP）**：只跑通基础链路
```
需求 → 脚本 → TTS配音 → 字幕 → FFmpeg合成 → 视频导出
```

| 阶段 | 新增功能 | 扩展内容 |
|------|----------|----------|
| MVP | 基础链路 | 脚本→TTS→字幕→FFmpeg→导出 |
| Phase 2 | 分镜设计 | + Storyboarder + AI图片生成 |
| Phase 3 | 视频素材 | + Pexels/Kling/Runway视频素材 |
| Phase 4 | 自动发布 | + Publisher + 平台API自动上传 |
| Phase 5 | 数据分析 | + 播放数据回传 + 爆款分析 |

## 七、Skill技术选型

| 环节 | 推荐工具 | 费用 |
|------|----------|------|
| TTS配音 | CosyVoice / EdgeTTS | 免费 |
| 图片生成 | ComfyUI+Flux / Midjourney | 免费/付费 |
| 视频素材 | Pexels API / Kling / Runway | 免费/付费 |
| 视频生成 | Kling / Runway Gen-3 | 付费 |
| 视频剪辑 | FFmpeg | 免费 |
| 字幕生成 | Whisper | 免费 |
| 素材搜索 | Pexels / Pixabay API | 免费额度 |

## 八、方法论总结

### 3条核心心得
1. **让大模型当导演，不当工人** — 编排>执行
2. **分工越细，质量越稳** — 一个Profile只干一件事
3. **DAG依赖链是自动化的核心** — 事件驱动，不轮询

### 5条复用技巧
1. Profile名要语义化（planner/copywriter/editor）
2. 任务输出强制JSON格式，方便下游消费
3. 先跑通MVP，再逐步扩展
4. 失败任务不要删除，回流重试（`hermes kanban unblock <id>`）
5. 看板按项目分开

### 相关技能
- `shortvideo-ai-full-chain-production` — AI全链路短视频生产
- `movie-level-short-video-script` — 电影级短视频脚本
- `ai-video-pipeline-voice-scene-sync` — 配音画面同步
