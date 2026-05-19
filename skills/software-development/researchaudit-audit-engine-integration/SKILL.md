---
name: ResearchAudit 检测引擎与控制台集成
description: 将ResearchAudit的5个检测器（逻辑/数据/方法/论文文本/表格验证）集成到纯Python HTTP Web控制台，检测入口在页面最显眼位置
tags: [researchaudit, web-console, audit, detectors, http-server]
trigger: |
  当需要将ResearchAudit的检测引擎集成到Web控制台时使用，特别是：
  - 用户要求检测功能作为核心入口
  - 需要在Web界面上传文件并运行检测
  - 需要显示检测历史记录
  - 使用纯Python HTTP Server（非Flask/Gradio）
---

# ResearchAudit 检测引擎与控制台集成指南

## 🎯 核心原则

1. **检测入口必须居中显眼** — 用户登录第一眼就看到检测功能
2. **操作简洁** — 上传文件 → 选择模式 → 运行检测 → 看结果
3. **所有检测器可用** — 5个检测器（LogicConsistencyDetector, DataIntegrityDetector, MethodCheckDetector, PaperTextAnalyzer, TableCheckDetector）
4. **纯Python** — 使用内置 http.server 模块，无需外部依赖

## 🏗️ 集成架构

```
Web控制台 (ceo_web_fixed_simple.py)
│
├── / → 主页（导航：审计、仪表板、文件状态）
│   └── 核心区域: 检测入口卡片（上传+运行）
│
├── /audit → 检测页面
│   ├── 上传文件
│   ├── 选择模式（code / paper）
│   └── 显示检测结果（评分、问题列表、建议）
│
├── /audit/history → 检测历史记录
├── /audit/view → 查看单次检测详情
├── /audit/search → 搜索历史记录
└── /audit/submit (POST) → 提交检测任务
```

## 🔌 关键代码模式

### 1. 导入检测器

```python
from researchaudit.detectors.logic_check import LogicConsistencyDetector
from researchaudit.detectors.data_check import DataIntegrityDetector
from researchaudit.detectors.method_check import MethodCheckDetector
from researchaudit.detectors.paper_analysis import PaperTextAnalyzer
from researchaudit.detectors.table_check import TableCheckDetector
```

### 2. 检测执行函数

```python
def run_audit(file_content, filename, mode="code"):
    """运行审计检测"""
    if mode == "code":
        # 代码审计模式
        from researchaudit.cli import analyze_file
        # 写入临时文件
        tmp_path = f"/tmp/audit_{int(time.time())}_{filename}"
        with open(tmp_path, 'w', encoding='utf-8') as f:
            f.write(file_content)
        result = analyze_file(tmp_path)
        os.remove(tmp_path)
    else:
        # 论文审计模式
        from researchaudit.detectors.paper_analysis import PaperTextAnalyzer
        from researchaudit.detectors.table_check import TableCheckDetector
        from researchaudit.detectors.data_check import DataIntegrityDetector
        from researchaudit.detectors.method_check import MethodCheckDetector
        
        text = file_content
        detectors = {
            "text": PaperTextAnalyzer.analyze(text),
            "table": TableCheckDetector.analyze(text),
            "data": DataIntegrityDetector.analyze_text(text),
            "method": MethodCheckDetector.analyze_text(text),
        }
        # ... 合并结果
    return result
```

### 3. HTTP路由注册

```python
def do_GET(self):
    parsed = urlparse.urlparse(self.path)
    path = parsed.path
    
    if path == '/':
        self._serve_homepage()      # 主页 - 检测入口居中
    elif path == '/audit':
        self._serve_audit_page()    # 检测页
    elif path == '/audit/history':
        self._serve_audit_history() # 历史记录
    # ... 其他路由

def do_POST(self):
    parsed = urlparse.urlparse(self.path)
    if path == '/audit/submit':
        self._handle_audit_submit(post_data)  # 处理检测提交
```

### 4. 主页检测入口HTML（居中显眼）

```html
<!-- 检测入口 - 页面正中间 -->
<div class="hero-section">
    <h1>🔬 ResearchAudit AI 研究审计</h1>
    <p class="subtitle">上传研究代码或论文，智能检测潜在问题</p>
    <form action="/audit" method="get" class="quick-audit-form">
        <div class="mode-selector">
            <label class="mode-btn active">
                <input type="radio" name="mode" value="code" checked>
                📝 代码审计
            </label>
            <label class="mode-btn">
                <input type="radio" name="mode" value="paper">
                📄 论文审计
            </label>
        </div>
        <button type="submit" class="big-action-btn">🚀 开始检测</button>
    </form>
</div>
```

### 5. 检测结果展示

```python
def _generate_audit_result_html(self, result):
    score = result.get("score", 0)
    score_color = "#27ae60" if score >= 0.8 else "#f39c12" if score >= 0.6 else "#e74c3c"
    
    html = f'''
    <div class="result-header">
        <div class="score-circle" style="border-color: {score_color}">
            <span class="score-value">{score:.0%}</span>
            <span class="score-label">可信度</span>
        </div>
    </div>
    '''
    
    # 检测器详情
    for name, label in [("logic","逻辑"), ("data","数据"), ("method","方法")]:
        dr = result.get("detector_results", {}).get(name, {})
        if dr:
            html += f'''
            <div class="detector-card">
                <div class="detector-header">{label}</div>
                <div class="detector-score">{dr.get("score", 0):.1%}</div>
            </div>
            '''
    
    # 问题列表
    issues = result.get("issues", [])
    if issues:
        html += '<div class="issues-section"><h3>⚠️ 发现的问题</h3><ul>'
        for issue in issues:
            html += f'<li>{issue}</li>'
        html += '</ul></div>'
    
    return html
```

### 6. 检测历史存储

```python
def save_audit_history(self, result, filename, mode):
    """保存检测结果到历史记录"""
    history_file = self.data_dir / "audit_reports" / f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    history_file.parent.mkdir(exist_ok=True)
    
    record = {
        "id": f"audit_{int(time.time())}",
        "filename": filename,
        "mode": mode,
        "timestamp": datetime.now().isoformat(),
        "score": result["score"],
        "issues_count": len(result["issues"]),
        "result": result,
    }
    
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
```

## ⚡ 快速修改模板

在现有控制台（`ceo_web_fixed_simple.py`）中集成检测入口：

1. **修改主页** `_generate_homepage()` — 把检测入口放到第一个卡片位置
2. **添加检测页面** `_serve_audit_page()` — 上传+运行+结果显示
3. **添加历史记录** `_serve_audit_history()` — 显示历史检测记录
4. **添加POST处理** `_handle_audit_submit()` — 接收文件并运行检测

## 🎨 样式要点

- 检测入口卡片：大标题、大按钮、居中对齐
- 评分圆形显示（绿色≥80%、橙色60-80%、红色<60%）
- 问题列表用图标区分严重级别
- 检测模式切换（代码/论文）用标签按钮

## ⚠️ 常见陷阱

1. **文件编码** — 论文PDF需要pdfminer.six支持，否则用纯文本模式
2. **临时文件** — 检测结果存储在 `audit_reports/` 目录，确保该目录可写
3. **大文件处理** — 超过10MB的文件需要分块读取或限制
4. **POST数据解析** — `self.rfile.read()` 后需要 json.loads 解析
5. **中文路径** — 确保所有路径操作使用 `str()` 而非 bytes
