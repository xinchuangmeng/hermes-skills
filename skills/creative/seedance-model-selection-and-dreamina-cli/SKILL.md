---
name: seedance-model-selection-and-dreamina-cli
description: Seedance各模型选型实战指南（1.0 pro-fast/1.5 pro/2.0的可用性、额度、价格对比）+ 即梦CLI(dreamina)的常用命令。适用于AI短视频制作时的模型选型和CLI操作。
version: 1.0.0
author: Hermes小书童
tags: [seedance, 模型选型, dreamina, 即梦CLI, 短视频]
---

# Seedance模型选型 + 即梦CLI指南

## Seedance模型选型实战（2026年5月）

| 模型 | 模型名 | 价格 | 出片质量 | 状态 |
|------|--------|------|---------|------|
| **1.0 pro-fast** | `doubao-seedance-1-0-pro-fast-251015` | 0.12元/秒 | 可接受 | ✅ 直接可用 |
| **1.5 pro** | `doubao-seedance-1-5-pro-251215` | 0.4元/秒 | 好 | ⚠️ 2M免费额度已耗尽 |
| **2.0** | `doubao-seedance-2-0-260128` | 1元/秒（API） | 最好 | ⚠️ 方舟需手动开通 |

### 踩坑记录
1. **1.5 pro** 有200万免费tokens，用完后报 `SetLimitExceeded`
2. **2.0** 在方舟上默认不开通，需要先去控制台开通模型服务，否则报 `ModelNotOpen`
3. **1.0 pro-fast** 是最稳妥的备选，不用开通直接API调用，0.12元/秒

## 即梦CLI（dreamina）常用命令

安装后在 `~/.local/bin/dreamina`，使用OAuth Device Flow登录（需手机即梦App扫码验证）：

```bash
dreamina login --headless       # 获取扫码链接
dreamina user_credit            # 查看积分余额
dreamina text2video             # 文字生成视频
dreamina multimodal2video       # Seedance 2.0 全能参考模式
dreamina query_result --submit_id=xxx  # 查询结果
dreamina list_task              # 查看任务列表
```

### 收费模式对比
- **即梦网页版**：会员制 69元/月（基础）→ 199元/月（标准）→ 499元/月（高级）
- **火山方舟API**：按量付费，1元/秒（2.0），0.12元/秒（1.0 pro-fast），无需排队
