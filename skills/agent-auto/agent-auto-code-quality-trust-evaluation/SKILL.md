---
name: agent-auto-code-quality-trust-evaluation
title: "Agent生成代码的质量评估与信任建立框架"
description: "基于Simon Willison的Vibe Coding反思和AI vs Non-AI实验的SonarQube数据——AI生成代码的隐藏成本。核心框架: 认知复杂度检查 + 技术债度量 + 实际使用验证。不再相信传统信号（commit数/README/测试覆盖率），建立新的信任评估标准。"
tags: [agent-auto, code-quality, trust, code-review, vibe-coding, code-gen]
trigger: |
  评估Agent生成的代码质量时
  需要决定是否信任Agent写的代码时
  构建Agent代码生成流水线的质量门禁时
  对比AI代码和手写代码的质量差异时
---

# Agent生成代码的质量评估与信任建立框架

## 问题: 传统质量信号已失效

Simon Willison指出: 以前看到一个GitHub仓库有100次commit + 漂亮的README + 自动化测试 -> 可以信任
现在Agent半小时就能生成这些 -> 传统信号全部失效

```
传统信任信号   ->  Agent半小时伪造
100次commit   ->  git commit -m "update" x 100
漂亮README    ->  Claude Code生成
全面测试覆盖   ->  AI生成测试用例
```

## 真实实验数据 (SonarQube)

来自"AI vs Non-AI: Building the Same Project Twice"实验:

### Sensor Reader项目

| 指标 | 手写代码 | AI代码 | 差距 |
|------|---------|--------|------|
| 圈复杂度 | 72 | 87 | AI更复杂 |
| 认知复杂度 | **19** | **87** | AI高4.5倍! |
| 技术债 | 50min | 7min | AI技术债少(凑巧) |

### Webapp项目

| 指标 | 手写代码 | AI代码 | 差距 |
|------|---------|--------|------|
| 圈复杂度 | 70 | 72 | 接近 |
| 认知复杂度 | **10** | **16** | AI高60% |
| 技术债 | 30min | **1h43min** | AI高3.4倍 |
| 代码重复率 | 0% | **3.6%** | AI有重复 |

**关键发现**: AI代码的认知复杂度普遍比手写高60%-4.5倍，意味着更难维护和理解

## 评估框架

### 维度1: 认知复杂度检查 (必做)

```bash
# 用SonarQube或类似工具检查
pip install radon  # Python代码复杂度检查

# 检查认知复杂度
radon cc my_agent_generated_code/ -s

# 输出示例
# file.py -- A 15 (非常低)
# file.py -- B 25 (低)
# file.py -- C 50 (中等)  
# file.py -- D 87 (高! AI代码典型值)
# file.py -- E 150 (非常高，需要重构)
```

**阈值建议**:
- 单函数认知复杂度 > 30 -> 需要人工review
- 单函数认知复杂度 > 50 -> 必须重构

### 维度2: 技术债度量

```bash
# 使用SonarQube (Docker)
docker run -d --name sonarqube -p 9000:9000 sonarqube

# 或用轻量方案: pylint + 自定义规则
pip install pylint
pylint agent_code/ --exit-zero | grep "code complexity\|too-many"
```

### 维度3: 实际使用验证 (Simon Willison的终极建议)

**新信任信号**: 有人实际用过了吗?

```yaml
trust_levels:
  level_0: "AI生成后无人review" -> 只用于个人/实验项目
  level_1: "AI生成 + 人工review" -> 可用于内部工具
  level_2: "AI生成 + review + 实际使用2周" -> 可用于非关键生产
  level_3: "AI生成 + review + 使用2周 + 测试覆盖" -> 可用于生产
  level_4: "AI生成 + review + 生产运行1个月无事故" -> 完全可信
```

### 维度4: 特定领域的回归测试

```python
# AI代码最容易引入的隐蔽Bug: 数据顺序依赖
# 在测试中明确验证

def test_ai_code_robustness():
    # 测试1: 输入顺序无关性
    result1 = process_data(["A", "B", "C"])
    result2 = process_data(["C", "B", "A"])
    assert result1 == result2, "AI代码可能依赖输入顺序!"
    
    # 测试2: 边界值
    result_empty = process_data([])
    assert result_empty is not None
    
    # 测试3: 错误处理
    with pytest.raises(ValueError):
        process_data(None)
```

## 操作的检查清单

在信任Agent写的代码前，逐项检查:

```
[ ] 1. 认知复杂度检查: 每个函数 < 30
[ ] 2. 圈复杂度检查: 每个函数 < 15
[ ] 3. 重复代码检查: 重复率 < 3%
[ ] 4. 边角测试: 空输入/NULL/异常输入
[ ] 5. 安全性: 没有硬编码密钥/SQL注入风险
[ ] 6. 实际使用: 至少在测试环境运行了1周
[ ] 7. 人工review: 至少让一个人review了关键逻辑
```

## 注意事项

- 认知复杂度高不一定是AI的问题 - 复杂业务逻辑本身就会导致高复杂度
- 技术债低不一定是好事 - AI可能只是没写错误处理/日志/文档
- AI代码的质量一致性更好 - 但上限不如有经验的开发者
- 最危险的不是AI写错代码 - 而是AI写出看起来正确但实际错误的代码
- Simon Willison的建议: 不要把Agent生成的代码用在服务他人的生产系统中，除非你亲自review并理解了每一行
