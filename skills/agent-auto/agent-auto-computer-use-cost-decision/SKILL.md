---
name: Agent任务成本决策 — API比Computer Use便宜45倍
description: 基于Reflex博客的实际测试数据：Computer Use（浏览器操作）比结构化API调用贵45倍。提供Agent开发时的成本决策框架——什么时候用API、什么时候用浏览器、什么时候用终端。
tags: [agent, cost-optimization, computer-use, API, decision-framework]
trigger: 当设计Agent工作流、选择Agent执行方式时，需要评估使用浏览器/API/终端的成本效益
---

# Agent任务成本决策框架 — API > 终端 > 浏览器

## 核心数据
Reflex团队的实际测试发现：
- **Computer Use（浏览器操作）**：最昂贵，45x于结构化API
- **结构化API调用**：最便宜，确定性强
- **终端/命令行操作**：介于两者之间

## 成本决策矩阵

| 执行方式 | 相对成本 | 适用场景 | 不适用场景 |
|---------|---------|---------|-----------|
| 结构化API | 1x（基准） | 确定性任务、CRUD、数据查询 | 需要视觉验证、复杂UI交互 |
| 终端命令 | 2-5x | 文件操作、git、构建、脚本执行 | 需要GUI交互 |
| Computer Use/浏览器 | 45x | 视觉验证、无API的场景、复杂Web操作 | 任何有API替代方案的场景 |

## 操作步骤

### 1. 任务分析
分析当前任务，确定最适合的执行方式：

```python
def analyze_task(task_description):
    """判断最佳执行方式"""
    has_api = "是否有可调用的API/CLI工具？"
    needs_vision = "是否需要看屏幕/图像验证？"
    is_deterministic = "操作步骤是否固定？"
    batch_size = "批量处理数量："
    
    if has_api and is_deterministic:
        return "API调用"  # 成本最低
    elif not needs_vision:
        return "终端命令"  # 中等成本
    else:
        return "浏览器/Computer Use"  # 仅在必要时使用
```

### 2. 批量操作优化
如果必须用浏览器（如无API的Web系统）：
- 合并操作：一次浏览器会话做多个操作
- 减少截图：尽量用DOM解析代替截图分析
- 缓存结果：浏览器获取的数据本地缓存
- 重试策略：失败时退避到结构化方法

### 3. 混合策略示例
```
任务：监控3个Web服务状态并报告
策略：
1. 终端 curl 检查 HTTP 状态码（低成本）
2. 如果状态异常，浏览器截图验证（仅在异常时花高成本）
3. API 拉取日志（低成本）自动分析
```

## 注意事项
- ⚠️ 45x是基准倍数，实际可能更高（取决于网络延迟和截图次数）
- ⚠️ 不要一刀切不用浏览器——需要视觉验证的场景仍必要
- ⚠️ 优先寻找API/CLI替代方案（很多Web服务有REST API）
- ⚠️ Computer Use适合探索性/一次性任务，不适合高频重复任务

## 参考
- https://reflex.dev/blog/computer-use-is-45x-more-expensive-than-structured-apis/
