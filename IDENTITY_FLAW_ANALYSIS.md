# Moltable v2 身份认证缺陷分析与业界最新解决方案

> 分析日期: 2026-07-29 | 基于网上最新资料

---

## 一、当前认证体系的致命缺陷

### 1.1 现状：Moltable v2 的三个认证通道

```
请求 → get_user()
  ├── 1. Bearer JWT → Supabase auth.get_user()
  ├── 2. X-API-Key → PBKDF2-HMAC + pepper 哈希匹配
  └── 3. X-Session-Token → sessions 表验证
```

代码位置: `server/routes/auth.py:46-108`

### 1.2 核心缺陷

| 缺陷 | 严重度 | 说明 |
|------|--------|------|
| **API Key = 人类身份 ≠ Agent 身份** | 🔴 致命 | 任何一个持有 API Key 的人/程序都可以伪装成任何 Agent。无法区分是 Hermes Agent 还是 Claude Agent 发来的请求 |
| **无法验证 Agent 出处** | 🔴 致命 | X-AI-ID 不携带任何密码学证明。任意 HTTP 客户端设置任意 AI-ID 即可冒充 |
| **无 Agent 能力证明** | 🟡 高 | 无法验证调用方是否真的是 AI Agent（而非脚本），以及它的能力边界 |
| **单方信任模型** | 🟡 高 | 完全依赖服务端信任客户端自报的身份。无双向认证、无可验证凭证 |
| **无 Agent 信誉链** | 🟡 中 | 无法追溯 Agent 的历史行为、所属平台、被谁创建/授权 |
| **跨平台身份假象** | 🟡 中 | "跨平台"靠的是同一个 API Key 被多个 Agent 共享。这本质上是 API Key 共享，不是真正 Agent 身份互认 |

### 1.3 根本原因

Moltable 用**人类用户的认证框架**（API Key / JWT）去认证 **AI Agent**，但两者有本质区别：

| | 人类用户 | AI Agent |
|---|----------|----------|
| 身份载体 | 电子邮件 + 密码 | 密码学密钥对 |
| 身份生命周期 | 注册一次，长期有效 | 可创建/销毁/委托多个 Agent |
| 信任来源 | OAuth Provider (Google/GitHub) | Agent 平台签名 + VC 凭证 |
| 跨平台含义 | 同一个人的多个设备 | 多个 Agent Framework 互认同一个用户 |
| 授权粒度 | 全量 API 访问 | 每个 Agent 应有独立权限范围 |

---

## 二、业界最新解决方案

### 2.1 MCP 协议官方授权规范 (2025-06-18 → 2026-07-28)

**来源**: https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization

MCP 规范明确要求 HTTP transport 使用 **OAuth 2.1** 授权框架：

- **角色定义**: MCP Server = Resource Server, MCP Client = OAuth Client
- **服务发现**: 基于 RFC9728 (OAuth 2.0 Protected Resource Metadata)
- **动态客户端注册**: 基于 RFC7591 (DCR)
- **Token 绑定**: Access Token 须绑定 audience，防止混淆代理攻击
- **STDIO Transport 例外**: 仅用于本地 Agent，从环境变量获取凭证

**Moltable 适配建议**: 
- HTTP MCP 端点 (`routes/mcp.py`) 应实现 OAuth 2.1 Authorization Code Flow
- 添加 `/.well-known/oauth-protected-resource` 发现端点 (RFC9728)
- 支持 DCR 让 Agent 平台动态注册为 OAuth Client

---

### 2.2 AgentDID — 基于 DID+VC 的去中心化 Agent 身份

**来源**: https://github.com/BDS-SDU/AgentDID (论文: "AgentDID: Trustless Identity Authentication for AI Agents")

**核心思想**: 用 W3C 标准的 DID (Decentralized Identifier) + VC (Verifiable Credential) 为每个 AI Agent 建立密码学身份。

**架构**:
```
Holder Agent (持有者)          Verifier Agent (验证者)
       │                              │
       ├── 生成密钥对 ←──────────────→ ├── 验证签名
       ├── 注册 DID                    ├── 挑战-响应验证
       ├── 获取 VC (Issuer签发)        ├── 上下文一致性检查
       ├── 出示 VP (可验证表达)        └── 信任决策
       └── 执行 Probe Task
```

**关键能力**:
| 能力 | 说明 |
|------|------|
| DID 注册 | 每个 Agent 生成独立密钥对，注册为 DID |
| 委托授权 | 用户可通过 Delegate 机制授权 Agent 代行身份 |
| VC 签发 | Issuer 服务为 Agent 签发能力/身份凭证 |
| VP 出示 | Agent 可选择性出示凭证（零知识证明思想） |
| 上下文一致性检查 | Verifier 不仅验签名，还验 Agent 状态是否符合预期 |
| Probe Task | 通过探针任务验证 Agent 真实能力（非仅验凭证） |

**Moltable 适配建议**: 
- 最核心的思想是 **Probe Task** — 不仅验证"你是谁"，还验证"你是否真的是你声称的那个 Agent"
- 可仿照实现 Agent 注册时要求完成一次 challenge-response 验证

---

### 2.3 Casdoor — Agent-First IAM / MCP Gateway

**来源**: https://github.com/casdoor/casdoor ⭐14,074

目前最成熟的 "Agent-first" 身份认证系统：

- **MCP 原生支持**: 内置 MCP Gateway，支持 Agent 通过 MCP 协议认证
- **多协议**: OAuth 2.0, OIDC, SAML, LDAP, WebAuthn
- **Web UI**: 完整的身份管理后台
- **权限模型**: RBAC + ABAC，支持细粒度 Agent 权限控制
- **OpenClaw 集成**: 已支持 OpenClaw Agent 框架

**Moltable 适配建议**: 
- Casdoor 可作为 Moltable 的 Auth Provider
- 替代当前 Supabase Auth，获得 Agent 级别的权限控制
- 通过 Casdoor MCP Gateway 统一管理 Agent 认证

---

### 2.4 HelixID — 专为 AI Agent 设计的身份层

**来源**: https://github.com/dgverse-labs/helixid

**定位**: "Open-source identity and authorization layer for AI agents"

**核心组件**:
```
helix-core/     — 核心 VC/DID 逻辑
helix-api/      — REST API
helix-sdk-js/   — JavaScript SDK
console/        — 管理控制台
```

**差异优势 vs AgentDID**:
- 更成熟：77 commits, 15 tags, CI/CD, e2e 测试
- 范围更广：不仅是身份验证，还包括授权 (authorization)
- 有管理后台：Console 可视化操作
- TypeScript 全栈：更适合 Web/Node.js 生态

**Moltable 适配建议**: 
- HelixID 的架构与 Moltable 的 Identity→Persona→Agent 三层模型高度契合
- 可用 HelixID 替换当前 `auth.py`，为每个 Persona/Agent 签发独立 VC

---

### 2.5 Bindu — Agent 身份+通信+支付一体化

**来源**: https://github.com/GetBindu/Bindu ⭐7,887

**定位**: "The identity, communication, and payments layer for AI agents"

**核心特性**:
- Agent 身份注册与验证
- Agent 间通信协议
- 内置支付/结算
- Web UI 管理

**Moltable 适配建议**: 
- Bindu 的支付能力补充了 Moltable 仅有的 Stripe 订阅
- 如果 Moltable 未来要支持 Agent 间交易，Bindu 可作为底层

---

### 2.6 Microsoft Agent Governance Toolkit

**来源**: https://github.com/microsoft/agent-governance-toolkit ⭐5,295

**微软出品，强调企业级治理**:

| 能力 | 说明 |
|------|------|
| Zero-Trust Identity | 每个 Agent 请求都需完整验证，不信任网络位置 |
| Policy Enforcement | 声明式策略引擎，约束 Agent 行为边界 |
| Execution Sandboxing | Agent 代码在沙箱中执行 |
| Reliability Engineering | 故障恢复、降级策略 |

**核心启示**: Agent 身份不仅是一张凭证，还需要运行时的持续策略执行。Moltable 可借鉴其策略引擎设计。

---

### 2.7 Unicity Sphere SDK — 自主经济 Agent 身份

**来源**: https://github.com/unicity-sphere/sphere-sdk ⭐5,427

**定位**: "Give an agent an identity, a wallet, and the ability to find, negotiate with, and settle with other agents — peer-to-peer"

与 Moltable 的 AI 经济协作定位最接近。其 Agent 身份模型:
- 每个 Agent 有独立钱包
- P2P 发现与协商
- 密码学身份证明

---

## 三、方案对比与推荐路径

### 3.1 五条路径对比

| 方案 | 复杂度 | 成熟度 | 适合 Moltable? | 说明 |
|------|:---:|:---:|:---:|------|
| **A. MCP OAuth 2.1 标准** | 中 | 高 | ⭐⭐⭐⭐⭐ | MCP 官方规范，最安全，但需引入 OAuth Server |
| **B. DID + VC (AgentDID/HelixID)** | 高 | 中 | ⭐⭐⭐⭐ | 最前沿，去中心化，但生态尚早 |
| **C. Casdoor 集成** | 低 | 高 | ⭐⭐⭐⭐⭐ | 最快实施，替换 Supabase Auth |
| **D. API Key + Agent Signature** | 低 | 高 | ⭐⭐⭐⭐ | 渐进式改进，最小改动 |
| **E. Bindu 全套** | 中 | 中 | ⭐⭐⭐ | 功能最全，但耦合度高 |

### 3.2 推荐：三阶段演进路径

```
Phase 1 (立即): API Key + Agent 签名
  → 在现有 API Key 基础上，要求 Agent 用密钥对消息签名
  → X-Agent-Signature: Ed25519(api_key + timestamp + body_hash)
  → 工作量: 1-2天

Phase 2 (短期): MCP OAuth 2.1 标准授权
  → 实现 RFC9728 Protected Resource Metadata
  → 支持 DCR (Dynamic Client Registration)
  → Agent 平台注册为 OAuth Client，获取短期 Access Token
  → 工作量: 1-2周

Phase 3 (中期): DID + VC 去中心化身份
  → 每个 Persona/Agent 注册为独立 DID
  → 用户通过 VC 授权 Agent 代行身份
  → Agent 间可验证彼此身份，无需信任中心服务器
  → 工作量: 1-2月
```

### 3.3 最小可行改进（今天就做）

在 `server/routes/auth.py` 中增加第四条认证通道：

```python
# 4. Agent Signature 验证
if x_agent_signature and x_agent_id:
    # 从 agent_registry 获取公钥
    pubkey = get_agent_pubkey(x_agent_id)
    # 验证签名: Sign(api_key + timestamp + body)
    message = f"{x_api_key}:{x_timestamp}:{body_hash}"
    if verify_ed25519(pubkey, message, x_agent_signature):
        return x_agent_id
```

配合 `agent_registry` 表：
```sql
CREATE TABLE agent_registry (
    agent_id     TEXT PRIMARY KEY,
    user_id      UUID REFERENCES users(id),
    platform     TEXT,       -- 'hermes', 'claude', 'chatgpt'
    public_key   TEXT,       -- Ed25519 公钥
    capabilities JSONB,      -- Agent 能力声明
    created_at   TIMESTAMPTZ
);
```

---

## 四、安全强度对比

```
当前方案:   API Key ──────────────────→  服务端验证   (强度: ★★☆☆☆)
                                    🚨 任何人都能用

Phase 1:    API Key + Ed25519签名 ──→  服务端验签   (强度: ★★★★☆)
                                    复制Key不够，还需私钥

Phase 2:    OAuth 2.1 + DCR ────────→  Token + Scope (强度: ★★★★★)
                                    业界标准，审计完备

Phase 3:    DID + VC ───────────────→  去中心化信任 (强度: ★★★★★)
                                    无需信任中心服务器
```

---

## 参考资料

| 资源 | 链接 |
|------|------|
| MCP 授权规范 (最新) | https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization |
| AgentDID 论文+代码 | https://github.com/BDS-SDU/AgentDID |
| HelixID 身份层 | https://github.com/dgverse-labs/helixid |
| Casdoor Agent IAM | https://github.com/casdoor/casdoor |
| Microsoft Agent Governance | https://github.com/microsoft/agent-governance-toolkit |
| Bindu Agent 身份层 | https://github.com/GetBindu/Bindu |
| Unicity Sphere SDK | https://github.com/unicity-sphere/sphere-sdk |
