# DID+VC 方案对用户体验的影响

> 逐触达点的前后对比 · 逐角色评估 · 基于真实当前 UX 推导

---

## 一、当前用户体验全景

Moltable v2 有 **三个用户触达点** + **一个 Agent 视角**：

### 1.1 Web Dashboard — 人类用户

```
注册(moltable.ai/register)
  → 邮箱注册(Supabase Auth)
  → 登录 Dashboard
  → Settings → 点"Generate API Key"
  → 看到一行 molt_xxxx... 
  → 点击复制 ✅ 完成
```

代码：`web/src/app/dashboard/settings/page.tsx` + `routes/auth.py:116-130`

### 1.2 Hermes Skill — Agent 配置

```
AI 提示用户注册
  → 用户去网站拿到 Key
  → 回来说"molt_xxxx..."
  → Agent: echo "KEY" > ~/.hermes/moltable.key ✅
  → 调用 auto_provision() → 身份加载
```

代码: `skills/moltable/SKILL.md:57-65`

### 1.3 Chrome 插件 — 浏览器用户

```
打开 ChatGPT/Claude 页面
  → 点右下角紫色 🧠 按钮
  → 弹出搜索面板
  → 首次使用: 点"Settings" → 粘贴 API Key → Save ✅
  → 搜索记忆 → 一键注入到 AI 输入框
```

代码: `extension/popup.html:174-184`

### 1.4 总结：当前是三处"粘贴一行 Key"

| 触达点 | 用户动作 | 步骤数 |
|--------|----------|:---:|
| Web Dashboard | 注册 → Settings → Generate → Copy | 4 |
| Hermes Skill | AI 引导 → 粘贴 Key 到终端 | 2 |
| Chrome 插件 | 打开插件 → 粘贴 Key → Save | 3 |

**当前 UX 的最大优势: "一行文本就能搞定一切"。**

---

## 二、DID+VC 后的用户体验

### 2.1 最大的变化：出现了"密钥"概念

当前用户只要记住一个东西——API Key（字符串）。DID+VC 后用户需要理解三个东西：

| 概念 | 是什么 | 用户怎么理解 |
|------|--------|-------------|
| DID | Agent 的去中心化标识符 | "Agent 的身份证号" |
| 私钥 | Agent 的签名密钥 | "Agent 的指纹锁" |
| VC | 签发的凭证 | "Moltable 给这个 Agent 开的证明" |

**对普通用户来说，这三个概念都是全新的认知负担。**

---

## 三、逐触达点详细对比

### 3.1 Web Dashboard

#### 当前流程 (4步)

```
Settings 页
┌─────────────────────────────────┐
│  API Keys                       │
│  ┌─────────────────────────┐    │
│  │ molt_xxxx...   [复制]    │    │  ← 一眼看到，一键复制
│  └─────────────────────────┘    │
│  [+ Generate New Key]           │
└─────────────────────────────────┘
```

#### DID+VC 后 (7步)

```
Settings → Agents 页 (新页面)
┌──────────────────────────────────────────────┐
│  Agents                                      │
│                                              │
│  [+ Register New Agent]                      │
│       ↓ 弹出对话框                            │
│  ┌────────────────────────────────────────┐  │
│  │ Register Agent                         │  │
│  │                                        │  │
│  │ Platform: [Hermes ▼]                   │  │  ← 用户必须理解这是什么
│  │ Agent Name: [我的AI助手]                │  │
│  │                                        │  │
│  │ [Generate Keys & Register]             │  │
│  │       ↓                                │  │
│  │ ⚠️ IMPORTANT: Save your private key.   │  │
│  │ It CANNOT be recovered.                │  │  ← 用户从未见过的警告
│  │                                        │  │
│  │ ┌──────────────────────────────────┐   │  │
│  │ │ -----BEGIN PRIVATE KEY-----      │   │  │
│  │ │ MC4CAQAwBQYDK2VwBCIEI...         │   │  │
│  │ │ -----END PRIVATE KEY-----        │   │  │
│  │ └──────────────────────────────────┘   │  │
│  │ [Download Key]  [Copy Key]             │  │
│  └────────────────────────────────────────┘  │
│                                              │
│  Agent "我的AI助手" (Hermes)                 │
│  DID: did:web:moltable.ai:agent:a1b2c3d4    │
│  Status: ✅ Active                           │
│  Credentials: AgentIdentityCredential (90d)  │
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │ Delegate Persona: [战略顾问 ▼]          │  │  ← 新概念：委托授权
│  │ Scopes: ☑ memory:read ☑ memory:write   │  │
│  │        ☑ persona:read ☐ persona:write   │  │
│  │ [Issue Delegation Credential]          │  │
│  └────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
```

**问题点**:
1. "私钥不可恢复"的警告让用户紧张 —— 以前 Key 丢了重新生成就好
2. Platform 选择（Hermes/Claude/ChatGPT）增加了选择负担
3. Persona 委托授权是全新概念，用户要理解 scopes
4. DID 字符串 (`did:web:...`) 对用户无意义但必须展示
5. 步骤从 4 步变成 7 步

#### 缓解措施

| 问题 | UX 方案 |
|------|--------|
| 私钥恐惧 | "一键配置 Hermes/Claude"按钮，自动下放密钥到对应 Agent，用户不碰密钥 |
| Platform 选择 | 默认选项 + 引导文字："不确定？选 Hermes" |
| Scopes 复杂 | 预设模板：只读模式 / 标准模式 / 完全信任 |
| DID 无意义 | 隐藏 DID，仅展示 Agent Name + Platform 图标 |
| 步骤多 | 合并 Registration + Persona Delegation 为一步 |

---

### 3.2 Hermes Skill — Agent 配置（影响最大）

#### 当前流程 (1分钟)

```
用户: "注册好了"
AI:   "把 Key 发给我"
用户: "molt_xxxx..."
AI:   echo "KEY" > ~/.hermes/moltable.key  ✅
      auto_provision() → 用户身份加载 ✅

全程: 1分钟, 用户只做一件事: 复制粘贴一个字符串
```

#### DID+VC 后 (~3分钟)

```
用户: "注册好了"  
AI:   "你的 Agent 叫什么名字？"              ← 多一步
用户: "我的AI助手"
AI:   "我需要你的 Agent 私钥来签名请求。你下载了吗？"
用户: "下载了，在哪..."
AI:   "把私钥文件内容发给我，或者告诉我文件路径"
用户: "/Users/me/Downloads/moltable-key.pem"

AI:   cat /Users/me/Downloads/moltable-key.pem  ← 读取私钥
      → 保存到 ~/.hermes/moltable.key
      
      # 第一次: 需要注册 DID
      POST /api/agents/register  {
        "agent_name": "我的AI助手",
        "platform": "hermes",
        "public_key": "MCowBQYDK2Vw..."
      }
      → 返回 agent_did + AgentIdentityCredential

      # 保存凭证
      echo "{did + vc + persona_vc}" > ~/.hermes/moltable.json
      
      auto_provision() → 用户身份加载 ✅

全程: 2-3分钟, 用户做两件事: 报名字 + 提供密钥文件
```

**Skill 文件需要重写**。当前 `skills/moltable/SKILL.md:11-65` 整个 "Auto-Connect Flow" 部分要大改。

#### 当前 → 目标对比

```
当前 SKILL.md:
  Step 2a: Key Found → Silent Connect   ← 一句话，不需要用户参与
  Step 2b: No Key → Anonymous Session   ← 自动

目标 SKILL.md:
  Step 1: Detect identity file (~/.hermes/moltable.json)
  Step 2a: Found → 用 VP 认证 → auto_provision()
  Step 2b: 有 Key 无 Credential → POST /api/agents/register → 获取 VC
  Step 2c: 全无 → Anonymous Session
```

#### 自动化缓解

```bash
# moltable CLI 工具 (新)
pip install moltable-cli

# 一键注册: 生成密钥 + 注册DID + 获取VC + 保存到 ~/.hermes/
moltable setup --api-key molt_xxxx  # 用旧 API Key 自动完成迁移
# 或
moltable setup --email jovon@email.com  # Web 登录后自动完成

# Agent 端零配置
export MOLTABLE_IDENTITY_FILE=~/.hermes/moltable.json
```

**这是最关键的 UX 优化**: 提供一个 `moltable` CLI 工具，把"生成密钥→注册DID→获取VC→配置Agent"压缩为一条命令。用户仍然只需要登录 Web Dashboard 一次。

---

### 3.3 Chrome 插件

#### 当前流程

```
popup.html:
  ┌──────────────┐
  │ API Key      │
  │ [粘贴 Key]   │  ← 一行输入框
  │ [Save]       │
  └──────────────┘
```

#### DID+VC 后

```
popup.html:
  ┌──────────────────────────────┐
  │ Moltable Connection          │
  │                              │
  │ ○ API Key (简化模式)         │
  │ ● Agent Identity (推荐)     │
  │                              │
  │ ┌──────────────────────────┐ │
  │ │ 粘贴 Identity Token      │ │  ← 也是粘贴，但东西更长
  │ │ [eyJhbGci...很长的JWT...]│ │
  │ │ [Save]                   │ │
  │ └──────────────────────────┘ │
  │                              │
  │ 或 → [Open Dashboard to      │
  │        generate Identity]    │
  └──────────────────────────────┘
```

**插件改动最小**——对用户来说仍然是一行粘贴。只是内容从 "molt_xxxx..." (24字符) 变成了 JWT (~500字符)。体验基本不变。

---

### 3.4 Agent 运行时体验（API Key vs VP 认证）

#### 当前 (API Key)

```python
# Agent 发起请求
headers = {"X-API-Key": "molt_xxxx..."}
response = requests.get(f"{base}/api/memories/search?q=最近的偏好", headers=headers)
# 1 个 HTTP 请求，1 次数据库查询，~5ms
```

#### DID+VC (带 Challenge)

```python
# Agent 发起请求
# Step 1: 获取 challenge
challenge = requests.get(f"{base}/api/challenge").json()["challenge"]  # ← 多一个请求

# Step 2: 构建 VP
vp = build_presentation(
    did="did:web:moltable.ai:agent:hermes-a1b2c3",
    vc=agent_vc,                           # AgentIdentityCredential
    persona_vc=persona_delegation_vc,      # PersonaDelegationCredential (可选)
    challenge=challenge,                   # 防重放
    audience=base,                         # token binding
)
vp_token = sign(vp, private_key)          # Ed25519 签名

# Step 3: 发送请求
headers = {"Authorization": f"Bearer {vp_token}"}
response = requests.get(f"{base}/api/memories/search?q=最近的偏好", headers=headers)
# 3 个 HTTP 请求 (challenge + search), ~10ms
```

**Agent 视角的多余开销**:
- 每次请求前多一个 `/api/challenge` 往返 (+1ms 延迟)
- 每次请求需本地 Ed25519 签名 (~50μs，可忽略)
- Token 大小: API Key 24 bytes → VP JWT 约 500-1500 bytes

#### 缓解

```python
# VP 可缓存 (5分钟有效期)
if vp_cache and not vp_cache.is_expired():
    headers = {"Authorization": f"Bearer {vp_cache.token}"}
else:
    challenge = get_challenge()
    vp_cache = build_and_sign_vp(challenge)
    headers = {"Authorization": f"Bearer {vp_cache.token}"}
```

**缓存后**: 每 5 分钟多 1 个请求，其余请求无额外开销。

---

## 四、三种用户角色的体验对比

### 4.1 普通用户（赵海东）

| | 当前 | DID+VC | 差 |
|---|---|---|---|
| 首次注册 | 3min (邮箱注册→生成Key) | 3min (同上) | 0 |
| 添加新 Agent | 把 Key 发给 AI | 去 Dashboard 点"注册 Agent" → 下载密钥 → 发密钥给 AI | +2min |
| 管理 Agent | 无（没法管） | Dashboard 看到所有 Agent 列表、到期时间、权限 | ✅ 新能力 |
| 吊销 Agent | 吊销 Key → 所有 Agent 一起断 | 只吊销那一个 Agent 的 VC | ✅ 改善 |
| 换 Persona | 对 AI 说"切换到战略顾问" | AI 会自动用 Persona VC 切换 | 0 |
| 密钥丢失 | 重新生成 Key → 所有 Agent 重新配 | 仅那个 Agent 失联 → 重新注册即可 | 0 |

**净影响**: 多个 Agent 管理时 DID+VC 更好（可独立吊销），单 Agent 时 API Key 更简单。

### 4.2 Agent 开发者

| | 当前 | DID+VC |
|---|---|---|
| 接入指南 | "设置 API Key 即可" | "生成密钥对 + 注册 DID + 获取 VC + 构建 VP" |
| SDK 集成 | 3 行代码 | ~20 行代码 |
| 调试 | curl + API Key 直接测 | 需要 VP 工具链 |
| 安全 | Key 泄露 = 账号被盗 | 私钥泄露 = 单个 Agent 失联 |

**净影响**: 开发者门槛明显提高。需要非常好的 SDK 封装。

### 4.3 Moltable 运营方

| | 当前 | DID+VC |
|---|---|---|
| 审计 | 只知道 API Key → user_id | 知道 agent_did + persona_id + presentation_id |
| 安全事件 | 一个 Key 被盗 → 全量重置 | 私钥泄露 → 吊销单个 VC |
| 跨平台互认 | 靠同一个 Key | 靠跨域 DID 解析 + VC 信任链 |
| 合规 | "我们用了 PBKDF2" | "我们符合 W3C VC 2.0 标准" |

---

## 五、关键 UX 风险与缓解

### 风险 1: 首次配置流失

> 用户看到"下载私钥""注册 DID"就关了页面

**缓解**: 提供 "一键配置" CLI 工具，用户不在 Web UI 里碰密钥:
```bash
moltable setup          # 向导模式, 3 个问题
moltable setup --quick  # 完全自动化
```

### 风险 2: Agent 不响应 (静默失败)

> 用户: "你怎么不记得我了？"  
> Agent: "我的 VC 过期了，请重新授权"  
> 用户: "？"

**缓解**: Skill 文件增加 VC 过期预警。到期前 7 天开始提醒。

### 风险 3: 私钥丢失焦虑

> "这个密钥文件不能恢复是什么意思？万一丢了怎么办？"

**缓解**: 
- 文案改为"这是 Agent 的唯一凭证，建议备份"。不提"不可恢复"。
- Dashboard 提供"重新生成"按钮（吊销旧 DID + 签发新 VC）

### 风险 4: 跨平台复制的摩擦

> 在 Dashboard 注册了 Claude Agent，生成密钥。想把同一个身份给 Hermes 也用。  
> 用 API Key: 复制粘贴 Key 就行。  
> 用 DID+VC: 得重新注册 Hermes Agent → 生成新密钥 → 委托同一个 Persona。

**缓解**: "Add Platform" 功能：从现有 Agent 一键扩展到新平台，自动生成新 DID+密钥，签发同样的 Persona VC。

---

## 六、总结

### 定量对比

| 指标 | API Key | DID+VC | 变化 |
|------|:---:|:---:|:---:|
| 首次配置步骤 | 4 | 7(缓解后 4) | - |
| 配置时间 | 3 min | 5 min (缓解后 3 min) | - |
| 添加第二个 Agent | 30s (复制 Key) | 2 min (注册新 DID) | ⚠️ |
| 每个请求延迟 | ~5ms | ~10ms (缓存后 ~5ms) | 0 |
| 每次请求代码量 | 1 行设置 header | 5 行 VP 构建 (SDK 封装后 1 行) | 0 |
| Token 大小 | 24 bytes | ~800 bytes | ⚠️ |
| 安全级别 | ★★ | ★★★★★ | 🚀 |
| 可审计性 | user_id only | agent_did + persona_id + presentation_id | 🚀 |
| 跨平台互认 | 假 (同一个 Key) | 真 (独立 DID + 信任链) | 🚀 |

### 一句话结论

**DID+VC 把配置复杂度从"运行时"移到了"首次接入时"**——Agent 每次调用更安全、更可审计，但用户第一次配置多花 1-2 分钟。这个代价可以通过 CLI 工具和 SDK 封装压缩到接近零，换来的是 Moltable "跨 AI 平台身份层"的产品承诺真正成立。
