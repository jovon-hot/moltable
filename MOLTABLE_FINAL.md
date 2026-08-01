# Moltable 完整方案

> 版本 3.1 · 2026-08-01  
> 核心理念：**AI Agent 的服务发现与环境同步层**  
> 一句话：旧 Agent 替你干活，新 Agent 瞬恢复环境。换台电脑，3 分钟一切就绪。

---

## 一、定位

### Moltable 是什么

```
Moltable = AI Agent 的服务发现 + 环境同步层

  不是 数据库           — 不存你的 PG 数据
  不是 笔记工具          — 不存你的 Obsidian 全文
  不是 记忆引擎          — 不是 mem0 的竞品
  不是 隧道代理          — 不暴露内网端口

  是   你的旧 Agent 在新电脑上能被发现
  是   你的身份和偏好在新 Agent 上自动恢复
  是   你的 Persona、Skills、MCP 配置一键同步
  是   你的 AI 环境的 iCloud + DNS
```

### 一句话

```
你在办公室 Mac 的 Hermes 工作了 6 个月。
去济南出差，新电脑装 Hermes，接入 Moltable。
你的旧 Hermes 被自动发现，新 Hermes 通过 A2A 协议
委托旧 Hermes 查询 PG、搜索 Obsidian、调用 Superset。

你只需要一个 Moltable 账号。其他都自动。
```

---

## 二、核心架构

### 双层架构

```
═══════════════════════════════════════════════════════════
第一层: 环境同步 (Moltable 直接存储)
═══════════════════════════════════════════════════════════

  身份                    偏好规则                  Persona 定义
  name: "王海东"           "中文回复"               CFO: system_prompt
  language: "zh"           "直接给结论"              CEO: system_prompt
  plan: "pro"              "数据驱动决策"

  Skills                   MCP 配置                  项目地图
  fost-report-generation   superset: url + headers   FOST 经营分析:
  fost-ceo                 wecom: url + bot token      PG at 93:5432
  (Pro: 完整内容同步)       (Pro: secret 加密)         Obsidian at hdlib

═══════════════════════════════════════════════════════════
第二层: Agent 间协作 (Moltable 做服务发现)
═══════════════════════════════════════════════════════════

  旧 Agent 注册                    新 Agent 发现
  ────────────                    ────────────
  "我是 office-mac"              auto_provision:
  A2A 端点: host:10000             knowledge_hosts:
  我能: search_knowledge             - office-mac: online
        query_database                  A2A: host:10000
        analyze_report                  能力: search + query + analyze
        push_wecom
                                   新 Agent → A2A → 旧 Agent:
  30s 心跳                          "帮我查 FOST 7 月利润率排名"
                                   ← "博山 23.1% 第一..."

═══════════════════════════════════════════════════════════
Pro 附加: 记忆缓存 (Moltable 云端存储，主机离线时兜底)
═══════════════════════════════════════════════════════════

  关键结论的热数据副本
  pgvector 向量 + 全文混合搜索
  "FOST 7 月份额 19.4%" — 办公室关机也能查到
```

### 架构图

```
┌─────────────────────────────────────────────────────────┐
│                    Moltable (云端)                       │
│                                                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐  │
│  │ 身份管理  │ │ 偏好规则  │ │ Persona │ │ 项目地图   │  │
│  │ whoami   │ │ rules    │ │ 角色切换 │ │ 数据在哪   │  │
│  └──────────┘ └──────────┘ └──────────┘ └───────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │          Agent 服务发现层 (A2A Registry)          │  │
│  │                                                  │  │
│  │  注册: "我是 office-mac, A2A at host:10000"       │  │
│  │  发现: "office-mac 在线, 能: search+query+analyze" │  │
│  │  心跳: 30s                                        │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │          记忆缓存 (Pro only)                      │  │
│  │  pgvector 混合搜索 · 离线兜底 · 关键结论热数据    │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
         │                              │
    注册 + 心跳                    发现 + 环境同步
         │                              │
    ┌────┴──────────┐          ┌───────┴──────────┐
    │  旧 Agent      │  A2A    │   新 Agent        │
    │  办公室 Mac    │◄────────►│   出差 Mac        │
    │               │          │                  │
    │ Hermes        │          │ Hermes           │
    │  ├ PG MCP     │  Task:   │  刚装好，空白     │
    │  ├ Superset   │ "查利润率"│                  │
    │  ├ Obsidian   │ ←Result: │  环境自动恢复     │
    │  ├ WeCom      │ "博山第一"│  数据委托旧Agent  │
    │  └ Skills     │          │                  │
    └───────────────┘          └──────────────────┘
```

---

## 三、A2A 协议：Agent 间委托

### 协议选择：Google A2A (Agent-to-Agent)

Google 2025 年发布的开放协议。核心概念：

| 概念 | 说明 |
|------|------|
| **Agent Card** | JSON 文档，声明 Agent 的身份、能力、端点 |
| **Task** | 一个 Agent 向另一个 Agent 发起的任务 |
| **Message** | 任务执行中的流式文本交换 |
| **Artifact** | 任务完成后的结构化产物 |

### Moltable 在 A2A 生态中的角色

```
A2A 标准定义了 Agent 间通信的协议。
但它不解决 "我的 Agent 在哪？" 的问题。

Moltable 做这一层:
  → "我的旧 Agent 在线吗？A2A 端点是多少？"
  → "它有什么能力？"
  → "我怎么认证自己就是王海东？"

Moltable = A2A Agent 的 DNS + 身份验证
```

### Agent Card 注册

```json
{
  "agent_card": {
    "name": "王海东的 Hermes (office-mac)",
    "description": "FOST 集团经营分析 Agent",
    "url": "http://192.168.14.17:10000",
    "provider": {"name": "Hermes", "url": "https://hermes-agent.nousresearch.com"},
    "capabilities": {
      "streaming": true,
      "push_notifications": false
    },
    "skills": [
      {"id": "search_knowledge", "description": "搜索 Obsidian 知识库和 PG 数据库"},
      {"id": "query_database", "description": "执行 PostgreSQL 查询 (FOST 业务数据)"},
      {"id": "analyze_report", "description": "生成 FOST 经营分析报表"},
      {"id": "push_wecom", "description": "推送企业微信消息"}
    ],
    "authentication": {
      "schemes": ["did_vc"],
      "issuer": "moltable"
    },
    "default_input_modes": ["text"],
    "default_output_modes": ["text"]
  }
}
```

---

## 四、端到端流程

### 场景：出差济南，恢复完整 AI 工作环境

```
T=0s  你打开新 Mac，装好 Hermes（完全空白）

T=2s  Hermes 接入 Moltable
      → curl -sL moltable.ai/connect.sh | bash -s -- <API-KEY>

T=3s  Hermes 调用 auto_provision
      → 身份恢复: "你是王海东，中文回复，数据驱动决策"
      → Persona 加载: CFO/CEO 定义
      → 项目地图: FOST 经营分析 — PG/Obsidian/Superset/WeCom
      → Skills 同步: fost-report-generation 自动写入
      → MCP 配置: superset + wecom 自动合并

T=4s  auto_provision 返回主机发现:
      knowledge_hosts:
        office-mac:
          status: "online"
          a2a_endpoint: "http://192.168.14.17:10000"
          a2a_capabilities: ["search_knowledge", "query_database", "analyze_report"]

T=5s  新 Hermes 通过 A2A 连接旧 Hermes
      → 验证 DID+VC 身份 (Moltable 签发)
      → 获取 Agent Card
      → "你能做什么？"
      → "我能搜 Obsidian、查 PG、跑报表、推 WeCom"

T=6s  用户: "查 7 月各站利润率排名"

      新 Hermes 构造 A2A Task:
        task = {
          "method": "analyze_report",
          "params": {
            "topic": "FOST 7月各检测站利润率排名",
            "persona": "CFO",
            "format": "ranked_table"
          }
        }

      旧 Hermes (办公室 Mac) 收到 Task，自动执行:
        → 调 MCP: superset → 拉 7 月数据
        → 调终端: PG → 跑利润率 SQL
        → 用 CFO Persona → 分析结果
        → 返回 Artifact

T=8s  新 Hermes 呈现结果:
      "7 月利润率排名:
       博山 23.1% 🥇  桓台 18.7% 🥈
       高青 15.3% 🥉  临淄 8.2% 垫底
       全市加权平均 14.6%，同比下降 2.1pp"

T=10s 用户: 完全恢复，开始工作 ✅
```

---

## 五、存储模型

### Moltable 直接存储

```
┌─────────────────────────────────────────────┐
│  身份层 (profile)                            │
│  ├─ name, email, language, timezone, plan    │
│  └─ 来源: 注册时设置，随时可更新              │
├─────────────────────────────────────────────┤
│  偏好规则 (preferences / rules)               │
│  ├─ "中文回复"                               │
│  ├─ "直接给结论，不啰嗦"                      │
│  ├─ "数据驱动决策，需要数字支撑"               │
│  └─ 纯文本列表，auto_provision 加载           │
├─────────────────────────────────────────────┤
│  Persona 定义                                 │
│  ├─ CFO: system_prompt, traits               │
│  ├─ CEO: system_prompt, traits               │
│  └─ Free ≤2 个, Pro ∞                       │
├─────────────────────────────────────────────┤
│  项目地图 (projects)                          │
│  └─ FOST 经营分析:                            │
│      knowledge_bases: [pg, obsidian, ...]    │
│      tools: [superset mcp, wecom, ...]        │
│      skills: [fost-ceo, fost-report, ...]     │
├─────────────────────────────────────────────┤
│  Agent 发现层 (knowledge_hosts)               │
│  ├─ hostname: office-mac                     │
│  ├─ a2a_endpoint: http://192.168.14.17:10000 │
│  ├─ agent_card: {capabilities, auth}         │
│  ├─ status: online                           │
│  └─ last_heartbeat: 2s 前                    │
├─────────────────────────────────────────────┤
│  记忆缓存 (Pro only)                          │
│  ├─ 关键结论热数据 (10,000 条上限)             │
│  ├─ pgvector 向量 + 全文混合搜索              │
│  ├─ 离线兜底 (主机断连时仍可用)                │
│  └─ 分类: preference / fact / decision / ...  │
└─────────────────────────────────────────────┘
```

### Moltable 不存储

```
  ❌ Obsidian 笔记全文 — 旧 Agent 通过 A2A 任务去搜
  ❌ PG 数据库数据 — 旧 Agent 通过 A2A 任务去查
  ❌ Superset 图表 — 旧 Agent 通过 A2A 任务去拉
  ❌ 本地文件内容 — 旧 Agent 通过 A2A 任务去读
  ❌ LLM 推理 — 旧 Agent / 新 Agent 各自的 LLM
  ❌ 对话历史 — Agent 自己的会话管理
```

---

## 六、MCP 工具清单

### Free 层（8 个）

| 工具 | 职责 |
|------|------|
| `restore_profile` | 一键恢复：身份 + 偏好 + Persona + 项目地图 + Agent 发现 |
| `list_projects` | 列出项目 + knowledge_bases + tools + skills |
| `get_project` | 获取单个项目的完整环境配置 |
| `create_project` | 创建项目环境 |
| `update_project` | 更新项目环境 |
| `list_personas` | 列出所有 Persona 定义（含 memory_count） |
| `get_persona` | 获取 Persona 完整 system_prompt |
| `ping` | 心跳检测 |

### Pro 层（+5 个）

| 工具 | 职责 |
|------|------|
| `search_memory` | 混合搜索（向量 + 全文，三级回退） |
| `save_memory` | 保存记忆（语义去重） |
| `update_memory` | 更新记忆 |
| `archive_memory` | 软删除记忆 |
| `list_skills` | 列出关联的 Skills（含版本号和安装源） |

### 明确砍掉

| 工具 | 原因 |
|------|------|
| ~~`consult_persona`~~ | 需 LLM。Agent 端模型更强 |
| ~~`match_persona`~~ | 同上 |
| ~~`compare_personas`~~ | 同上 |
| ~~`save_memories`~~ | 合并到 save_memory |
| ~~`search_by_tag`~~ | 合并到 search_memory (加 tags 参数) |

---

## 七、定价

| | Free | Pro (¥19/月) |
|--|------|------------|
| 身份 | ✅ | ✅ |
| 偏好规则 | ✅ ≤50 条 | ✅ |
| Persona | ✅ ≤2 个 | ✅ ∞ |
| 项目地图 | ✅ ∞ | ✅ |
| Agent 发现 | ✅ 1 主机 | ✅ ∞ |
| Skills 同步 | ✅ (git 引用) | ✅ +内容同步 |
| MCP 配置 | ✅ | ✅ +secret 加密 |
| **记忆缓存** | **100 条** | **10,000 条** |
| 混合搜索 | ✅ | ✅ |
| 离线兜底 | ⚠️ 100 条 | ✅ 10,000 条 |

**设计逻辑：** Free 层 100 条记忆 = 诱饵。重度用户 2-3 天打满 → 触发 Pro 升级。Pro ¥19/月 ≈ 一杯咖啡，比 mem0 便宜 10 倍。

---

## 八、与现有生态的关系

| 系统 | 关系 |
|------|------|
| **mem0** | 旧记忆原地保留。新记忆存 Moltable。mem0 用户是最精准的 Pro 转化池 |
| **Obsidian** | 知识库，不在 Moltable。旧 Agent 通过 A2A 任务去搜 |
| **Notion** | 同 Obsidian |
| **PG 数据库** | 业务数据，不在 Moltable。旧 Agent 通过 A2A 任务去查 |
| **Hermes Skills** | Free 存 git 引用，Pro 存完整内容自动同步 |
| **MCP 服务器** | 配置存 Moltable，Agent 自动恢复连接 |

### 与 mem0 的差异化

```
mem0:    "我替你存记忆"
Moltable: "我让你的旧 Agent 替新 Agent 干活"

mem0 卖的是存储。Moltable 卖的是连接。
mem0 你还需要自己管环境。Moltable 环境也自动恢复。

mem0 用户 + Moltable = 完美组合
  记忆存 mem0 或 Moltable Pro (你自己选)
  环境恢复靠 Moltable (只有 Moltable 做)
```

---

## 九、安全模型

```
A2A 方案的安全模型 vs 隧道方案:

  隧道方案:
    办公室端口 → Cloudflare 公网 → 全球可达 ❌
    Cloudflare 能看到所有 SQL 查询结果 ❌
    需要额外安全措施 (JWT, 路径白名单, mTLS) ❌

  A2A 方案:
    旧 Agent 的内部端点 ← A2A 协议 → 新 Agent ✅
    旧 Agent 已有的全部认证和权限控制 ✅
    不暴露任何新端口 ✅
    不需要额外安全组件 ✅
    攻击面: 仅 A2A 端点 (Agent 已有的攻击面) ✅

  Moltable 的角色:
    签发 DID+VC 身份凭证 → 两个 Agent 互信
    不做数据中转 → 看不见你的数据
```

---

## 十、竞品格局

| 维度 | mem0 | Zep | Letta | ChatGPT | **Moltable** |
|------|:---:|:---:|:---:|:---:|:---:|
| 记忆存储 | ✅ | ✅ | ✅ | ✅ | ✅ (Pro) |
| **跨平台身份** | ❌ | ❌ | ❌ | ❌ | **✅** |
| **Persona** | ❌ | ❌ | ✅ | ⚠️ | **✅** |
| **Agent 发现** | ❌ | ❌ | ❌ | ❌ | **✅** |
| **A2A 注册** | ❌ | ❌ | ❌ | ❌ | **✅** |
| **环境同步** | ❌ | ❌ | ❌ | ❌ | **✅** |
| MCP | ✅ | ❌ | ❌ | ❌ | ✅ |
| 开源 | ✅ | ❌ | ✅ | ❌ | ✅ (MIT) |
| 入门价 | $19/月 | $125/月 | $20/月 | 免费 | ¥19/月 |

**Moltable 唯一做的：Agent 环境快照 + Agent 间服务发现。**

mem0 做记忆引擎。Zep 做企业记忆。Letta 做有状态 Agent。ChatGPT 做端到端体验。
Moltable 做它们都不做的事——让你换台电脑，3 分钟一切就绪。

---

## 十一、实施路线

| 阶段 | 内容 | 预估 |
|:--:|------|:--:|
| **P0** | 精简 MCP 至 13 工具。quota 门控。Free/Pro 隔离 | 3h |
| **P1** | restore_profile 更名为 auto_provision。补全 plan/instructions/skills 字段 | 2h |
| **P2** | Agent 发现层：knowledge_hosts 表 + API + Agent Card 注册 | 4h |
| **P3** | A2A 端点支持：Hermes 端 Agent Card 暴露 + Moltable 签发凭证 | 6h |
| **P4** | 记忆缓存增强：RRF 混合搜索 + 语义去重 + 离线兜底 | 4h |
| **P5** | Dashboard：记忆管理 + Agent 状态 + 知识源管理 | 6h |
| **P6** | 计费上线：Stripe + 免费额度 + 升级流程 | 3h |

---

## 十二、一句话

```
Moltable 不存你的数据，不转发你的请求，不替代你的 Agent。

Moltable 只做一件事:
  让你的新 Agent 找到旧 Agent，
  旧 Agent 替你干活，
  新 Agent 瞬间恢复你的完整 AI 工作环境。

  就像换 iPhone 时 iCloud 恢复一切。
  就像换电脑时 Git clone 拉回代码。

  Moltable = AI Agent 的 iCloud + DNS。
```
