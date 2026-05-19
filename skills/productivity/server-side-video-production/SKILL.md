---
name: server-side-video-production
description: 全自动AI短视频生产线——从文案/分镜到手，在服务器上完成：SiliconFlow CosyVoice2声音克隆+TTS配音生成、Seedance 1.5-pro AI画面生成、FFmpeg封面+配音+画面+字幕合成成品视频。用户只需提供录音样本（29秒内）和文案主题，服务器自动出片。支持scp传成品到Windows。
version: 2.0.0
author: Hermes 小书童
tags: [声音克隆, TTS, CosyVoice2, Seedance, FFmpeg, 视频合成, 自动化, SiliconFlow, 火山引擎, 方舟, 短视频, 视频号]
---

# 全自动AI短视频生产线 v3

## 适用场景
用户给一个主题/文案，在服务器上完成大部分工作（文案→配音→AI画面→粗合成），产出粗剪版成品，再由用户在剪映专业版做最后20%的精修（套LUT+加音效+BGM）。

## 两种交付模式

### 模式A：纯自动化（快速交付，质感⭐⭐⭐）
服务器全自动完成全部流程，用户直接下载发布。
**适用**：赶时间/测试选题/日更时的保底方案。
**缺点**：画面循环生硬、无调色、无情感音效、质感上限低。

### 模式B：混合模式（推荐，质感⭐⭐⭐⭐）
服务器完成80%工作 → 用户在剪映专业版做最后20%精修。
**适用**：正式发布的视频、追求质感的视频。
**优势**：LUT调色+音效+BGM分层，5分钟精修质感翻倍。

```
┌────────────────────────────────────────────┐
│  服务器自动完成（80%）：                       │
│  文案→配音→Seedance画面→FFmpeg粗合成        │
│  ↓                                            │
│  产出：粗剪版MP4（画面+配音+基础字幕+封面）    │
└────────────────────────────────────────────┘
        ↓ SCP传至Windows
┌────────────────────────────────────────────┐
│  用户剪映精修（20%，5-8分钟）：               │
│  ① 套LUT预设（暗金电影感）                   │
│  ② 加音效（开场/转折/收尾3处）               │
│  ③ 加BGM分层（15-20%音量+淡出）             │
│  ④ 导出1080P 30fps                           │
└────────────────────────────────────────────┘
```

## 完整工作流

### 第一阶段：文案与分镜
1. 确认选题和尾钩接续
2. 写60-75秒口播稿（悬念故事型，含数字锚点）
3. 写逐秒分镜脚本（含运镜/灯光/景别/音效）
4. 确认BGM、封面、引导话术
5. 写Seedance画面提示词（5-7段）

### 第二阶段：声音克隆（一次性设置，以后复用）
#### 2.1 上传录音样本
```bash
# 原始录音(m4a/wav) → 16kHz单声道wav，**必须≤29秒！**
ffmpeg -i voice_sample.m4a -acodec pcm_s16le -ar 16000 -ac 1 /tmp/voice_16k.wav
ffmpeg -i /tmp/voice_16k.wav -t 29 -acodec copy /tmp/voice_29s.wav

# 上传到SiliconFlow做零样本声音克隆
curl -X POST "https://api.siliconflow.cn/v1/uploads/audio/voice" \
  -H "Authorization: Bearer $SILICONFLOW_API_KEY" \
  -F "file=@/tmp/voice_29s.wav" \
  -F "model=FunAudioLLM/CosyVoice2-0.5B" \
  -F "customName=jinge-voice" \
  -F "text=录音对应的文本内容"
# → 保存返回的uri: speech:voice-name:userId:token
```

#### 2.2 生成配音（每段文案）
```bash
# ⚠️ 每段生成的配音不能超过30秒（API限制）
# 文案要切成短段（每段20-25秒口播）
# 文本太短（<30字）可能返回空文件

curl -s -X POST "https://api.siliconflow.cn/v1/audio/speech" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"FunAudioLLM/CosyVoice2-0.5B\",
    \"input\": \"文案文本\",
    \"voice\": \"speech:voice-name:userId:token\",
    \"response_format\": \"wav\",
    \"speed\": 1.0
  }" -o voice_s01.wav
```

#### 2.3 合并配音
```bash
for f in voice_s01.wav voice_s02.wav voice_s03.wav; do
  echo "file '$PWD/$f'" >> concat_list.txt
done
ffmpeg -f concat -safe 0 -i concat_list.txt \
  -acodec pcm_s16le -ar 24000 -ac 1 voice_full.wav -y
```

### 第三阶段：AI画面生成（Seedance 1.5-pro）
#### 3.1 批量生成5-7段场景画面
```bash
API_KEY="ark-xxx"

curl -s -X POST "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "doubao-seedance-1-5-pro-251215",
    "content": [{"type": "text", "text": "运镜+主体+环境+灯光+氛围 --duration 5 --resolution 720p"}]
  }'
```
#### 3.2 轮询等待并下载
```bash
# 所有视频生成完成后（约30-60秒），下载到本地
# video_url有效期24小时，必须及时下载
curl -s "$VIDEO_URL" -o scene1.mp4
```

### 第四阶段：封面图
```python
from PIL import Image, ImageDraw, ImageFont
font_cn_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
# 1080×1920竖版，深灰蓝底+白字+金色强调
```

### 第五阶段：视频合成
#### 5.1 封面→视频片段
```bash
ffmpeg -y -loop 1 -i cover.png -c:v libx264 -t 3 \
  -pix_fmt yuv420p \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" \
  cover_video.mp4
```

#### 5.2 合并所有画面片段
```bash
for f in cover_video.mp4 scene1.mp4 scene2.mp4; do
  echo "file '$PWD/$f'" >> video_concat.txt
done
ffmpeg -f concat -safe 0 -i video_concat.txt -c copy scenes_combined.mp4 -y
```

#### 5.3 画面+配音合成（核心：画面循环匹配配音长度）
```bash
# 画面通常27秒（封面3s+5场景各5s），配音57秒
# 用-stream_loop -1让画面无限循环，-shortest在配音结束时停止
ffmpeg -y -stream_loop -1 -i scenes_combined.mp4 \
  -i voice_full.wav \
  -map 0:v -map 1:a \
  -c:v copy -c:a aac -b:a 128k \
  -shortest -t 57.5 \
  final_video.mp4
```

#### 5.4 字幕硬编码（可选）
```bash
ffmpeg -i final_video.mp4 -vf "subtitles=subs.srt:force_style='FontName=Noto Sans CJK SC,FontSize=18,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=1,MarginV=40'" \
  -c:a copy final_with_subs.mp4 -y
```

### 第六阶段：交付成品
```bash
# scp给用户（Windows cmd执行）
scp agentuser@42.193.201.6:/home/agentuser/sea-ecommerce/video_assets/final_video_simple.mp4 C:\Users\Administrator\Downloads\
```

## 关键配置

### SiliconFlow（声音克隆+TTS）
- API端点：`https://api.siliconflow.cn`
- 模型：`FunAudioLLM/CosyVoice2-0.5B`
- 上传声音：`POST /v1/uploads/audio/voice`（multipart/form-data）
- TTS生成：`POST /v1/audio/speech`
- 预设声音测试：`:alex`（男）, `:bella`（女）
- **录音样本必须≤29秒**，否则报20015
- **每段生成音频必须≤30秒**
- **需要账户有余额**，最低充1元可用

### 火山引擎方舟（Seedance视频生成）
- API端点：`https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks`
- 模型：`doubao-seedance-1-5-pro-251215`（首选，200万免费tokens）
- 参数：`--duration 5 --resolution 720p`
- 并发：10条同时
- video_url有效期24小时

## 已知坑点
1. **KbdInteractiveAuthentication**：SSH密码登录默认被禁用（Ubuntu），需改`sshd_config`中`KbdInteractiveAuthentication no`为`yes`，然后`sudo systemctl restart sshd`
2. **飞书传文件**：webhook不能直接发文件，需OAuth2的tenant_access_token调用im/v1/files；App Secret不对就无法工作。最终方案：scp是唯一稳定方式
3. **腾讯云安全组**：端口默认全关，需要控制台放行。scp走22端口（SSH），通常默认开放
4. **Seedance画面有音频**：自动生成环境音，合成时需要注意音频轨冲突
5. **短文本返回空文件**：TTS文本太短（<30字）可能返回0字节WAV；文本太长（>30秒时长）报20015错误
6. **GitHub下载受限**：腾讯云服务器连GitHub可能超时，用wget+代理或换源
7. **CosyVoice2零样本克隆音质有限**：相似度尚可但音质差（像电话音），清晰度不如真人录音。对音质要求高→换火山引擎声音复刻2.0（150元/年，97.5%相似度，支持情感指令控制）
8. **视频画面循环缺陷**：用`-stream_loop -1`让画面循环时，生硬的重复循环导致观感差。正确做法：设计足够多的独特场景（每12秒切一次），让画面总时长≈配音时长，避免循环
9. **声画时长不匹配**：画面通常27秒（封面3s+5场景各5s），配音57秒。画面不足就得循环→品质差。**解决方法：增加场景数量到7-10个，或把每个场景拉长到10秒**

## 声音方案选择
| 方案 | 音质 | 情感控制 | 成本 | 推荐场景 |
|------|------|---------|------|---------|
| **CosyVoice2零样本克隆** | ⭐⭐ 像电话音 | ❌ 无 | 按量付费≈0.003元/条 | 快速测试/赶时间 |
| **火山引擎声音复刻2.0** | ⭐⭐⭐⭐ 97.5%相似 | ✅ 指令式+上下文 | 150元/年/音色 | **生产级最佳选择** |
| **用户真人录音** | ⭐⭐⭐⭐⭐ 最好 | ✅ 天然情感 | 免费（但花时间） | 高品质视频首选 |
| **预设TTS声音** | ⭐⭐⭐ 清晰但不像人 | ❌ 平 | 免费/低费 | 无品牌声音需求 |

## Seedance模型选型

| 模型 | 质量 | 速度 | 价格 | 适用场景 |
|------|------|------|------|---------|
| **1.0 pro-fast** | ⭐⭐⭐ | 最快（无队列） | 0.12元/秒 | 测试/赶时间/非关键帧 |
| **1.5 pro** | ⭐⭐⭐⭐ | 中等（可能有队列） | ~1元/秒 | 正式画面（首帧/尾帧/关键场景） |
| **2.0** | ⭐⭐⭐⭐⭐ 电影级 | 需等待（2-8小时免费） | 看套餐 | 追求极致质感（需账号开通） |

**实战经验**：1.5 pro的免费tokens用完后，pro-fast是最经济的替代方案。如要质感，优先在即梦网页版用2.0生成关键画面（首帧/尾帧），再下载到服务器合成。

## 即梦AI 5.0做文字标题（补充）
用在服务器端生成黑色背景的文字标题图（PIL/FFmpeg）效果有限。**推荐用户直接在即梦网页版操作**：
1. 图片生成 → 图片5.0模型
2. 提示词用英文双引号包裹文字：`"第一个月·5件事"`
3. 搭配"黑底金字、行楷、金辉光效、电影级质感"
4. 生成的图片下载后发给我，我用来做图生视频的动态标题

## 输出物清单
| 输出物 | 路径 |
|--------|------|
| 成品视频MP4 | sea-ecommerce/video_assets/final_video.mp4 |
| 封面图PNG | sea-ecommerce/video_assets/cover_*.png |
| 配音WAV | sea-ecommerce/video_assets/voice_full.wav |
| AI画面MP4 | sea-ecommerce/video_assets/scene*.mp4 |
| 字幕SRT | sea-ecommerce/video_assets/*.srt |
| LUT调色.cube | sea-ecommerce/video_assets/*.cube |
| 文案+分镜MD | sea-ecommerce/video_scripts/*.md |
| 录音样本 | sea-ecommerce/voice_cloning/voice_sample_original.* |
