# 多Agent共享技能库方案：GitHub仓库同步

## 背景

小书童（云端Hermes 301技能）积累了大量技能，小强（OpenClaw/本地Win）和旺财（Hermes微软版/本地Win）也想复用这些技能。
同时，三个Agent各自学习到的新知识需要汇总到同一份技能库里。

## 目标架构

```
小书童(云端) ────┐
小强(OpenClaw) ──┼──→ GitHub共享技能仓库 ←── 三方都从该源安装/同步
旺财(Hermes)  ───┘
     ↑
  三方都往这里贡献新技能
```

## 方案对比

### 方案A：GitHub仓库 + skillhub安装（推荐）

1. 建一个GitHub公共仓库，结构：
   ```
   shared-hermes-skills/
   ├── SKILLS_INDEX.md     # 技能清单和描述
   ├── skill-a/
   │   └── SKILL.md
   ├── skill-b/
   │   └── SKILL.md
   └── ... (按类别分目录)
   ```

2. 仓库配置为skillhub源 → 三方都能用 `skillhub install` 安装

**优点：** 标准化、版本控制、三方独立更新
**缺点：** 需要GitHub Token、国内网络可能有障碍

### 方案B：tar包飞书直传（快速上手）

1. 我（小书童）打包：`cd ~/.hermes && tar -czf skills.tar.gz skills/`
2. 飞书发送给敬哥 → 小强/旺财本地解压到对应技能目录
3. 定期手动同步（或写脚本自动拉取最新包）

**优点：** 零配置、一次搞定
**缺点：** 手动同步、没有版本管理

### 方案C：scp/rsync + 飞书通知（半自动）

1. 服务器端写cron脚本，定时打包技能库
2. scp传到一个共享位置或通过飞书发送
3. 客户端脚本自动解压合并

**优点：** 自动、不需要额外基础设施
**缺点：** 需要scp互通、合并可能冲突

## 推荐实施路径

### Phase 1：快速共享（马上能用）
1. 小书童打包技能库 → 飞书发给敬哥
2. 小强/旺财本地解压到各自技能目录
3. 确认三方都能正常加载

### Phase 2：GitHub仓库（长期方案）
1. 准备GitHub Token（fine-grained token，scope=repo）
2. 在云端创建仓库、初始化、推代码
3. 本地配置为skillhub源
4. 三方约定提交规则（见下）

### Phase 3：自动同步（成熟方案）
1. 服务器cron定期拉取其他两方的更新
2. 冲突检测和自动合并
3. 三方共享的「技能提交-审核-合并」流程

## 技能提交规则（三方约定）

当任一Agent学到了新知识并创建了技能，应该：
1. 本地创建/更新skill后，推送到共享仓库
2. 在SKILLS_INDEX.md中更新索引
3. 其他Agent通过cron或手动拉取更新

**命名规范：**
- 技能名用小写字母+连词符（如 `shopee-pricing-calculator`）
- 分类按功能领域（business/shortvideo/software-development等）
- 有依赖关系的技能在description中标注`depends-on: xxx`

## 需要解决的问题

1. **GitHub网络**：如果云端连GitHub不稳定，需要fallback方案
2. **技能冲突**：两个Agent同时修改同一个技能怎么办？
3. **敏感信息**：技能文件中不能包含API Key/密码（已在Hermes技能规范中禁止）
4. **Windows路径差异**：技能文件中的路径引用要考虑跨平台兼容
