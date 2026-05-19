# Hermes Vision 看图问题排查

## 问题现象
- 调用 `vision_analyze` 时报错：`unknown variant 'image_url', expected 'text'`
- 不管是 DeepSeek Chat 还是 KIMI，核心模型都不支持 vision_analyze 的 image_url 输入

## 根因
Hermes 的 `vision_analyze` 工具依赖 `auxiliary.vision` 配置的后端来解析图片。
`auxiliary.vision.provider` 设为 `auto` 时，Hermes 自动选后端，但可能选到了不支持 Vision 的 provider。

## 排查步骤
```bash
# 查看当前 vision 配置
hermes config show | grep -A5 "auxiliary.vision"
```

## 已知解法
1. 设置 `GOOGLE_API_KEY` 环境变量（Google Gemini 原生支持 Vision）
2. 或显式指定 vision provider：
```bash
hermes config set auxiliary.vision.provider openrouter
hermes config set auxiliary.vision.model google/gemini-3.1-flash-lite-preview
```
3. 或使用其他支持 Vision 的 provider

## 已知不支持
- ❌ DeepSeek Chat（核心模型不支持 image_url）
- ❌ KIMI K2.6（同样不支持 image_url）
