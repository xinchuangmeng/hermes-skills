---
name: whaleclip-openclaw-skill
description: "WhaleClip(鲸剪) OpenClaw Skill 完整知识体系——AI视频剪辑桌面软件，给小强（OpenClaw）安装后，小强能用CLI命令自动调用鲸剪完成：视频文案提取、智能字幕、气口剪辑、BGM配乐、一键去重、数字人视频、AI绘画、画质修复等。装在Windows桌面端上使用，服务器不能跑。"
tags: [whaleclip, 鲸剪, openclaw, 视频剪辑, AI自动化]
---

# WhaleClip（鲸剪）OpenClaw Skill 知识体系

## 是什么

**WhaleClip（鲸剪）** 是一款AI智能视频剪辑桌面软件（Windows），官网 `https://www.whaleclip.com/`。

**OpenClaw Skill** 是让AI智能体（如小强/OpenClaw）通过CLI命令自动调用鲸剪功能的"技能包"。装了这个skill后，小强能用一句话调用鲸剪自动剪片。

## 给小强安装命令

在小强飞书对话里发：
```
clawhub install whaleclip
```

或者：
```
clawhub install whaleclip-skills
```

## 前置条件

| 项目 | 说明 |
|------|------|
| 系统 | **Windows + PowerShell**（必须） |
| 鲸剪桌面端 | 从 `https://www.whaleclip.com` 安装，建议至少登录一次 |
| 小强 | 已安装OpenClaw |

## 核心CLI能力清单

### 管理类（无需VIP）
- `cli list` — 查看已开放命令
- `cli enable --id <commandId>` — 开放命令
- `cli disable --id <commandId>` — 禁用命令

### 视频处理（需VIP）
- `mcp process-video --input <路径> --instructions "加速1.5倍"` — 视频处理
- `mcp intelligent-subtitles --input <路径>` — 智能字幕
- `mcp breath-cutter --input <路径> [--threshold -20]` — 气口剪辑
- `mcp smart-music --input <路径> --volume 0.5` — 智能BGM
- `mcp unique --input <路径>` — 一键去重

### 数字人 & 声音（需VIP）
- `dh list-characters` — 列出数字人角色
- `dh generate --text "文案" --characterId <ID>` — 文生数字人
- `voice list` — 列出音色库
- `voice clone --text "文案" --voice "音色名"` — 声音克隆

### 文案 & 下载（需VIP）
- `transcript extract --input <视频路径或链接>` — 提取视频文案
- `video download --input <链接>` — 视频去水印下载
- `ai draw --prompt <提示词> --size 1024*1024` — AI绘画

## 对小强的操作提示

装了后可以说：
> "小强，下载这个抖音链接：https://v.douyin.com/xxx"
> → 自动调 `video download`

> "小强，把这个视频加上智能字幕"
> → 自动调 `mcp intelligent-subtitles`

## 注意事项

1. **OpenClaw生态的技能**，Hermes没有
2. **必须Windows+鲸剪桌面版**，服务器跑不了
3. **VIP功能需付费**
4. 小强可能用 `clawhub install` 而非 `claw install`，取决于小强版本
5. 对用户回复时**不能暴露技术细节**（Whisper/ffmpeg等）
