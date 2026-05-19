---
name: hermes-sandbox-troubleshooting
title: Hermes沙箱分层分析与浏览器自动化环境排查
description: Hermes Agent的沙箱不是单一概念，而是分3层——Terminal后端隔离（local/docker/modal）、Chrome浏览器沙箱（--no-sandbox参数）、Tirith安全策略拦截。轻量服务器本身不是沙箱，能正常上网和登录网站。浏览器启动失败通常是Chrome沙箱内核权限问题（user namespaces被AppArmor禁用），而非Hermes自身限制。解决浏览器自动化登录问题的首选方案是在本地Windows电脑装Hermes（无沙箱问题），其次是用Shopee官方API对接。
category: software-development
---

# Hermes沙箱分层分析与浏览器自动化环境排查

## 一、核心认知：沙箱不是单一概念

Hermes的"沙箱"经常被误解为单一开关，实际上分3层独立机制：

| 层级 | 作用 | 对登录的影响 |
|:----:|:------|:-----------|
| **Layer 1: Terminal后端** | 命令执行环境隔离 | **不影响** |
| **Layer 2: Chrome浏览器沙箱** | 浏览器进程安全隔离 | ❌ **不让启动浏览器** |
| **Layer 3: Tirith安全策略** | 高危命令拦截 | **不影响登录** |

### Layer 1: Terminal后端

Hermes的terminal支持多种后端，配置在config.yaml中：

| backend值 | 是否沙箱 | 说明 |
|:---------:|:--------:|------|
| `local` | ❌ 不沙箱 | 直接执行，无隔离 |
| `docker` | ✅ 容器隔离 | 在Docker容器内执行 |
| `modal` | ✅ 云端隔离 | Modal云沙箱 |

**敬哥的场景：** 用 `local` 后端，Terminal层面无沙箱限制。

### Layer 2: Chrome浏览器沙箱（常见坑点）

这是最常见的"装好Hermes但用不了浏览器"的原因——

**根因：** 轻量服务器（腾讯云/阿里云/华为云）上的Chrome默认用沙箱模式启动，但Ubuntu 23.10+通过AppArmor禁用了user namespaces，导致Chrome的沙箱功能无法使用。

**这不代表Hermes有问题，是Chrome自身的沙箱在服务器环境中缺少内核权限。**

**解决方法（服务器端）：**
在Chrome启动参数中加 `--no-sandbox`。

**注意：** Hermes内置的 `browser_navigate` 工具用的是agent-browser，不一定支持自定义启动参数，所以即使装了Chrome也不一定能正常调用。

### Layer 3: Tirith安全策略

只拦截高危系统操作命令，不影响浏览器登录。

---

## 二、轻量服务器≠沙箱

| 概念 | 说明 |
|:----|:-----|
| **轻量服务器本身** | 就是一台普通Linux服务器，能正常上网、能登录网站 |
| **沙箱/容器隔离** | 只有给AI智能体专门开了沙箱（Docker容器、systemd-nspawn）才会受限 |

**判断当前环境是否沙箱：**
```bash
# 检查是否为容器
cat /.dockerenv 2>/dev/null

# 检查网络是否隔离
ip addr
```

---

## 三、浏览器自动化的可行方案（按推荐顺序）

### 方案A：本地Windows电脑装Hermes ✅ 最推荐

- **原因：** 本地Windows Chrome没有沙箱问题，agent-browser可以直接调本地Chrome
- **安装：** Hermes v0.13.0已原生支持Windows（不再需要WSL2）
- **能力：** 可登录Shopee/Lazada等网站，操作后台，自动上架商品
- **局限：** Computer Use仅支持macOS 15+

### 方案B：用Shopee官方API对接

- **最合规：** 通过 open.shopee.com 注册开发者账号，用API操作
- **零被封风险：** 所有第三方ERP（妙手、店小秘、EasyBoss）都走这个方式

### 方案C：服务器上装Camofox反检测浏览器

- Camofox是自托管的Firefox修改版，带指纹伪装
- 通过REST API暴露浏览器操作能力
- 需要先装Node.js环境

---

## 四、避免踩坑的检查清单

| 步骤 | 检查什么 | 如果不行怎么办 |
|:----:|:---------|:-------------|
| 1 | 确认 `terminal.backend` 是 `local` | 改配置即可 |
| 2 | 确认服务器上有没有Chrome | 没有就装，或换方案A |
| 3 | `google-chrome --no-sandbox` 能不能启动 | 如果还崩，走方案A或B |
| 4 | 检查 `.dockerenv` 是否在容器里 | 在容器里要改容器配置 |

---

## 五、敬哥场景总结

| 项目 | 当前状态 |
|:----|:---------|
| **服务器环境** | 腾讯云轻服务器，Ubuntu，非容器 |
| **Terminal后端** | `local`（无沙箱） |
| **Chrome浏览器** | snap版chromium，沙箱问题导致无法启动 |
| **最佳方案** | Windows电脑装Hermes 或 走Shopee API |
| **不建议尝试** | 在服务器上折腾Chrome沙箱（投入产出比低） |
