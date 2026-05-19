# 学习进度迁移记录 & 已知题目标

迁移时间: 2026-05-16
源路径: /home/agentuser/.hermes/
目标路径: /root/.hermes/

## 当前进度

- 已完成轮次: 第1-6轮全30题 = 180题
- 当前轮次: 第7轮第22题（2026-05-16已做，shortvideo-business-ip-persona-positioning v7.0）
- 30道主干题全部有对应技能，多数已深化至v3.0-v7.0

## 30道主干题索引

| # | 题目 | 技能名 | 最新版本 |
|---|------|--------|---------|
| 1 | 全球主流跨境平台商业模式、算法逻辑与长期红利对比 | crossborder-platform-selection-2026 | v7.0 |
| 2 | 东南亚TikTok/Shopee/Lazada平台顶层规则、风控防封底层逻辑 | crossborder-platform-compliance-2026 | v6.0 |
| 3 | 跨境无货源/精品/DTC三种模式优缺点与入局门槛 | crossborder-three-models-2026 | - |
| 4 | 跨境供应链全链路：1688工厂筛选、代发、海外仓、履约流程 | crossborder-supply-chain-full-chain | v5.0 |
| 5 | 全球各国跨境电商合规、知识产权、禁售类目深度拆解 | crossborder-global-compliance-guide | v4.0 |
| 6 | 跨境收款、财税报关、个体户/公司主体架构布局方案 | crossborder-payment-tax-entity | v3.0 |
| 7 | 海外社媒全域引流：TikTok/YouTube/Facebook/Instagram流量底层打法 | crossborder-social-media-traffic | v5.0 |
| 8 | 跨境小众蓝海赛道挖掘逻辑、新兴国家电商渗透率风口分析 | crossborder-blue-ocean-discovery | v3.0 |
| 9 | 跨境AI工具全矩阵：选品、翻译、客服、剪辑自动化落地 | crossborder-ai-tools-matrix | - |
| 10 | 跨境店铺矩阵布局、多账号防关联、规模化放大运营逻辑 | crossborder-store-matrix-2026 | v5.0 |
| 11 | 全球AI智能体行业发展趋势、商业落地赛道与未来五年风口 | ai-agent-industry-trends-2026 | - |
| 12 | 通用AI Agent底层架构、记忆系统、任务编排核心原理 | ai-agent-core-architecture | - |
| 13 | 多模型路由、私有部署、本地私有化智能体搭建完整方案 | ai-agent-private-deployment-guide | - |
| 14 | 飞书/企业微信/微信 智能体机器人商业接入与自动化流程 | feishu-wechat-enterprise-agent-integration | - |
| 15 | AI自动化工作流搭建：替代人工办公、客服、运营全场景 | ai-agent-automation-workflows | v4.0 |
| 16 | 小成本AI创业可落地赛道拆解、变现模式与起步路径 | ai-low-cost-entrepreneurship-roadmap | v6.0 |
| 17 | AI提示词工程顶层方法论、角色定制、模板工业化制作 | prompt-engineering-top-methodology | v4.0 |
| 18 | 智能体自我进化、自动知识归档、技能自我迭代机制搭建 | agent-auto-self-evolution-mechanism | - |
| 19 | 全网顶级AI生产力工具矩阵、场景适配与组合使用玩法 | ai-tools-matrix-2026 | v7.0 |
| 20 | 企业级AI数字化改造、小公司低成本智能化落地案例 | enterprise-ai-digital-transformation | v4.0 |
| 21 | 全平台算法底层差异拆解：抖音/视频号/小红书/B站/TikTok | shortvideo-algorithm-bottom-differences | v4.0 |
| 22 | 商业IP与人设定位顶层逻辑、长期复利打造方法论 | shortvideo-business-ip-persona-positioning | v7.0 |
| 23 | 爆款短视频底层逻辑：选题、脚本、情绪、完播率核心公式 | shortvideo-viral-content-core-formula | v6.0 |
| 24 | 账号矩阵搭建、多账号运营、防关联、批量起号标准化流程 | shortvideo-account-matrix-building | v6.0 |
| 25 | AI全链路短视频生产：文案、数字人、配音、剪辑自动化 | shortvideo-ai-full-chain-production | v2.0 |
| 26 | 短视频私域导流、粉丝资产沉淀、高转化承接流程 | shortvideo-private-domain-conversion | v2.0 |
| 27 | 内容商业化全赛道：带货、知识付费、广告、社群、咨询变现 | shortvideo-content-monetization | v3.0 |
| 28 | 对标账号拆解方法论、复制爆款逻辑、低成本复刻起号 | shortvideo-benchmark-account-deconstruction | v2.0 |
| 29 | 短视频发布权重、标签打法、流量撬动与热门推荐机制 | shortvideo-publish-weight-seo-hot-recommend | v3.0 |
| 30 | 跨境短视频本土化创作、海外内容适配与带货脚本逻辑 | crossborder-short-video-localization | v4.0 |

## 新三分类 vs 旧题号映射

新用户规则中的分类映射：
- ① 跨境电商运营篇 → 旧题 #1-10, #30
- ② 短视频图文剪辑篇 → 旧题 #21-29
- ③ 智能体学习与落地应用篇 → 旧题 #11-20

## 服务器迁移要点

- 老服务器数据在 /home/agentuser/.hermes/（agentuser 用户）
- 当前会话以 root 运行，~/.hermes/ = /root/.hermes/
- 技能已 cp -a 从 agentuser 复制到 root
- auto_learn_progress.txt 已复制
- auto-learn-core-rules.md 已复制
- 旧网关进程 (PID 70212, 3570427) 已清理
- DEEPSEEK_API_KEY 已修复（.env 重写 + bashrc export）
- TiRith 已安装
