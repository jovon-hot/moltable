# Moltable 市场包装完整方案

> 生成日期：2026-08-01 | 版本：v1.0  
> 用途：官网文案、融资材料、渠道投放、社区宣发  
> 目标市场：中国 AI 开发者 / Agent 重度用户（一期），全球 SaaS（二期）

---

## 一、Slogan（中英文各 3 个候选）

### 中文 Slogan

| # | Slogan | 适用场景 | 推荐 |
|---|--------|---------|:--:|
| 1 | **你的 AI，永远认识你。** | 首页 Hero（情感共鸣） | ⭐ |
| 2 | **换电脑 3 分钟，AI 环境全回来。** | 功能页 / 广告（场景驱动） | ⭐ |
| 3 | **一个身份，所有 AI 共享。** | 技术社区 / 博客标题 | |

### English Slogan

| # | Slogan | Best Use |
|---|--------|----------|
| 1 | **Your AI, everywhere you are.** | Hero headline |
| 2 | **One identity. Every agent.** | Tech community / docs |
| 3 | **iCloud for your AI self.** | Elevator pitch / investor deck |

### 推荐组合（中英文双语文案）

> **中文主 slogan**：你的 AI，永远认识你。  
> **English subline**：One identity. Every agent.  
> **功能 tagline**：基于 Google A2A 协议 | 换电脑 3 分钟恢复完整 AI 环境

---

## 二、产品定位宣言

> **Moltable 是 AI Agent 的服务发现与身份同步层。基于 Google A2A 协议，让你的所有 AI 助手共享同一个身份、偏好、技能和记忆。换设备 3 分钟恢复完整 AI 环境，旧 Agent 注册后新 Agent 自动发现并协同工作。**

**50 字版本（官网 Hero 区）**：

> AI 的身份中枢。一个身份接入，所有 Agent 自动同步。换电脑 3 分钟恢复，旧 Agent 能力新 Agent 直接用。

---

## 三、核心卖点（3 个，每个带一句话解释）

### 卖点 1：3 分钟环境恢复

> **不是配置，是同步。** 身份、偏好规则、Persona 定义、Skills、MCP 服务器连接 — 换电脑后一条 `auto_provision` 命令全部恢复，无需手动迁移任何配置文件。比 Docker 快，比手动配置准。

*用户说的：你会在新电脑上先装什么？以后第一个装 Moltable。*

### 卖点 2：Agent 自动发现与协同

> **你的旧 Agent 不会退休。** 基于 Google A2A 协议，旧 Agent 注册后持续运行，新 Agent 自动发现并委托任务。你的 Hermes、Claude、Cursor — 它们不是孤岛，是团队。

*类比：不是"换 AI"，是"扩 AI 团队"。*

### 卖点 3：10,000 条跨 Agent 记忆

> **你在 Claude 里说的事，Hermes 也记得。** Pro 版 10K 条记忆跨平台同步 — 偏好、决策、知识点 — 任何接入的 AI 都能检索。搜"我上次对定价的结论是什么？"→ 秒回。比 mem0 便宜 10 倍，比 Zep 轻 100 倍。

*一句话：AI 越用越懂你，不因换平台而清零。*

---

## 四、目标用户画像（3 类）

### 画像 1："多 Agent 用户"（占比 ~50%，早期核心用户）

> 日常使用 2+ 个 AI 助手（Hermes + Claude Code + Cursor），频繁在不同项目/环境间切换，苦于"每个 AI 都要重新调教"。

**痛点**：每换一个 AI、每换一台电脑，都要重新自我介绍、重新配 MCP 工具、重新定义 Persona。  
**触点**：GitHub Trending、V2EX、即刻、Twitter AI 圈  
**转化语**："三个 AI 共用一个大脑。"

### 画像 2："独立开发者 / 技术 Leader"（占比 ~30%，Pro 付费主力）

> 管理多个项目（后端 + 前端 + 数据分析），每个项目有独立的数据库、知识库、工具链。需要环境配置可复用、可追溯、可共享。

**痛点**：项目环境配置散落在 `mcp.json`、`.env`、shell 脚本里，换电脑 = 重建半天。希望团队成员或未来的自己能一键继承。  
**触点**：Product Hunt、Hacker News / V2EX、掘金、少数派  
**转化语**："你的项目环境，一键继承给明天的自己。"

### 画像 3："AI 深度用户 / 早期 adopter"（占比 ~20%，口碑传播者）

> 已经在用 mem0 或其他记忆工具，追求最优工具组合。对 A2A 协议、Agent 协同有认知，愿意尝鲜并写文分享。

**痛点**：现有记忆工具贵（mem0 $249/月）或重（Zep 需自建），且各 Agent 之间的记忆和身份仍然割裂。  
**触点**：Twitter / X、GitHub Discussions、即刻、少数派  
**转化语**："10 倍便宜的 Agent 记忆层，还带身份同步。"

---

## 五、Landing Page 结构大纲

```
═══════════════════════════════════════════════
SECTION 1: HERO
═══════════════════════════════════════════════
  H1: 你的 AI，永远认识你。
  Sub: 基于 Google A2A 协议 · 换电脑 3 分钟恢复完整 AI 环境
  CTA: [免费开始] [查看演示]
  Visual: 一台 Mac → 3 分钟倒计时 → 三台设备同步完成的动画
  Social proof: "已有 xxx 开发者接入" + GitHub stars badge

═══════════════════════════════════════════════
SECTION 2: WHY MOLTABLE（场景痛点）
═══════════════════════════════════════════════
  三个场景对比卡片：
  
  ❌ 没有 Moltable:
    "换了一台新电脑 → 装 Hermes → 重新写 mcp.json → 
     重新建 Persona → 重新告诉 AI 我是谁 → 2 小时过去了"
  
  ❌ 没有 Moltable:
    "Claude 里讨论过的技术方案 → 切到 Hermes → 
     完全不记得 → 重新解释 → 浪费 15 分钟"
  
  ✅ 有 Moltable:
    "打开新电脑 → 装 Hermes → 点一下'接入 Moltable' → 
     3 分钟后：身份/偏好/项目/Agent 全部就绪"

═══════════════════════════════════════════════
SECTION 3: 核心能力（3 列图文）
═══════════════════════════════════════════════
  🚀 3 分钟环境恢复
     icon + 简短描述 + "了解更多" 链接
  
  🤝 Agent 自动发现
     icon + 简短描述（A2A 协议示意动画）
  
  🧠 跨平台记忆同步
     icon + 简短描述 + Pro 标签

═══════════════════════════════════════════════
SECTION 4: 工作原理（简版）
═══════════════════════════════════════════════
  三步骤可视化流程：

  Step 1: 注册 → 获取 API Key（30 秒）
  Step 2: Agent 接入 → 一条命令（10 秒）
  Step 3: 自动同步 → 身份/偏好/项目/Agent 全部就绪
  
  Protocol: 基于 Google A2A 开放协议，不绑定任何单一平台

═══════════════════════════════════════════════
SECTION 5: 定价（三栏）
═══════════════════════════════════════════════
  Free          Pro（推荐）      Team
  ¥0/月         ¥19/月           ¥39/月/人
  100 条记忆    10,000 条记忆    50,000 条记忆
  2 个 Persona  无限 Persona     无限 Persona
  1 个身份      3 个身份         10 个身份
  50 API/天     500 API/天       2000 API/天
  基础 MCP      Skills 同步      管理面板
  [开始使用]    [升级 Pro]       [联系咨询]

  "最受欢迎" badge 在 Pro 栏，黄色高亮
  月付/年付 切换按钮（年付 ¥149/年，省 35%，但不主动推）

═══════════════════════════════════════════════
SECTION 6: 竞品对比简化表
═══════════════════════════════════════════════
  （详见第九节 — 官网用简化版 4 列）

═══════════════════════════════════════════════
SECTION 7: 用户证言（3 条）
═══════════════════════════════════════════════
  预留位置，上线后收集真实用户 quote

═══════════════════════════════════════════════
SECTION 8: 开始使用
═══════════════════════════════════════════════
  CTA: [免费注册 — 30 秒完成]
  
  三步快速开始：
  1. 注册账号 → 获取 API Key
  2. 安装 Moltable Skill → 填写 API Key
  3. Agent 自动拉取你的身份、偏好和项目环境

  开发者入口: curl -sL moltable.ai/setup.py | python3 -
  
  支持平台列表: Hermes · Claude Code · Cursor · ChatGPT MCP · 任意 MCP 客户端

═══════════════════════════════════════════════
SECTION 9: Footer
═══════════════════════════════════════════════
  产品: 功能介绍 · 定价 · 文档 · API · 更新日志
  资源: Blog · GitHub · 社区 · 状态页
  法律: 隐私政策 · 服务条款 · 安全白皮书
  Copyright © 2026 Moltable · 基于 Google A2A 开放协议构建
```

---

## 六、定价页优化建议

### 现状分析

| 项目 | 现状 | 问题 |
|------|------|------|
| Free 层 | 100 条记忆 | ✅ 诱饵模型合理（2-3 天打满） |
| Pro 月付 | ¥19/月 | ✅ 价格合理（用户反馈：¥9 毫不犹豫，¥19 犹豫 3 秒） |
| Pro 年付 | ¥149/年（¥12.4/月） | ⚠️ 中国用户对年付天然抗拒（"你先活过 6 个月"） |
| Team | ¥39/月/人 | ⚠️ 过早暴露 B2B 定价可能稀释 Pro 转化 |

### 优化建议

#### 建议 1：弱化年付，不主动推

- 移除"最受欢迎"标签从年付（如果有）
- 年付仅作为月付切换按钮下方的小字选项，不单独占一栏
- 文案："年付 ¥149/年（省 ¥79）"而非"推荐"

#### 建议 2：加"按季付"作为中间选项

| | 月付 | 季付（新） | 年付 |
|---|---|---|---|
| 单价 | ¥19/月 | ¥16/月 (¥48/季) | ¥12.4/月 (¥149/年) |
| 节省 | — | 16% | 35% |
| 话术 | "随时取消" | "季度计划" | "最佳性价比" |

季付是低承诺选项，适合"想试试但不想年付"的用户。

#### 建议 3：Free → Pro 转化优化

**触发时机**：Free 用户记忆条数达到 80/100 时（不是 100/100）  
**触发方式**：轻提醒弹窗（非打断式弹窗）

> "还有 20 条记忆空间。Pro 解锁 10,000 条记忆 + 无限 Persona + Agent 发现，仅 ¥19/月。"  
> [升级 Pro] [稍后再说]

**触发时机 2**：用户创建第 2 个 Persona 后尝试创建第 3 个时  
**响应**：402 错误 + upgrade_url → 跳转定价页

#### 建议 4：定价页视觉

- 三栏布局，Pro 栏加 2px 彩色边框 + "最受欢迎"badge（非年付标签）
- 每栏列出"包含功能"checlist（不要只列差异）
- Free 栏底部 CTA: "免费开始"（灰底），Pro 栏: "升级 Pro"（品牌色实心按钮）
- 底部加 FAQ 手风琴：3-5 个常见问题（"可以随时取消吗？""数据能导出吗？""支持哪些平台？"）

#### 建议 5：终身套餐（可选，后期考虑）

针对早期支持者，限量终身套餐：

> 前 500 名 Pro 终身：¥299/一次性 · 限时 · 已售 xxx/500

此策略参考了 Notion/Linear 的早期推广模式，适合种子用户积累期。但需谨慎：一旦用完早期用户，后续收入会断层。

---

## 七、首发渠道和内容策略

### 渠道矩阵（按优先级）

| 渠道 | 类型 | 优先级 | 内容形式 | 预期效果 |
|------|------|:--:|---------|---------|
| **GitHub** | 开源社区 | P0 | README + Demo gif + MCP 接入指南 | 自然流量 + 开发者信任 |
| **即刻** | 中文 AI 圈 | P0 | 帖子："我做了个 AI 身份同步工具" | 精准触达早期 adopter |
| **V2EX** | 中文开发者 | P0 | 分享创造节点发布，带使用场景 | 开发者种子用户 |
| **Twitter / X** | 全球 AI | P1 | 英文帖："iCloud for your AI identity" | 海外曝光 |
| **掘金** | 中文前端/全栈 | P1 | 技术文章：A2A 协议实战 | 技术品牌建立 |
| **少数派** | 效率工具 | P1 | 测评文："换电脑后如何 3 分钟恢复 AI 环境" | 付费转化 |
| **Product Hunt** | 全球首发 | P2 | 正式发布帖（需精心准备） | 爆发式流量 |
| **Hacker News** | 全球技术 | P2 | Show HN 帖 | 技术圈认同 |
| **B站/YouTube** | 视频 | P2 | 3 分钟演示视频 | 可视化传播 |

### 内容日历（首发 30 天）

```
Week 0（发布前）
  └─ GitHub README 完善 + demo gif 录制
  └─ 官网 Landing Page 上线
  └─ 知乎/即刻预热带话题 #AI身份同步

Week 1（发布周）
  Day 1: 即刻首发帖（带真实使用场景截图）
  Day 2: V2EX "分享创造" 节点发布
  Day 3: 掘金技术文章：《Google A2A 协议是什么？我用来做 Agent 间服务发现》
  Day 5: Twitter/X 英文 announcement thread
  Day 7: 少数派投稿：效率工具测评

Week 2-3（发酵期）
  └─ Product Hunt 发布（需提前联系 Hunter）
  └─ Hacker News Show HN
  └─ B站 3 分钟上手视频
  └─ 每周一篇 Blog: "本周 Moltable 使用技巧"

Week 4（复盘期）
  └─ 用户反馈收集 → 优化 onboarding
  └─ 首批用户证言收集
  └─ 数据复盘：注册数/激活率/Pro 转化率
```

### 内容角度库（可直接用的标题）

**技术类**：
- "Google A2A 协议实战：让 Claude 和 Hermes 共享记忆"
- "换电脑后 3 分钟恢复完整 AI 环境 — Moltable 技术实现"
- "为什么你的 Agent 记忆不该锁在单一平台里"

**场景类**：
- "我换了新 Mac，这是唯一不用重新配置的 AI 工具"
- "三个 AI 助手共用一个大脑是什么体验？"
- "从 mem0 迁移到 Moltable 的 3 个理由"

**观点类**：
- "AI Agent 的未来：不是更强的模型，而是共享的身份层"
- "为什么"AI 永远认识你"比"更强的 AI"更重要"
- "Agent-to-Agent 协议正在成为 AI 基础设施的 TCP/IP"

---

## 八、竞品对比表

### 官网用（面向用户，非内部分析）

| | Moltable | mem0 | Zep | Letta |
|---|:---:|:---:|:---:|:---:|
| **定位** | AI 身份 + 发现层 | AI 记忆引擎 | 企业记忆平台 | Agent 记忆框架 |
| **身份同步** | ✅ 跨 Agent 同步 | ❌ 仅平台内 | ❌ 仅平台内 | ❌ 仅框架内 |
| **Agent 发现** | ✅ A2A 协议 | ❌ | ❌ | ❌ |
| **环境恢复** | ✅ 3 分钟 | ❌ | ❌ | ❌ |
| **记忆容量 (入门)** | 100 条（免费） | 10,000 条 | 10,000 credits | 3 Agent |
| **Pro 价格** | **¥19/月** | $19/月 → $249/月 | $125/月 | $20/月 |
| **协议** | Google A2A | 自有 | 自有 | 自有 |
| **开源** | ✅ MIT | ✅ Apache 2.0 | ❌ 闭源核心 | ✅ MIT |
| **自托管** | ✅ SQLite | ✅ | ❌ | ✅ |
| **中文优化** | ✅ 原生双语 | ❌ | ❌ | ❌ |

### 官网"为什么选 Moltable"模块

> **不只记记忆，更记身份。**
> 
> mem0 和 Zep 是优秀的记忆引擎 — 但它们只管"记忆存在哪"。Moltable 管的是"你是谁、你的 AI 在哪、你的项目环境是什么" — 这是更底层的问题，也是换平台时最先碰到的问题。
> 
> **Google A2A，不是又一个私有协议。**
> 
> 我们选择 A2A 是因为相信 Agent 之间的互操作应该是开放的，不是又一个需要"迁移数据"的围墙花园。

---

## 九、"为什么是现在"（市场时机论证）

### 4 个结构性机会，2026 年下半年同时出现

#### 机会 1：Agent 碎片化是 2026 年最大的 AI 体验问题

- 2026 年，一个重度 AI 用户日常使用 3-5 个 Agent（Claude Code、Cursor、Hermes、Copilot、Windsurf）
- 每个 Agent 有独立的 MCP 配置、独立的"记忆"、独立的身份理解
- 用户在这 3-5 个 Agent 之间切换时，**每次都要重新建立上下文**
- **多 Agent 同步层** 是 2024 年"API 层"和 2025 年"MCP 层"之后的下一代基础设施需求

#### 机会 2：Google A2A 协议刚刚发布（2026 Q2），生态处于真空期

- Google A2A 协议于 2026 年 4 月发布，定义了 Agent 间服务发现和任务委托的标准
- 目前市场上 **几乎没有面向终端用户** 的 A2A 产品
- 这是一个"协议有了但产品没有"的时间窗口 — Moltable 可以用 `moltable-connector` 做第一个 A2A 消费级应用
- 类比：1995 年的 HTTP — 协议存在，但浏览器（Netscape）刚出现。第一个做出易用产品的 = 定义品类

#### 机会 3：记忆引擎价格断崖，存在 10 倍性价比空白

| | 入门价 | 中档价 | 高端价 |
|---|:--:|:--:|:--:|
| mem0 | $0（限制严格） | $19 | **$249** |
| Zep | $0 (1万 credits 试用) | **$125** | $375 |
| Moltable | ¥0（100 条，够体验） | **¥19** | ¥39（Team） |

- mem0 的 Graph Memory 锁在 $249/月档 — 普通用户完全够不着
- Zep 的入门即 $125/月 — 面向企业，不是个人
- **¥19/月 的记忆层在 2026 年是价格空白** — 个人用户付得起，企业觉得便宜

#### 机会 4：AI 换机潮 + 多设备场景刚需

- 2026 年 Mac/PC 升级周期加速（Apple Silicon M4/M5、Windows AI PC）
- 更多人拥有"工作机 + 个人机"两台设备
- **换设备后重配 AI 环境**的痛点越来越普遍 — 而目前没有任何产品解决这个问题
- Moltable 的 3 分钟恢复 = 这个痛点的针对性答案

### 一句话总结

> **2026 年下半年的 AI 世界：Agent 越来越多、A2A 协议刚出来、记忆引擎太贵、换机潮来了。Moltable 站在四个趋势的交汇点。**

---

## 十、命名评估和改进建议

### 当前命名：Moltable

| 维度 | 评分 | 评价 |
|------|:--:|------|
| 独特性 | 8/10 | 无重名，Google 搜索零噪音 |
| 含义传达 | 5/10 | Mol = molecule（需要解释），table = 元素台 / 表格（指向不明） |
| 拼写易记 | 6/10 | 8 字母，不短不长。"mol" 开头在中文圈可能误读 |
| 品牌扩展性 | 7/10 | "Moltable Connect""Moltable Sync""Moltable Cloud" 可以衍生 |
| 国际化 | 7/10 | 英文友好，中文无负面联想 |
| 品类联想 | 4/10 | "table" 暗示表格/数据库，而非"身份/同步/发现" |

### 核心问题

1. **Moltable 不传递品类信号** — 用户看到名字无法联想到"AI 身份同步"或"Agent 发现"
2. **Logo 的分子隐喻和产品定位脱节** — 分子结构图暗示化学/科学，不是 AI Agent 基础设施
3. **中文用户叫不出口** — "摩尔表格"？"莫表格"？缺乏朗朗上口的中文名

### 改进方案（三档）

#### 方案 A：保留 Moltable，加副标题（风险最低，推荐）

```
Moltable
━━━━━━━━━━━━━━━
AI Identity Sync
```

- 不改名，避免迁移成本
- 强化"Moltable = AI Identity Sync"认知
- 在所有平台（GitHub、即刻、Product Hunt）统一用 `Moltable — AI Identity Sync`
- 中文：Moltable（你的 AI 身份中枢）

#### 方案 B：保留 Moltable 品牌，增加中文名

| 候选中文名 | 含义 | 评价 |
|-----------|------|------|
| **默识** | 默 = 隐性（AI 默默记住你），识 = 认知/标识 | ⭐ 推荐。音近"Mol"，意好 |
| **同身** | 一个身份，跨 Agent 同步 | 简洁但略抽象 |
| **识桥** | 认知的桥梁，连接 Agent | 清晰但不够酷 |
| **灵犀** | 李商隐"心有灵犀一点通" | 诗意但可能太文雅 |

推荐：**Moltable · 默识**

#### 方案 C：激进改名（品牌价值尚低，可承受）

全新命名候选（按品类联想排序）：

| 候选 | 含义 | 优势 | 劣势 |
|------|------|------|------|
| **AISync** | AI Sync，直白 | 品类联想 10/10 | 太 generic，商标难注册 |
| **AgentID** | Agent Identity | 技术圈好懂 | ID 缩写可能歧义 |
| **SyncMind** | 同步心智 | 好听好记 | .com 域名可能已被占用 |
| **MeshAI** | 网状连接所有 AI | 隐喻 A2A 网络 | 竞品 Mesh 类产品已存在 |
| **A2Hub** | A2A Protocol Hub | 绑定 A2A 生态 | 太技术，非技术用户不懂 |

### 推荐决策

> **短期（未来 3 个月）：方案 A**  
> 保留 Moltable，统一副标题为 "AI Identity Sync"，中文文案使用"Moltable（AI 身份中枢）"。
> 
> **中期（6-12 个月）：方案 A + B**  
> 加入中文名 **"默识"**，品牌升级为 **"Moltable · 默识 — AI 身份同步层"**。
> 
> **长期：不排除方案 C**  
> 如果产品从"身份同步"扩展到更广泛的基础设施层（如 Agent 协作市场、任务委托结算），可考虑更名为更通用的品牌。

---

## 附录：可直接使用的市场物料

### A. 一句话介绍（各种长度）

| 长度 | 文案 |
|:--:|------|
| 5 字 | AI 的身份中枢 |
| 15 字 | 一个身份接入，所有 Agent 自动同步。 |
| 30 字 | Moltable 是 AI Agent 的身份同步层。基于 Google A2A 协议，换设备 3 分钟恢复完整 AI 环境，所有 Agent 共享记忆。 |
| 50 字 | Moltable 是 AI Agent 的服务发现与身份同步层。一个身份接入，所有 Agent 自动同步偏好、技能和记忆。换电脑 3 分钟恢复完整 AI 环境，旧 Agent 注册后新 Agent 自动发现并协同工作。基于 Google A2A 开放协议。 |

### B. GitHub README 简介

```markdown
# Moltable — AI Identity Sync

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Protocol: A2A](https://img.shields.io/badge/Protocol-Google%20A2A-4285F4)](https://a2a.google)

**One identity. Every agent.**

Moltable is the identity sync layer for AI agents. Built on Google's A2A protocol, it lets your AI assistants share the same identity, preferences, skills, and memory — across platforms and devices.

- 🔄 **3-minute environment restore** — switch computers, not your AI context
- 🤝 **Agent discovery via A2A** — old agents register, new agents auto-discover
- 🧠 **Cross-agent memory** — what you told Claude, Hermes remembers too

## Quick Start

```bash
# Register and get your API key in 30s
curl -sL https://moltable.ai/setup.py | python3 -
```

## Pricing

- **Free**: 100 memories, 2 personas, basic MCP tools
- **Pro**: ¥19/mo — 10,000 memories, unlimited personas, agent discovery
```

### C. 社交媒体首帖模板

**即刻 / V2EX**：

> 🚀 做了一件事：让你的 AI 永远认识你。
> 
> 我的日常：早上用 Claude Code 写代码，白天用 Hermes 做分析，晚上切到 Cursor 改前端。问题是 — 每个 AI 都要重新告诉它"我是谁、偏好什么、项目在哪"。
> 
> 所以做了 Moltable：一个身份接入，所有 AI 自动同步。基于 Google A2A 协议，换电脑 3 分钟恢复完整 AI 环境。
> 
> 免费版 100 条记忆，够体验。Pro ¥19/月，比 mem0 便宜 10 倍。
> 
> 🔗 moltable.ai | ⭐ GitHub: github.com/nous/molt…
> 
> #AI工具 #独立开发 #Agent

**Twitter / X (English)**：

> Your AI shouldn't forget who you are when you switch tools.
> 
> Built Moltable — iCloud for AI identity. One profile, every agent. 3-min restore when you switch computers. A2A protocol.
> 
> Free tier, ¥19/mo Pro (10x cheaper than mem0).
> 
> 🔗 moltable.ai

---

## 附录 B：命名评估矩阵（完整版）

| 维度 | 权重 | Moltable | AISync | AgentID | SyncMind | 默识 |
|------|:--:|:--:|:--:|:--:|:--:|:--:|
| 独特性 | 15% | 8 | 2 | 4 | 5 | 7 |
| 品类联想 | 25% | 4 | 9 | 7 | 7 | 6 |
| 易记性 | 20% | 6 | 7 | 8 | 8 | 6 |
| 国际友好 | 15% | 7 | 7 | 7 | 7 | 2 |
| 品牌扩展 | 15% | 7 | 4 | 6 | 6 | 7 |
| 商标可用 | 10% | 7 | 3 | 4 | 5 | 8 |
| **加权总分** | — | **6.1** | **5.6** | **6.2** | **6.5** | **5.8** |

**结论**：SyncMind 总分最高但商标风险大。Moltable 在独特性上占优，品类联想是短板（可用副标题弥补）。不改名风险最低。

---

> 本文档由 Moltable 市场包装方案生成，版本 v1.0。  
> 如需更新或导出为 PPT/PDF/网页文案，请基于此文档二次加工。
