# Moltable 社区建设三步走方案

> 核心理念：**Moltable = iCloud for AI Identity** — 社区不是"拉人"，是让每个接入的用户自然地成为传播节点。
>
> 日期：2026-08-01 | 版本：v1.0 | 作者：社区&生态运营专家

---

## 目录

1. [总体策略与核心原则](#一总体策略)
2. [阶段一：种子用户激活（Day 0-30）](#二阶段一种子用户激活)
3. [阶段二：社区自增长（Day 31-90）](#三阶段二社区自增长)
4. [阶段三：生态网络效应（Day 91-180）](#四阶段三生态网络效应)
5. [渠道详细操作手册](#五渠道详细操作手册)
6. [KOL / 布道者合作策略](#六kol--布道者合作策略)
7. [度量指标与里程碑](#七度量指标与里程碑)
8. [附录：即用物料清单](#八附录即用物料清单)

---

## 一、总体策略

### 1.1 Moltable 社区的特殊性

Moltable 不是一个"用完即走"的工具——它是一个**基础设施层**。这意味着：

| 普通 SaaS | Moltable |
|-----------|----------|
| 社区 = 用户群 + 反馈渠道 | 社区 = 生态共建者 + SDK 贡献者 + Persona 作者 |
| 增长靠投放 | 增长靠**身份网络效应**（你用 Moltable → 你的 Agent 被更多 Agent 发现 → 更多人接入） |
| 留存靠功能 | 留存靠**数据积累**（10K 记忆再也舍不得离开） |
| 口碑靠好评 | 口碑靠**切换成本降低**（"换 AI 终于不用重新调教了"） |

### 1.2 北极星指标

**月活跃 Agent 连接数（MAAC）** — 不是注册用户数，是实际通过 Moltable MCP 发起了 `auto_provision` 的 Agent 数。

```
注册用户 ≠ 活跃用户
活跃用户 ≠ 连接中的 Agent
连接中的 Agent = 真正依赖 Moltable 的用户

北极星 = "昨天有多少个 Agent 通过 Moltable 完成了身份同步"
```

### 1.3 三阶段概览

```
阶段一（Day 0-30）          阶段二（Day 31-90）        阶段三（Day 91-180）
   种子激活                   社区自增长                  生态网络效应
┌──────────────────┐    ┌──────────────────┐     ┌──────────────────┐
│ 100 活跃用户      │ → │ 首个 1000 Star   │  →  │ 第三方集成涌现     │
│ 前20个真实反馈    │    │ 首批贡献者       │     │ Persona 市场活跃  │
│ GitHub 公开      │    │ 布道者自发推广    │     │ Plugin/Connector 扩展│
│ 核心体验闭环      │    │ 社区内容飞轮      │     │ 网络效应护城河     │
└──────────────────┘    └──────────────────┘     └──────────────────┘
   一对一拉人             一对多裂变                 多对多网络
```

---

## 二、阶段一：种子用户激活（Day 0-30）

> **目标**：100 个活跃用户，每个用户完成了 "注册 → 接入 Agent → 第一次 auto_provision → 保存第一条记忆" 的完整闭环。
>
> **核心信念**：前 100 个用户不是靠"宣传"获得的——是靠"找到 100 个正在痛的人，然后让他们 3 分钟内体验到解脱"。

### 2.1 种子用户画像

优先触达两类人：

#### 类型 A：多 Agent 重度用户（60 人目标）

- 日常使用 2+ 个 AI 助手（Hermes / Claude Code / Cursor / Copilot）
- 频繁换电脑或在不同项目之间切换
- **痛点明确**："每个 AI 都要重新自我介绍，烦死了"
- **获客渠道**：即刻 AI 圈、V2EX、Hermes 社区、Claude Code Discord

#### 类型 B：独立开发者 / 技术博主（40 人目标）

- 有个人项目，管理复杂工具链（多数据库、多知识库）
- 喜欢写技术文章或发推分享工具
- **痛点明确**："mcp.json 和 .env 散落一地，换个电脑要重建半天"
- **获客渠道**：掘金、少数派、Twitter AI 圈、GitHub Trending 读者

### 2.2 获客策略：一对一邀请，不是广撒网

| 渠道 | 方式 | 目标数 | 时间 |
|------|------|:--:|------|
| **即刻 AI 圈** | 私信 + 帖子分享个人使用场景 | 20 人 | Day 1-7 |
| **V2EX 分享创造** | 发布产品帖 + 逐条回复 | 15 人 | Day 3 |
| **Hermes 社区** | 内置 Skill 的 natural upgrade 引导 | 25 人 | Day 1-30 |
| **Claude Code Discord** | 在 #showcase 或 #tools 频道分享 | 10 人 | Day 5-10 |
| **朋友圈 / 技术群** | 个人社交网络，1对1 私聊邀请 | 15 人 | Day 1-7 |
| **Twitter/X** | "I built iCloud for AI identity" 英文帖 | 10 人 | Day 7-14 |
| **掘金** | 技术文章：《Google A2A 协议实战：让 Claude 和 Hermes 共享记忆》 | 5 人 | Day 10 |

### 2.3 种子用户 Onboarding 流程

**目标**：从注册到"AHA moment"不超过 3 分钟。

```
用户到达 Landing Page
  ↓ （30秒）
注册 → 复制 API Key
  ↓ （10秒）
粘贴到 Hermes/Claude Code
  ↓ （即时）
auto_provision() 返回完整身份 + 项目地图
  ↓ （AHA!）
"我的 AI 真的认识我了！"
  ↓ （自然行为）
开始对话 → search_memory 返回历史记忆
  ↓ （留存锚点）
save_memory → 第 1 条记忆入库
```

**关键设计**：

1. **注册即送"记忆种子"**：注册后自动创建 3 条预置记忆（"偏好中文回复"、"关注 AI Agent 生态"、"使用 Hermes + Claude Code"），让用户第一次 `search_memory` 就能搜到东西，立刻体会到"AI 记得我"。
2. **匿名会话 7 天 → 注册转化**：未注册用户也能体验记忆功能，但 7 天后过期。第 3 天、第 7 天分别提醒一次。
3. **第 10 条记忆时触发 Pro 推荐**：Free 用户打满 80/100 条记忆时，轻提醒而非打断式弹窗。

### 2.4 种子用户留存动作

| 时间 | 动作 | 目的 |
|------|------|------|
| Day 0（注册当天） | 自动发送欢迎邮件，含 3 分钟上手视频链接 | 降低弃用率 |
| Day 3 | 个人微信/私信回访："用起来了吗？碰到什么问题？" | 收集首次摩擦点 |
| Day 7 | 邀请加入核心用户微信群/Discord | 建立归属感 |
| Day 14 | 分享 Roadmap，邀请投票决定下个功能优先级 | 参与感 |
| Day 30 | "你已经在 Moltable 上存了 X 条记忆"回顾邮件 | 数据积累的可视化满足 |

### 2.5 阶段一交付物清单

- [x] GitHub 仓库公开（README 优化 + Demo GIF + MCP 接入指南）
- [x] Discord 服务器搭建（基础频道结构）
- [x] 即刻首发帖 + V2EX 分享创造帖
- [x] 核心用户微信群（20-30 人）
- [x] Onboarding 邮件自动化
- [x] 第一个版本 Changelog（发布时创建）
- [ ] 30 天内收集 20 个真实用户反馈
- [ ] 完成 3 次产品迭代（基于反馈）

---

## 三、阶段二：社区自增长（Day 31-90）

> **目标**：前 100 个种子用户中，涌现出 5-10 个布道者和 3-5 个代码贡献者。社区不再只靠创始人拉人，开始有自然增长。
>
> **核心转变**：从"我在推"到"大家在传"。

### 3.1 贡献者培养计划

#### 3.1.1 贡献阶梯（Contribution Ladder）

```
Level 0: 用户（User）
  └→ 用 Moltable，不提 issue

Level 1: 反馈者（Reporter）
  └→ 提交 Bug Report / Feature Request
  └→ 门槛：知道 GitHub Issue 怎么提
  └→ 激励：Issue 被标记为 "good first issue" 时 @他

Level 2: 文档贡献者（Docs Contributor）
  └→ 修正 README 错别字、翻译文档、补充接入指引
  └→ 门槛：会 Markdown
  └→ 激励：贡献者名单 + "Docs Contributor" Discord 角色

Level 3: 代码贡献者（Code Contributor）
  └→ 修 Bug、加小功能、写测试
  └→ 门槛：会 Go/Python
  └→ 激励：合并 PR + 官网贡献者墙 + 限量周边

Level 4: 维护者（Maintainer）
  └→ 审核 PR、管理 Issue、参与 Roadmap 讨论
  └→ 门槛：持续贡献 3+ 月
  └→ 激励：GitHub 组织成员 + 直接 commit 权限 + Pro 终身免费

Level 5: 布道者（Evangelist）
  └→ 写博客、做视频、社区演讲、帮助新人
  └→ 门槛：有影响力的内容产出
  └→ 激励：Moltable Ambassador 称号 + 官方推广资源 + 收入分成（如有）
```

#### 3.1.2 "Good First Issue" 策略

每周预留 3-5 个标记为 `good first issue` 的小任务：

| 类型 | 示例 | 适合 |
|------|------|------|
| 文档 | "补充 macOS 上 Python 3.13 兼容性说明" | 新手 |
| 测试 | "为 search_memory 增加混合搜索的单元测试" | 有一定基础 |
| Bug | "修复 memory archive 后仍出现在搜索结果中的问题" | 中级 |
| Feature | "支持 search_by_tag 的模糊匹配" | 进阶 |

**关键原则**：`good first issue` ≠ 不重要。要做"高可见度、低复杂度"的任务——让新手的第一份贡献被看到。

### 3.2 社区内容飞轮

```
用户分享使用体验
  → 新用户被吸引
    → 新用户开始用
      → 新用户存了更多记忆
        → 记忆越多，切换成本越高
          → 用户更愿意分享
            → （循环加速）
```

**加速手段**：

1. **案例收集**：主动联系活跃用户，帮他们整理成"用户故事"发布在 Blog
2. **周报**：每周一篇 "This Week in Moltable"，汇总社区动态、合并的 PR、新 Persona 模板
3. **社区挑战赛**："用 Moltable 创建最有创意的 Persona，赢 Pro 一年"

### 3.3 Discord 社区激活

#### 频道结构（阶段二升级版）

```
📢 ANNOUNCEMENTS
  #announcements    — 版本发布、重要通知
  #changelog        — 自动同步 GitHub Releases

💬 COMMUNITY
  #general          — 日常讨论
  #showcase         — 用户分享自己的 Persona / 用例 / 环境配置
  #help             — 问答互助

🔧 DEVELOPMENT
  #contributing     — 贡献者讨论
  #pr-reviews       — PR 审核请求
  #ideas            — 功能建议投票

🎭 PERSONA HUB
  #persona-showcase — 分享 Persona 模板
  #persona-help     — Persona 创建帮助

🌏 中文社区
  #中文-general      — 中文用户专属频道
  #中文-资源         — 教程、翻译、案例
```

#### AMA 活动节奏

| 频率 | 主题 | 形式 |
|------|------|------|
| 每两周 | "Ask Me Anything" — 创始人回答社区问题 | Discord 文字 AMA，1 小时 |
| 每月 | 嘉宾 AMA — 邀请 AI Agent 生态的 KOL | Discord Stage 语音 |
| 每季度 | Roadmap 直播 — 公开展示下季度计划并投票 | Discord Stage + YouTube 直播 |

### 3.4 阶段二关键动作

| 时间 | 动作 | 目标 |
|------|------|------|
| Day 31-45 | 发布第一个 "good first issue" batch | 吸引前 3 个社区贡献者 |
| Day 45 | 启动 "Persona 创作挑战赛" | 积累 20+ 社区 Persona 模板 |
| Day 60 | 发布 Moltable SDK（Go/Python） | 降低开发者接入门槛 |
| Day 75 | 首次社区 AMA | Discord 活跃度提升 |
| Day 90 | 达成 500 GitHub Stars | 里程碑庆祝 + 周边发放 |

---

## 四、阶段三：生态网络效应（Day 91-180）

> **目标**：Moltable 不再只是一个产品——它是一个**协议层**。第三方集成自发出现，用户创造的内容（Persona、Connector、Tutorial）超过官方产出。
>
> **核心转变**：从"中心化社区"到"去中心化生态"。

### 4.1 第三方集成策略

#### 4.1.1 Connector Program（连接器计划）

Moltable 的核心价值是"连接所有 AI Agent"。每个新 Connector 都是一个新的用户获取渠道。

```
Connector 类型：

1. AI 平台 Connector
   ├─ Hermes Skill（已有）    — 内置 auto_provision
   ├─ Claude Code Plugin      — MCP 接入 + 项目地图
   ├─ Cursor Integration      — 同 MCP
   ├─ VS Code Copilot         — 浏览器插件桥接
   ├─ ChatGPT Plugin          — ChatGPT MCP 客户端
   └─ Windsurf / Cody / etc   — 社区贡献

2. 知识库 Connector
   ├─ mem0 → Moltable 迁移工具  — 最高优先级
   ├─ Notion → Moltable 同步     — API 桥接
   ├─ Obsidian → Moltable 索引   — 本地文件扫描
   └─ Slack/Discord → 记忆导入   — 对话历史导入
```

**激励方案**：

| 贡献类型 | 奖励 |
|----------|------|
| 新 Connector 合并到主仓库 | Pro 一年 + 官网 Connector 页面展示 |
| Connector 被 50+ 用户安装 | $50 奖金 |
| Connector 被 500+ 用户安装 | $200 奖金 + 收入分成讨论 |

#### 4.1.2 开源生态定位

```
Moltable 的技术栈生态位：

                    ┌──────────────────┐
                    │   MCP 协议层      │  ← Anthropic 定义
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │   Moltable       │  ← 身份 + 记忆 + 项目地图
                    │   (基础设施)     │
                    └────────┬─────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
   ┌──────▼──────┐   ┌──────▼──────┐   ┌──────▼──────┐
   │  Hermes     │   │  Claude     │   │  Cursor     │
   │  (Agent)    │   │  Code       │   │  (IDE)      │
   │             │   │  (CLI)      │   │             │
   └─────────────┘   └─────────────┘   └─────────────┘
```

**差异化定位**：mem0 做记忆，Moltable 做身份 + 记忆 + 环境。不对标、不 PK——鼓励 mem0 用户同时用 Moltable 来同步身份和环境。

### 4.2 UGC 内容生态

#### 4.2.1 Persona 市场

阶段三的目标是让 Persona 成为一个**有网络效应的独立模块**：

```
Persona 市场功能：

- 发布：用户可将自己创建的 Persona 公开发布
- 浏览：按类别（开发、设计、管理、写作）浏览社区 Persona
- 评分/评论：下载量 + 星标 + 评论
- 一键克隆：点击即复制到自己的 Persona 列表
- 官方认证：高质量 Persona 获得 "Verified" 徽章
- 版本管理：Persona 更新后通知所有克隆者
```

**冷启动策略**：

1. 官方首发 10 个高质量 Persona（CFO、CEO、数据分析师、代码审查员、产品经理、DevOps、UX 设计师、学术研究者、小红书博主、Prompt 工程师）
2. 阶段二挑战赛的获奖作品入场
3. 邀请 3-5 位 KOL 发布独家 Persona

#### 4.2.2 内容渠道放大器

| 内容类型 | 渠道 | 频率 | 目的 |
|----------|------|------|------|
| 用户故事 | Blog + 社交媒体 | 每两周 1 篇 | 社会证明 |
| 技术教程 | 掘金 / Dev.to / Medium | 每周 1 篇 | SEO + 开发者获取 |
| 视频演示 | B站 / YouTube | 每月 2 期 | 降低理解门槛 |
| Changelog | GitHub + Discord + Blog | 每次发版 | 透明度 + 活跃感 |
| Newsletter | Email + 即刻 | 每两周 | 留存 + 唤醒 |

### 4.3 网络效应的三层飞轮

```
第一层：身份网络效应
  "你用 Moltable → 你的 Claude 认识你 →
   Claude 回答更准 → 你更愿意用 Moltable →
   你推荐给朋友 → 朋友也用 Moltable → ..."

第二层：Persona 网络效应
  "社区 Persona 越来越多 → 新用户注册就有高质量 Persona 可用 →
   新用户贡献自己的 Persona → 总数更多 → 吸引力更大 → ..."

第三层：Connector 网络效应
  "支持平台越多 → 覆盖用户越广 → 接入的人越多 →
   更多开发者做 Connector → 平台更多 → ..."
```

### 4.4 阶段三关键动作

| 时间 | 动作 | 里程碑 |
|------|------|--------|
| Day 91-120 | Persona 市场上线 | 社区 Persona > 50 个 |
| Day 120 | 首个外部 Contributor 的 Connector 合并 | 生态自发贡献出现 |
| Day 135 | Product Hunt 正式发布 | 单日 500+ upvotes |
| Day 150 | 社区 Meetup（线上/线下） | 首次社区线下联动 |
| Day 180 | 1000 GitHub Stars | 开源项目里程碑 |

---

## 五、渠道详细操作手册

### 5.1 GitHub

#### 5.1.1 README 优化

当前 README 的基础不错，需要在以下维度增强：

```markdown
# Moltable — AI Identity Sync  （✅ 已有）

## 优化项：

1. 顶部 Demo GIF/视频（⭐ 最重要）
   → 30 秒展示：注册 → 粘贴命令 → auto_provision → AI 认识你
   → 工具：Screen Studio / OBS → mp4/gif → 嵌入 README

2. Badge 增强
   [![Stars](https://img.shields.io/github/stars/jovon-hot/moltable)]  ← 已有
   [+] [![MCP](https://img.shields.io/badge/MCP-Compatible-blue)](链接)
   [+] [![Discord](https://img.shields.io/discord/xxxxx)](Discord邀请)
   [+] [![A2A](https://img.shields.io/badge/Protocol-Google%20A2A-4285F4)](a2a链接)

3. "Why Moltable" 章节 （新增）
   → 对比表：Moltable vs mem0 vs raw MCP config
   → 三个场景描述（见 MARKETING_PACKAGE.md Section 5）

4. "Who is this for" 章节 （新增）
   → 3 类用户画像简述

5. 自托管指引 （✅ 已有，但需要验证）
   → 确保 Docker Compose 可运行（当前阻塞项！）
   → 加上一键部署按钮：Deploy to Railway / Deploy to Render
```

#### 5.1.2 Issue 模板

创建 `.github/ISSUE_TEMPLATE/` 目录下的三个模板：

**`bug_report.yml`**：
```yaml
name: Bug Report
description: 报告一个 bug
labels: [bug, triage]
body:
  - type: textarea
    attributes:
      label: 描述
      description: 发生了什么？
  - type: textarea
    attributes:
      label: 复现步骤
      description: 如何触发这个问题？
  - type: input
    attributes:
      label: Moltable 版本
  - type: input
    attributes:
      label: Agent 类型（Hermes/Claude/Cursor）
  - type: textarea
    attributes:
      label: 日志/截图
```

**`feature_request.yml`**：
```yaml
name: Feature Request
description: 建议一个新功能
labels: [enhancement]
body:
  - type: textarea
    attributes:
      label: 你希望解决什么问题？
      description: 描述你的使用场景和痛点
  - type: textarea
    attributes:
      label: 你期望的解决方案
  - type: textarea
    attributes:
      label: 你考虑过的替代方案
```

**`persona_submission.yml`**：
```yaml
name: Persona 投稿
description: 提交一个 Persona 模板
labels: [persona, community]
body:
  - type: input
    attributes:
      label: Persona 名称
  - type: textarea
    attributes:
      label: System Prompt
  - type: textarea
    attributes:
      label: 适用场景
  - type: checkboxes
    attributes:
      label: 授权
      options:
        - label: 我同意将此 Persona 以 MIT 协议授权给 Moltable 社区
```

#### 5.1.3 CONTRIBUTING.md

```markdown
# Contributing to Moltable

## 首次贡献？
→ 看 `good first issue` 标签
→ 加入 Discord #contributing 频道

## 开发环境
```bash
git clone https://github.com/jovon-hot/moltable.git
cd moltable/server
pip install -r requirements.txt
python main.py
```

## 提交 PR
1. Fork 仓库
2. 创建 feature 分支: `git checkout -b feat/xxx`
3. 写测试（如有新功能）
4. 运行测试: `python -m pytest`
5. 提交: 使用 conventional commits (`feat:`, `fix:`, `docs:`, `test:`)
6. 提 PR 到 `main` 分支

## 行为准则
见 CODE_OF_CONDUCT.md
```

#### 5.1.4 Star 增长策略

| 阶段 | 策略 | 目标 |
|------|------|------|
| Day 0-30 | GitHub 公开 + 即刻/V2EX 带 GitHub 链接 | 100 Stars |
| Day 31-60 | 在 MCP 相关 Awesome List 提交 PR | 300 Stars |
| Day 61-90 | Hacker News Show HN + Product Hunt 关联 | 500 Stars |
| Day 91-180 | Trending 自然流量 + 社区分享回流 | 1000 Stars |

**关键技巧**：

- **"Star 触发 Hook"**：README 里嵌入一个真实的用户故事或数据 ——"10 天内 100 个开发者用 Moltable 同步了 5,000+ 条记忆"
- **在 README 里放 GitHub Star History 图**（用 star-history.com）— 增长曲线本身是说服力
- **每个新 Connector / 新功能都提一个独立的 Discussion** — 增加互动数据
- **合并 PR 时在 commit message 里感谢贡献者** — 激励更多人贡献

### 5.2 Discord 社区

#### 5.2.1 频道结构（完整版）

```
═══════════════════════════════════════
📌 入门区
═══════════════════════════════════════
#👋welcome          — 新人报到（仅管理员可发言，机器人自动欢迎）
#📋rules            — 社区规则
#🚀getting-started  — 安装指引、常见问题
#📢announcements    — 版本发布、活动公告

═══════════════════════════════════════
💬 讨论区
═══════════════════════════════════════
#💬general          — 随便聊
#🎭persona-hub      — Persona 分享与讨论
#🛠️showcase         — 用例展示
#🤖agent-talk       — AI Agent 生态讨论（不限 Moltable）

═══════════════════════════════════════
🔧 开发
═══════════════════════════════════════
#🔨contributing     — 贡献讨论
#🐛bug-reports      — Bug 讨论
#💡feature-ideas    — 功能建议（带投票）
#📦pr-reviews       — PR 审核请求

═══════════════════════════════════════
🌏 中文专区
═══════════════════════════════════════
#🇨🇳中文-闲聊
#🇨🇳中文-求助
#🇨🇳中文-资源分享

═══════════════════════════════════════
🎤 活动
═══════════════════════════════════════
#🎙️stage-chat       — Stage 活动文字互动
#📅events           — 活动日历
```

#### 5.2.2 新人引导（Onboarding Bot）

新人加入 Discord 时的自动化流程：

```
用户加入 Discord
  → 机器人 DM:
    "欢迎加入 Moltable 社区！👋
     
     快速开始：
     1. 在 #getting-started 看 3 分钟上手指南
     2. 去 https://moltable.ai 注册（30秒）
     3. 把你的 Agent 接进来
     
     有什么问题？在 #help 频道问，社区伙伴很快回复。
     中文用户 → #🇨🇳中文-闲聊"
     
  → 自动分配 @Newcomer 角色
  → 24 小时后自动移除 @Newcomer 角色，分配 @Member
```

#### 5.2.3 AMA 活动详细执行

**创始人 AMA（每两周）**：

```
格式: Discord 文字频道 #ama
时长: 1 小时
预热: 提前 3 天在 #announcements 和 Twitter 发预告
流程:
  - 前 30 分钟：收集问题（用 Discord Thread 整理）
  - 后 30 分钟：创始人逐条文字回复
  - 结束后：整理成 Blog 文章 "Moltable AMA #1: 大家最关心的 10 个问题"
```

**嘉宾 AMA（每月）**：

```
目标嘉宾:
  - AI Agent 生态工具的创始人/核心开发者
  - 开源社区知名维护者
  - 技术博主/YouTuber
  
流程:
  - 提前 2 周邀请，确认时间
  - 提前 1 周发预告（含嘉宾介绍 + 话题方向）
  - 当天用 Discord Stage（语音）进行
  - 录制并上传 YouTube
  - 结束后写一篇 Recap Blog
```

### 5.3 Twitter / X

#### 5.3.1 账号定位

| 维度 | 策略 |
|------|------|
| 人格 | 技术博主 + 产品创始人混合体：有技术深度但不失趣味 |
| 语言 | 双语（英文主帖 + 中文引用转发） |
| 内容比例 | 60% 产品/技术内容 + 20% AI Agent 行业洞察 + 20% 个人/社区互动 |
| 发布频率 | 每天 1-2 条（不轰炸） |
| 互动策略 | 每条推文发布后，30 分钟内回复所有评论 |

#### 5.3.2 内容日历模板（每周）

```
周一：行业观点
  例："Agent 碎片化是 2026 年最大的 AI 体验问题。每个人用 3-5 个 Agent，
       但没有一个共享身份层。这就是我们做 Moltable 的原因。"
  目标：建立思想领导力

周二：产品/技术
  例："换了一台新 Mac。只用了 3 分钟，Hermes 就恢复了我的所有环境配置。
       Moltable auto_provision: 一行命令，身份/偏好/项目地图全部到位。"
  目标：产品功能展示

周三：用户故事 RT
  转发社区用户的使用体验推文 + 评论
  目标：社会证明 + 社区激励

周四：开发日志
  例："这周在 Moltable 上加了混合搜索 RRF：
       向量相似度 + 全文搜索 + 标签过滤，一个 search_memory 调用搞定。
       今晚合并，下周发版。"
  目标：透明度 + 技术品牌

周五：互动/轻松
  例：投票："你们现在用几个 AI Agent？"
      选项：1个 / 2-3个 / 4-5个 / 6个以上
  目标：社区互动 + 市场调研

周末：分享他人内容
  转发 AI Agent、MCP、开源生态相关的优质推文 + 简短评论
  目标：生态融入 + 关系建立
```

#### 5.3.3 互动策略

- **在 AI Agent 圈 KOL 的推文下积极评论**（提供见解，不是推销）
- **回复每个提到 Moltable 的推文**（即使在别人帖子下的评论里）
- **关注竞品用户**：在 mem0、Letta 相关讨论中提供有价值的观点（"Moltable 和 mem0 是互补的——mem0 做记忆引擎，Moltable 做身份同步层"）
- **使用 Thread 深度展开**：每个产品功能介绍用 Thread（5-8 条），比单条推文传播力强 3-5 倍

### 5.4 中国社区运营

#### 5.4.1 即刻

> 即刻是中文 AI 圈最活跃的社区，没有之一。AI 工具讨论在这里有天然的高互动。

**策略**：

| 动作 | 频率 | 内容 |
|------|------|------|
| 产品动态帖 | 每周 2 次 | 新功能发布、Changelog 精选、使用技巧 |
| 个人故事帖 | 每周 1 次 | "我为什么做 Moltable"、"换电脑的痛" |
| 互动投票 | 每两周 1 次 | 新产品方向投票、功能优先级 |
| 转发圈友内容 | 随时 | 转发即刻上其他人的 AI 工具讨论 + 观点 |

**首发帖模板**：

```
📢 我做了一个 AI 身份同步工具：Moltable

问题：你用 Hermes + Claude Code + Cursor，三个 AI 各不认识对方。
     换台电脑，mcp.json 要重新写，Persona 要重新建，记忆全丢。

Moltable 解决了这件事：

🔗 一个身份接入，所有 Agent 自动同步
🧠 在 Claude 里聊过的事，Hermes 也记得
⚡ 换电脑 3 分钟恢复完整 AI 环境
💰 Free 就能用，Pro 只要 ¥19/月

开源：github.com/jovon-hot/moltable
注册：moltable.ai（30秒）

欢迎即刻的旁友们试试，反馈直接评论区说 👇
（附图 3-4 张：Landing Page + auto_provision 结果 + search_memory 截图）
```

#### 5.4.2 V2EX

**策略**：

```
节点：分享创造
标题：【分享创造】Moltable — AI 身份同步层，让你的所有 AI 共享记忆和配置

正文结构：
1. 痛点（2 句话）
2. 我的解决方案（3 句话）
3. 技术栈（Go + Supabase pgvector + MCP）
4. 开源链接
5. 邀请反馈

关键：
- V2EX 用户不吃纯营销，必须有技术细节
- 每一条评论都要回复（V2EX 互动率直接决定帖子热度排序）
- 帖子发出后 24 小时内是流量高峰，要蹲守回复
- 亮出"自托管"选项（V2EX 特别看重数据主权）
```

#### 5.4.3 掘金

**策略**：

```
系列文章计划：

第 1 篇：《Google A2A 协议实战：让 Claude 和 Hermes 共享上下文》
  → 技术深度 + 代码示例
  → 掘金用户爱看"协议 + 实战"

第 2 篇：《从零搭建 Agent 记忆系统：pgvector + RRF 混合搜索》
  → 技术教程向
  → 顺便引出 Moltable 的实现

第 3 篇：《换电脑后 3 分钟恢复 AI 环境是怎么做到的》
  → 场景 + 技术解析
  → 适合掘金沸点栏目

第 4 篇：《Agent 身份同步：为什么你的 AI 不该"失忆"》
  → 观点 + 趋势
```

**发布节奏**：每 2 周一篇，保持持续曝光。

#### 5.4.4 知乎

**策略**：

知乎更适合长尾 SEO 和深度讨论，不要指望短期爆发。

```
内容方向：
- 回答："有哪些好用的 AI Agent 工具？" → 融入 Moltable 介绍
- 回答："如何在不同 AI 助手之间共享记忆？" → Moltable 是最直接的答案
- 文章：《AI Agent 的"身份危机"——当我们换了 AI 助手，一切都要重来》
- 专栏：Moltable 开发周记（持续更新）

技巧：
- 知乎回答要"先给干货，再带产品"
- 截图要真实（不要营销图）
- 利用盐选专栏做技术深度输出
```

---

## 六、KOL / 布道者合作策略

### 6.1 分层合作模型

```
           影响力
              ↑
        ┌─────┼─────┐
        │ Tier 1    │  ← 行业 KOL / GitHub 万 Star 项目作者
        │ (<5 人)   │     深度合作：联名内容、独家 Persona、顾问角色
        ├───────────┤
        │ Tier 2    │  ← AI 领域博主 / 技术 YouTuber / 社区活跃者
        │ (10-20人) │     内容合作：测评、教程、产品反馈
        ├───────────┤
        │ Tier 3    │  ← 社区活跃用户 / 自发分享者
        │ (不限)     │     社区激励：周边、积分、荣誉角色
        └───────────┘
```

### 6.2 Tier 1：深度合作 KOL（<5 人）

**画像**：

- GitHub 5K+ Stars 开源项目作者
- AI Agent / MCP / 开发者工具领域的知名人物
- 中文 AI 圈有影响力的技术博主（即刻大 V / 掘金知名作者）

**合作方式**：

| 方式 | 细节 |
|------|------|
| **产品顾问** | 邀请成为 Moltable 产品顾问，参与 Roadmap 讨论，提供行业视角 |
| **联名 Persona** | KOL 独家发布以其命名的 Persona 模板（如 "@zhangsan-全栈视角"），增强双方品牌 |
| **深度测评** | KOL 深度使用 1 周，产出测评文章/视频（非付费软文，是真实体验分享） |
| **社区 AMA** | 在 Moltable Discord 做嘉宾 AMA |
| **收入分成** | 如未来有 Persona 市场付费功能，KOL 的独家 Persona 可参与分成 |

**邀请话术**：

```
[KOL 名字] 你好！

我是 [你的名字]，在做 Moltable (moltable.ai) — 
一个 AI Agent 身份同步层，基于 Google A2A 协议，开源。

我一直在关注你在 [领域] 的分享，特别认同你对 [具体观点] 的看法。

Moltable 解决的是"换 AI 就得重新调教"的问题 —
我自己用 Hermes + Claude Code，每天在两个 Agent 之间切，烦死了。
现在 auto_provision 一下，3 分钟恢复全部环境。

想邀请你试用一下，也想听听你的专业意见。
不需要写文章或推广 — 我就是想知道这个方向对不对，以及还有哪些坑。

有兴趣的话我可以发你一个 Pro 邀请码。
谢谢！
```

### 6.3 Tier 2：内容合作博主（10-20 人）

**画像**：

- 即刻 AI 圈活跃用户（1000+ 粉丝）
- B 站/YouTube 技术 UP 主（AI 工具/效率工具方向）
- 少数派/掘金作者
- Twitter AI Agent 生态关注者（500+ followers）

**合作方式**：

| 方式 | 激励 |
|------|------|
| 产品测评/教程 | Pro 一年 + 官网推荐位 |
| 视频演示 | Pro 一年 + 视频描述链接（UTM 追踪） |
| Bug Bounty | 找到 bug → 官网 Hall of Fame + Pro 一年 |
| Persona 投稿 | 优秀 Persona → 官方推荐 + 收益分成 |

**合作邀约 DM 模板**（即刻/Twitter）：

```
嘿！看到你经常分享 AI 工具，想问一下你有没有遇到过"换 AI 就要重新自我介绍"的痛？

我做了个工具 Moltable — 一个身份连上，所有 Agent 都能认识你。
免费，开源，30 秒注册。

想请你试用一下，如果你觉得有价值，可以分享一下体验。
没兴趣也可以直接说不，完全 OK 🙏
moltable.ai
```

### 6.4 Tier 3：社区自发布道者（不限）

**识别方式**：

- 在 Discord/即刻/Twitter 自发分享 Moltable 使用体验的用户
- 在 GitHub 提有价值 Issue/PR 的用户
- 在他人讨论中主动推荐 Moltable 的用户

**激励体系**：

```
🏅 Moltable 社区积分（Community Points）

积分获取：
  - 邀请新用户注册: +10 分（通过 referral link）
  - 提交有效 Bug Report: +5 分
  - 合并 PR: +20 分
  - 发布 Persona 模板: +5 分（被克隆一次额外 +1 分）
  - 帮助新人（Discord 标记为 "Answered"）: +2 分
  - 写 Blog/视频分享: +15 分
  - 翻译文档: +10 分

积分兑换：
  - 50 分：Moltable 贴纸套装
  - 100 分：Moltable 限量 T 恤
  - 200 分：Pro 一年
  - 500 分：Pro 终身 + 官网贡献者墙永久展示
  - 1000 分：Moltable Ambassador（官方认证 + 专属权益）
```

### 6.5 KOL 合作时间线

| 时间 | 动作 |
|------|------|
| Day 0-15 | 联系 Tier 2 博主（5-10 人），邀请早期试用 |
| Day 15-30 | 收集第一批评测内容，整理成"用户说"模块 |
| Day 30-60 | 联系 Tier 1 KOL（2-3 人），深度合作 |
| Day 60-90 | 启动 Ambassador 计划，开放社区申请 |
| Day 90-180 | 每月新增 2-3 位合作博主，形成持续内容产出 |

---

## 七、度量指标与里程碑

### 7.1 核心指标看板

| 指标 | 当前（Day 0） | 阶段一目标（Day 30） | 阶段二目标（Day 90） | 阶段三目标（Day 180） |
|------|:---:|:---:|:---:|:---:|
| **GitHub Stars** | 0（私有） | 100 | 500 | 1,000 |
| **注册用户** | 0 | 200 | 1,000 | 5,000 |
| **月活跃 Agent 连接（MAAC）** | 0 | 50 | 300 | 1,500 |
| **Pro 付费用户** | 0 | 10 | 50 | 200 |
| **Discord 成员** | 0（未建） | 100 | 500 | 2,000 |
| **GitHub Contributors** | 0 | 3 | 15 | 40 |
| **社区 Persona 数** | 0 | 10（官方） | 50 | 200 |
| **第三方 Connector** | 0 | 0 | 2 | 8 |
| **Twitter Followers** | 0 | 200 | 1,000 | 3,000 |
| **即刻粉丝** | 0 | 300 | 1,000 | 3,000 |

### 7.2 关键漏斗

```
流量来源
  ├─ 即刻/V2EX/掘金/知乎: ____ 访问/月
  ├─ Twitter/X: ____ 访问/月
  ├─ GitHub: ____ 访问/月
  ├─ 搜索引擎: ____ 访问/月
  └─ 直接/口碑: ____ 访问/月

Landing Page 访问
  └→ 注册转化率: ___%  （目标: >15%）

注册用户
  └→ Agent 连接率: ___%  （目标: >60%）
  └→ 首次记忆保存率: ___%  （目标: >40%）

月活跃用户
  └→ Pro 转化率: ___%  （目标: >5%）
  └→ 留存率（Day 7）: ___%  （目标: >30%）
  └→ 留存率（Day 30）: ___%  （目标: >20%）
```

### 7.3 预警机制

| 预警信号 | 阈值 | 响应动作 |
|----------|------|----------|
| Landing Page → 注册转化率 | <10% | 审查 Landing Page 文案 + 缩短注册流程 |
| 注册 → Agent 连接率 | <40% | 审查 Onboarding 指引 + 补充各平台截图教程 |
| Agent 连接 → 首次记忆 | <25% | 增加"种子记忆"自动创建 + AHA moment 引导 |
| Day 7 留存 | <20% | 强化邮件/通知触达 + 回访流失用户 |
| Pro 转化 | <3% | 审查定价 + Free 层体验优化 |
| Discord 消息量 | 连续 3 天 <5 条/天 | 发起讨论话题 + 举办活动 |

---

## 八、附录：即用物料清单

### 8.1 上线前必做清单

- [ ] GitHub 仓库公开（README 优化、Demo GIF、Issue 模板、CONTRIBUTING.md）
- [ ] Discord 服务器搭建（频道结构 + 欢迎 Bot + 规则）
- [ ] Landing Page SEO 优化（Title / Description / OG Tags / 结构化数据）
- [ ] 注册后自动欢迎邮件（含 3 分钟上手视频链接）
- [ ] "种子记忆"自动创建（3 条预置记忆）
- [ ] 匿名会话 7 天过期提醒机制
- [ ] 即刻首发帖准备（文字 + 配图）
- [ ] V2EX 分享创造帖准备
- [ ] Twitter 账号创建 + 首月内容日历准备
- [ ] 掘金第 1 篇文章《Google A2A 协议实战》准备
- [ ] 知乎关键词监控（"AI 记忆"、"Agent 同步"、"MCP 工具"）
- [ ] Blog 框架搭建 + 首篇 Changelog 准备

### 8.2 快速参考

| 链接 | 内容 |
|------|------|
| [moltable.ai](https://moltable.ai) | 官网 |
| [github.com/jovon-hot/moltable](https://github.com/jovon-hot/moltable) | GitHub（需公开） |
| MARKETING_PACKAGE.md | 市场包装完整方案（Slogan/定价/竞品对比/内容角度库） |
| ROADMAP.md | 产品路线图 |
| MOLTABLE_V3_PLAN.md | 产品方案 v3 |

### 8.3 社区建设核心原则

```
1. 前 100 个用户是一对一拉来的，不是等来的
2. 每一个用户反馈都要回复——即使只是 "知道了，已加入 backlog"
3. 社区不是你的用户群，是你的共建团队
4. Discord 不是广播频道，是双向对话
5. 让用户的故事被看到（Showcase、用户证言、Guest Blog）
6. 公开 Roadmap + 投票 = 最好的 community engagement
7. 永远不要用"沉默"回应社区——即使是坏消息也公开说
8. 竞品不是敌人，mem0 的用户也是 Moltable 的潜在用户
9. 身份网络效应是 Moltable 唯一的护城河——让用户离不开不是因为功能，是因为"所有 AI 都认识我"
10. 做基础设施的心态：用户 10 年后还在用，比用户 10 天内暴涨更重要
```

---

> **Moltable 不是一个工具——它是 AI 世界的 DNS。**
>
> 你的任务不是卖更多 Pro 账号，而是让"AI 身份同步"成为像"登录"一样的默认行为。当未来的 AI Agent 默认就带着 Moltable 连接时，你现在建立的社区就是那个标准的起源。
