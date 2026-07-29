# 🦀 ClawHunt（爪寻）深度调研报告

> 调研日期：2026-06-17 | 项目阶段：早期（黑客松筹备期）

---

## 一、项目概况

| 维度 | 详情 |
|------|------|
| **项目名称** | ClawHunt / 爪寻 |
| **标语** | "让每个 Builder 被看见" / "Product Hunt for AI Agents" |
| **定位** | AI Agent 赏金市场 + 工具评价平台 + 开发者社区 |
| **主站** | [clawhunt.store](https://clawhunt.store) |
| **国际站** | [clawhunt.com](https://clawhunt.com) — Product Hunt for AI Agents |
| **中文站** | [clawhunt.site](https://clawhunt.site) — AI Creator Accelerator |
| **模型广场** | [gate.clawhunt.site](https://gate.clawhunt.site) — "一个 Key，用所有模型" |
| **GitHub** | [team-to-be-found/Clawhunt-profile](https://github.com/team-to-be-found/Clawhunt-profile) |
| **公众号** | 微信搜一搜「爪寻Clawhunt」 |
| **许可证** | MIT |
| **创建时间** | 2026-06-16（仅1天前！） |
| **团队** | team-to-be-found（GitHub Organization） |

---

## 二、产品矩阵（4个站点）

### 2.1 clawhunt.store — 主站（赏金市场）

**核心功能**：甲方发布悬赏 → AI Agent 自动竞标 → 完成任务 → 收款。

```
注册 → 发布需求/接单/上架Agent与作品
```

- **赏金市场**：甲方发布任务，Agent 竞标执行
- **公共舞台**：Builder 展示作品的公开广场
- **开发者社区**：飞书群 + 微信群 3个

### 2.2 clawhunt.com — 国际站（工具评价平台）

定位为 **"AI Agent 版的 Product Hunt"** — Agent 对工具进行真实评价，提供性能数据。

**当前数据（2026-06-17）**：
| 指标 | 数值 |
|------|------|
| 已评价工具 | 134 |
| 活跃 Agent | 47 |
| 性能评价 | 892 |
| Agent 需求 | 63 |

**工具卡片展示**：
- ⭐ 评分（如 8.5、9.2）
- ⏱ 响应时间（如 245ms、180ms）
- 💰 每次调用成本（如 $0.002、$0.050）
- 👥 使用该工具的 Agent 数量
- 📝 Agent 评价语录

**分类体系**：
| 分类 | 工具数 | 平均评分 |
|------|--------|----------|
| 🤖 AI | 23 | 8.2⭐ |
| 💳 Payments | 15 | 9.1⭐ |
| 🔐 Auth | 18 | 8.9⭐ |
| 📊 Analytics | 19 | 7.9⭐ |
| 💾 Storage | 14 | 8.4⭐ |
| 📧 Email | 12 | 8.7⭐ |
| 🔔 Messaging | 8 | 8.1⭐ |
| 🎯 Other | 25 | 7.6⭐ |

### 2.3 clawhunt.site — AI Creator Accelerator

"Multilingual AI creator accelerator for product discovery, evidence packs, community missions and VC matching."

- **产品发现**（Product Discovery）
- **证据包**（Evidence Packs）
- **社区任务**（Community Missions）
- **VC 匹配**（VC Matching）

这是一个面向 AI 创作者的加速器平台，提供从产品发现到融资对接的全链路支持。

### 2.4 gate.clawhunt.site — LLMgate 模型广场

"一个 Key，用所有模型" — 统一的模型 API 网关，让开发者用一个 API Key 访问所有主流 LLM。

---

## 三、商业模式分析

### 3.1 当前阶段：社区驱动 + 黑客松获客

ClawHunt 目前处于 **极早期验证阶段**，以黑客松作为冷启动引擎：

**ClawHunt Builder Camp 2026（深圳 7/3-7/5）**：
| 项目 | 详情 |
|------|------|
| 时间 | 2026.07.03 – 07.05 |
| 地点 | 深圳 · 星河先锋科技展厅 |
| 规模 | 限额 100 人，5 大赛区 |
| 奖金池 | ¥20,000 |
| 一等奖 | ¥10,000 ×1 |
| 二等奖 | ¥3,000 ×2 |
| 三等奖 | ¥1,000 ×3 |
| 人气奖 | ¥1,000 |

**三天日程**：
- **D1** — 嘉宾分享 · 闪电组队 · 命题发布（18:30）
- **D2** — Workshop · Build Sprint · Demo 彩排
- **D3** — 赛区预选 → 12 强 Demo Day → 投资机构+嘉宾 Review → 颁奖

**命题方向**（48H 跑出能用的 Demo）：
- **A · 让 Agent 干活** — 自动化/效率工具
- **B · 把 AI 玩出花** — 创意/内容/体验
- **C · 做成一门生意** — 商业/行业落地

**硬性要求**：能现场运行的 Demo，不接受纯 PPT。

### 3.2 潜在收入模型

| 收入流 | 模式 | 成熟度 |
|--------|------|--------|
| **赏金抽成** | 平台从悬赏金额中抽佣（如 10-20%） | ⏳ 待验证 |
| **LLMgate API** | 模型网关按调用量收费 | ⏳ 待上线 |
| **Pro 订阅** | Agent 高级功能（优先展示、数据导出） | ⏳ 待开发 |
| **VC 匹配** | 加速器项目成功后的 carry/佣金 | ⏳ 远期 |
| **工具推广** | 工具方付费获得推荐位 | ⏳ 远期 |

### 3.3 商业画布速览

| 维度 | 内容 |
|------|------|
| **客户细分** | ① AI Agent 开发者 ② 有自动化需求的企业 ③ 工具/SaaS 提供商 |
| **价值主张** | Agent 能找到活干；企业能找到能干活的 Agent；工具能被 Agent 真实评价 |
| **渠道** | 网站 + 公众号 + 飞书群/微信群 + 黑客松 |
| **关键资源** | Agent 社区、工具评价数据、赏金交易流 |
| **成本结构** | 服务器 + 黑客松奖金 ¥20,000 + 运营人力 |

---

## 四、产品核心机制

### 4.1 赏金市场三边网络

```
        发布悬赏
  企业 ──────────→ 平台
                    │
              匹配/竞标
                    │
                  Agent ──→ 执行 → 收款
                    
  工具/SaaS ──→ 被Agent评价 → 获得真实性能数据
```

### 4.2 Agent Needs（需求广场）

Agent 可以发布自己需要的 API/工具，附带明确规格：

```
例：
📊 Real-time event tracking API
   - 最大成本：$0.001/次调用
   - 最低可用性：99.9%
   - 所需功能：custom_dimensions, real_time, webhooks
   - 规模：100万事件/月
```

对工具开发者来说，这是**最精准的 PMF 信号**。

### 4.3 AI-First 设计

- **Agent 可自主注册、竞标、评价** — 不依赖于人类操作
- **SuperClaw 内置 Agent** — 平台原生 AI（与 ChatGPT 插件生态对标）
- **"Agent Arena" 竞技场** — Agent 之间可进行能力竞赛

---

## 五、竞品分析

### 5.1 直接竞品

| 项目 | 定位 | 状态 | 差异 |
|------|------|------|------|
| **Product Hunt** | 人类产品发现平台 | 成熟（被收购） | ClawHunt 是 Agent 版，增加赏金+性能数据 |
| **BountySource** | 开源赏金平台 | 中等 | 面向人类开发者，非 Agent |
| **Gitcoin** | Web3 赏金平台 | 成熟 | 区块链原生，非 AI 特化 |
| **Upwork/Fiverr** | 自由职业平台 | 成熟 | 面向人类，非 Agent 自动化 |

### 5.2 相邻竞品

| 项目 | 领域 | 关系 |
|------|------|------|
| **G2/Capterra** | SaaS 评价 | ClawHunt 是 Agent 视角的 G2 |
| **OpenRouter** | LLM 网关 | 与 gate.clawhunt.site 直接竞争 |
| **AgentOps** | Agent 可观测性 | 互补（Agent 用 ClawHunt 找工具，用 AgentOps 监控） |
| **Moltable** | Agent 身份系统 | 互补 — ClawHunt 是工作市场，Moltable 是身份层 |

### 5.3 核心护城河判断

| 壁垒 | 强度 | 说明 |
|------|------|------|
| **Agent 评价数据** | ⚠️ 中 | 数据网络效应，但初期数据少 |
| **赏金交易流** | ⚠️ 低 | 容易被 Upwork/Fiverr 等功能覆盖 |
| **社区** | ⚡ 中高 | 黑客松+社群是真正的差异化 |
| **多站点矩阵** | ⚠️ 低 | 4个站互相导流但功能重叠 |

**结论**：ClawHunt 目前的核心壁垒是 **"AI Agent 社区 + 黑客松 IP"**，产品护城河还需要时间沉淀。

---

## 六、与 Moltable 的关系

### 6.1 互补关系

```
Moltable（身份层）         ClawHunt（工作层）
    │                          │
    ├─ Identity                ├─ 赏金接单
    ├─ Persona                 ├─ 工具评价
    ├─ Agent 记忆              ├─ Agent Arena
    └─ auto_provision()        └─ Builder 展示
         │                          │
         └──────── 互补 ────────────┘
              Agent 身份 + Agent 收入
```

### 6.2 具体协作场景

1. **Agent 接单前**：通过 Moltable 查询甲方的历史偏好、决策风格
2. **Agent 接单后**：用 Moltable 记录项目上下文，下次续单不丢失
3. **Agent 评价工具**：Moltable 记录 "这个 Agent 用过哪些工具、评价如何"
4. **auto_provision**：Agent 首次接入 ClawHunt 时，一键获得 Moltable 上的画像

### 6.3 集成可行性

| 方案 | 难度 | 价值 |
|------|------|------|
| Moltable MCP Server → ClawHunt Agent 调用 | 低 | ⭐⭐⭐⭐ |
| ClawHunt 平台嵌入 Moltable Widget | 中 | ⭐⭐⭐⭐⭐ |
| OAuth 互通（Moltable 登录 ClawHunt） | 中 | ⭐⭐⭐ |

---

## 七、风险评估

### 7.1 项目风险

| 风险 | 等级 | 说明 |
|------|------|------|
| **阶段过早** | 🔴 高 | 成立仅1天，只有 GitHub Profile 页 + 网站 Demo |
| **产品未验证** | 🔴 高 | 网站数据为静态 Demo，无真实交易 |
| **三边冷启动** | 🟡 中 | 需要同时吸引 Agent、企业、工具方 |
| **AI Agent 生态不成熟** | 🟡 中 | 目前自主 Agent 极少，大多数是 Copilot 模式 |
| **团队未知** | 🟡 中 | team-to-be-found 组织信息有限 |

### 7.2 机会点

| 机会 | 价值 |
|------|------|
| **赛道先发** | "AI Agent 赏金市场"概念新，无明确竞品 |
| **黑客松 IP** | 如成功举办，可获得 100 名 Builder 种子用户 |
| **多站点联动** | 评价站→赏金站→模型站形成产品矩阵 |
| **中国团队** | 中国市场对 AI 热情高，微信社群获客成本低 |
| **MIT 开源** | 社区可参与共建 |

---

## 八、关键洞察

### 8.1 ClawHunt 的本质

ClawHunt 不是简单的 "AI 版 Upwork"。

它是一个 **三层网络**：
1. **工作层**：赏金市场（Agent 赚钱）
2. **数据层**：工具评价（Agent 选工具）
3. **社区层**：Builder Camp（人连接人）

三层互为增强——Agent 接单越多，评价越多；评价越多，工具发现越好；社区越大，赏金越多。

### 8.2 最大的变量：AI Agent 何时真正自主

目前 99% 的 "AI Agent" 其实是被人类驱动的 Copilot。ClawHunt 的赏金市场假设的是**Agent 可以自主接单、议价、完成、收款**——这在 2026 年 Q3 来看仍然是超前假设。

但超前未必是错。Product Hunt 诞生时，"产品发布"也不是主流行为。

### 8.3 与 Moltable 的战略协同

ClawHunt 解决的是 **"Agent 去哪里找活干"**。
Moltable 解决的是 **"Agent 如何记住你是谁"**。

从 Agent 视角看，两个产品解决了同一件事的两个面：
- **对外**（ClawHunt）：发现机会、建立声誉、获得收入
- **对内**（Moltable）：记忆用户、维护身份、沉淀知识

如果 Moltable 的 MCP Server 能被 ClawHunt 上的 Agent 调用，那就是 **"Agent 带着记忆去上班"** 的完整闭环。

---

## 九、建议

### 对 Moltable 项目

| 优先级 | 行动 | 理由 |
|--------|------|------|
| P0 | 继续独立开发 Moltable MVP | 两个产品互补但不重叠 |
| P1 | 关注 ClawHunt 黑客松成果 | 7/3-5 后评估其真实社区质量 |
| P2 | 设计 Moltable MCP Server → ClawHunt 集成方案 | 先发制人建立生态位 |
| P3 | 考虑参加下一届 Builder Camp | 让 Moltable 出现在 Agent 社区 |

### 对 ClawHunt 的观察

1. **如果黑客松成功**（100人实到、产出≥20个Demo）→ 值得深入关注
2. **如果黑客松冷清**（<50人、Demo质量差）→ 可能只是概念炒作
3. **关键指标**：7/5 之后，平台是否出现真实的赏金交易

---

## 附录：信息来源

| 来源 | 内容 |
|------|------|
| clawhunt.com | 国际站首页（Next.js SSR），含工具卡片、分类、评价数据 |
| clawhunt.store | 主站（赏金市场） |
| clawhunt.site | AI Creator Accelerator |
| gate.clawhunt.site | LLMgate 模型广场 |
| GitHub: team-to-be-found/Clawhunt-profile | 开源品牌页面，含黑客松海报、微信群二维码 |
| GitHub API | 55个相关仓库，1个直接关联 |

---

*报告生成：2026-06-17 | 版本 v1.0*
