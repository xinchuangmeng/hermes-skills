---
name: agent-auto-vision-vs-api-cost
description: >
  Vision Agent（浏览器截图+点击模式）vs API Agent（结构化HTTP端点）的成本/性能对比——
  基于Reflex.dev的真实基准测试：Vision Agent成本是API Agent的45倍（551K vs 12K token/次）。
  帮助你在设计Agent架构时决策用视觉方案还是API方案，以及何时混用。
tags:
  - cost-optimization
  - vision-agent
  - api-agent
  - browser-use
  - agent-architecture
  - cost-benchmark
trigger:
  - "vision agent 成本"
  - "computer use vs structured api"
  - "browser-use 太费钱"
  - "agent 用视觉还是 API"
  - "web自动化方案选型"
  - "Agent 架构成本优化"
  - "45x cost difference"
  - "screenshot vs API agent"
---

# Vision Agent vs API Agent 成本对比指南（45x差距）

## 核心发现

> "一个必须通过看才能行动的Agent，永远要为'看'付费——模型再好也改变不了这个事实。"

Reflex.dev团队做了真实基准测试，同一个管理后台任务，用两种方式：
- **Vision Agent（视觉方案）**：Claude Sonnet通过截图+点击操作UI（browser-use 0.12）
- **API Agent（接口方案）**：Claude Sonnet直接调用自动生成的HTTP端点

**任务**：找客户→查订单→审核评论→标记发货

## 关键数据对比

| 指标 | Vision Agent | API Agent | 差距 |
|------|-------------|-----------|------|
| 步骤数 | 53±13 | 8±0 | 6.6x |
| 耗时 | ~17分钟 | ~20秒 | 51x |
| 输入token | 551K±179K | 12.2K±27 | **45x** |
| 输出token | 38K±11K | 0.9K±41 | 41x |
| 成本 | ~$1.5-3/次 | ~$0.03-0.08/次 | **45x+** |
| 方差 | 高（407K-751K tokens） | 零（±27 tokens） | - |

## 关键发现

### 1. Vision Agent没导览就失败
- 同样6句话的提示词，Vision Agent只找到了**1/4**的待审评论
- **从来不翻页**——下面的评论看不到
- "Agent在推理渲染好的页面，没有任何信号告诉它页面没显示全"

### 2. 需要14步的手工导览
- 为了让对比公平，研究者写了**14步UI导览**（左侧栏、标签页、表单字段）
- 有了导览才能完成任务，但花了14分钟+500K tokens
- "每一步都是工程投入，没有计入token成本但反映真实开销"

### 3. API Agent零方差
- 每次运行都是**8个工具调用**，一模一样
- token差异仅±27（来自随机数种子）
- "Agent调用同样的处理函数、同样的顺序，因为结构化响应没有理由偏离"

### 4. Haiku做不了Vision路径
- 在browser-use 0.12的结构化输出模式下失败
- 但走API路径：**8秒以内**，不到10K tokens——最便宜的方案

## 适用场景判断

### ✅ 用 Vision Agent（视觉方案）
- **第三方应用**（你不控制的SaaS、旧系统、不可修改的工具）
- 没有API可用的遗留系统
- 需要兼容多种版本UI的场景

### ✅ 用 API Agent（接口方案）
- **自己开发的内部工具**（尤其是API生成成本趋近于零时）
- 有OpenAPI/GraphQL文档的系统
- 对成本敏感的运维场景

### 💡 混合策略
- 核心流程用API Agent（稳定+便宜）
- 意外/异常处理用Vision Agent兜底
- 使用自动API生成工具（如Reflex 0.9的auto-generated endpoints）

## 直接可用的命令/配置

### 1. Reflex自动生成API端点
```bash
# Reflex 0.9+ 会自动从UI组件生成HTTP端点
pip install reflex==0.9.*
reflex init
# 终端会显示自动生成的事件处理API
```

### 2. 测试自己的Agent成本
```bash
# 克隆基准测试仓库
git clone https://github.com/reflex-dev/agent-benchmark
cd agent-benchmark

# Vision Agent测试
python run_vision_agent.py

# API Agent测试
python run_api_agent.py

# 成本对比
python compare_costs.py
```

### 3. Hermes中配置API Agent模式
```yaml
# config.yaml 中设置
agent:
  mode: api  # 或 'vision'
  api_endpoint: http://localhost:8000/api
  tool_surface: auto-generated  # 自动发现API
```

## ⚠️ 注意事项

1. **不要轻信单次Vision Agent测试**——视觉方案方差极大，需要多次测试求均值
2. **Vision Agent的可见成本只是冰山一角**——导览编写、调试、容错的人工成本更高
3. **API Agent并非永远可行**——获取第三方API可能需要商务对接、权限申请
4. **模型升级不会缩小差距**——更好的模型降低的是单步成本，不是步数
5. **browser-use 0.12+版本的结构化输出模式**可能导致廉价模型完全不可用

## 参考来源

- https://reflex.dev/blog/computer-use-is-45x-more-expensive-than-structured-apis/
- https://github.com/reflex-dev/agent-benchmark
