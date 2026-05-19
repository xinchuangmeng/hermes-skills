---
name: agent-auto-free-cloud-ai-assistant
title: "免费云服务器搭建个人AI助手——Oracle Free Tier方案"
description: "基于Dev.to文章'Personal AI Assistant - Setting Up Free Cloud Server - The Complete Guide'——用Oracle Cloud Always Free Tier（4核24GB ARM + 200GB存储）搭建个人AI助手。包括：Oracle注册避坑、SSH配置、Docker部署Open WebUI+Ollama、内网穿透、域名绑定。适用于想免费搭建私有AI助手或Agent测试环境的场景。"
tags: [agent-auto, free-tier, oracle-cloud, ai-assistant, self-hosted, open-webui]
trigger: |
  当需要免费云服务器搭建AI服务、想用Oracle Free Tier、或评估自托管AI服务的成本时
---

# 免费云服务器搭建个人AI助手

## 🎯 核心方案

### Oracle Cloud Always Free Tier
```yaml
免费资源:
  - 4核 ARM Ampere CPU（足够跑7B-13B模型）
  - 24GB RAM（可以跑Qwen3-Coder 7B）
  - 200GB 存储（够装多个模型权重）
  - 10TB 出站流量/月
  - 完全免费，永久有效

需注意:
  - Oracle注册对某些国家/地区的信用卡审核严格
  - ARM实例要选对区域（某些区域已被抢光）
  - 用完即毁策略：空闲资源可能被回收
```

### 部署栈
```yaml
stack:
  底层: Oracle Cloud Ubuntu 22.04 ARM
  
  运行环境: Docker + Docker Compose
  
  LLM推理: Ollama（支持ARM原生）
  - Qwen3-Coder 7B: 高质量编程Agent
  - DeepSeek V4 Lite: 通用任务
  - LLaMA 3-8B: 日常对话
  
  前端界面: Open WebUI（类ChatGPT界面）
  - 多模型切换
  - 对话历史管理
  - RAG文件上传
  - 插件系统
  
  网络访问: 
  - Cloudflare Tunnel（免费内网穿透）
  - 或 Nginx Proxy Manager + 域名
```

## 📋 完整部署流程

### 第1步：注册Oracle Cloud账号
```bash
# 准备工作
- 护照或身份证（验证用）
- Visa/Mastercard信用卡（扣$1验证，会退还）
- 非中国IP注册（容易被拒）
- 推荐区域: 首尔、东京、新加坡（延迟低）

# 注册地址
https://signup.cloud.oracle.com

# 避坑提示
- 如果注册失败，换一个邮箱和信用卡重试
- 注册成功后，先创建预算告警（防止误用付费服务）
- 即使只是Free Tier，也建议设置每月$0的预算告警
```

### 第2步：创建ARM实例
```bash
# 在OCI控制台操作
1. 创建VM实例
   - 镜像: Ubuntu 22.04 Minimal (ARM)
   - 形状: VM.Standard.A1.Flex
   - 配置: 4核 OCPU, 24GB RAM
   - 存储: 200GB
   - SSH密钥: 上传你的公钥

2. 安全组配置
   开放端口:
    - 22（SSH）— 仅限你的IP
    - 80（HTTP）
    - 443（HTTPS）
    - 3000（Open WebUI界面）

3. 分配弹性公网IP
```

### 第3步：安装Docker和Ollama
```bash
# SSH连接
ssh ubuntu@<你的公网IP>

# 安装Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

# 安装Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 拉取模型（7B级，ARM兼容）
ollama pull qwen3-coder:7b
ollama pull llama3:8b

# 验证Ollama
ollama list
curl http://localhost:11434/api/tags
```

### 第4步：部署Open WebUI
```bash
# 使用Docker Compose
mkdir ~/open-webui && cd ~/open-webui

cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: open-webui
    ports:
      - "3000:8080"
    volumes:
      - ./data:/app/backend/data
    environment:
      - OLLAMA_BASE_URL=http://<你的服务器IP>:11434
      - WEBUI_SECRET_KEY=<生成一个随机密钥>
    restart: unless-stopped
EOF

# 启动
docker-compose up -d

# 访问: http://<你的公网IP>:3000
# 首次访问注册管理员账号
```

### 第5步：配置内网穿透（安全访问）
```bash
# 方案A：Cloudflare Tunnel（推荐）
# 免费的域名DNS代理+隧道，比直接暴露IP更安全

# 方案B：Nginx + Let's Encrypt + 域名
sudo apt install nginx certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 🔧 在Hermes中集成

```yaml
# 将自托管的Ollama设为Hermes的后端Provider
hermes_config:
  providers:
    - name: "self-hosted"
      type: "ollama"
      base_url: "http://<你的Oracle实例>:11434"
      models:
        - "qwen3-coder:7b"  # 编程任务
        - "llama3:8b"       # 通用任务
  
  # 分层使用
  routing:
    cheap: "self-hosted/qwen3-coder:7b"  # 免费使用
    medium: "deepseek-chat"               # API按需
    expensive: "claude-sonnet-4"          # 仅在关键任务用
```

## 💰 成本对比

```yaml
# 每月成本
Oracle Free Tier: $0
Ollama推理: $0（完全本地）
Open WebUI: $0（开源）
域名: $0-10/年（可选）

对比:
  - OpenAI ChatGPT Plus: $20/月 = $240/年
  - Claude Pro: $20/月 = $240/年
  - 自托管方案: $0-10/年（域名费）
  - 且自托管的数据完全私有
```

## ⚠️ 注意事项

1. **Oracle注册可能被拒** — 某些国家的信用卡容易被拦，换卡或换区域试试
2. **ARM实例可能被回收** — Oracle会回收长期空闲资源，保持SSH定期连接
3. **24GB跑7B模型刚好** — 跑13B模型需要更多内存，建议用量化版本
4. **SSH密钥一定要备份** — 丢了密钥就再也连不上实例
5. **安全性不能忽视** — 即使免费，也要配置防火墙和定期更新
6. **模型推理速度** — ARM上的推理速度不如x86 GPU，但7B模型在对话场景下够用
