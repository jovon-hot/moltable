# Moltable v2 (DID+VC) — 竞品分析与上线就绪度评估

> 日期: 2026-07-29 | 版本: 0.2.0 | 综合评分: **尚未就绪** (B / 72)

---

## 一、竞品全景图

### 1.1 快速对比

```
                    记忆存储  跨平台  身份层  Persona  MCP    VC/DID   开源   Stars
mem0                 ✅        ⚠️      ❌      ❌       ✅     ❌        ✅   24k+
Letta (MemGPT)       ✅        ❌      ❌      ✅       ❌     ❌        ✅   13k+
LangMem              ✅        ❌      ❌      ❌       ❌     ❌        ✅    2k+
ChatGPT Memory       ✅        ❌      ❌      ⚠️       ❌     ❌        ❌    —
Zep                  ✅        ✅      ❌      ❌       ❌     ❌        ✅    2k+
Bindu                ✅        ✅      ✅      ❌       ❌     ❌        ✅    8k
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Moltable v2          ✅        ✅      ✅      ✅       ✅     ✅        ✅    —
```

**Moltable 是唯一同时覆盖 7 个维度的产品。**

---

### 1.2 逐竞品分析

#### mem0 (⭐24k) — 最大竞品

| 维度 | 评价 |
|------|------|
| 核心能力 | 开发者 AI 记忆 SDK，自动从对话中提取+存储事实/偏好 |
| 覆盖度 | 纯记忆层，无身份/Persona/VC。Python/TS 双语言 SDK |
| 与 Moltable 重叠 | 高——`search_memory` / `save_memory` 直接竞争 |
| Moltable 差异化 | Persona 系统、DID+VC 密码学身份、auto_provision 一键配置、匿名会话 |
| Moltable 不足 | mem0 有 24k stars + YC 背书 + 完整文档 + 社区插件；Moltable 对比体量悬殊 |

**结论**: mem0 赢了开发者心智。Moltable 不需要赢 mem0——mem0 是 SDK，Moltable 是平台。**互补而非替代**。

---

#### Letta (⭐13k) — 最像 Moltable Persona

| 维度 | 评价 |
|------|------|
| 核心能力 | "有状态的 AI Agent"，Agent 有持久化记忆和人格 |
| 覆盖度 | Letta 的 "Agent 状态" ≈ Moltable 的 "Persona + Memory" |
| 与 Moltable 重叠 | 中——Persona 概念重叠，但 Letta 偏向单 Agent 自记忆 |
| Moltable 差异化 | 跨 Agent 身份共享（同一套记忆，多 Agent 多 Persona）、DID+VC、MCP 原生 |
| Moltable 不足 | Letta 有成熟的 Agent 运行时和部署方案；Moltable 仅是 HTTP/MCP 服务 |

**结论**: Letta 是 Agent 框架，Moltable 是身份平台。**互补**。

---

#### LangMem (⭐2k)

LangChain 生态的记忆 SDK。纯代码库，无平台。Moltable 可被 LangMem 用户作为外部记忆后端接入。

**结论**: 不竞争。Moltable 可提供 MCP endpoint 给 LangChain Agent 用。

---

#### ChatGPT Memory

OpenAI 内置，用户无感知，自动从对话中提取"记忆"。封闭生态、不跨平台、不可审计。

| 维度 | 评价 |
|------|------|
| vs Moltable | ChatGPT Memory 的用户体验最好（零配置），但锁在 OpenAI 生态内 |
| Moltable 优势 | 跨平台（Hermes/Claude/ChatGPT 共享记忆）、用户可控、DID+VC 密码学身份 |
| Moltable 劣势 | 用户需要注册+配置，ChatGPT Memory 完全无感 |

**结论**: 最可怕的竞品——不是因为技术，而是因为用户量。Moltable **必须**做到注册体验跟 ChatGPT Memory 一样简单否则没人用。

---

#### Zep (⭐2k) — 企业级

持久化对话历史 + 摘要 + 向量搜索。面向企业、有 SaaS 版。

| 维度 | 评价 |
|------|------|
| vs Moltable | Zep 是企业级对话记忆，无身份/Persona/DID |
| Moltable 优势 | Persona、DID+VC、匿名会话、零注册体验 |
| Zep 优势 | 生产就绪（监控、SLA、合规）、完整企业特性 |

**结论**: 分层竞争——Zep 是企业对话存档，Moltable 是个人 AI 身份。不冲突。

---

#### Bindu (⭐8k)

"Agent 身份+通信+支付层"。概念上与 Moltable 最接近。

| 维度 | 评价 |
|------|------|
| 核心能力 | Agent 注册、发现、通信、支付。有 Web UI |
| 与 Moltable 重叠 | 概念重叠最高——都有"Agent 身份"概念 |
| Moltable 差异化 | DID+VC 密码学身份（Bindu 未开源核心）、MCP 原生、Persona 系统 |
| Bindu 优势 | 内置支付、Agent 间通信协议、更大社区 |

**结论**: 最直接的竞争对手。但 Bindu 偏 Agent-to-Agent 交易，Moltable 偏 Human-Agent 身份层。**市场定位不同**。

---

### 1.3 竞争结论

```
同赛道内 Moltable 有两层防御：
  
  1. 上层（产品定位）: 唯一同时做"身份 + 记忆 + Persona"的平台
     — mem0 只有记忆，Letta 只有 Agent 状态，Bindu 偏 A2A 交易
  
  2. 下层（技术壁垒）: DID+VC 密码学身份
     — 无竞品实现（Bindu 有身份但不开源核心，AgentDID 是论文代码）
```

**但这不是蓝海。mem0 和 ChatGPT Memory 已经定义了用户的期待：AI 记忆应该是零配置、自动的。Moltable 的注册流程即使已做得足够简单，对用户来说仍是"多一步"。**

---

## 二、Moltable v2 上线就绪度

### 2.1 逐维度评分

| 维度 | 分数 | 状态 | 阻塞上线？ |
|------|:---:|------|:---:|
| 产品完整度 | **78** | MVP 核心功能完好，但缺：博客(占位)、多语言记忆搜索体验 | ❌ |
| 技术架构 | **85** | 分层清晰、降级优雅、离线友好 | ❌ |
| 安全 | **90** | PBKDF2 + RLS + AuditLog + DID+VC | ❌ |
| 测试 | **65** | 4 个单元测试 + E2E 脚本，无集成测试、无真实 Supabase 环境 | 🟡 |
| 部署运维 | **50** | Docker 有但未验证、缺 web Dockerfile、无监控、无备份 | 🔴 |
| MCP 合规 | **92** | JSON-RPC 2.0 完整实现、12 工具 | ❌ |
| 前端 | **78** | 9 页面功能完整，但博客占位、无 SEO、无邮件验证 | 🟡 |
| 浏览器插件 | **65** | 代码完整但零实机验证 | 🟡 |
| 文档 | **85** | README/PRD/DESIGN/3轮PDCA复盘——内部文档齐全，缺用户教程 | ❌ |
| **综合** | **72** | **B 级——可内测，不可公开上线** | |

---

### 2.2 阻塞上线的问题（P0 — 修完才能上线）

| # | 问题 | 严重度 | 后果 |
|---|------|:---:|------|
| **1** | `web/Dockerfile` **不存在** | 🔴 | `docker-compose up` 构建 web 服务直接失败 |
| **2** | **无法完整构建运行** | 🔴 | 源代码缺少关键文件，任何新用户在本地跑不起来 |
| **3** | **无生产数据库** | 🔴 | Supabase 仅用于开发，生产环境需独立的 DB 实例或有 Supabase Pro |
| **4** | **Issuer 私钥管理** | 🔴 | 首次启动自动生成私钥并 log 到控制台。重启后密钥丢失 → 所有 VC 验证失败。生产环境必须 KMS/Vault |
| **5** | **零实机测试** | 🔴 | Agent experience 脚本是本地 mock，未对接真实 Hermes/Claude |

---

### 2.3 建议上线前完成（P1 — 强烈建议）

| # | 问题 | 工作量 |
|---|------|:---:|
| 6 | Chrome 插件在 Chrome 上实机加载测试 | 1h |
| 7 | 前端 SEO + 邮件验证（依赖 Supabase模板） | 2h |
| 8 | 集成测试（真实 Supabase + Docker Compose） | 3h |
| 9 | 补充 `web/Dockerfile` | 0.5h |
| 10 | 博客页替换为实际 Changelog | 1h |

---

### 2.4 上线后迭代（P2）

| # | 问题 |
|---|------|
| 11 | 监控（Prometheus/Grafana） |
| 12 | Redis 缓存层 |
| 13 | 负载测试 |
| 14 | 数据库连接池 |
| 15 | 性能分析 |
| 16 | HTTPS/TLS 自动配置 |

---

## 三、如果明天上线用户会碰到什么

### 3.1 新用户注册流程

```
用户访问 moltable.ai
  → Landing 页 ✅ 好看
  → 点注册 → ✅ 能注册
  → Dashboard "连接 Agent" → 生成 Enrollment Token ✅
  → 发给 AI...

  🚨 问题1: AI 没有装 Moltable Skill → 不知道怎么用
  🚨 问题2: Skill 文件在本地硬编码了 localhost:8701 → 远程用不了
  🚨 问题3: Chrome 插件未在 Chrome Web Store 发布 → 浏览器用户无法安装
```

### 3.2 老用户日常使用

```
用户打开 Hermes:
  → ai_provision() 正常 ✅
  → search_memory 正常 ✅

  🚨 问题4: 如果 Supabase 挂了，全部降级到 in-memory demo 模式
            → 用户记忆丢失 → 体验灾难
  🚨 问题5: 无数据备份 → Supabase 数据损坏不可恢复
```

### 3.3 开发者接入

```
开发者看文档 → pip install moltable-sdk → 5 行代码 OK

  🚨 问题6: 没有 Go SDK → 非 Python 用户无法接入
  🚨 问题7: 没有 Swagger → 看源码才知道 API 端点
  🚨 问题8: 没有 Postman Collection → 手动 curl
```

---

## 四、阶段性结论与建议

### 4.1 定位判断

| | |
|---|---|
| **是个好产品吗？** | 是。概念清晰（AI Identity Layer）、差异化明确（DID+VC+Persona）、技术架构完整 |
| **有竞品吗？** | mem0 是最大威胁（24k stars + YC）。但定位不同——Moltable 唯一同时做身份+记忆+Persona |
| **现在能上线吗？** | **不能。** P0 有 5 个阻塞项。先跑通完整 Docker Compose 构建 + 对接真实 Agent |

### 4.2 上线路径

```
Week 1: 修 P0（Dockerfile + 生产配置 + Issuer 密钥管理）
Week 2: 修 P1（插件实机 + SEO + 集成测试）
Week 3: 内测 — 赵海东本人作为唯一用户，连接真实 Hermes
Week 4: 灰度 — 邀请 3-5 个内测用户
Week 5: 公开 Beta
```

### 4.3 一句话

**Moltable v2 已经是市场上概念最完整的 AI 身份平台，但还要再跑 2-3 周才能面对真实用户。目前的状态是"内测就绪，公开不够"。**
