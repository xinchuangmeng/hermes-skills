---
name: seedance-20-prompt-formula
category: creative
description: Seedance 2.0 提示词万能公式和核心技巧——七维度固定顺序、动作拆解、@语法、负向提示词，出片率从30%提升到90%。含五大核心运镜、三级进阶体系、API配额处理策略
---

# Seedance 2.0 提示词万能公式

## 核心公式（七维度固定顺序）

```
[风格/美学] + [画质/分辨率] + [主体/角色] + [具体动作] + [运镜方式] + [光影/氛围] + [稳定性/约束]
```

> **顺序不可错位**：将"自然柔光"前置可能削弱角色一致性。固定顺序是出片率90%的根基。

## 等级体系：三级进阶

### ⭐ Lv1 新手级（出片率30%）
`一个美丽的女孩在樱花树下微笑`
→ 太笼统，AI自由发挥，画面不可控

### ⭐⭐ Lv2 进阶级（出片率70%）
```
cinematic film still, 4k, a Chinese girl in a white dress, standing under sakura tree,
soft smile then look up, dolly in 缓慢推近, golden hour warm sunlight,
shallow depth of field, avoid camera shake
```

### ⭐⭐⭐ Lv3 大神级（出片率90%+）
```
Glico CM cinematic style, 4k HDR 24fps film grain, a Chinese girl in pure white dress,
抬头看樱花→伸手接花瓣→温柔微笑→低头思考,
slow push-in from medium shot to close-up over 10 seconds,
golden hour backlight creating hair rim light, sakura petals falling in foreground,
warm filmic color grading with slight teal-orange,
avoid static camera, avoid over-saturated, avoid motion blur
```

## 万能运镜公式

```
[主体描述] + [环境氛围] + [光影风格] + [运镜指令] + [画面质感] + [稳定约束]
```

**隐藏玄机：中英文混写效果更好**——中文表达意境，英文精准执行专业镜头术语。

## 五大核心运镜（搞定80%场景）

| 运镜类型 | 核心指令 | 适用场景 | 16种影视级运镜分类 |
|---------|---------|---------|---------|
| **推镜头** | slow push in / dolly in / 缓慢推近 | 聚焦细节、表现情绪变化 | 推进、聚焦、吸入 |
| **跟镜头** | tracking shot / follow / 紧紧跟随 | 主角移动，代入感强 | 追踪、跟随、并行 |
| **拉镜头** | pull back / dolly out / 缓慢拉远 | 交代环境，制造反差 | 后退、揭示、脱离 |
| **摇/移镜头** | pan left/right / tilt / 横向扫视 | 展现风景、画卷式展开 | 摇摄、升降、平移 |
| **环绕镜头** | 360 orbit / arc movement / 围绕旋转 | 全方位展示，增加立体感 | 环绕、螺旋、蝴蝶 |

### 16种影视级运镜全解

| 编号 | 运镜类型 | 英文术语 | 效果 | 适用场景 |
|------|---------|---------|------|---------|
| 1 | 推镜 | Dolly In / Push In | 聚焦主体，增强沉浸感 | 产品特写，情绪爆发 |
| 2 | 拉镜 | Dolly Out / Pull Back | 揭示全貌，放大格局 | 开场建立环境，结尾收束 |
| 3 | 摇镜 | Pan Left/Right | 横向扫视，介绍环境 | 展示场景全貌，跟踪运动 |
| 4 | 移镜 | Tracking Shot | 平行移动，代入感 | 跟随角色行走，穿梭场景 |
| 5 | 升降 | Boom Up/Down | 高低变化，气势对比 | 升高展现场景规模，下降聚焦 |
| 6 | 跟镜 | Follow Cam | 紧随主角身后 | 第一人称带入，惊悚追逐 |
| 7 | 环绕 | 360 Orbit | 全身展示，立体感 | 产品展示，角色亮相 |
| 8 | 晃镜 | Handheld / Shake | 真实感/紧张感 | 动作场景，战地纪实 |
| 9 | 俯拍 | Top Down | 全局视角，俯瞰 | 桌面操作，地图展示 |
| 10 | 仰拍 | Low Angle | 增强主体威慑力 | 角色登场，氛围压迫 |
| 11 | 鸟瞰 | Bird's Eye View | 上帝视角，格局宏大 | 城市全景，自然风光 |
| 12 | 主观 | POV | 代入感极强 | Vlog，记录日常生活 |
| 13 | 变焦 | Zoom In/Out | 聚焦主体或扭曲空间 | 戏剧性发现，突然惊吓 |
| 14 | 旋镜 | Dutch Angle / Roll | 眩晕感/不安感 | 心理扭曲，梦境幻觉 |
| 15 | 延时 | Time-lapse | 压缩时间 | 日落云海，城市人流 |
| 16 | 慢动作 | Slow Motion | 放大瞬间 | 水花四溅，情感高潮 |

## 四大核心技巧

### 1. 动作拆解为"微动作链"
不要写"女孩做菜"——要写"洗手→拿起菜刀→切西红柿→擦汗→继续切"
每个微动作都是给模型的精确指令。

### 2. @素材语法（图生视频/参考视频）
```
@图片1作为首帧画面，@视频1参考运镜效果，@音频1背景音乐
```
- `@图片1` 固定人脸/形体 → 视频不崩的核心
- `@视频1` 参考镜头语言/动作 → 直接复刻优秀运镜

### 3. 负向提示词（定义"不要做什么"）
```
[主提示词], 避免静态摄像机, 避免模糊运动, 避免过度饱和的颜色
```
加入"避免静态镜头"几乎总能带来巨大改进。

### 4. 每段只做一件事
- 一段画面 = 一个运镜 + 一个动作 + 一种情绪
- 禁止：跳跃、快速转身、复杂舞蹈（必崩）
- 推荐：连续慢动作、单一方向运镜（dolly in/out, pan, track）

## 完整提示词结构模板

```python
prompt = f"""
{style_reference}, {quality}, {subject},
{action_chain},
{camera_movement},
{lighting_atmosphere},
{negative_constraints}
"""
```

## 五维架构法（进阶）

| 层级 | 内容 | 示例 |
|------|------|------|
| 技术基底 | 分辨率、帧率、色彩空间、动态模糊 | 4K HDR 24fps, film grain |
| 镜头语言 | 景别、运镜、视角 | 微距特写, slow push-in, 第一人称 |
| 场景构建 | 环境、道具、氛围 | 古老寺庙庭院, 樱花飘落 |
| 角色行为 | 微动作链、情绪曲线 | 拿起→查看→放下, 微笑→叹气→皱眉 |
| 叙事节奏 | 时间轴、转场 | 0-3秒开场, 4-7秒过渡, 8-10秒高潮 |

## 避雷指南

- ❌ 不要写抽象情绪词（"伤心"）→ 写具体画面（"崩溃大叫、咬牙切齿"）
- ❌ 不要写剧烈动作（"快跑、跳跃"）→ 写慢动作（"缓缓起身、慢慢转身"）
- ❌ 不要一个提示词里写多个场景 → 一段画面只拍一个场景
- ❌ 不要忽略背景 → AI会脑补出不可控的背景
- ❌ 不要叠加太多运镜指令 → 元素冲突导致画面崩坏
- ✅ 时间轴写法最可控：`0-3秒：[画面A] 3-6秒：[画面B] 6-10秒：[画面C]`
- ✅ 每段只设置一种运镜—每种运镜对应一种景别—简单高效

## Seedance 1.5 Pro API配额限制处理

### 已知限制
- **安全体验模式(Safe Experience Mode)**：方舟Seedance 1.5 Pro默认开启，每次调用最多生成2段画面（约10秒）
- 超出返回：`SetLimitExceeded: account X reached inference limit for doubao-seedance-1-5-pro`
- 需要用户去控制台手动关闭：https://console.volcengine.com/ark/region:ark+cn-beijing/activation

### API配置
- 端点：`https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks`
- 鉴权：`Authorization: Bearer arK-key`
- 模型ID：`doubao-seedance-1-5-pro-251215`
- 参数：`content` 数组传参（非`prompt`）

### 批处理策略
1. 先测试1段确认配额可用
2. 确认可用后批量提交（7-14段并行）
3. 轮询状态（每15秒）
4. 下载完成后合成

## 口播类视频模板（适用于跨境电商短视频）

```python
template = {
    "scene1": {
        "prompt": "[主体]: medium close-up of a man talking to camera, "
                  "[动作]: naturally gesturing while speaking, subtle head movement, "
                  "[运镜]: slow dolly in from medium shot to close-up, "
                  "[光影]: dramatic Rembrandt lighting, warm amber tones, "
                  "[画质]: 4k cinematic, film grain, shallow depth of field",
        "duration": 10,
        "negative": "avoid static camera, avoid sudden movements, avoid over-saturated colors"
    }
}
```

## 数据可视化模板

```
[场景]: glowing digital data matrix, holographic charts floating in dark space
[动作]: data numbers pulsing and transforming, charts rotating slowly
[运镜]: smooth orbit camera around the data display
[光影]: deep blue and cyan neon lighting, golden highlights on key numbers
[画质]: 4k cinematic, futuristic tech atmosphere
```

## 参考资料

- Atlas Cloud: 15个Seedance 2.0最佳提示词
- 知乎: Seedance 2.0 提示词攻略（万能公式）
- 站酷: Seedance 2.0 15套专属提示词
- 极客公园: Seedance 2.0 完全创作攻略
- Seedance 2.0 运镜分镜完全指南（16种影视级运镜、7景别分配、3级进阶体系）
