---
name: troubleshoot-agent-edge-case-contamination
description: Agent的输出被下游脚本/系统当作确定性行为依赖，导致修改输出边界引发连锁故障。核心原则：Agent不能假设"只输出必要信息"，下游一定会依赖任何可观察的行为。适用于Agent输出变更导致系统故障的排查和预防。
tags:
  - troubleshooting
  - edge-cases
  - system-integration
  - output-contamination
  - hyrums-law
trigger:
  - 修改了Agent输出格式后下游系统报错
  - Agent增加了日志/warning后脚本报错
  - 下游系统把Agent的调试输出当成了正常输出
  - "agent output breaking downstream"
  - "Hyrum's law agent"
  - "agent edge case"
  - "modifying agent output causes failures"
---

# Agent输出边界污染排查与预防

> **来源:** [All Means Are Fair Except Solving the Problem](https://yosefk.com/blog/all-means-are-fair-except-solving-the-problem.html) — Yossi Kreinin
>
> **核心教训：** Hyrum定律说"你系统的所有可观察行为都会被某些人依赖。" Agent尤其是这样——下游系统会把Agent输出的任何信息都当作API。

## 问题模式

### 经典案例

一个库增加了warning信息（打印在stdout），但下游脚本依赖"yay, done"是最后一行输出。warning偶尔在析构函数阶段打印，出现在"yay, done"之后，导致脚本认为程序失败。

```
正常：初始化 → 执行 → "yay, done" → 退出 ✓
加warning后：初始化 → 执行 → "yay, done" → [析构中]Warning: xxx → 脚本报错 ✗
```

### 对Agent的影响

Agent比传统软件更容易触发出问题：

1. **Agent输出格式不固定** — LLM的输出天然多变，下游解析器却期望固定格式
2. **Agent增加日志/Warning** — 调试时加的print/warning会后门变成"行为"
3. **Agent回复开头尾巴被依赖** — "好了！" "搞定了" "以下是结果" 这些语气词都可能被自动化脚本依赖
4. **Agent输出增加信息** — 以前只输出结果，现在加了解释，下游解析器崩溃

## 排查步骤

### 第1步：确认是边界污染

检查是否是以下模式：
```
Agent输出 → 下游解析器 → 报错
           ↑
        Agent新增了输出内容（warning、额外说明、格式变化）
```

### 第2步：定位依赖点

找到下游系统具体依赖Agent输出的**哪一部分**：
- 输出文本的**最后一行**？
- 特定关键词的位置？
- 输出的**行数**？
- 是否包含某个前缀/后缀？

### 第3步：修复策略（优先级排序）

1. **最佳：让下游系统容错** — 修复解析器不要依赖非合同的输出特性
2. **次优：Agent输出结构化** — 用JSON/XML等格式明确合同边界
3. **临时：恢复旧输出格式** — 去掉新增内容，保持向后兼容
4. **最差：增加更多的"保证"** — 如总是最后追加"yay, done"（治标不治本）

## 预防措施

### 设计时

```yaml
# Agent输出合同（Output Contract）
# 明确声明Agent的输出格式和边界
output_contract:
  format: json
  fields:
    - name: result
      type: string
      description: 主要输出内容
    - name: status
      type: string
      enum: ["success", "error"]
  # ⚠️ 以下内容不保证稳定性
  unstable:
    - logging_output
    - timing_information
    - debug_messages
```

### 开发时

- Agent的**调试输出和正式输出分离**（stdout vs stderr，或独立log文件）
- 输出格式**版本化**，变更时通知下游
- 用结构化输出工具（outlines/guidance）保证格式一致性

### 部署时

- Agent输出变更前**检查所有已知的下游消费者**
- 即使"只是加个warning"也要做回归测试
- 考虑用**输出校验器**拦截不符合格式的输出

## Agent特有场景

| 场景 | 风险等级 | 典型症状 |
|------|---------|---------|
| Agent增加了Markdown格式 | 🔴 高 | 下游解析纯文本出错 |
| Agent多了段分析说明 | 🟡 中 | 下游取了第二段而非第一段 |
| Agent回复开头多了emoji | 🟡 中 | 正则匹配失败 |
| Agent debug mode加了日志 | 🔴 高 | 日志被当作正式输出 |
| Agent换了语气词 | 🟢 低 | 除非下游靠语气词判断成功 |
| Agent输出行数变了 | 🟡 中 | 尾行截取/行数计数失败 |

## 真实案例

### 案例1: Python库的warning
- **问题**：库析构函数打印warning，出现在"done"之后
- **"修复"**：增加另一个destructor在warning后打印"done"
- **真正的问题**：下游脚本写了`if last_line == "done"`——脆弱的合约
- **教训**：找"怎么不让warning影响脚本"而非"怎么解决真正的warning"

### 案例2: AI Agent的生产日志
- **问题**：Agent在生产中增加了一个"正在思考..."日志，下游监控脚本解析输出_发现日志行不是JSON格式_触发了报警
- **修复**：将所有非JSON输出写入stderr，stdout只输出JSON
- **教训**：Agent的工具调用和实际输出要严格分离

## 检查清单

- [ ] 下游解析器是否只依赖合同声明的输出字段？
- [ ] Agent的所有新增输出是否通过了回归测试？
- [ ] 调试日志是否写入了不同于stdout的通道？
- [ ] 输出格式变更是否有版本号？
- [ ] Agent输出是否有Schema验证？
- [ ] 下游系统是否有熔断机制（而非静默崩溃）？

## 注意事项

- ⚠️ 别笑——"在warning后加'搞定'"这种方案真的有人生产用过，而且能用
- ⚠️ 输出合同的变更需要像API版本变更一样正式对待
- ⚠️ Agent输出天然不稳定（LLM的多样性），用结构化输出工具强制格式
- ⚠️ 最惨的情况：上游增加信息是为了帮下游，下游因此挂了
