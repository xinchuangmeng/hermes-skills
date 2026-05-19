---
name: agent-auto-business-monitor-automation
title: "用Python脚本自动化业务监控——4个实战模式"
description: "基于Dev.to文章《4 Python Scripts That Monitor Your Business While You Sleep》(2026-05-15)和《I Automated My Business Emails with Python》。核心模式：定时健康检查、异常交易告警、竞品价格变化监控、自动化邮件回复。这些模式可直接转化为Agent的定时任务工作流。适用于需要业务自动化监控的Agent场景。"
tags: [agent-auto, business-monitor, automation, python-scripts, cronjob]
trigger: |
  当需要构建业务监控自动化、设置Agent的cronjob定时检查、或设计业务告警系统时
---
# 用Python脚本自动化业务监控

## 🎯 核心洞察

来自Dev.to两篇实战文章的4个业务自动化监控模式，这些模式可以直接在Hermes中用cronjob + Agent实现。

### 模式1：系统健康检查

```python
# 定时检查系统/服务是否正常运行
import requests, smtplib, json
from datetime import datetime

def health_check(config_file="services.json"):
    with open(config_file) as f:
        services = json.load(f)
    
    results = []
    for svc in services:
        try:
            resp = requests.get(svc["url"], timeout=5)
            status = "UP" if resp.status_code < 500 else "DOWN"
        except Exception as e:
            status = f"DOWN ({str(e)})"
        
        results.append({
            "service": svc["name"],
            "status": status,
            "time": datetime.now().isoformat()
        })
    
    # 如果有DOWN的服务，发送告警
    down = [r for r in results if "DOWN" in r["status"]]
    if down:
        send_alert(f"Services DOWN: {json.dumps(down, indent=2)}")
    
    return results
```

**Hermes中实现：**
```yaml
# 在config.yaml中配置cronjob
cronjob:
  - name: "health-check"
    schedule: "*/15 * * * *"  # 每15分钟
    task: "检查所有服务的健康状态，发现异常立即报告"
    silence_if_nothing: true  # 一切正常时沉默
```

### 模式2：关键业务指标监控

```python
# 监控销售额、订单量、用户注册量等关键指标
import pandas as pd
from datetime import datetime, timedelta

def monitor_kpis(db_connection):
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    
    metrics = {
        "daily_revenue": query_revenue(db_connection, yesterday),
        "new_users": query_new_users(db_connection, yesterday),
        "orders_count": query_orders(db_connection, yesterday),
        "avg_order_value": query_avg_order(db_connection, yesterday),
    }
    
    alerts = []
    # 与7天平均值对比
    for name, value in metrics.items():
        avg_7d = query_7d_avg(db_connection, name)
        if value < avg_7d * 0.7:  # 低于70%时告警
            alerts.append(f"⚠️ {name}: {value} (7天均值: {avg_7d:.2f})")
    
    if alerts:
        send_report("Daily KPI Alert", "\n".join(alerts))
    else:
        send_report("Daily KPI Summary", json.dumps(metrics, indent=2))
```

### 模式3：竞品价格监控

```python
# 定期检查竞品的价格变化
def monitor_competitor_prices(product_urls):
    changes = []
    for url in product_urls:
        current_price = fetch_price(url)
        last_price = get_last_price(url)
        
        if current_price != last_price:
            changes.append({
                "url": url,
                "from": last_price,
                "to": current_price,
                "diff": current_price - last_price,
                "time": datetime.now().isoformat()
            })
            update_last_price(url, current_price)
    
    if changes:
        send_alert(f"价格变动: {len(changes)} 个商品价格发生变化")
        for c in changes:
            print(f"  {c['url']}: {c['from']} → {c['to']} ({c['diff']:+.2f})")
    
    return changes
```

### 模式4：自动化邮件处理

```python
# 自动化处理业务邮件（来自第二篇文章）
import imaplib, email, smtplib
from email.mime.text import MIMEText

def process_business_emails():
    # 连接邮箱
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login("user@gmail.com", "app_password")
    mail.select("INBOX")
    
    # 搜索未读邮件
    status, messages = mail.search(None, "UNSEEN")
    
    for msg_id in messages[0].split():
        status, data = mail.fetch(msg_id, "(RFC822)")
        msg = email.message_from_bytes(data[0][1])
        
        subject = msg["subject"]
        sender = msg["from"]
        
        # 根据主题自动回复
        if "order inquiry" in subject.lower():
            auto_reply_order_inquiry(msg)
        elif "support" in subject.lower():
            auto_reply_support(msg)
        elif "refund" in subject.lower():
            # 退款需要人工处理
            forward_to_human(msg)
        else:
            mark_for_review(msg)
```

## 🔧 在Hermes中实现监控Agent

### 完整的监控Agent配置

```yaml
# Hermes config.yaml 监控配置
cronjob:
  - name: "business-health-check"
    schedule: "*/5 * * * *"  # 每5分钟
    task: "检查所有业务服务状态"
    silence_if_nothing: true
    
  - name: "daily-summary"
    schedule: "0 9 * * *"  # 每天早上9点
    task: "汇总昨日业务数据并生成报告"
    
  - name: "competitor-monitor"
    schedule: "0 */6 * * *"  # 每6小时
    task: "检查竞品价格变动"
    
  - name: "error-analysis"
    schedule: "0 * * * *"  # 每小时
    task: "分析最近1小时的错误日志"
```

### 监控模板

```python
# 通用监控脚本模板
class BusinessMonitor:
    def __init__(self, name, check_fn, alert_fn=None):
        self.name = name
        self.check_fn = check_fn
        self.alert_fn = alert_fn
        self.last_status = None
    
    def run(self):
        """执行一次检查"""
        try:
            result = self.check_fn()
            status = "PASS" if result.get("healthy", True) else "FAIL"
            
            if status == "FAIL":
                self.alert_fn(result.get("message", "Unknown error"))
            elif self.last_status == "FAIL" and status == "PASS":
                self.alert_fn(f"✅ {self.name} 已恢复")
            
            self.last_status = status
            return {"status": status, "details": result}
            
        except Exception as e:
            return {"status": "ERROR", "details": str(e)}
```

## ⚠️ 注意事项

1. **监控本身也需要监控** — 如果监控脚本挂了，谁来通知你？
2. **告警疲劳** — 太多无关告警会让你无视所有告警。只告警真正需要关注的事
3. **silence_if_nothing很重要** — 一切正常时保持安静，只有异常才通知
4. **敏感信息保护** — 邮箱密码/API Key必须通过环境变量传入，不要硬编码
5. **重试与容错** — 网络波动可能导致临时失败，重试3次后再告警
6. **业务监控需要业务知识** — 仅仅"服务在线"不够，要监控"业务正常运转"
