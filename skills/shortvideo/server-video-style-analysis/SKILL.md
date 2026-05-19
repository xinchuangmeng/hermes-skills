---
name: server-video-style-analysis
description: "在服务器上分析用户上传的视频风格——用户通过SCP上传MP4到服务器，用ffmpeg抽帧+vision_analyze分析卡片/画面风格。适用于抖音图文视频、录屏教程等参考视频的分析，用户无法直接分享小文件时用此流程。"
tags: [视频分析, 风格分析, 图文卡片, ffmpeg, ai-vision]
---

# 服务器视频风格分析流程

当用户有一个参考视频想给你看，但：
- 文件太大（飞书200MB限制）
- 无法通过飞书/IM直接发送
- 抖音链接服务器IP被封（403）

使用这个流程来分析视频风格。

## 第一步：让用户上传视频到服务器

### 方式A：SCP上传（用户电脑有SSH客户端）
用户执行：
```powershell
scp "C:\Users\xxx\Downloads\video.mp4" agentuser@服务器IP:/home/agentuser/video_analysis/
```

### 方式B：网页上传（备用）
如果scp密码不对，在服务器开一个简单HTTP上传页面。

## 第二步：确认文件到达

```bash
mkdir -p /home/agentuser/video_analysis
ls -lh /home/agentuser/video_analysis/
```

## 第三步：ffmpeg抽帧

从视频中提取关键帧画面：

```bash
# 单个视频抽帧（从第0秒开始，每隔2秒一张）
ffmpeg -i /home/agentuser/video_analysis/video.mp4 \
  -ss 00:00:00 -frames:v 1 -update 1 \
  /home/agentuser/video_analysis/frame_0.jpg -y 2>&1 | tail -3

# 批量抽帧（从多个时间点）
for i in 0 2 4 6 8; do
  ffmpeg -i /home/agentuser/video_analysis/video.mp4 \
    -ss 00:00:0$i -frames:v 1 -update 1 \
    /home/agentuser/video_analysis/frame_$i.jpg -y 2>/dev/null
done
```

注意：`-update 1` 参数是必要的（否则ffmpeg会要求用%03d模式）。

## 第四步：用Vision分析每张帧

```python
# 用vision_analyze分析每张卡片
vision_analyze(
    image_url="/home/agentuser/video_analysis/frame_0.jpg",
    question="分析这张卡片的完整设计风格：背景颜色/图案、文字排版（字体、大小、位置、间距）、整体风格类型。详细描述你看到的一切。"
)
```

## 第五步：风格对比

如果有多组视频，对比它们的风格差异：

| 维度 | 风格A | 风格B |
|------|-------|-------|
| 背景色 | | |
| 文字排版 | | |
| 制作难度 | | |
| 适合场景 | | |

## 关键技巧

1. **抽帧时间点**：视频前8秒通常有封面/关键信息，优先抽0s, 2s, 4s, 6s, 8s
2. **Vision提问要具体**：不是"这是什么"而是"分析这张卡片的背景颜色、文字排版、整体风格"
3. **ffmpeg的-update 1参数**：这是写单张jpg的正确方式（不要用%03d格式）
4. **大视频处理**：168MB的视频也能正常抽帧（ffmpeg只读开头部分）
5. **多个视频对比**：同时抽多组帧，然后并行调用vision_analyze对比
