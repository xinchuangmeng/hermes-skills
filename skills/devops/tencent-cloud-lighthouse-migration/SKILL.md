---
name: tencent-cloud-lighthouse-migration
title: "腾讯云轻量应用服务器购买+迁移+环境部署完整流程"
description: "从腾讯云轻量应用服务器选购、新账号注册、镜像选型、搭配产品评估、SSH连接配置、旧服务器数据迁移的全流程实操指南。含真实踩坑经验（时间预估、文件损坏、版本搞混、内网传输等）"
tags: [腾讯云, 轻量应用服务器, Lighthouse, 迁移, SSH, Docker, 运维, Hermes]
trigger: 
  当需要购买腾讯云服务器、迁移数据到新服务器、配置新环境时使用
  当用户问"服务器怎么买"、"镜像选哪个"、"搭配产品要不要买"时使用
---

# 腾讯云轻量应用服务器购买+迁移+部署完整流程

## ⚠️ 铁律：实事求是报时间

**不要说"几分钟就好"实际是二十多分钟。** 用户最反感这个。
预估时间必须留30%余量，说多久就是多久。

## 核心场景

用户已有腾讯云轻量应用服务器（2核2G），需要升级为更高配置（4核4G），利用**新用户优惠**降低成本，涉及：新账号注册 → 服务器购买 → 镜像选型 → 搭配产品决策 → 数据迁移 → 环境部署。

---

## 一、新账号注册

利用新用户优惠需要**新手机号**注册新账号。

**重要规则：**
- 腾讯云新用户定义：该产品（轻量应用服务器）无订单记录或累计订单金额为0
- 云服务器CVM和轻量应用服务器**视为非同类商品**，之前买过CVM仍可享受轻量首单
- 同一实名认证主体限购1次（换手机号不换实名也不行！）

## 二、购买配置

### 2.1 规格选择
- **现状升级：** 2核2G → **4核4G**（内存翻倍是解决卡顿的关键，多花在CPU和内存上）
- 敬哥案例：旧服务器2核2G内存经常满（244MB余量+600MB swap），升级到4核4G后空闲3GB

### 2.2 镜像选择
| 推荐 | 镜像 | 理由 |
|------|------|------|
| ✅ **首选** | **Docker CE 27.5.1** | 自带Docker，装Hermes和项目方便，用户熟悉的Ubuntu系统 |
| ❌ 别选 | Hermes Agent v0.10.0 | 版本太旧（0.12.0才是最新），镜像里的内容不是用户的 |
| ❌ 别选 | WordPress/WooCommerce等 | 不建网站用不上 |
| ❌ 别选 | Dify/n8n | 工作流工具，暂时用不上 |
| ⚠️ 备选 | 纯净系统+自己装Docker | 也能用但多一步 |

### 2.3 搭配产品策略
- **轻量对象存储100GB：** ❌ 不需要（40G硬盘还有23G空余）
- **域名1元：** ❌ 不需要（不做网站）
- **SSL证书：** ❌ 不需要
- **轻量DDoS/数据库：** ❌ 都不需要
- **结论：** 只买服务器自己，79元/年

## 三、SSH连接

### 3.1 认证方式
- Docker CE镜像默认**用户名是 `ubuntu`**，不是 `root`
- 重置密码时记得选对用户名
- 腾讯云控制台自带的WebShell可以直接登录（推荐）

### 3.2 常用命令
```bash
# 从旧服务器传文件到新服务器（公网）
scp ~/xxx.tar.gz ubuntu@新服务器IP:~/
# 密码：新服务器密码

# 同地域传文件（更推荐走内网）
# 先查内网IP
ip addr show | grep "inet " | grep -v 127.0.0.1
# 然后用内网IP传（速度100MB/s+）
scp ~/xxx.tar.gz ubuntu@内网IP:~/
```

## 四、数据迁移（关键步骤，踩坑最多）

### 推荐方案：rsync增量同步（免密+内网直连）

比tar打包+scp更推荐的方式是 **rsync增量同步**，尤其是迁移进行中还有数据在更新的场景。

#### 前置：配置SSH免密登录

```bash
# 在旧服务器上生成SSH Key（如果还没生成过）
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""

# 把公钥复制到新服务器
ssh-copy-id -p <新服务器SSH端口> <新服务器用户>@<新服务器IP>

# 测试免密
ssh -p <新服务器SSH端口> <新服务器用户>@<新服务器IP> "hostname"
```

#### 关键：目标目录权限处理

**这是最常见的坑：** 用新服务器的 `ubuntu` 用户SSH过去，默认没有写入 `/home/agentuser/` 的权限，rsync会报 `Permission denied (13)`。

**解决方法：** SSH远程执行sudo修权（需配好新服务器的sudo密码，或已在VNC里配好）

```bash
ssh -p <端口> <新用户>@<新IP> "sudo chown -R agentuser:agentuser /home/agentuser/sea-ecommerce && sudo chmod -R 755 /home/agentuser/sea-ecommerce"
```

#### 执行同步

```bash
# 同步.hermes（核心配置/记忆/技能/会话数据）
rsync -avz --progress -e "ssh -p <端口>" /home/agentuser/.hermes/ <新用户>@<新IP>:/home/agentuser/.hermes/

# 同步工作文件
rsync -avz --progress -e "ssh -p <端口>" /home/agentuser/sea-ecommerce/ <新用户>@<新IP>:/home/agentuser/sea-ecommerce/
```

**rsync优势：**
- 增量同步，只传差异部分（首次全量，之后只传变化的）
- 支持断点续传
- 自动跳过相同文件
- `-z` 压缩传输，省带宽

#### 验证同步结果

```bash
ssh -p <端口> <新用户>@<新IP> "du -sh /home/agentuser/.hermes/ /home/agentuser/sea-ecommerce/"
```

**更彻底的验证：** 对比关键数据量级
```bash
ssh -p <端口> <新用户>@<新IP> "find /home/agentuser/.hermes/sessions/ -type f | wc -l && ls -lh /home/agentuser/.hermes/state.db && ls -1 /home/agentuser/.hermes/skills/ | wc -l"
```

#### ⚠️ rsync常见错误速查

| 错误 | 原因 | 解决 |
|------|------|------|
| `Permission denied (13)` | SSH用户对目标目录无写入权限 | 先通过SSH执行 `sudo chown` 修权 |
| `rsync error: some files/attrs were not transferred (code 23)` | 部分文件因权限失败 | 修权后重新rsync即可 |
| `mkdir \"...\" failed: Permission denied` | 子目录无权限 | 同上 |
| 修权后依然报Permission denied | sudo chown看似成功但实际没生效 | 1) 确认新服务器用户有sudo权限（`sudo -n true`测试） 2) 务必在VNC里执行sudo修权（最可靠） 3) chmod用755不够→临时用777先传完再收紧 |
| `Connection reset by [IP] port 22` | SSH连接因超时被断开 | 重新SSH登录旧服务器，重新跑rsync（会自动跳过已传文件） |

### 备用方案：tar打包+scp（适合一次性全量迁移）

### 4.1 需要迁移的文件

| 文件 | 大小（案例） | 说明 |
|------|------------|------|
| /home/agentuser/ | 全部数据+配置 | Hermes完整配置、技能库、记忆等 |
| /home/agentuser/projects/ | ~21MB | 项目代码 |
| Hermes程序目录 | ~462MB | ~/.hermes/hermes-agent/ |

### 4.2 打包命令
```bash
# 打包数据（不压缩更快更稳）
tar -cf ~/xxx.tar -C /home/agentuser .hermes projects

# 如果有需要可以按目录分开打包
tar -czf ~/projects.tar.gz -C /home/agentuser projects
```

### 4.3 ⚠️ 文件损坏处理
- scp中断后文件损坏 → 报错 `tar: Unexpected EOF in archive`
- **解决方案：** 删掉损坏文件重新传（不能续传，必须重传）
- 不压缩打包（tar -cf 而非 tar -czf）更稳

### 4.4 解压恢复
```bash
# 解压数据
sudo tar -xf ~/xxx.tar -C /

# 修权限
sudo chown -R agentuser:agentuser /home/agentuser/
```

## 五、环境部署

### 5.1 Hermes安装陷阱：pip版本 vs GitHub版本
| 安装方式 | 版本 | 说明 |
|---------|------|------|
| `pip install hermes` | v0.9.1 ❌ | 学术工具包，不是Hermes Agent |
| GitHub克隆 | v0.12.0+ ✅ | 真正的Hermes Agent |

**正确安装方式：**
```bash
# 方式1：从GitHub克隆
git clone https://github.com/HermesAI/Hermes.git
cd Hermes && pip install -e .

# 方式2：迁移已有安装（更推荐）
# 从旧服务器打包 ~/.hermes/hermes-agent/ 目录
# 直接复制到新服务器的 /home/agentuser/
```

### 5.2 依赖包安装
Hermes Agent需要大量Python包。手动安装完整列表：
```bash
pip3 install openai anthropic lark-oapi tavily-python httpx jinja2 aiohtml
markdown beautifulsoup4 lxml Pillow requests python-dotenv fire rich pydantic prompt_toolkit colorama --break-system-packages
```

### 5.3 Hermes启动
```bash
# 后台运行gateway
cd /home/agentuser && nohup ~/.hermes/hermes-agent/hermes gateway run > /tmp/hermes_gateway.log 2>&1 &

# 检查状态
~/hermes-agent/hermes status
```

## 5.4 迁移后磁盘空间分析

用户迁移后常问"服务器上占了多少空间、都是什么"。用这套流程快速排查：

### 总览
```bash
df -h /
```

### 逐层透视
```bash
# 用户目录 -> 分类
du -sh /home/agentuser/* /home/agentuser/.* 2>/dev/null | sort -rh | head -30

# 隐藏目录单独看
du -sh /home/agentuser/.hermes  # Hermes核心数据
du -sh /home/agentuser/.cache    # pip缓存等（可清理）
du -sh /home/agentuser/.local    # 用户级安装的包
```

### Hermes目录内部解构
```bash
du -sh /home/agentuser/.hermes/* | sort -rh | head -15
```

### 常见大块说明

| 大块 | 典型大小 | 说明 | 能否删 |
|------|---------|------|--------|
| `/.hermes/hermes-agent/` | 1.3G | 旧备份的Hermes本体 | 可删（跟新服务器重复） |
| `/home/agentuser/.hermes/` | 1.9G | 当前运行的Hermes数据 | **不能删** |
| `venv/` | ~758M | Python虚拟环境 | 不能删（删了要重建） |
| `node_modules/` | ~175M | 前端依赖 | 可删（不跑前端） |
| `.cache/pip/` | ~73M | pip下载缓存 | 可删（`pip cache purge`） |
| `sea-ecommerce/` | ~157M | 项目文件 | 不能删 |

### 检查"重复备份"场景

#### 1️⃣ 先全盘扫描可能重复的.hermes目录
```bash
find / -maxdepth 3 -name ".hermes" -type d 2>/dev/null
```

#### 2️⃣ 快速对比总览
```bash
# 看两边大小和日期
du -sh /.hermes/ /home/agentuser/.hermes/
ls -la /.hermes/state.db /home/agentuser/.hermes/state.db

# 对比skills数量
ls -1 /.hermes/skills/ 2>/dev/null | wc -l
ls -1 /home/agentuser/.hermes/skills/ 2>/dev/null | wc -l

# 对比sessions数量
find /.hermes/sessions/ -type f 2>/dev/null | wc -l
find /home/agentuser/.hermes/sessions/ -type f 2>/dev/null | wc -l
```

#### 3️⃣ 精确到子目录级别对比
```bash
# 顶级目录列表差异
diff <(ls -1 /.hermes/) <(ls -1 /home/agentuser/.hermes/) | head -20

# 每个大子目录的大小对比
for dir in sessions cron logs skills bin checkpoints image_cache scripts; do
  old_size=$(du -sh /.hermes/$dir 2>/dev/null | awk '{print $1}')
  new_size=$(du -sh /home/agentuser/.hermes/$dir 2>/dev/null | awk '{print $1}')
  echo "$dir: 旧=${old_size:-无}  新=${new_size:-无}"
done

# 唯一skills差异
diff <(ls -1 /.hermes/skills/ 2>/dev/null) <(ls -1 /home/agentuser/.hermes/skills/ 2>/dev/null) | head -20
```

#### 4️⃣ 判断哪个数据更全的核心指标

| 指标 | 含义 | 旧数据更大说明 | 新数据更大说明 |
|------|------|-------------|-------------|
| **state.db大小** | DB文件记录了所有会话/设置 | 可能在旧服务器上运行更久 | 新服务器使用更频繁（更优） |
| **sessions文件数** | 历史对话记录数量 | 旧服务器对话更多 | 新服务器已积累足够记录 |
| **最早session日期** | 最早的会话时间戳 | 可能有遗漏的早期记录 | 新服务器覆盖更广 |
| **profiles目录** | 各profile配置 | 可能有独有的profile配置 | — |
| **skills数量** | 安装的技能数 | 可能有旧版独有技能 | 可能有新装技能 |

**判断标准：** 如果新服务器的state.db是旧服务器的3倍以上大、session数更多、最早记录日期相同或更早 → 新服务器数据已完全覆盖旧的，不需要合并。

#### 5️⃣ 特别检查：sea-ecommerce等非.hermes数据

如果sea-ecommerce也在迁移范围内，用同样的方法对比：
```bash
# 文件数量对比
find /旧路径/sea-ecommerce/ -type f 2>/dev/null | wc -l
find /新路径/sea-ecommerce/ -type f 2>/dev/null | wc -l

# 文件数一样后对比子目录大小
for dir in video_scripts voice_cloning series video_assets; do
  old=$(du -sh /旧路径/sea-ecommerce/$dir 2>/dev/null | awk '{print $1}')
  new=$(du -sh /新路径/sea-ecommerce/$dir 2>/dev/null | awk '{print $1}')
  echo "$dir: 旧=$old 新=$new"
done
```
如果文件数和子目录大小完全一致，说明sea-ecommerce已经迁移完整。

### 清理重复备份的权限问题

**典型场景：** 旧数据在 `/.hermes/`，但agentuser用户没有sudo密码（或密码试错3次后被锁定）。

**排查步骤：**
```bash
# 1️⃣ 先试试当前用户能否直接删（少数情况不需要sudo）
rm -rf /.hermes/ 2>&1

# 2️⃣ 测试sudo权限
sudo -n true 2>&1    # 如果要求输密码说明有sudo但没免密

# 3️⃣ 如果有sudo权限，直接删
sudo rm -rf /.hermes/

# 4️⃣ 如果sudo密码不对（3次错误尝试后会被锁15分钟以上）
# 方案A：用VNC窗口的另一个用户执行（如ubuntu）
sudo rm -rf /.hermes/   # 密码：ubuntu用户的密码

# 方案B：在VNC里设agentuser的sudo密码
sudo passwd agentuser
# 输入新密码两次

# 方案C：用root用户（如果已知root密码）
su -c "rm -rf /.hermes/"
```

**⚠️ 注意：** agentuser的sudo密码跟SSH登录密码通常是同一个。如果旧服务器和新服务器的agentuser密码不同，注意区分。

如果所有方案都不可行，删除不紧急，可以先留着——`.hermes/` 在根目录不影响运行，只是占空间。

---

## 六、多实例Hermes server配置（profile模式）

迁移完成后，可以在同一台服务器上运行多个Hermes实例，每个实例用不同profile加载不同的配置。

### 场景

- **实例A（通用）**：端口3001，日常对话/运维
- **实例B（东南亚电商助手）**：端口3000，配飞书，专门处理电商运营

### 操作步骤

#### 1. 查看已有profile

```bash
ls -1 /home/agentuser/.hermes/profiles/
# 输出类似：agent2  project2  southeast-ecommerce
```

每个profile是一个独立目录，包含自己的`config.yaml`、`.env`（飞书密钥等）、`state.db`。

#### 2. 修改profile的端口（避免冲突）

```bash
# 查看当前端口配置
grep -A3 "gateway:" /home/agentuser/.hermes/profiles/xxx/config.yaml
```

输出类似：
```yaml
gateway:
  host: 0.0.0.0
  port: 3001
```

修改端口：
```bash
# 用patch或改config.yaml中的port值为不同端口（3000/3002等）
```

#### 3. 用profile启动

```bash
# 指定profile启动（会在后台运行，端口独立）
cd /home/agentuser && nohup /home/agentuser/.hermes/hermes-agent/venv/bin/hermes gateway run --profile southeast-ecommerce > /tmp/southeast_gateway.log 2>&1 &
```

#### 4. 验证

```bash
# 看进程
ps aux | grep "hermes gateway" | grep -v grep

# 看日志确认飞书连接
tail -5 /tmp/southeast_gateway.log
# 期望输出：connected to wss://msg-frontier.feishu.cn/ws/v2...
```

#### 5. 注意事项

- **飞书是WebSocket长连接**，不占用TCP端口监听。所以即使配置了端口3000，不会显示监听3000端口的进程——这正常
- 飞书App ID/Secret在profile目录的`.env`里
- 不同profile可以用同一个飞书App，也可以各自独立的App
- 如果去掉`--profile`参数，启动的是默认的通用实例（读取`~/.hermes/config.yaml`）

#### 6. 停止实例

```bash
# 找到PID后kill
ps aux | grep "hermes gateway.*--profile.*xxx" | grep -v grep
kill <PID>
```

## 七、后续检查清单

- [ ] `.env` 中的API Key（DeepSeek/Kimi/Tavily）都写对
- [ ] `hermes status` 查看API Key状态
- [ ] `hermes cron list` 查看定时任务是否继承
- [ ] 飞书/webhook配置是否正常
- [ ] 旧服务器可以停掉/到期不续费

---

## ⚠️ 实战避坑总结（2026年5月亲身踩坑记录）

### 坑1：先检查内网IP再传文件！
- 同地域（都是广州）的轻量服务器有内网互通
- 内网传输速度可达100MB/s+，公网只有300KB/s
- **教训：** 拿到新服务器后第一件事是查旧服务器的内网IP（`ip addr`），两边的`scp`走内网IP传，快300倍

### 坑2：scp中断后文件损坏，必须重传
- 如果`scp`中途Ctrl+C中断，之前传的部分会损坏
- `tar: Unexpected EOF in archive` 就是这个原因
- **教训：** 中断后必须删掉损坏文件重新传，不能续传

### 坑3：pip装的hermes vs hermes-agent是两个不同东西
- `pip install hermes` 装的是学术工具包 v0.9.1（不是Agent）
- Hermes Agent的正确安装方式是从GitHub克隆后 `pip install -e .`
- 或者从旧服务器打包`hermes-agent`目录直接复制过去用

### 坑4：SSH密钥是单向的——旧→新配了，但新→旧可能没配
- **典型场景：** 为了rsync从旧服务器传数据到新服务器，在旧服务器上配了到新服务器的SSH免密（旧→新方向）。
- **但是新服务器想SSH到旧服务器时没有密钥**（新→旧方向没配）。这时新服务器想查旧服务器数据就查不了。
- **教训：** 迁移前**双向都配好**SSH密钥（既配旧→新，也配新→旧），省很多事。或者直接在旧服务器SSH窗口执行命令查数据，不用跨服务器查。
- **如果忘了配新→旧密钥：** 用户在旧服务器SSH窗口执行命令贴结果就行，省去跨服务器查的麻烦。

### 坑5：迁移后数据完整性验证——文件数+子目录大小双校验
- 只看 `du -sh` 总大小不够（可能接近但差异很小）
- **正确方法：** `find ... -type f | wc -l` 对比文件数 + 每个子目录 `du -sh` 对比
- 如果文件数和子目录大小都一致 → 数据迁移完整

### 坑6：agentuser sudo密码被锁的几种解法
1. 3次密码错误后sudo会被锁至少15分钟
2. 解法按优先级：VNC里用ubuntu用户sudo → su - 切换到root → 等15分钟后再试
3. 如果用户自己也不知道sudo密码：试试 `rm -rf` 不加sudo（目录如果属于agentuser就不需要sudo）

### 坑7：时间预估要留余量
- 3M带宽传462MB ≈ 24分钟，不是"几分钟"
- 用户明确要求：**实事求是说时间，不要为了好听缩水**

### 坑8：用户密码要确认用户名
- Docker CE镜像的默认用户名是 `ubuntu`，不是 `root`
- 重置密码时要确认选了正确的用户名

### 坑9：双向SSH密钥——从新服务器查旧服务器时才发现没配
- rsync迁移时只在旧服务器配了到新服务器的免密（旧→新方向），但新→旧方向没配
- 迁移结束后想从新服务器远程查旧服务器文件时，发现连不上
- 解法：
  1. 用户在旧服务器SSH窗口执行命令、贴结果（最快，不需要跨服务器）
  2. 或者在新服务器生成密钥对，把公钥手动加到旧服务器的 authorized_keys 里
  3. 注意旧服务器sshd配置中如果 PubkeyAuthentication 被注释（#PubkeyAuthentication yes），需取消注释并重启sshd才生效
  4. 多次认证失败后sshd会锁IP（Too many authentication failures），等待几分钟自动解锁，或用 sudo systemctl restart sshd 重置
- 教训：迁移前就配好双向SSH密钥，或在旧服务器窗口执行命令

### 坑10：删除旧备份时的sudo密码困境
- 旧服务器数据备份到根目录 /.hermes/ 后，如果目录属于当前用户，可以直接删不需要sudo
- 如果agentuser的sudo密码试错3次被锁，可以用 su - 切换到root（如果知道root密码）
- 或者去VNC窗口用另一个用户（如ubuntu）执行 sudo rm -rf /.hermes/

### 坑11：迁移完成后的数据清理——跨服务器对比确认哪些数据是重复的
- 迁移后旧数据可能残留在根目录 /.hermes/，跟运行中的 /home/agentuser/.hermes/ 重复
- 删除前必须对比确认：看两边state.db大小、session数量、最早记录日期
- 如果新服务器的state.db是旧的3倍以上大、session更多、最早记录日期相同或更早 → 新服务器数据已完全覆盖旧的，可以直接删旧的
- sea-ecommerce用文件数+子目录大小双校验确认完整性

### 坑12：SSH公钥写入后仍连不上——检查authorized_keys指纹要匹配
- 在新服务器生成密钥后 ssh-keygen，把公钥写入旧服务器的 authorized_keys
- 验证：两边指纹一致才算成功（ssh-keygen -lf ~/.ssh/id_rsa.pub 对比）
- 如果还连不上，用 ssh -v 看详细日志定位原因

### 坑13：SSH公钥认证失败却看不到明显错误——检查家目录权限
- 症状：密钥指纹匹配、authorized_keys 内容正确、SSH端口正常，但 `ssh -v` 显示 `Offering public key` 后直接被拒（没有尝试密码）
- 根本原因：**SSH要求用户家目录不能是其他用户可写的**（`others` 不能有 `w` 权限）
- 排查：`ls -la /home/<user>/` 看权限是不是 `drwx------` 或 `drwxr-xr-x`
- 修复：
  ```bash
  chmod 755 /home/<user>/
  chmod 700 /home/<user>/.ssh
  chmod 600 /home/<user>/.ssh/authorized_keys
  ```
- 修复后无需重启sshd，立即生效
- **常见触发条件：** 之前用 `sudo chmod -R 777` 修权时把家目录权限也改松了
- 用 `ssh -v` 看日志时，如果看到 `Offering public key: ... RSA` 后直接 `Permission denied`（没有进入 password 阶段），基本就是这个原因

### 坑14：迁移后清理——跨服务器对比确认哪些数据是重复的

- 场景：数据已从旧服务器迁移到新服务器，旧服务器上既有原始数据也有各种 `hermes_backup.tar`、`hermes_prog.tar.gz`、旧Hermes副本（如 `hermes2/`）
- 删除旧服务器上的备份前，先用SSH对比确认：
- 场景：数据已从旧服务器迁移到新服务器，旧服务器上既有原始数据也有各种 `hermes_backup.tar`、`hermes_prog.tar.gz`、旧Hermes副本（如 `hermes2/`）
- 删除旧服务器上的备份前，先用SSH对比确认：
  ```bash
  # 从新服务器SSH到旧服务器，做结构化对比
  echo "=== sea-ecommerce目录结构对比 ==="
  diff <(ssh 旧 "find /path/sea-ecommerce/ -type f | sort") <(find /path/sea-ecommerce/ -type f | sort)
  
  echo "=== skills差异 ==="
  diff <(ssh 旧 "ls -1 /path/.hermes/skills/ | sort") <(ls -1 /path/.hermes/skills/ | sort)
  
  echo "=== 核心指标 ==="
  ssh 旧 "du -sh /path/.hermes/ && ls -lh /path/.hermes/state.db && find /path/.hermes/sessions/ -type f | wc -l"
  # 在本机对比同样指标
  ```
- **删除收益评估：** 对比后如果发现旧服务器的hermes_backup.tar（~1.8G）、hermes_prog.tar.gz（~460M）、hermes2/（~1.2G）在新服务器上根本没有 → 直接删除节省 ~4GB
- **安全删除：**
  ```bash
  rm -f ~/hermes_backup.tar ~/hermes_backup.tar.gz ~/hermes_prog.tar.gz
  rm -rf ~/hermes2/  # 仅当确认该副本已迁移
  ```
- **原则：** 迁移对比不仅是确认“数据到了”，还要确认“哪些是备份可以删的”。备份文件和重复的Hermes副本通常是最值得清理的大块

**数据来源：** 2026年5月6日+5月16日敬哥腾讯云服务器迁移实战经验