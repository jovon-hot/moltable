# Moltable 增长策略

> **定位**: AI Identity Sync — "iCloud for AI Agents"  
> **产品状态**: 生产运行中 | 14 MCP 工具 | 限时免费 | moltable.ai 上线  
> **当前增长基准**: 审计得分 18/100（Umami + GitHub Public + Onboarding Guide）  
> **文档版本**: v1.0 | 2026-08-01

---

## 目录

1. [竞品增长案例研究](#1-竞品增长案例研究)
2. [关键洞察提炼](#2-关键洞察提炼)
3. [Moltable 增长策略](#3-moltable-增长策略)
4. [北极星指标 & AARRR 漏斗](#4-北极星指标--aarrr-漏斗)
5. [量化增长目标（30/60/90天）](#5-量化增长目标306090天)
6. [执行路线图](#6-执行路线图)

---

## 1. 竞品增长案例研究

### 1.1 mem0 — "Universal Memory Layer for AI Agents"

**最接近 Moltable 的竞品**。同为 MCP-native AI Agent 中间件，同有 OSS + Pro 分层。

| 维度 | 数据 |
|------|------|
| GitHub Stars | **62.3k**（~2 年） |
| Forks | 7.3k |
| Commits | 2,540 |
| 开放 Issues/PRs | 231 / 508 |
| 定价 | Free OSS → Pro $249/月 → Enterprise |
| SDK | Python + TypeScript（双语言） |
| Agent 插件 | Claude, Cursor, Codex, OpenCode, n8n |

**增长引擎**:

1. **开源即渠道** — GitHub 是核心获客来源。每个 Star 背后都是一个潜在用户。双语言 SDK（Python + TypeScript）覆盖了两个最大的 AI Agent 开发生态。
2. **Agent 插件生态** — 为 Claude Code、Cursor、Codex 等主流 AI 编码工具提供一键安装插件，每个插件都是分发渠道。
3. **docs.mem0.ai** — 独立文档站（Mintlify 驱动），SEO 友好，内容持续更新（2,540 commits）。
4. **MCP 协议卡位** — 早早接入 MCP 标准，Agent 生态自然增长时自动受益。
5. **YC 背书** — Y Combinator 带来的初始曝光和投资人网络。

**可复用的策略**:
- ✅ Agent 插件作为分发渠道（Moltable 已有 Hermes Skill）
- ✅ 双语言 SDK 覆盖更大生态
- ❌ Pro $249 定价不适合中国市场

---

### 1.2 Linear — "Issue Tracking is Dead"

**开发者工具 PLG 的教科书案例**。从 0 做到 $100M+ ARR，未在营销上花一分钱。

| 维度 | 数据 |
|------|------|
| 估值 | $1.8B（2024 Accel 领投） |
| ARR | ~$100M+（2025 估算） |
| 团队规模 | ~100 人 |
| 用户获取 | 100% word of mouth + content |

**增长引擎**:

1. **极度优秀的产品设计** — Linear 的产品本身就是最好的营销。设计师和工程师用了后会自发推荐。
2. **"Now" changelog** — `linear.app/now` 是一个持续更新的产品博客，内容包括:
   - Product launches（产品发布）
   - From the team（团队工程/设计深度文章）
   - Customer stories（Ramp、Coinbase、Cursor、Cars24 等知名客户案例）
   - Changelog（每周更新）
3. **客户故事即社会证明** — 每个客户故事都是高质量内容 + 品牌背书。"Coinbase's bet on agent-first development" 这类文章自带传播力。
4. **工程/设计思想领导力** — Karri Saarinen 的 "Output isn't design"、"Issue tracking is dead" 等文章在开发者圈广泛传播。
5. **邀请制起步** — 早期通过邀请制制造稀缺感，每个受邀用户变成传播节点。

**可复用的策略**:
- ✅ Changelog + 产品博客作为持续内容引擎
- ✅ 客户故事（特别是 AI Agent 场景的故事）作为社会证明
- ❌ 不能依赖纯 word of mouth（Moltable 市场阶段更早）

---

### 1.3 Vercel — "Frontend Cloud"

**开源框架 → 云平台的经典路径**。Next.js 是获客漏斗，Vercel 是变现层。

| 维度 | 数据 |
|------|------|
| 估值 | $3.25B（2024） |
| ARR | ~$200M+（2025 估算） |
| Next.js 下载 | 600 万+/周（npm） |
| 客户 | Shopify, Speechify, Sandstone (40x growth in 147 days) |

**增长引擎**:

1. **OSS 作为获客漏斗** — Next.js 免费开源，但部署最简单的方式是 Vercel。自然转化路径: 用 Next.js → 部署到 Vercel → 付费。
2. **Vercel Ship 年度大会** — 类似 Apple WWDC 的开发者大会，发布重大产品更新，制造行业话题。
3. **客户成功故事** — "How Speechify serves 500,000 pages to 60 million users on Vercel" 等案例证明平台能力。
4. **Developer Advocacy 团队** — 写教程、做视频、在会议上演讲，持续教育开发者。
5. **收购策略** — 收购 Better Auth 等工具，补全生态。
6. **v0.dev** — AI 生成前端 UI，免费试用 → 引导到 Vercel 部署。

**可复用的策略**:
- ✅ OSS/免费工具作为获客漏斗（Moltable 已有免费 12 工具 + 开源）
- ✅ 年度发布事件（Launch Week 模式更适合早期产品）
- ✅ Developer Advocacy 内容（教程、视频、会议演讲）

---

### 1.4 Raycast — "Your Shortcut to Everything"

**社区驱动增长的典范**。从 macOS 工具做到跨平台（macOS + Windows + iOS），融资 $45M+。

| 维度 | 数据 |
|------|------|
| 融资 | $15M Series A (2021) → $30M Series B (2024) |
| 社区 | Slack 社区 + GitHub + Twitter + Dribbble |
| 用户获取 | 产品设计 > 社区口碑 > 内容营销 |
| 变现 | Pro $8/月（AI + Cloud Sync） |

**增长引擎**:

1. **"Be obsessed with feedback, not metrics"** — 早期不依赖数据面板，而是逐条读用户反馈。社区 Slack 是产品迭代的核心驱动力。
2. **Launch Week** — 一周内每天发布一个重大功能，制造连续的话题和传播。
3. **Affiliate Program** — 30% 佣金分成，激励社区成员推广 Pro。
4. **Extension Store** — 社区贡献的 1000+ 扩展，每个扩展都是留存钩子。
5. **质量即增长** — "No code reviews by default" 的工程文化让团队极快迭代，产品体验极致。
6. **Ambassador 计划** — 社区大使帮助推广和本地化。

**可复用的策略**:
- ✅ Launch Week 模式（Moltable 早期适合）
- ✅ Affiliate/Ambassador 计划
- ✅ 社区反馈驱动迭代（Slack/Discord + GitHub Discussions）
- ✅ 高质量内容工程博客

---

### 1.5 Notion — "Your Wiki, Docs & Projects"

**PLG 教科书**。从 0 做到 1 亿用户，$10B 估值。

| 维度 | 数据 |
|------|------|
| 估值 | $10B（2021） |
| 用户 | 1 亿+ |
| ARR | $300M+（2024 估算） |
| 中国用户 | 大量自发用户，无官方中文版 |

**增长引擎**:

1. **模板即获客** — Notion Template Gallery 是巨大的 SEO + 获客引擎。用户搜索"项目管理模板"→ 进入 Notion 模板页 → 注册。
2. **社区 Ambassador 计划** — Notion Certified 认证，社区大使组织 Notion Meetup 全球活动。
3. **UGC SEO** — 用户在 Reddit、Twitter、YouTube 自发创建内容，形成长尾搜索流量。
4. **Freemium 诱饵** — 免费版足够有用，但协作/存储限制自然推动升级。
5. **病毒循环** — 分享 Notion 页面给他人 → 接收者需要 Notion 查看 → 注册。

**可复用的策略**:
- ✅ 模板/Template 作为获客钩子（Persona 模板、Project 模板）
- ✅ Freemium 诱饵模型（Moltable 已有: 100 条记忆 → 2-3 天打满 → Pro 升级）
- ✅ 病毒循环设计（分享 Persona、分享环境配置）

---

## 2. 关键洞察提炼

### 2.1 五家公司增长的共性模式

| 模式 | mem0 | Linear | Vercel | Raycast | Notion | Moltable 适用性 |
|------|-------|--------|--------|---------|--------|-----------------|
| **开源/免费工具获客** | ✅ GitHub | ❌ 闭源 | ✅ Next.js | ❌ 闭源 | ❌ 闭源 | ✅ 已有 |
| **开发者内容营销** | ✅ Docs | ✅ Blog | ✅ Blog+教程 | ✅ Blog | ✅ 模板 | ✅ 博客已建 |
| **社区驱动** | ✅ GitHub | ❌ | ✅ GitHub | ✅ Slack | ✅ Reddit | 🔧 待建 |
| **Launch Week/事件** | ❌ | ❌ | ✅ Ship | ✅ Launch Wk | ❌ | 🔧 待做 |
| **客户故事/社会证明** | ❌ | ✅ 强 | ✅ 强 | ❌ | ✅ 强 | 🔧 待收集 |
| **Affiliate/Ambassador** | ❌ | ❌ | ❌ | ✅ 30% | ✅ | 🔧 待建 |
| **病毒循环** | ✅ 插件 | ❌ | ✅ 部署 | ✅ 扩展 | ✅ 分享 | 🔧 待建 |

### 2.2 针对 Moltable 的核心启示

1. **mem0 模式最接近** — MCP-native + Agent 记忆层，Moltable 应学习其开源+插件生态策略，但走差异化（Identity ≠ Memory，你的资产是你的身份，而不是你的聊天记录）。
2. **开发者内容 > 任何广告** — 五家公司没有一家在传统广告上花钱。内容（博客、教程、深度文章、客户故事）是唯一有效渠道。
3. **社区是护城河** — Raycast 的 1000+ 扩展、mem0 的插件生态、Notion 的模板——这些都不是公司自己做的，是社区做的。
4. **品质是最好的增长** — Linear 和 Raycast 的极致产品体验让用户成为自发传播者。Moltable 的产品品质已接近这个标准。
5. **早期要在 1-2 个渠道做到极致** — 不是「在所有渠道出现」，而是「在一个渠道成为标杆」。

---

## 3. Moltable 增长策略

### 3.1 核心增长渠道（前 3 优先级）

#### 🥇 优先级 1: GitHub 开源生态

**为什么**: mem0 用这个策略做到 62k Stars。Moltable 已有完整开源代码，只需释放。

**具体动作**:

| 动作 | 目标 | 时间 |
|------|------|------|
| GitHub Repo 公开 | Star 积累的起点 | Day 1 |
| Awesome List 收录申请 | 被动发现流量 | Week 1 |
| `README.md` 杀手级首屏 | 5 秒内理解产品价值 | Day 1 |
| CONTRIBUTING.md + 标签 `good first issue` | 社区贡献入口 | Week 2 |
| GitHub Discussions 开启 | 社区问答 + SEO | Week 1 |
| Star History 图表嵌入 README | 社会证明（增长动量） | 持续 |
| Release Notes 规范 | 每次发布都有传播素材 | 持续 |

**README 关键要素**:
```
# Moltable — AI Identity Sync
[![Stars](https://img.shields.io/github/stars/moltable/moltable)](...)
[![MCP](https://img.shields.io/badge/MCP-Compatible-blue)](...)

> "iCloud for AI Agents." 一次注册，所有 AI Agent 自动同步身份、偏好和配置。
> 换电脑 3 分钟恢复完整 AI 环境。不是记忆引擎——而是 Agent 的 iCloud + DNS。

## 5 秒 demo
curl -sL moltable.ai/setup.py | python3 -

## 为什么选 Moltable 而不是 mem0?
| | Moltable | mem0 |
|---|---|---|
| 定位 | Identity 同步 | Memory 存储 |
| 安装 | 一条命令 | pip install |
| MCP 工具 | 14 个 | 4 个 |
| Pro 价格 | ¥19/月 | $249/月 |
```

**目标**: 30 天 200 Stars → 60 天 500 Stars → 90 天 1,000 Stars

---

#### 🥈 优先级 2: 开发者内容营销

**为什么**: Linear、Vercel、Raycast 的博客是它们最大的有机流量来源。开发者通过搜索找解决方案 → 发现产品。

**内容矩阵**:

| 内容类型 | 频率 | 平台 | 目标 |
|----------|------|------|------|
| 技术深度文章 | 2 篇/周 | moltable.ai/blog | 长尾 SEO + 思想领导力 |
| 教程/GitHub Gist | 1 篇/周 | GitHub Gist + 博客 | 实操传播 |
| MCP 协议解读 | 1 篇/月 | 博客 + Medium | 行业卡位 |
| Changelog | 持续 | linear.app/now 模式 | 产品透明度 |

**前 10 篇博客标题（精确到关键词）**:

1. "MCP 协议：为什么它是 AI 的 USB-C"（已有）
2. "AI 身份层的设计哲学：从 Memory 到 Identity"（已有）
3. "跨平台 Persona 管理：一个身份，多种人格"（已有）
4. **"为什么你的 AI Agent 每次都忘记你是谁——以及如何修好它"** ← AI forgetfulness 是最大痛点
5. **"iCloud for AI Agents：换电脑后 3 分钟恢复完整 AI 环境"** ← 类比营销
6. **"Agent 失忆症：AI 为什么不记得你的偏好（以及 Moltable 如何解决）"**
7. **"MCP 工具开发指南：从 0 到 12 个工具的完整过程"**
8. **"AI Agent 的 Identity Stack：身份 > 记忆 > 知识"**
9. **"用 MCP 协议 3 行代码接入全平台 AI Agent"**
10. **"对比评测：mem0 vs Moltable — AI 记忆还是 AI 身份？"**

**SEO 关键词策略**:
- 核心词: `AI identity sync`, `MCP server`, `AI agent memory`, `AI persona management`
- 长尾词: `how to make AI remember me`, `sync AI preferences across devices`
- 竞品词: `mem0 alternative`, `open source AI memory`, `free MCP tools`

**分发策略**:
- Hacker News: 每篇深度文章都提交
- Reddit: r/LocalLLaMA, r/ClaudeAI, r/MCP
- Twitter/X: @moltable_ai 账号
- 中文: 即刻、V2EX、知乎

---

#### 🥉 优先级 3: MCP 生态插件/集成

**为什么**: mem0 的 Claude/Cursor/Codex 插件是它增长最快的渠道。AI Agent 生态自带增长飞轮。

**具体动作**:

| 集成 | 形式 | 优先级 |
|------|------|--------|
| Hermes Skill（已完成） | SKILL.md + MCP config | P0 ✅ |
| Claude Code Plugin | `.claude-plugin/` 目录 | P0 |
| Cursor Plugin | `.cursor-plugin/` 目录 | P0 |
| OpenCode Plugin | `.opencode-plugin/` 目录 | P1 |
| ChatGPT MCP 接入教程 | Docs + Blog | P1 |
| Windsurf/Cline 等 | README 引导用户贡献 | P2 |
| n8n 社区节点 | 自动化工作流集成 | P2 |

**插件标准化**（参考 mem0 做法）:
```
moltable/
├── .claude-plugin/     # Claude Code 一键安装
├── .cursor-plugin/      # Cursor 一键安装
├── .opencode-plugin/    # OpenCode 一键安装
├── skills/              # Hermes Skill 定义
└── integrations/        # 其他集成
```

**目标**: 60 天覆盖 5 个主流 AI Agent 平台，90 天覆盖 10 个。

---

### 3.2 辅助增长渠道

| 渠道 | 说明 | 优先级 |
|------|------|--------|
| **Affiliate 计划** | 参考 Raycast 30% 佣金，月付 ¥19 分 30% | P1 |
| **Launch Week** | 5 天连续发布，每天一个大功能 | P1 |
| **Ambassador 计划** | 中文 AI 社区大使，组织 Workshop | P2 |
| **Persona 模板市场** | 预置 Persona 模板（参考 Notion 模板） | P2 |
| **客户故事** | 早期用户案例采访（参考 Linear/Vercel） | P2 |
| **YouTube 教程** | MCP + Moltable 实操视频 | P3 |

---

## 4. 北极星指标 & AARRR 漏斗

### 4.1 北极星指标

**定义**: **7 天内通过 MCP 协议调用 Moltable 的活跃 Agent 数**

**为什么不是注册用户数？**  
Moltable 是基础设施层。注册但不用 = 挂名用户，对业务无意义。真正的价值是：有多少 AI Agent 真正通过 MCP 调用了 Moltable。

**为什么是 7 天？**  
Agent 调用频率低于普通 SaaS。一个用户可能每天都用 AI，但 Agent 不一定每天都调用 Moltable。7 天窗口足够捕捉使用模式。

**测量方式**:
```sql
SELECT COUNT(DISTINCT user_id) 
FROM mcp_access_log 
WHERE timestamp > NOW() - INTERVAL '7 days'
```

### 4.2 AARRR 漏斗

| 阶段 | 指标 | 当前基线 | 30天目标 | 60天目标 | 90天目标 | 关键动作 |
|------|------|---------|---------|---------|---------|---------|
| **Acquisition** | 网站 UV/月 | ~50 | 500 | 1,500 | 3,000 | GitHub + Blog + HN |
| **Acquisition** | 注册用户总数 | ~10 | 100 | 300 | 600 | setup.py 一键注册 |
| **Activation** | 注册后 48h 内完成首次 MCP 调用 | ~50%* | 70% | 75% | 80% | 优化 onboarding |
| **Activation** | 连接 2+ 个 Agent 平台的用户比例 | 0% | 15% | 25% | 35% | 多平台插件 |
| **Retention** | 7 天活跃 Agent (WAA) | ~5 | 30 | 80 | 160 | Persona + Memory 钩子 |
| **Retention** | 30 天留存率 | N/A | 40% | 45% | 50% | 自动记忆保存 |
| **Revenue** | Pro 付费用户 | 0（限免） | — | 30 | 60 | 限免到期转化 |
| **Revenue** | MRR | ¥0 | — | ¥570 | ¥1,140 | Pro ¥19/月 |
| **Referral** | 推荐注册占比 | 0% | 10% | 15% | 20% | Affiliate 计划 |

*\*当前 48h 激活率为估算值，需 Umami 埋点验证。*

### 4.3 AARRR 每阶段关键动作

#### Acquisition（获客）

```
优先级 1: GitHub 自然流量
  └─ Star 增长 → GitHub Trending → 更多人 Star → 注册
  └─ Awesome List 收录 → 持续被动流量

优先级 2: 搜索引擎优化（SEO）
  └─ 博客长尾关键词 → Google/Bing 排名
  └─ Docs 文档 SEO → 开发者搜索"MCP tools"时发现

优先级 3: 社交媒体分发
  └─ HN / Reddit / V2EX / 即刻
  └─ Twitter/X 开发者圈
```

**具体动作**:
1. 提交到 GitHub Trending（Star 增长速度要快）
2. 申请 awesome-mcp、awesome-ai-agents 等 List 收录
3. 每篇博客同步发到 Medium、Dev.to（cross-post，加 canonical URL）
4. Product Hunt 上线（准备好视频 Demo）
5. Hacker News "Show HN" 帖子

---

#### Activation（激活）

```
定义: 注册后 48h 内完成首次 MCP tools/call 调用
目标: 70% → 80%
```

**当前激活路径的摩擦点**:
1. 用户注册后不知道下一步做什么
2. setup.py 虽然好但不够明显
3. `/connect` 页面的平台选择不够直观

**优化动作**:
1. **注册后即时引导** — 注册成功 → 弹窗/跳转到 `/connect` 页，而非 `/dashboard`
2. **5 秒 Wow Moment** — setup.py 改名为 `curl moltable.ai/go | python3 -`，跑完后自动展示 14 个工具列表
3. **MCP 连接成功反馈** — Agent 首次调用 auto_provision 后，返回欢迎内容 + 个性化建议
4. **激活邮件序列**:
   - Day 0: "欢迎！点击这里 3 分钟接入"（含平台特定教程）
   - Day 1: "你已经注册但还没接入——需要帮助吗？"
   - Day 3: "试试这个 Persona 模板，让你的 AI 更有用"

---

#### Retention（留存）

```
定义: 7 天内至少有一次 MCP 调用的用户
目标: WAA 从 5 → 160（90天）
```

**留存钩子设计**:

1. **记忆自动保存** — Agent 每次对话结束时自动调用 `save_memory`，用户回来看时记忆已累积（参考 mem0 的 agent memory）
2. **Persona 使用频率** — 每次切换 Persona，AI 表现不同 → 用户感知到价值 → 持续使用
3. **跨平台一致性** — 在 Claude 设置的偏好，Hermes 自动同步 → "哇，它真的记住了"的体验
4. **使用摘要邮件** — 周报: "本周你的 AI 记住了 12 条新偏好，在 3 个平台上使用"
5. **Pro Memory Cache** — 免费 100 条 2-3 天打满 → 触发 Pro 升级 → 解锁 10K 记忆，留存自然提升

---

#### Revenue（收入）

```
当前: 限时免费（Stripe 未开通）
目标: 限免到期后 MRR ¥1,140（60 个 Pro 用户 × ¥19/月）
```

**转化策略**:

1. **Bait Pricing** — 100 条记忆免费，2-3 天打满。Pro 10K 记忆 + 语义搜索。80% 激活用户在 7 天内触发配额预警。
2. **限免后转化** — 限免用户到期前 7 天邮件通知：¥19/月继续，否则记忆降级为 100 条。
3. **季付优惠** — ¥16/月（季付 ¥48），降低决策门槛。
4. **不推年付** — 中国用户"你先活过 6 个月"心态。先做月付/季付。

---

#### Referral（推荐）

```
目标: 推荐注册占 15-20%
```

1. **Affiliate 计划**（参考 Raycast）:
   - 30% 佣金（¥5.7/月/用户）
   - Dashboard 内生成专属链接
   - 前 10 个推荐用户永久 30% 分成

2. **病毒循环**:
   - 分享 Persona 配置链接 → 接收者点击 → 注册 Moltable → 导入 Persona
   - "我的 AI 配置" 一键分享功能

3. **Ambassador 计划**:
   - 招募 10 位中文 AI 社区大使
   - 提供专属福利 + 早期功能内测

---

## 5. 量化增长目标（30/60/90天）

### 5.1 30 天目标（Day 1-30）

| 指标 | 目标 | 当前 |
|------|------|------|
| GitHub Stars | 200 | ~0（私有） |
| 网站 UV | 500/月 | ~50/月 |
| 注册用户 | 100 | ~10 |
| 7 天活跃 Agent (WAA) | 30 | ~5 |
| 48h 激活率 | 70% | ~50%* |
| 博客文章 | 8 篇 | 3 篇 |
| MCP 平台集成 | 3 个（Hermes + Claude + Cursor） | 1 个 |
| HN/Reddit 帖子 | 3 次 | 0 |

**本月关键里程碑**:
- Week 1: GitHub 公开 + Product Hunt 上线
- Week 2: HN "Show HN" 帖子 + 前 2 篇博客
- Week 3: Claude + Cursor 插件上线
- Week 4: 第一个 Launch Week 预告

---

### 5.2 60 天目标（Day 31-60）

| 指标 | 目标 |
|------|------|
| GitHub Stars | 500 |
| 网站 UV | 1,500/月 |
| 注册用户 | 300 |
| 7 天活跃 Agent (WAA) | 80 |
| 48h 激活率 | 75% |
| 30 天留存率 | 40% |
| Pro 付费用户 | 30 |
| MRR | ¥570 |
| 博客文章累计 | 16 篇 |
| MCP 平台集成 | 5 个（+ OpenCode + ChatGPT） |

**本月关键里程碑**:
- Launch Week: 5 天连续发布
- 第一个 Affiliate 用户转化
- 第一个客户故事发布
- Persona 模板市场上线（5+ 模板）

---

### 5.3 90 天目标（Day 61-90）

| 指标 | 目标 |
|------|------|
| GitHub Stars | 1,000 |
| 网站 UV | 3,000/月 |
| 注册用户 | 600 |
| 7 天活跃 Agent (WAA) | 160 |
| 48h 激活率 | 80% |
| 30 天留存率 | 50% |
| Pro 付费用户 | 60 |
| MRR | ¥1,140 |
| 博客文章累计 | 24 篇 |
| MCP 平台集成 | 10 个 |
| Ambassador 大使 | 10 人 |
| 推荐注册占比 | 20% |

**本月关键里程碑**:
- 第二次 Launch Week
- Ambassador 社区首次线下 Meetup
- SEO 关键词排名前 3: "MCP server"、"AI identity sync"
- 首次外部媒体报道

---

## 6. 执行路线图

### 6.1 Week-by-Week 行动清单

#### Week 1: 释放基础

| 天 | 行动 | 负责人 | 产出 |
|----|------|--------|------|
| Day 1 | GitHub Repo 公开 | 技术 | Public repo + README 杀手级首屏 |
| Day 2 | 安装 Umami analytics + 埋点 | 技术 | 准确流量/注册/激活数据 |
| Day 3 | Product Hunt 准备（文案+截图+Demo 视频）| 产品 | PH 上线材料 |
| Day 4 | 提交 Awesome List PRs | 任何人 | awesome-mcp, awesome-ai-agents 等 |
| Day 5 | 撰写 HN "Show HN" 帖子 | 产品 | 标题 + 第一段 + 为什么做 |
| Day 6 | setup.py 优化（缩短路径，加首次体验）| 技术 | `curl moltable.ai/go` 管道 |
| Day 7 | 激活邮件序列 3 封 | 产品 | Day 0/1/3 邮件 |

#### Week 2: 内容引擎启动

| 天 | 行动 | 产出 |
|----|------|------|
| Day 8 | 博客: "为什么你的 AI 每次都不记得你是谁" | 核心痛点文章 |
| Day 10 | HN Show HN 发帖 | 首次 Reddit/HN 曝光 |
| Day 12 | 博客: "iCloud for AI Agents" | 类比营销文章 |
| Day 14 | Claude Code Plugin 上线 | `.claude-plugin/` 目录 + 文档 |

#### Week 3: 社区建设

| 天 | 行动 | 产出 |
|----|------|------|
| Day 15 | 开启 GitHub Discussions | Q&A + Feature Request + Showcase |
| Day 17 | Cursor Plugin 上线 | `.cursor-plugin/` 目录 + 文档 |
| Day 19 | 博客: "mem0 vs Moltable 对比" | 竞品对比文章 |

#### Week 4: Launch Week 预告

| 天 | 行动 | 产出 |
|----|------|------|
| Day 22 | Launch Week 内容准备 | 5 天发布计划 + 素材 |
| Day 25 | 博客: MCP 工具开发指南 | 实操教程 |
| Day 28 | Product Hunt 正式上线 | PH Launch |

---

### 6.2 Launch Week 执行计划

**参考 Raycast Launch Week 模式**: 5 天连续发布，每天一个大动作。

| 天 | 主题 | 发布内容 |
|----|------|---------|
| Day 1 | "开源" | GitHub Public + README 大改版 + Star History |
| Day 2 | "全平台" | Claude + Cursor + OpenCode + ChatGPT 4 个插件同时上线 |
| Day 3 | "模板" | Persona 模板市场上线（10 个预置 Persona）|
| Day 4 | "故事" | 第一个用户案例采访 + 视频 |
| Day 5 | "路标" | Roadmap 公开 + 社区投票下个功能 |

**宣传配合**:
- 每天 Twitter/X 发一条带截图/视频的发布推文
- 每天更新 Changelog
- HN / Reddit / V2EX / 即刻 分发

---

### 6.3 所需资源

| 资源 | 说明 | 状态 |
|------|------|------|
| Umami analytics | 网站分析（替代 GA）| 🔧 待安装 |
| GitHub Public | Repo 公开 | 🔧 待执行 |
| 邮件服务（Resend/SendGrid） | 激活邮件 + 周报 + 限免到期通知 | 🔧 待集成 |
| Twitter/X 账号 | 社交媒体分发 | 🔧 待创建 |
| Discord/Slack 社区 | 用户社区 | 🔧 待创建 |
| Product Hunt 账号 | PH 上线 | 🔧 待准备 |
| Canva/Figma 模板 | 社交媒体图片素材 | 🔧 待准备 |

---

## 附录

### A. 指标体系参考

```
增长飞轮:
  GitHub Stars ↑ → 自然流量 ↑ → 注册 ↑ → MCP 调用 ↑
  → 留存 ↑ → 推荐 ↑ → GitHub Stars ↑ (循环)
```

### B. 竞争对手监控

| 竞品 | Stars | MCP 工具数 | 定价 |
|------|-------|-----------|------|
| mem0 | 62.3k | 4 | $249/mo Pro |
| Cognee | 29.6k | N/A | 开源 |
| Zep | N/A | N/A | $125-375/mo |
| Letta | N/A | N/A | $20/mo |
| **Moltable** | **0 → 1,000** | **14** | **¥19/mo** |

**Moltable 差异化**: 最多的 MCP 工具、最低的价格、Identity（非 Memory）的独特定位。

### C. 数据驱动决策原则

1. **每个动作必须有可测量指标** — 不发没有追踪链接的帖子
2. **每周 Review 北极星指标** — WAA 是唯一最重要的数字
3. **A/B 测试关键页面** — Landing Page CTA、Onboarding 流程
4. **失败快速放弃** — 如果一个渠道 30 天没有带来注册，停止投入
5. **成功加倍下注** — 如果一个渠道带来 10+ 注册，立即加倍资源

---

> **最后的话**: 增长不是一个部门，是一种文化。Moltable 的增长引擎不是某个营销人员的任务，而是产品、工程、内容的合力。mem0 没有市场部却 62k Stars，因为它的产品本身就是最好的增长。Moltable 的 14 个 MCP 工具、¥19 的定价、Identity 的独特定位——这些就是增长的种子。我们的工作是把它们放到合适的地方，浇水，然后等它们发芽。
>
> "Be obsessed with feedback, not metrics." — Raycast
