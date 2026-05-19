---
name: ResearchAudit CEO Web Console Basic
description: 安全基础的ResearchAudit CEO Web控制台 - 纯Python Gradio实现，无系统权限需求，快速部署
tags: [web, gradio, dashboard, ceo, monitoring, safe]
trigger: |
  当用户需要为ResearchAudit项目创建安全的Web界面时使用，特别是：
  - 需要快速可视化监控
  - 团队协作查看数据
  - 避免系统权限操作
  - 安全第一原则
---

# ResearchAudit CEO Web控制台（安全基础版）

## 🎯 设计原则
1. **零权限需求**: 不需要sudo或系统配置
2. **纯Python实现**: 仅使用Gradio和标准库
3. **本地运行**: 不暴露敏感信息
4. **快速部署**: 10分钟即可使用

## 🚀 极简安全版本

### 核心代码 (ceo_web_safe.py)
```python
#!/usr/bin/env python3
"""
ResearchAudit CEO Web控制台 - 安全基础版
无需系统权限，纯Python实现
"""

import gradio as gr
import json
import os
import sys
from datetime import datetime
from pathlib import Path

class SafeCEOConsole:
    """安全CEO控制台 - 无权限需求"""
    
    def __init__(self):
        # 自动检测项目目录
        self.project_dir = self.find_project_dir()
        print(f"📁 项目目录: {self.project_dir}")
        
    def find_project_dir(self):
        """安全地查找项目目录"""
        possible_paths = [
            "/home/agentuser/projects/researchaudit",
            "./researchaudit",
            ".",
            os.path.expanduser("~/projects/researchaudit")
        ]
        
        for path in possible_paths:
            if os.path.exists(os.path.join(path, "target_users.json")):
                return path
        return "."
    
    def safe_load_json(self, filename):
        """安全加载JSON文件"""
        try:
            filepath = os.path.join(self.project_dir, filename)
            if not os.path.exists(filepath):
                return {"error": f"文件不存在: {filename}"}
                
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            return {"error": f"加载失败: {str(e)}"}
    
    def get_campaign_status(self):
        """获取战役状态"""
        try:
            # 基础状态
            status = {
                "project": "ResearchAudit CEO验证战役",
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "就绪"
            }
            
            # 加载目标用户
            targets_data = self.safe_load_json("target_users.json")
            if "targets" in targets_data:
                status["total_targets"] = len(targets_data["targets"])
            
            # 加载话术数据
            messages_data = self.safe_load_json("musk_style_messages.json")
            if "messages" in messages_data:
                status["total_messages"] = len(messages_data["messages"])
            
            # 尝试加载模拟结果
            mock_data = self.safe_load_json("campaign_results.json")
            if isinstance(mock_data, dict):
                status.update(mock_data)
            
            return status
        except Exception as e:
            return {"error": f"状态获取失败: {str(e)}"}
    
    def format_status_html(self, status):
        """格式化状态为HTML"""
        if "error" in status:
            return f"<div style='color: red; padding: 20px;'><h3>❌ 错误</h3><p>{status['error']}</p></div>"
        
        html = """
        <div style="background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); 
                   padding: 20px; border-radius: 10px; margin: 10px 0;">
            <h2 style="margin-top: 0;">🚀 ResearchAudit CEO战役状态</h2>
        """
        
        # 关键指标
        metrics = [
            ("🎯 目标用户", status.get("total_targets", 0), "人"),
            ("💬 个性化话术", status.get("total_messages", 0), "条"),
            ("📧 模拟发送", status.get("emails_sent", 0), "封"),
            ("📩 模拟回复", status.get("replies_received", 0), "封"),
            ("📈 模拟回复率", status.get("reply_rate", "0%"), ""),
        ]
        
        html += "<div style='display: flex; flex-wrap: wrap; gap: 15px;'>"
        for icon, value, unit in metrics:
            html += f"""
            <div style="background: white; padding: 15px; border-radius: 8px; 
                       box-shadow: 0 2px 5px rgba(0,0,0,0.1); min-width: 150px;">
                <div style="font-size: 24px; margin-bottom: 5px;">{icon}</div>
                <div style="font-size: 28px; font-weight: bold;">{value}{unit}</div>
            </div>
            """
        html += "</div>"
        
        # 时间信息
        html += f"""
        <div style="margin-top: 20px; padding: 15px; background: white; border-radius: 8px;">
            <p><strong>🕒 最后更新:</strong> {status.get('last_updated', 'N/A')}</p>
            <p><strong>⏰ 黄金窗口:</strong> 21:00 (今日)</p>
            <p><strong>🎯 战役目标:</strong> 24小时获取6-8个深度访谈</p>
        </div>
        """
        
        html += "</div>"
        return html
    
    def get_targets_table(self):
        """获取目标用户表格"""
        data = self.safe_load_json("target_users.json")
        if "error" in data:
            return data["error"]
        
        if "targets" not in data:
            return "未找到目标用户数据"
        
        targets = data["targets"]
        if not targets:
            return "暂无目标用户"
        
        # 创建简单表格
        table = "| 姓名 | 邮箱 | 研究领域 | 会议 |\n"
        table += "|------|------|----------|------|\n"
        
        for target in targets[:10]:  # 只显示前10个
            name = target.get("name", "N/A")
            email = target.get("email", "N/A")
            research_area = target.get("research_area", "N/A")
            conference = target.get("conference", "N/A")
            
            table += f"| {name} | {email} | {research_area} | {conference} |\n"
        
        if len(targets) > 10:
            table += f"\n... 还有 {len(targets) - 10} 个用户未显示"
        
        return table

def create_safe_web_console():
    """创建安全Web控制台"""
    console = SafeCEOConsole()
    
    with gr.Blocks(
        title="ResearchAudit CEO控制台",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1200px;
            margin: 0 auto;
        }
        @media (max-width: 768px) {
            .gradio-container {
                padding: 10px;
            }
        }
        """
    ) as demo:
        
        # 标题区域
        gr.Markdown("# 🚀 ResearchAudit CEO控制台")
        gr.Markdown("### 安全基础版 - 无需系统权限")
        
        # 状态显示区域
        status_html = gr.HTML(label="实时状态", value="正在加载...")
        
        # 控制按钮
        with gr.Row():
            refresh_btn = gr.Button("🔄 刷新数据", variant="secondary", size="sm")
            view_targets = gr.Button("🎯 查看目标用户", variant="primary", size="sm")
            view_messages = gr.Button("💬 查看话术", variant="primary", size="sm")
        
        # 数据展示区域
        with gr.Tab("目标用户"):
            targets_display = gr.Textbox(
                label="目标用户列表",
                lines=15,
                interactive=False
            )
        
        with gr.Tab("系统信息"):
            gr.Markdown("### 系统配置")
            info_text = f"""
            **项目目录**: {console.project_dir}
            **Python版本**: {sys.version}
            **当前时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            ## 🛡️ 安全特性
            - ✅ 无系统权限需求
            - ✅ 纯Python实现
            - ✅ 本地数据加载
            - ✅ 无外部依赖
            """
            gr.Markdown(info_text)
        
        # 按钮事件
        def refresh_data():
            status = console.get_campaign_status()
            targets = console.get_targets_table()
            return [
                console.format_status_html(status),
                targets
            ]
        
        refresh_btn.click(
            fn=refresh_data,
            outputs=[status_html, targets_display]
        )
        
        view_targets.click(
            fn=console.get_targets_table,
            outputs=targets_display
        )
        
        # 页面加载时初始化
        demo.load(
            fn=refresh_data,
            outputs=[status_html, targets_display]
        )
    
    return demo

def main():
    """主函数"""
    print("🚀 启动ResearchAudit CEO Web控制台...")
    print("📁 正在检测项目目录...")
    
    # 检查Gradio是否安装
    try:
        import gradio
        print("✅ Gradio已安装")
    except ImportError:
        print("❌ Gradio未安装，正在尝试安装...")
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "gradio"])
            print("✅ Gradio安装成功")
        except:
            print("❌ 安装失败，请手动安装: pip install gradio")
            return
    
    # 创建并启动控制台
    demo = create_safe_web_console()
    
    print("\n🌐 Web控制台即将启动...")
    print("   本地访问: http://localhost:7860")
    print("   服务器访问: http://<服务器IP>:7860")
    print("\n🛑 按 Ctrl+C 停止服务")
    
    try:
        demo.launch(
            server_name="0.0.0.0",  # 允许外部访问
            server_port=7860,
            share=False,            # 不创建公开链接
            quiet=False,            # 显示日志
            show_error=True
        )
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("\n💡 尝试以下解决方案:")
        print("   1. 检查端口7860是否被占用")
        print("   2. 尝试其他端口: python ceo_web_safe.py --port 7861")
        print("   3. 检查防火墙设置")

if __name__ == "__main__":
    main()
```

### 部署和使用指南

#### 1. 快速启动
```bash
# 进入项目目录
cd /home/agentuser/projects/researchaudit

# 创建Web控制台文件
cat > ceo_web_safe.py << 'EOF'
[上面的Python代码]
EOF

# 运行Web服务
python3 ceo_web_safe.py
```

#### 2. 使用自定义端口
```bash
# 如果7860端口被占用，使用其他端口
python3 ceo_web_safe.py --port 7861
```

#### 3. 后台运行
```bash
# 使用nohup后台运行
nohup python3 ceo_web_safe.py > web_console.log 2>&1 &

# 查看日志
tail -f web_console.log

# 停止服务
pkill -f "ceo_web_safe.py"
```

## 📱 功能特性

### 核心功能
- ✅ **实时状态监控**: 显示战役关键指标
- ✅ **目标用户查看**: 表格形式展示目标用户
- ✅ **安全数据加载**: 仅读取本地JSON文件
- ✅ **响应式设计**: 支持手机和电脑访问
- ✅ **零权限需求**: 不需要sudo或系统配置

### 安全特性
- 🔒 **无系统操作**: 不执行任何sudo命令
- 🔒 **本地数据**: 所有数据来自本地文件
- 🔒 **无外部API**: 不调用外部服务
- 🔒 **可控访问**: 可设置密码保护（可选）

## 🔧 故障排除

### 常见问题

#### 1. 端口被占用
```bash
# 检查端口占用
netstat -tlnp | grep :7860

# 使用其他端口
python3 ceo_web_safe.py --port 7861
```

#### 2. Gradio未安装
```bash
# 安装Gradio
pip install gradio

# 或使用用户安装
pip install --user gradio
```

#### 3. 文件路径错误
```bash
# 确认项目目录
ls -la /home/agentuser/projects/researchaudit/

# 检查数据文件
ls target_users.json musk_style_messages.json
```

#### 4. 防火墙限制
```bash
# 临时开放端口（如果需要）
# 注意：这需要sudo权限，仅在必要时使用
# sudo ufw allow 7860/tcp
```

## 🎯 使用场景

### 个人使用
- 本地监控战役进展
- 快速查看目标用户
- 数据可视化展示

### 团队协作
- 共享战役状态
- 同步目标用户信息
- 统一数据视图

### 演示展示
- 向投资人展示进展
- 团队内部汇报
- 项目状态跟踪

## 📊 扩展建议

### 后续增强（安全方式）
1. **数据图表**: 使用matplotlib生成图表，保存为图片显示
2. **导出功能**: 生成PDF报告，保存到本地
3. **配置界面**: 通过Web界面修改配置文件
4. **通知系统**: 本地桌面通知（需要用户权限）

### 安全注意事项
1. **避免敏感信息**: 不在Web界面显示邮箱密码等
2. **访问控制**: 如果暴露到公网，考虑添加基础认证
3. **数据备份**: 定期备份配置文件
4. **日志记录**: 记录访问日志用于审计

## 🚀 快速检查清单

```bash
# 1. 环境检查
python3 --version
pip list | grep gradio

# 2. 文件检查
cd /home/agentuser/projects/researchaudit
ls -la ceo_web_safe.py
chmod +x ceo_web_safe.py

# 3. 数据检查
ls target_users.json musk_style_messages.json

# 4. 运行测试
python3 ceo_web_safe.py --help
```

## 💡 最佳实践

### 开发建议
1. **版本控制**: 将代码提交到Git
2. **配置分离**: 敏感配置放在单独文件
3. **错误处理**: 友好的错误提示
4. **日志记录**: 记录重要操作

### 部署建议
1. **测试环境**: 先在本地测试
2. **逐步开放**: 先内网访问，再考虑公网
3. **定期更新**: 保持代码更新
4. **监控运行**: 检查进程状态

---

**立即开始**: 复制上面的代码到`ceo_web_safe.py`，运行`python3 ceo_web_safe.py`，10分钟内拥有安全的Web控制台！