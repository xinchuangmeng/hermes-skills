---
name: agent-auto-llm-code-review-evaluation
title: "LLM代码审查评测框架——离线测试你的AI审查员准不准"
description: "基于Dev.to文章'Evaluating LLM code reviewers: an offline harness for precision, recall, and routing'。核心框架：用离线测试集评估LLM代码审查工具的准确率（Precision）和召回率（Recall），以及路由决策（哪些问题给AI查，哪些给人查）。适用于搭建或评估AI代码审查系统的团队。"
tags: [agent-auto, code-review, llm-evaluation, precision-recall, testing]
trigger: |
  当搭建AI代码审查系统、需要评估LLM代码审查质量、或决定哪些审查任务可以交给AI时
---
# LLM代码审查评测框架

## 🎯 核心洞察

### 来源
> "Evaluating LLM code reviewers: an offline harness for precision, recall, and routing"
> — Dev.to @prakharsingh_17

大多数团队直接扔一个prompt就让AI审查代码，从未系统评估过AI审查的准确率。

### 为什么需要评测框架
- **Precision（精确率）**：AI说"这里有bug"——但真的每回都说对了吗？没有，AI经常误报
- **Recall（召回率）**：代码里的bugAI发现了多少？通常漏掉很多
- **Routing（路由）**：哪些审查给AI，哪些给人？取长补短才是最优

## 📊 评测框架设计

### 第1步：构建测试集
```yaml
# test-cases/review-test-set.yaml
test_cases:
  - name: "SQL注入漏洞"
    code_diff: |
      -    user = User.find_by(username: params[:username])
      +    query = "SELECT * FROM users WHERE username = '#{params[:username]}'"
      +    result = ActiveRecord::Base.connection.execute(query)
    severity: "critical"
    expected_findings:
      - type: "security"
        description: "SQL injection via string interpolation"
        line: 2
    
  - name: "空指针未检查"
    code_diff: |
      +    def process(data)
      +      result = data[:user][:name].upcase
      +      return result
      +    end
    severity: "high"
    expected_findings:
      - type: "null-safety"
        description: "data[:user]可能为nil"
        line: 2
```

### 第2步：运行评测
```python
# evaluation_harness.py
class LLMCodeReviewEvaluator:
    """LLM代码审查质量评测框架"""
    
    def __init__(self, llm_func, test_set):
        """
        llm_func: 调用LLM进行代码审查的函数
        test_set: 批注了预期发现的测试用例列表
        """
        self.llm_func = llm_func
        self.test_set = test_set
    
    def evaluate(self):
        results = {
            "true_positives": 0,   # AI说有问题，确实有问题
            "false_positives": 0,  # AI说有问题，实际没问题（误报）
            "false_negatives": 0,  # AI说没问题，实际有问题（漏报）
            "total_expected": sum(len(tc["expected_findings"]) for tc in self.test_set),
        }
        
        for test_case in self.test_set:
            # 让LLM审查这段diff
            findings = self.llm_func(test_case["code_diff"])
            
            # 匹配AI发现与预期发现
            for expected in test_case["expected_findings"]:
                found = self._match_finding(findings, expected)
                if found:
                    results["true_positives"] += 1
                else:
                    results["false_negatives"] += 1
            
            # 计算AI多报的
            ai_unexpected = self._get_unexpected(findings, test_case["expected_findings"])
            results["false_positives"] += len(ai_unexpected)
        
        # 计算指标
        total_detected = results["true_positives"] + results["false_positives"]
        results["precision"] = results["true_positives"] / total_detected if total_detected > 0 else 0
        results["recall"] = results["true_positives"] / results["total_expected"] if results["total_expected"] > 0 else 0
        results["f1_score"] = 2 * results["precision"] * results["recall"] / (results["precision"] + results["recall"]) if (results["precision"] + results["recall"]) > 0 else 0
        
        return results
```

### 第3步：结果解读
```yaml
# 评测结果示例
evaluation_result:
  precision: 0.78  # AI说有问题时，78%是正确的
  recall: 0.45     # AI只发现了45%的bug
  
  # 分析
  strengths:
    - "格式问题、命名规范 → 高精度(>90%)"
    - "明显的语法错误 → 高召回(>80%)"
    
  weaknesses:
    - "逻辑bug、并发问题 → 低召回(<30%)"
    - "安全漏洞 → 中召回(40-60%)"
    - "性能问题 → 低精度(<50%，大量误报)"
```

### 第4步：路由决策
```yaml
# 根据评测结果制定路由规则
routing_rules:
  # 交给AI审查
  ai_review:
    - type: "code-style"
      threshold: 0.9  # AI准确率>90%
    - type: "syntax-errors"
      threshold: 0.8
    - type: "naming-convention"
      threshold: 0.85
  
  # 必须人工审查
  human_review:
    - type: "security-critical"
      reason: "误报代价太大"
    - type: "architecture-decision"
      reason: "需要业务理解"
    - type: "logic-bugs"
      reason: "AI召回率低"
  
  # AI初筛+人确认
  hybrid:
    - type: "performance"
      process: "AI标记可疑代码 → 人确认后决定"
    - type: "documentation"
      process: "AI检查文档完整性 → 人审查内容质量"
```

## 🔧 实操建议

### 评测数据集的构建方法
```yaml
# 从哪里获取测试用例
sources:
  1: "从历史PR中提取（已知有bug的提交）"
     # 找到以前出过bug的commit，把修复前的版本作为测试用例
  2: "人工构造（常见bug模式）"  
     # SQL注入、XSS、空指针、内存泄漏等经典问题
  3: "开源项目的bug修复PR"
     # 从GitHub上找已知问题的修复PR
  
  size: "50-100个测试用例足够评估"
  diversity: "覆盖不同编程语言和bug类型"
```

### 持续迭代
```yaml
# 定期重新评估
review_cycle:
  frequency: "每月一次"
  triggers:
    - "LLM模型更新"
    - "提示词修改"
    - "新增编程语言"
    - "发现新的bug模式"
  
  actions:
    - "重新运行评测"
    - "对比历史指标（有进步吗？）"
    - "更新路由规则"
```

## ⚠️ 注意事项

1. **不准≠没用** — 即使AI审查只有60%的准确率，也能帮人类节省大量时间
2. **精度和召回要平衡** — 误报太多人就不看了（精度问题），漏报太多等于没用（召回问题）
3. **不同类型bug差异巨大** — 别指望一个prompt能搞定所有类型的代码审查
4. **测试集会过时** — 新编程范式、新框架需要新的测试用例
5. **不要用测试集的代码改prompt** — 会过拟合，让AI只擅长找到你特意放进去的bug
6. **人机协作 > 纯AI > 纯人** — AI做粗筛，人做精查，效率最高
