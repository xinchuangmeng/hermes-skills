---
name: agent-auto-sentinel-browser-automation
title: "Sentinel——更高效的LLM浏览器自动化（节省10倍Token）"
description: "基于HN文章'Show HN: Sentinel – LLM browser automation using 10x fewer tokens'——传统LLM浏览器自动化把整个DOM/Screenshot发给LLM，Token消耗巨大。Sentinel用更高效的压缩策略，节省约10倍Token的同时保持任务完成率。核心方法：智能提取关键DOM元素+增量更新+结构化指令。适用于需要减少LLM浏览器自动化成本的场景。"
tags: [agent-auto, browser-automation, cost-optimization, token-efficiency, sentinel]
trigger: |
  当需要做LLM驱动的浏览器自动化、想降低自动化成本、或评估浏览器自动化方案时
---

# Sentinel——更高效的LLM浏览器自动化

## 🎯 核心洞察

### 传统浏览器自动化的Token浪费

```yaml
传统方式（高成本）:
  每次操作:
    1. 截图整个页面 → 发给视觉模型 → 大量token
    2. 获取完整DOM树 → 发送全部HTML → 大量token
    3. 页面变化 → 重新发送全部内容 → 重复浪费

# 问题：页面上90%的内容对当前任务无关
# 但传统方法必须全部发送给LLM
```

### Sentinel的优化方法

```yaml
Sentinel方法（节省10倍Token）:
  核心优化点:
    1. 只提取当前任务相关的DOM元素
    2. 缓存页面结构，只发送变化的部分
    3. 结构化指令而非自然语言描述
    4. 增量更新而非全量刷新
  
  效果:
    - Token消耗降至传统方案的1/10
    - 任务完成率保持相同水平
    - 响应时间显著降低
    - 成本降低10倍
```

## 📋 核心优化策略

### 策略1：智能DOM提取

```python
# 不是发送完整DOM，而是提取关键元素
def extract_relevant_dom(html, task):
    """
    根据任务提取相关DOM元素
    """
    # 1. 解析DOM树
    soup = BeautifulSoup(html, 'html.parser')
    
    # 2. 根据任务关键词过滤
    if task == "填表单":
        return soup.find_all(['input', 'select', 'textarea', 'button'])
    elif task == "读取数据":
        return soup.find_all(['table', 'div.content', 'span.data'])
    elif task == "导航":
        return soup.find_all(['a', 'nav', 'button'])
    
    # 3. 返回结构化摘要（含元素标识、类型、文本、坐标）
    return structured_elements
```

### 策略2：增量更新

```yaml
# 不是每次操作后都重新获取全部
# 而是只记录变化的部分

session_state:
  initial_snapshot: "页面的初始DOM结构（已缓存）"
  deltas: 
    - action: "click_button_#submit"
      result: "出现新弹窗"
      changed_elements: [".modal", "#loading"]
    - action: "fill_input_#name"
      result: "输入框内容变化"
      changed_elements: ["#name"]

# LLM每次只需要看变化部分
# + 少量上下文来理解当前页面状态
```

### 策略3：结构化指令

```yaml
# 不用自然语言描述页面状态
# 用结构化数据

# 传统方式（Token密集型）
"页面上有一个蓝色的登录按钮在右上角，旁边还有注册按钮..."

# Sentinel方式（Token高效）
page_state:
  elements:
    - id: "login-btn"
      type: "button"
      text: "登录"
      location: {x: 920, y: 20}
      state: "visible"
    - id: "register-btn"
      type: "button"
      text: "注册"
      location: {x: 1000, y: 20}
      state: "visible"
```

## 🔧 实操模板

### 在Hermes中应用Sentinel思路

```yaml
# Hermes浏览器自动化优化
hermes_browser_optimization:
  1. 任务描述:
     "登录淘宝 → 搜索'蓝牙耳机' → 获取前5个结果"
  
  2. DOM提取（只取相关）:
     - 登录按钮/输入框
     - 搜索框
     - 搜索结果列表
  
  3. 增量更新:
     - 登录后：只发送"已登录，页面导航栏变化"的变更
     - 搜索后：只发送"搜索结果列表"相关的DOM
  
  4. 结构化输出:
     results:
       - name: "XX蓝牙耳机"
         price: "¥199"
         sales: "10万+"
         link: "..."
```

### 成本对比计算

```bash
# 传统方式（10次操作）
传统成本:
  每次操作: ~5000 tokens（完整页面描述）
  10次操作: 50000 tokens
  LLM成本: 50000 × $0.002/1K = $0.10

# Sentinel方式（10次操作）
优化成本:
  初始加载: 5000 tokens
  增量更新: 平均每次 500 tokens
  10次操作: 5000 + 9×500 = 9500 tokens
  LLM成本: 9500 × $0.002/1K = $0.019

# 节省: 约5倍（$0.10 → $0.019）
# 实际场景可能节省更多（页面越大，节省比例越高）
```

## ⚠️ 注意事项

1. **提取策略依赖任务准确性** — 如果任务描述不准确，提取的相关DOM可能不完整
2. **增量更新对动态页面不友好** — JavaScript频繁更新DOM的页面，增量优势减弱
3. **结构化指令需要提前设计** — 需要预定义元素类型和状态表示格式
4. **SSR页面效果最好** — 服务端渲染的页面DOM结构稳定，增量更新效果最佳
5. **SPA页面需要额外处理** — 单页应用的DOM变化频繁，增量策略需要更精细
6. **Sentinel是2026年5月的新项目** — 方法和工具有待生产环境验证
