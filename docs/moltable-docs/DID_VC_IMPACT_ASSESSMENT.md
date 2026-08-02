# DID+VC 方案对 Moltable v2 的影响评估

> 日期: 2026-07-29 | 评估尺度: 逐文件、逐模块、逐接口

---

## 一、方案定义

**目标**: 用 W3C DID (Decentralized Identifier) + VC (Verifiable Credential) 替换现有的 API Key/JWT 认证体系。

**参考实现**: HelixID (dgverse-labs, W3C VC 2.0 + DID 1.0 标准) + AgentDID (BDS-SDU, DID+VC+Probe Task)

**HelixID 五层信任栈**:

| 层 | 功能 |
|---|---|
| Identity | 每个 Agent 有 DID，绑定到 Ed25519 密钥对 |
| Authority | 限范围的 VC，证明 Agent 被授权做什么 |
| Enforcement | 运行时验证 + 授权检查 |
| Discovery | 跨组织服务发现，无需预先交换密钥 |
| Accountability | 密码学审计链，所有操作可追溯 |

---

## 二、数据库 Schema 变更

### 2.1 新增表（必须）

```sql
-- 替换 api_keys 表的核心
CREATE TABLE did_registry (
    did             TEXT PRIMARY KEY,       -- did:web:moltable.ai:agent:xxx
    user_id         UUID REFERENCES users(id),
    public_key      TEXT NOT NULL,          -- Ed25519 公钥 (base58)
    key_type        TEXT DEFAULT 'Ed25519VerificationKey2020',
    controller      TEXT NOT NULL,          -- 谁控制这个 DID (user_id 的 DID)
    status          TEXT DEFAULT 'active',  -- active/revoked/expired
    created_at      TIMESTAMPTZ DEFAULT now(),
    revoked_at      TIMESTAMPTZ
);

-- VC (Verifiable Credential) 存储
CREATE TABLE credentials (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    credential_jwt  TEXT NOT NULL,          -- JWT 格式的 VC
    issuer_did      TEXT NOT NULL,          -- 签发者 DID (Moltable Issuer)
    subject_did     TEXT NOT NULL,          -- 被签发者 DID (Agent)
    credential_type TEXT NOT NULL,          -- 'AgentIdentityCredential' | 'PersonaDelegationCredential' | ...
    claims          JSONB NOT NULL,         -- 声明内容 (platform, capabilities, persona_id 等)
    expires_at      TIMESTAMPTZ,
    revoked_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- VP (Verifiable Presentation) 审计
CREATE TABLE presentations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    presentation_jwt TEXT NOT NULL,         -- JWT 格式的 VP
    holder_did      TEXT NOT NULL,
    verifier_did    TEXT NOT NULL,          -- 验证者 (Moltable Server)
    challenge       TEXT NOT NULL,          -- 随机数防重放
    verified_at     TIMESTAMPTZ DEFAULT now()
);
```

### 2.2 修改表

```sql
-- api_keys 表: 保留但废弃，添加迁移标记
ALTER TABLE api_keys ADD COLUMN migrated_to_did TEXT;

-- personas 表: 添加 did 关联
ALTER TABLE personas ADD COLUMN did TEXT;
ALTER TABLE personas ADD COLUMN credential_id UUID REFERENCES credentials(id);

-- audit_logs: 添加 did 关联
ALTER TABLE audit_logs ADD COLUMN agent_did TEXT;
ALTER TABLE audit_logs ADD COLUMN presentation_id UUID REFERENCES presentations(id);
```

### 2.3 需要 Issuer 服务

当前没有，需要新增。`server/services/issuer_service.py`:

```python
class IssuerService:
    """签发 Agent 身份 VC 和 Persona 委托 VC"""
    
    def issue_agent_credential(self, agent_did, platform, capabilities):
        """CreatePersona → 签发 AgentIdentityCredential"""
        vc = {
            "@context": ["https://www.w3.org/ns/credentials/v2"],
            "type": ["VerifiableCredential", "AgentIdentityCredential"],
            "issuer": self.issuer_did,
            "credentialSubject": {
                "id": agent_did,
                "platform": platform,       # 'hermes' | 'claude' | 'chatgpt'
                "capabilities": capabilities,
                "controller": user_did,     # 用户 DID
            },
            "validFrom": now,
            "validUntil": now + 90_days,
        }
        return sign_vc(vc, self.issuer_key)
    
    def issue_persona_delegation(self, agent_did, persona_id, scopes):
        """Persona 委托: 授权 Agent 以特定 Persona 身份操作"""
        vc = {
            "type": ["PersonaDelegationCredential"],
            "credentialSubject": {
                "id": agent_did,
                "persona_id": persona_id,
                "scopes": scopes,           # ['memory:read', 'memory:write', 'provision:read']
            }
        }
        return sign_vc(vc, self.issuer_key)
```

**Schema 变更汇总**: 3 张新表 + 3 张修改 + 1 个新 Issuer 服务

---

## 三、auth.py 变更（核心改动最大）

### 3.1 当前认证流程 → 目标流程

```
当前:
  Request → get_user()
    ├── Bearer JWT → supabase.auth.get_user()
    ├── X-API-Key → PBKDF2 hash match
    └── X-Session-Token → sessions 表查询
  → 返回 user_id (UUID)

目标:
  Request → authenticate_agent()
    ├── Bearer DID VP → verify_presentation() → 验签名+验凭证+验有效期
    │   ├── 验证 VP 签名 (Ed25519)
    │   ├── 验证 VC 未被吊销
    │   ├── 验证 VC 未过期
    │   ├── 验证 VP 挑战值未被重放
    │   └── 提取 agent_did + persona_id + scopes
    ├── X-DID-Auth (简化模式，向后兼容)
    │   └── 验证固定 DID 签名
    └── X-API-Key (旧模式，逐步废弃)
        └── 同前，但多一条废弃 warning
  → 返回 AuthContext(agent_did, user_id, persona_id, scopes)

class AuthContext:
    agent_did: str          # did:web:moltable.ai:agent:hermes-a1b2c3
    user_id: UUID           # 关联的人类用户
    persona_id: UUID | None # 当前使用的 Persona (如果有 Persona VC)
    platform: str           # 'hermes' | 'claude' | 'chatgpt'
    scopes: list[str]       # 授权范围
```

### 3.2 代码改动量

| 文件 | 当前行数 | 改动行数 | 改动性质 |
|------|:---:|:---:|------|
| `auth.py` | 163 | ~120 | **重写**: get_user() → authenticate_agent(), 新增 verify_presentation(), 新增 challenge 端点 |
| 新增 `issuer_service.py` | 0 | ~200 | **全新**: DID 签发、VC 签发、密钥管理 |
| 新增 `verifier_service.py` | 0 | ~150 | **全新**: VP 验证、签名验证、凭证吊销检查 |
| `app_state.py` | 47 | ~20 | 新增 issuer/verifier 单例 |
| `main.py` | 146 | ~10 | 注册 issuer 路由 |

### 3.3 auth.py 具体改动

**删除**:
- `hash_api_key()` — 不再需要 PBKDF2
- `CreateAPIKeyRequest` — API Key 创建废弃
- `create_api_key()` — 替换为 `register_agent_did()`
- `list_api_keys()` / `revoke_api_key()` — 替换为 DID 管理

**新增**:
```python
# 1. Agent 注册 (替代 create_api_key)
@router.post("/agents/register")
def register_agent(body: AgentRegisterRequest, user_id: str = Depends(get_user)):
    """为 Agent 生成 DID + 公私钥对，签发 AgentIdentityCredential"""
    
# 2. Persona 委托 (新能力)
@router.post("/agents/{agent_did}/delegate/{persona_id}")
def delegate_persona(agent_did, persona_id, user_id):
    """为用户 Persona 签发 PersonaDelegationCredential"""

# 3. VP 验证 (核心替代)
async def verify_presentation(presentation_jwt: str, challenge: str):
    """验证 Agent 出示的 VP：验签名→验链→验吊销→验挑战"""

# 4. Challenge 端点 (防重放)
@router.get("/challenge")
def get_challenge():
    """返回一次性随机数，Agent 用私钥签名后嵌入 VP"""
```

**保留**:
- `get_user()` — 保留用于前端 Dashboard 的用户登录，标记 `@deprecated_for_agent`
- `get_me()` — 保留用于 Web 前端

---

## 四、MCP 协议层变更 (mcp.py)

### 4.1 initialize 握手增强

```python
# 当前
def handle_initialize(params):
    return {"protocolVersion": "2024-11-05", ...}

# 目标
def handle_initialize(params):
    # Agent 在 initialize 时声明 DID
    client_did = params.get("clientDid")
    return {
        "protocolVersion": "2024-11-05",
        "serverInfo": {"name": "moltable", "did": SERVER_DID},
        "auth": {
            "type": "did_vc",
            "challenge": generate_challenge(),  # 一次性挑战值
            "supportedCredentials": [
                "AgentIdentityCredential",
                "PersonaDelegationCredential",
            ]
        }
    }
```

### 4.2 tools/call 认证增强

```python
# 当前: X-API-Key header → 解析 user_id
user_id = await _resolve_api_key(x_api_key)

# 目标: Authorization: Bearer <VP_JWT> → 解析 AuthContext
auth_ctx = await verify_presentation(vp_jwt, challenge)
# auth_ctx.agent_did  = did:web:moltable.ai:agent:hermes-xxx
# auth_ctx.persona_id = uuid-xxx  (如果带了 Persona VC)
# auth_ctx.scopes     = ['memory:read', 'memory:write']
```

### 4.3 工具权限控制（新增能力）

```python
# Persona 相关工具需要 Persona VC
TOOL_SCOPE_MAP = {
    "consult_persona":   ["persona:read"],
    "compare_personas":  ["persona:read"],
    "match_persona":     ["persona:read"],
    "get_persona":       ["persona:read"],
    "list_personas":     ["persona:read"],
    "save_memory":       ["memory:write"],
    "archive_memory":    ["memory:write"],
    "search_memory":     ["memory:read"],
    "auto_provision":    ["provision:read"],
}

def _check_scopes(tool_name, auth_ctx):
    required = TOOL_SCOPE_MAP.get(tool_name, [])
    if required and not all(s in auth_ctx.scopes for s in required):
        raise JSONRPCError(AUTH_ERROR, f"Insufficient scopes: need {required}")
```

**mcp.py 改动量**: ~50 行修改 + ~30 行新增，核心认证逻辑委托给 verifier_service

---

## 五、客户端/SDK 变更

### 5.1 Go SDK 改动 (`sdk/go/client/client.go`)

```go
// 当前
type Client struct {
    baseURL string
    nodeID  string
    apiKey  string       // ← 替换
}

// 目标
type Client struct {
    baseURL    string
    agentDID   string          // did:web:moltable.ai:agent:xxx
    privateKey ed25519.PrivateKey
    vc         *Credential     // AgentIdentityCredential
    personaVC  *Credential     // PersonaDelegationCredential (可选)
}

func (c *Client) request(method, path string, body interface{}) {
    // 1. 获取 challenge
    ch := c.getChallenge()
    // 2. 构建 VP
    vp := c.buildPresentation(ch, c.vc, c.personaVC)
    // 3. 签名 VP
    signed := ed25519.Sign(c.privateKey, vp)
    // 4. 发送请求
    req.Header.Set("Authorization", "Bearer " + signed)
}
```

**SDK 改动量**: ~80 行修改 + ~100 行新增密钥管理

### 5.2 Hermes Skill 变动 (`skills/moltable/SKILL.md`)

技能文件需更新认证指引，从"设置 API Key" 变为"注册 Agent DID"。

### 5.3 Chrome 插件变动

`extension/content.js` 中原有的 API Key 输入框变为：
- 首次使用时引导用户在 Web Dashboard 注册 Agent
- 自动生成密钥对并注册 DID
- 存储 `did + privateKey` 替代 `apiKey`

---

## 六、前后端对接变更

### 6.1 Web Dashboard 新增页面

| 当前 | 目标 | 说明 |
|------|------|------|
| `/dashboard/settings` — API Key 管理 | 替换为 DID 管理页面 | 显示已注册 Agent，管理凭证 |
| 无 | `/dashboard/agents` — Agent 列表 | 查看所有关联 Agent 及其 DID/状态 |
| 无 | `/dashboard/agents/{id}` — Agent 详情 | 查看 VC、权限、吊销 |

### 6.2 前端 API 客户端 (`web/src/lib/api.ts`)

```typescript
// 当前
headers['X-API-Key'] = apiKey

// 目标 (Agent 用)
headers['Authorization'] = `Bearer ${vpToken}`

// 目标 (人类用户用 Dashboard)
headers['Authorization'] = `Bearer ${supabaseJwt}`
```

人类用户的 Dashboard 登录不受影响（仍用 Supabase Auth），只有 Agent 的 MCP/REST 调用改用 DID+VC。

---

## 七、迁移策略

### 7.1 四阶段迁移

```
Phase 1 (兼容期, 2周)
  ├── 新增 DID/VC 基础设施 (schema + issuer + verifier)
  ├── 保留旧认证通道
  ├── 新 Agent 同时支持 API Key (旧) 和 DID+VC (新)
  └── 旧 Agent 无感知，继续用 API Key

Phase 2 (双轨期, 2周)
  ├── Hermes Skill 升级至 DID+VC
  ├── Go SDK 升级至 DID+VC
  ├── 新注册 Agent 默认用 DID+VC
  └── 旧 API Key 标记 deprecated，请求中增加 deprecation warning

Phase 3 (过渡期, 4周)
  ├── 通知所有 API Key 用户迁移
  ├── Dashboard 提供一键迁移 (自动生成密钥对+注册DID+签发VC)
  └── API Key 请求延迟 +1s，推动迁移

Phase 4 (清理期, 2周)
  ├── 关闭 API Key 认证
  ├── 删除 hash_api_key / PBKDF2 代码
  └── 归档旧 api_keys 表数据
```

### 7.2 自动化迁移

```python
@router.post("/migrate-to-did")
def migrate_to_did(user_id: str = Depends(get_user)):
    """一键迁移: 生成 DID+密钥对，为已有 API Keys 签发对应 VC"""
    # 1. 读取用户所有 API Key
    old_keys = supabase.table("api_keys").select("*").eq("user_id", user_id).execute()
    
    # 2. 为每个 Key 生成 DID 密钥对
    for key in old_keys.data:
        private_key, public_key = generate_ed25519_keypair()
        agent_did = f"did:web:moltable.ai:agent:{uuid4().hex[:12]}"
        
        # 3. 注册 DID
        supabase.table("did_registry").insert({...})
        
        # 4. 签发 VC
        vc = issuer.issue_agent_credential(agent_did, platform="migrated", capabilities=key.permissions)
        
        # 5. 标记旧 Key
        supabase.table("api_keys").update({"migrated_to_did": agent_did}).eq("id", key.id)
    
    return {"migrated": len(old_keys.data)}
```

---

## 八、风险评估

### 8.1 技术风险

| 风险 | 概率 | 影响 | 缓解 |
|------|:---:|:---:|------|
| Ed25519 密钥丢失 → Agent 失联 | 中 | 高 | Dashboard 支持密钥重新生成+VC 重新签发 |
| Issuer 私钥泄露 → 可伪造所有 VC | 低 | 致命 | Issuer 私钥用 HSM/KMS 管理(生产环境) |
| VP 重放攻击 | 中 | 高 | Challenge 机制 + 短期有效期 (5min) |
| 跨平台 DID 解析不一致 | 低 | 中 | 统一用 `did:web` 方法 |
| Python crypto 性能瓶颈 | 中 | 中 | Ed25519 验签极快(~50μs)，非瓶颈 |

### 8.2 业务风险

| 风险 | 说明 |
|------|------|
| 用户学习成本 | 从"复制 API Key"变为"生成密钥对+注册DID"，流程变复杂 |
| 旧 Agent 兼容 | 现有 Hermes Skill / SDK 需要升级 |
| 调试变难 | VP 是 JWT 二进制，肉眼不可读，需新工具 |
| VC 吊销延迟 | 吊销 VC 后可能有 CRL (Certificate Revocation List) 同步窗口 |

### 8.3 性能影响

| 操作 | 当前 (API Key) | DID+VC | 影响 |
|------|:---:|:---:|:---:|
| 认证 | 1 SQL 查询 (indexed) | 1 Ed25519 验签 + 2 SQL 查询 | +0.5ms |
| VC 验证 | — | 签名验证 + 吊销检查 + 过期检查 | +1ms |
| VP 验证 | — | 签名验证 + Challenge 检查 + VC 递归验证 | +2ms |
| **总体** | ~1ms | ~4ms | **可忽略** |

### 8.4 依赖风险

| 依赖 | 说明 |
|------|------|
| HelixID / AgentDID | 都处于早期 (⭐<10)，API 可能变更。建议直接实现 W3C 标准，不完全依赖第三方库 |
| `pycryptodome` / `cryptography` | 成熟稳定，无风险 |
| W3C DID/VC 标准 | W3C 推荐标准，已稳定 |

---

## 九、工作量估算

| 模块 | 文件 | 工作量 | 说明 |
|------|------|:---:|------|
| Schema 变更 | `schema.sql` | 0.5天 | 3 新表 + 3 修改 + migration.sql |
| Issuer 服务 | `services/issuer_service.py` | 2天 | DID 生成、VC 签发、密钥管理 |
| Verifier 服务 | `services/verifier_service.py` | 2天 | VP 验证、签名验证、吊销检查 |
| auth.py 重写 | `routes/auth.py` | 2天 | authenticate_agent(), DID 管理端点 |
| mcp.py 适配 | `routes/mcp.py` | 1天 | initialize 增强, tools/call 认证, 权限控制 |
| provision_service 适配 | `services/provision_service.py` | 0.5天 | 从 AuthContext 而不是 user_id 读取 |
| 其他路由适配 | 5 个路由文件 | 1天 | 替换 `Depends(get_user)` → `Depends(authenticate_agent)` |
| Go SDK 升级 | `sdk/go/` | 2天 | 密钥管理 + VP 构建 + HTTP header |
| Hermes Skill 升级 | `skills/` | 0.5天 | 认证指引更新 |
| Web 前端 | 3 个页面 | 2天 | Agent 管理页面 + DID 替换 API Key |
| Chrome 插件 | `extension/` | 1天 | 密钥本地生成 + DID 注册流程 |
| 测试 | `server/tests/` | 2天 | 新 auth 流程 + VP 验证 + mock issuer |
| 迁移工具 | 脚本 | 1天 | 一键迁移 + 数据校验 |
| 文档更新 | 多文件 | 1天 | README/PRD/DESIGN/auth.md |
| **合计** | | **18.5天** | 约 3-4 周单人全职，或 2 周两人并行 |

---

## 十、投资回报评估

### 10.1 获得的能力

| 能力 | 当前 | DID+VC 后 |
|------|:---:|:---:|
| 区分 Agent 身份 | ❌ 只能区分"谁的Key" | ✅ 区分"哪个 Agent 以什么角色" |
| Agent 能力证明 | ❌ | ✅ VC 携带 capabilities |
| Persona 委托授权 | ❌ | ✅ PersonaDelegationCredential |
| 防伪造 Agent | ❌ 完全依赖 Key 保密 | ✅ 密码学签名不可伪造 |
| 跨组织互信 | ❌ | ✅ DID 可跨域解析 |
| 操作审计链 | ❌ 仅记录 user_id | ✅ 记录 agent_did + presentation_id |
| 细粒度权限 | ❌ API Key 全量 | ✅ scoped VC 按 Persona/功能授权 |
| Zero-Trust | ❌ 信任 API Key 持有者 | ✅ 每个请求都需 VP 证明 |

### 10.2 失去的

| 方面 | 影响 |
|------|------|
| API Key 简洁性 | "一键复制 Key" 变为 "注册 Agent → 保存密钥 → 获取 VC"，多两步 |
| 无网络侧验证 | 当前 API Key 只需查一次数据库；DID `did:web` 解析需要 HTTPS 请求（可缓存） |
| 存储复杂度 | API Key 一条记录；DID+VC 三条记录 + 密钥文件 |

### 10.3 结论

**DID+VC 方案的核心价值在于实现 Moltable 的定位承诺——"跨 AI 平台身份层"**。

当前方案本质上是"一个 API Key 多处用"，DID+VC 才能实现真的"Agent 身份互认"：Hermes Agent 和 Claude Agent 各自拥有独立的可验证身份，共享同一套用户记忆和 Persona，每个操作都有密码学证明。

**建议**: 如果 Moltable 的目标是"AI Agent 的身份基础设施"，DID+VC 不是锦上添花，而是核心交付。Phase 1+2 投入 2 周建立双轨，验证价值后再决定是否全力投入 Phase 3+4。
