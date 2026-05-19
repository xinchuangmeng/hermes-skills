---
name: server-blocked-from-social-platforms
description: 当腾讯云服务器IP被抖音/小红书等平台拉黑(403)时，获取参考视频/图文的替代方案清单。
  根因是服务器IP在平台黑名单中，安装任何爬虫工具(crawl4ai/Jina Reader)都无法绕过。
tags:
  - 抖音
  - 403
  - IP封锁
  - 腾讯云
  - 内容获取
  - 参考素材
trigger:
  - "抖音看不了"
  - "403"
  - "被屏蔽"
  - "被封"
  - "服务器访问不了"
  - "social blocked"
  - "IP拉黑"
  - "platform blocked"
---

# 服务器被社交平台封锁的替代方案

## 根因诊断

**不是工具的问题，是IP的问题。** 腾讯云服务器IP被抖音/小红书等平台拉黑后：
- ✅ 服务器可正常访问百度、GitHub、必米云等
- ❌ 抖音返回403（不接受任何请求）
- ❌ 即使用crawl4ai/Playwright/Chrome浏览器模拟，一样403
- ❌ Jina Reader（r.jina.ai）在这类服务器上也可能连不上

## 从"服务器不能看"到"能拿到素材"的5种方案

### 方案A：用户截图（最快，推荐）
用户用手机打开目标抖音/小红书/视频号，**截3-5张关键画面**发到飞书/微信。
AI用`vision_analyze`分析截图，就能了解排版风格和内容结构。
- 耗时：30秒
- 不需要任何特殊工具

### 方案B：用户录屏后传给服务器（需指导）
- 用户用手机录屏MP4
- 方式1：SCP传输
  `scp video.mp4 agentuser@SERVER_IP:/home/agentuser/`
- 方式2：启动临时HTTP上传页面（Python Flask/AIOHTTP），用户浏览器打开链接上传
- 方式3：用户上传到对象存储（COS/OSS），给链接下载

### 方案C：用户本地电脑上的Hermes（需要Windows原生版）
如果用户本地装了Hermes Windows版（v0.13.0+），直接从本地电脑访问抖音。
**PowerShell一行安装：**
```powershell
irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1 | iex
```
本地电脑IP不会被封，可以直接用浏览器工具打开抖音链接。

### 方案D：用户描述参考风格
让用户描述目标视频的核心元素：
- 背景颜色/图案
- 文字排版（居中/左对齐）
- 字体风格（粗体/细体）
- 整体风格（简约商务/卡通/科技/手绘）
- 每张卡片的文案量（大致字数）

### 方案E：新服务器换IP（长期方案）
购买新服务器（不同IP段），抖音等平台对新IP无封锁记录。
- 腾讯云轻量服务器约60元/月
- 迁移前先测试新IP能否访问抖音

## 什么工具装上了也没用

| 工具 | 效果 | 原因 |
|------|------|------|
| crawl4ai | ❌ 无济于事 | 工具能模拟浏览器，但IP被封一样403 |
| Jina Reader | ❌ 可能连不上 | 国内服务器到r.jina.ai可能网络不通 |
| Playwright | ❌ 无济于事 | 浏览器换壳，IP还是被封的 |
| yt-dlp | ❌ 抖音不支持 | 抖音note/图文类型不被yt-dlp支持 |
| 任何代理/转发 | ⚠️ 除非有干净的代理IP | 需要买没被封的代理IP池 |

## Hermes v0.13.0 Windows原生支持

从v0.13.0 (2026.5.7)起，Hermes Agent正式支持**Windows原生运行**（early beta）：
- 一行PowerShell安装：`irm ...install.ps1 | iex`
- 自动安装Python/Node.js/ffmpeg/内置Git Bash（MinGit 45MB）
- 安装目录：`%LOCALAPPDATA%\hermes`
- **唯一还依赖WSL2的**：浏览器仪表板的聊天面板（POSIX PTY）
- CLI和网关都已原生支持Windows

这对内容获取的意义：用户本地Windows电脑装的Hermes，IP是自己的宽带IP，不会被社交平台封禁，可以直接用browser工具打开抖音链接观看内容。
