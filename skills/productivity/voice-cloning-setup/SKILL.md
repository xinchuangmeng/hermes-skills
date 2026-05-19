---
name: voice-cloning-setup
description: 在服务器上用API（SiliconFlow CosyVoice2 / Fish Audio）做零样本声音克隆+TTS配音，用户只需提供录音样本+文案，剩下的全自动完成。注意：这是AI的工作，不能推给用户手动操作。
version: 2.1.0
author: Hermes 小书童
tags: [声音克隆, TTS, 服务器端, SiliconFlow, CosyVoice, FishAudio, 自动化, 短视频配音, 口播]
---

# 服务器端声音克隆+TTS全自动工作流

## 铁纪律：必须自动化，不能推给用户

**核心教训：** 声音克隆是我的工作。用户只需提供录音样本和文案。不要叫用户去剪映操作声音克隆、不要叫用户去注册账号、不要叫用户去录口播——**"你只需要提供素材，剩下的归我"**。

### 正确流程
1. 用户提供：录音样本（1条）+ 文案（文本）
2. 我来做：上传克隆 → 生成TTS配音 → FFmpeg合成视频 → 出成品
3. 用户只需要：下载成品 → 发布

### 错误示范（踩过的坑）
- ❌ "你去剪映声音克隆一下" → 用户说"你要把流程形成技能，以后你每天都要用来做视频的"
- ❌ "你手机录个口播传给我" → 用户回复"模型都给你配了"

## 方案选型

### 方案A：SiliconFlow CosyVoice2 API（首选 ⭐）
- **成本：** 免费注册送18元额度，充值1元起步
- **质量：** CosyVoice2中文TTS优秀，零样本声音克隆
- **操作：** REST API，无需安装任何库
- **延迟：** <150ms首包延迟
- **注册：** https://cloud.siliconflow.cn/ → API Keys
- **端点：** `https://api.siliconflow.cn/v1/audio/speech`
- **注意：** 余额不足会报 `"Sorry, your account balance is insufficient"`(code 30001)

### 方案B：Fish Audio API（备选）
- **成本：** 免费注册有月额度
- **质量：** S2模型在盲测中胜ElevenLabs 60/40
- **注册：** https://fish.audio/app/api-keys/
- **文档：** https://docs.fish.audio/developer-guide/getting-started/quickstart

### 方案C：火山引擎豆包声音复刻2.0（高质量推荐 ⭐）
- 150元/年/音色，97%+相似度，支持**情感指令控制**（生气/悲伤/开心/暧昧/撒娇/吵架/颤抖等）
- 训练14-30秒录音即可，支持通过 `context_texts` 让合成匹配对话语境
- **官网：** https://www.volcengine.com/product/speech（豆包语音）
- **控制台入口：** https://console.volcengine.com/speech/new/overview
- 开通路径：控制台 → 豆包语音 → 开通管理 → 开通声音复刻2.0
- **⚠️ 重要踩坑：API层鉴权复杂，建议直接让用户在控制台操作复刻训练！**

**⚠️ 核心教训：不要花时间在API鉴权上折腾！**
让用户在控制台完成：
1. 点链接 https://console.volcengine.com/speech/new/overview 登录
2. 开通管理 → 开通声音复刻2.0服务
3. 在音色库 → 点"复刻音色" → 上传14-30秒录音样本 → 自动训练
4. 训练完成后得到 **speaker_id**（如 `S_W4fKDzY12`）
5. 拿到speaker_id后，我在服务器侧调API合成配音

**合成API的正确调用方式（HTTP Chunked流式）：**
```python
import base64, json, uuid, requests

API_KEY = "用户控制台的API Key"
SPEAKER_ID = "S_xxxx"

def synthesize(text, output_path):
    """合成语音 - HTTP Chunked流式"""
    resp = requests.post(
        "https://openspeech.bytedance.com/api/v3/tts/unidirectional",
        headers={
            "Content-Type": "application/json",
            "X-Api-Key": API_KEY,
            "X-Api-Resource-Id": "seed-icl-2.0",
            "X-Api-Request-Id": str(uuid.uuid4()),
        },
        json={
            "user": {"uid": "jinge_user"},
            "event": 100,
            "req_params": {
                "text": text,
                "speaker": SPEAKER_ID,
                "audio_params": {"format": "mp3", "sample_rate": 24000}
            }
        },
        stream=True,
        timeout=60
    )
    
    all_audio = bytearray()
    for line in resp.iter_lines(decode_unicode=True):
        if line:
            data = json.loads(line)
            b64 = data.get("data", "")
            if b64:
                padding = 4 - len(b64) % 4
                if padding != 4: b64 += "=" * padding
                all_audio.extend(base64.b64decode(b64))
    
    with open(output_path, "wb") as f:
        f.write(all_audio)
```

**关键踩坑点：**
- 响应不是单个JSON，而是**多行JSON（HTTP Chunked）**，每行一个chunk！
- 必须用 `resp.iter_lines(decode_unicode=True)` 读取
- `X-Api-Resource-Id` 必须传 `"seed-icl-2.0"`（声音复刻2.0），不能是 `"seed-tts-2.0"`（语音合成）
- 合成时用 **V3接口**（`/api/v3/tts/unidirectional`），不用旧版V1
- 不同的Voice SDK鉴权方式不互通，直接让用户用**新版控制台**获取API Key

### 方案D：本地模型（仅离线要求时）
- pocket-tts / CosyVoice需下载PyTorch（800MB+）
- 服务器网速慢时安装耗时过长

## 完整工作流

### 第一步：用户提供素材
1. **录音样本**（推荐1-3分钟，含不同语气：陈述/疑问/强调/鼓励等）
2. **文案文本**（要生成配音的完整文案，60秒口播约150-200字）

### 第二步：用户注册并获取API Key
让用户去SiliconFlow注册，拿到Key后发给我：
1. 打开 https://cloud.siliconflow.cn/
2. 注册/登录（微信/手机号均可）
3. 进API Keys页面创建Key
4. 需要充值才能用TTS（最低1元）
5. 把Key发给我

### 第三步：检查余额
```bash
curl -s "https://api.siliconflow.cn/v1/user/info" \
  -H "Authorization: Bearer $API_KEY" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'余额: {d[\"data\"][\"balance\"]}')"
```

### 第四步：上传录音做零样本声音克隆

方式1：上传文件（推荐，支持长音频）
```bash
# 录音样本如为.m4a，先转为wav
ffmpeg -i sample.m4a -acodec pcm_s16le -ar 16000 -ac 1 sample.wav -y

# 上传
curl -s -X POST "https://api.siliconflow.cn/v1/uploads/audio/voice" \
  -H "Authorization: Bearer $API_KEY" \
  -F "file=@sample.wav" \
  -F "model=FunAudioLLM/CosyVoice2-0.5B" \
  -F "customName=my-voice" \
  -F "text=录音中说的文本内容，要尽量准确，帮助AI理解参考音频的内容"
```
返回：`{"uri": "speech:my-voice:xxx:xxx"}`

**注意：** 录音样本不能超过30秒！如果用户给的录音超过30秒，先裁剪：
```bash
ffmpeg -i original.wav -t 30 -acodec copy clip_30s.wav -y
```

**注意：** CosyVoice2零样本克隆在复刻上像用户声音，但**音质清晰度差**（类似电话音质），用户反馈"听不清"、"音质太差"。建议：
- 如果要求音质高（口播类短视频），直接换 **火山引擎声音复刻2.0**（150元/年）
- 或者让用户**手机直接录口播**（最自然，音质最好）

方式2：base64编码（适合短音频）

### 第五步：用克隆声音生成TTS配音

使用上传时返回的URI：
```bash
VOICE_URI="speech:my-voice:xxx:xxx"

curl -s -X POST "https://api.siliconflow.cn/v1/audio/speech" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"FunAudioLLM/CosyVoice2-0.5B\",
    \"input\": \"要生成配音的文案文本\",
    \"voice\": \"$VOICE_URI\",
    \"response_format\": \"wav\",
    \"speed\": 1.0
  }" -o output.wav
```

### 第六步：分段生成+合并（文案较长时）

60秒口播文案约150-200字，建议分2-3段生成。

**分段策略：** 每段控制在 **30-50字** 最稳定（约5-8秒语音）。
过长的文本（60字+）会触发 `"audio longer than 30s is not supported"` 错误。
建议按自然语义断句拆分，每段是一个完整的信息点。

**如果返回HTTP 200但WAV文件为空（0字节）：**
- 可能是声音URI还没完全就绪
- 重试1-2次即可
- 或者先切换到预设声音 `FunAudioLLM/CosyVoice2-0.5B:alex` 测试可通性

```bash
```bash
# 每段生成保存为 part_01.wav, part_02.wav ...

# 合并
for f in /tmp/tts_parts/part_*.wav; do echo "file '$f'" >> /tmp/filelist.txt; done
ffmpeg -f concat -safe 0 -i /tmp/filelist.txt -c copy /tmp/full_tts.wav -y
```

### 第七步：视频合成

```bash
# 口播配音 + AI画面片段 + BGM + 字幕
ffmpeg -i full_tts.wav -i cover.png -i scene1.mp4 ... \
  -c:v libx264 -preset medium -crf 23 \
  output_final.mp4
```

## 踩坑记录（全是实战经验）

### 1. edge-tts ≠ 声音克隆 ❌
edge-tts只能选微软预设语音（xiaoxiao/xiaoyi等），不能克隆用户声音。不要误以为装了edge-tts就能克隆。

### 2. 录音样本不能超过30秒 ⚠️
SiliconFlow上传接口限制：`"audio longer than 30s is not supported"`（code 20015）
解决方案：用ffmpeg截取前30秒即可，质量依然够用。

### 3. API端点要用 .cn 不是 .com 🔑
- ✅ `https://api.siliconflow.cn/v1/audio/speech`
- ❌ `https://api.siliconflow.com/v1/audio/speech`（401无权）
Key跨域名不通，必须和注册域一致。

### 4. 余额不足会报403 ⚡
- 错误码 `30001`：`"Sorry, your account balance is insufficient"`
- 需要充值才能用TTS
- 免费注册给的18元额度用完后就需充值

### 5. 模型禁用也会报错 ❌
- 错误码 `30003`：`"Model disabled."`
- `fishaudio/fish-speech-1.5` 在部分端点已被禁用
- 用 `FunAudioLLM/CosyVoice2-0.5B` 代替

### 8. 火山引擎声音复刻API踩坑 ❌

火山引擎声音复刻API的鉴权方式非常混乱，**不建议在API层浪费时间**：
- **新版控制台 `X-Api-Key`**：文档说用这个就行，但实际报 `55000000 resource ID is mismatched`（你的API Key没有关联voice clone服务）
- **旧版 `X-Api-App-Key` + `X-Api-Access-Key`**：报 `45000010 grant not found`（已废弃的鉴权方式）
- **V4签名（AK/SK）**：需要 `X-Api-Request-Id` 头，还要签名，非常复杂

**✅ 最佳实践：直接让用户进控制台操作**  
👉 https://console.volcengine.com/speech/new/overview  
进去后：开通声音复刻2.0服务 → 在音色库点"复刻音色" → 上传录音样本（14-30秒） → 控制台自动训练好 → 拿到speaker_id（如 `S_W4fKDzY12`）
```
👉 https://console.volcengine.com/speech/new/overview
```
进去后：开通声音复刻2.0服务 → 在音色库点"复刻音色" → 上传录音样本（14-30秒） → 控制台自动训练好

**情感控制能力：** 声音复刻2.0支持通过 `context_texts` 字段让合成语音适配对话上下文情感，支持指令式控制（生气/悲伤/开心/吵架等），是CosyVoice2不具备的能力。

**⚠️ 注意：** 控制台操作不要推给用户细节——直接告诉用户"点这个链接进去，点'复刻音色'上传你的录音"，不要叫用户研究文档。
PyTorch约800MB，4M带宽服务器下载需数分钟
优先用API方案

### 7. 动态声音URI的调用格式
上传返回的URI格式：`speech:customName:userID:hash`
TTS调用时要全部带上，不能只传customName

## 前提条件
1. ✅ SiliconFlow API Key（用户先注册充值）
2. ✅ 录音样本文件（<30秒，格式wav/mp3/m4a均可）
3. ✅ 文案文本
