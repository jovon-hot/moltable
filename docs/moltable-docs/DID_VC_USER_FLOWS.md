# DID+VC 方案：完整用户操作流程

> 所有场景：新用户 · 老用户 · 新建Agent · 日常使用 · 续期 · 丢失密钥 · 切换Persona · 吊销

---

## 核心设计原则

```
用户永远只需要做一件事：从 Dashboard 复制一行文本，发给 AI。

Enrollment Token = 今天 API Key 的形态，但一次性，用完即焚。
后面的 DID 生成、密钥对创建、VC 签发、VP 构建 → 全部自动。
```

---

## 场景 1：新用户首次接入

### 步骤

```
第 1 步 / 用户在 AI 对话中说：
  "帮我注册 Moltable"
  ↓
第 2 步 / AI 回复：
  "打开 moltable.ai/register，用邮箱注册（30 秒）。
   注册后进入 Dashboard → 点「连接 Agent」→ 把生成的代码发给我。"
  ↓
第 3 步 / 用户打开网页：
  ┌─────────────────────────────────────┐
  │ moltable.ai/register                │
  │                                     │
  │ Email: [jovon@email.com      ]     │
  │ Password: [···················]     │
  │ [注册]                              │
  └─────────────────────────────────────┘
  ↓
  注册成功 → 自动跳转 Dashboard

  ┌─────────────────────────────────────┐
  │ Dashboard                           │
  │                                     │
  │ 👋 欢迎！连接你的第一个 AI Agent。     │
  │                                     │
  │ 你的 Agent 在什么平台？              │
  │  ○ Hermes (推荐)                    │
  │  ○ Claude Desktop                   │
  │  ○ ChatGPT                          │
  │  ○ 其他                             │
  │                                     │
  │ Agent 名称: [我的AI助手]            │
  │                                     │
  │ [生成连接码]                        │
  │   ↓                                 │
  │ ┌─────────────────────────────┐     │
  │ │ molt_enroll_a1b2c3d4e5f6g7h │     │
  │ │              [📋 复制]       │     │
  │ └─────────────────────────────┘     │
  │                                     │
  │ ⚡ 一次性代码，5 分钟有效            │
  └─────────────────────────────────────┘
  ↓
第 4 步 / 用户复制这行代码发给 AI：
  "molt_enroll_a1b2c3d4e5f6g7h"
  ↓
第 5 步 / AI 自动处理（用户看不到）：

  # 1. 本地生成 Ed25519 密钥对 (50ms)
  private_key, public_key = generate_keypair()
  
  # 2. 用 Enrollment Token 注册
  POST /api/agents/enroll
  {
    "enrollment_token": "molt_enroll_a1b2c3d4e5f6g7h",
    "platform": "hermes",
    "public_key": "MCowBQYDK2Vw..."
  }
  → 服务端验证 Token → 生成 DID did:web:moltable.ai:agent:h001
  → 签发 AgentIdentityCredential (90天)
  → 签发 PersonaDelegationCredential (如有默认 Persona)
  ← { did, agent_vc, persona_vc }
  
  # 3. 保存到本地
  echo "{did, private_key, agent_vc, persona_vc}" > ~/.hermes/moltable.json
  
  # 4. 加载身份
  auto_provision() → 返回用户画像、偏好、记忆、项目 ✅

  ↓
第 6 步 / AI 回复：
  "已连接 Moltable ✅
   加载了你的 0 条记忆、3 个默认 Persona。以后每次对话我都会记住。"

全程用户操作：
  1. 注册邮箱
  2. 点"生成连接码"
  3. 复制粘贴给 AI

跟今天的 API Key 流程完全一样。
区别：Dashboard 上多了一个选平台的步骤，但可以默认填 Hermes。
```

### 背后自动发生了什么

```
Dashboard 点"生成连接码"
  → POST /api/enrollment-tokens  → 生成 molt_enroll_xxx
  → 存入 redis/enrollment_tokens 表 (5min TTL, 绑定 user_id)

AI 收到 molt_enroll_xxx
  → 本地生成密钥对
  → POST /api/agents/enroll
  → 服务端:
      1. 查 enrollment_tokens 表 → 找到 user_id
      2. 删除 token (一次性)
      3. INSERT INTO did_registry (did, user_id, public_key, platform)
      4. 签发 AgentIdentityCredential → INSERT INTO credentials
      5. 如果用户有活跃 Persona → 签发 PersonaDelegationCredential
      6. 返回 {did, agent_vc, persona_vc}
  → Agent 保存到 ~/.hermes/moltable.json

用户看不到任意一步。
```

---

## 场景 2：老用户添加第二个 Agent

### 步骤

```
用户已经有 Hermes Agent 在用了。现在想在 Claude Desktop 也接上 Moltable。

第 1 步 / 打开 Dashboard → Agents 页面
  ┌──────────────────────────────────────────┐
  │ Agents                                   │
  │                                          │
  │ ✅ 我的AI助手 (Hermes)                   │
  │   DID: did:web:moltable.ai:agent:h001    │
  │   VC: 到期 2026-10-27                    │
  │   [吊销]                                 │
  │                                          │
  │ [+ 连接新 Agent]  ← 点击                 │
  │   ↓                                      │
  │ Platform: [Claude Desktop ▼]             │
  │ Agent 名称: [Claude助手]                 │
  │ Persona: [使用已有 Persona ▼]  ← 可选    │
  │   ☑ 战略顾问                             │
  │   ☐ 保守审核员                           │
  │                                          │
  │ [生成连接码]                              │
  │ ┌─────────────────────────────────┐      │
  │ │ molt_enroll_z9y8x7w6v5u4t3s2r  │      │
  │ │            [📋 复制]             │      │
  │ └─────────────────────────────────┘      │
  └──────────────────────────────────────────┘
  ↓
第 2 步 / 在 Claude Desktop 中对 AI 说：
  "molt_enroll_z9y8x7w6v5u4t3s2r"
  ↓
第 3 步 / Claude Desktop 的 Moltable Skill 自动：
  → 生成密钥对
  → POST /api/agents/enroll (带着 token)
  → 收到 {did: did:web:moltable.ai:agent:c001, vc, persona_vc}
  → 保存到本地
  → auto_provision()
  → 加载了跟 Hermes 一模一样的偏好、记忆、Persona ✅

第 4 步 / Dashboard 自动刷新：
  ┌──────────────────────────────────────────┐
  │ ✅ 我的AI助手 (Hermes)    到期 2026-10-27│
  │ ✅ Claude助手 (Claude)    到期 2026-10-27│
  │   DID: did:web:moltable.ai:agent:c001    │
  │   Persona: 战略顾问                      │
  │   [吊销]                                 │
  └──────────────────────────────────────────┘

比今天多的一步：选择 Persona（可选，不选也行）。
今天用 API Key 是直接把同一个 Key 给 Claude——两个 Agent 无法区分。
```

---

## 场景 3：日常使用（每天发生）

### 用户感受到的

```
用户打开 Hermes：
  "帮我做 7 月经营分析"

AI：
  [读取 ~/.hermes/moltable.json]  ← 0.01 秒
  [auto_provision()]               ← 0.03 秒
  [加载到上下文]                    ← 随 Prompt 一起注入
  "好的，已加载你的偏好和当前项目。
   7 月数据从 192.168.1.93 拉取..."

用户感觉：跟今天一模一样。没有任何额外步骤。
```

### 背后自动发生的

```
每次会话开始：
  1. 读 ~/.hermes/moltable.json
  2. 检查 VP 缓存是否有效 (5min TTL)
     → 有效: 直接用缓存 VP 调 API
     → 过期: GET /api/challenge → Ed25519 签名 → 新 VP → 调 API
  3. auto_provision() → 身份加载

普通 API 调用：
  search_memory("最近的偏好")
    → 走缓存 VP → 1 次 HTTP → 5ms
    → 跟今天用 API Key 完全一样快

VP 缓存过期时（每 5 分钟一次）：
  GET /api/challenge → 本地签名 → search_memory(...)
    → 2 次 HTTP → ~10ms
    → 比今天多 5ms → 用户无感知

全程用户零操作。
```

---

## 场景 4：Agent 身份自动续期

### 用户感受到的

```
[VC 到期前 7 天]

用户打开 AI 对话：
  "帮我看看上个月数据"

AI：
  [auto_provision() 时检测到 VC 将在 7 天后过期]
  [自动: POST /api/agents/renew {agent_did, old_vc}]
  [获得新 VC → 更新 moltable.json]
  "数据已加载。"   ← 正常回复，续期是静默的

用户完全不知道发生了什么。

[如果 VC 已经过期]
  AI: "我的 Moltable 凭证需要刷新，已自动续期 ✅。继续..."
  用户可能看到这一行，也可能看不到。
```

### 自动续期协议

```
Agent 检测到 VC 距离过期 ≤ 7 天
  → POST /api/agents/renew
    {agent_did: "did:web:moltable.ai:agent:h001", old_vc: "eyJ..."}
  → 服务端:
      1. 验证旧 VC 签名有效（确实是 Moltable 签发的）
      2. 验证旧 VC 确实即将过期
      3. 签发新 VC（重新签 90 天）
      4. 旧 VC 标记 replaced_by=new_vc_id
  ← {new_vc: "eyJ..."}
  → Agent 更新本地 moltable.json 中的 vc 字段

如果 VC 已经过期:
  → 旧 VC 无法通过签名验证
  → 服务端检查: 这个 agent_did 的注册用户是谁？
  → 如果用户仍然活跃 → 签发新 VC
  → 如果用户已注销 → 拒绝续期
```

---

## 场景 5：丢失密钥

```
用户换了电脑，或者不小心删了 ~/.hermes/moltable.json。

当前（API Key）:
  去 Dashboard 重新生成 Key → 发给 AI → 搞定
  ⚠️ 但旧 Key 还在别人手里的话，没法单独吊销

DID+VC:
  去 Dashboard → Agents → 点那个 Agent 的 [重新生成]
  → 旧 DID 吊销，新 DID + 新连接码
  → 发给 AI → 搞定
  ✅ 旧密钥即使泄露了也无法再使用

Dashboard 上：
  ┌──────────────────────────────────────────┐
  │ Agents                                   │
  │                                          │
  │ ⚠️ 我的AI助手 (Hermes)                   │
  │   状态: 已吊销 (2026-08-15)              │
  │   [重新生成]  ← 用户点这里               │
  │                                          │
  │ ✅ 我的AI助手 (Hermes)  ← 新的           │
  │   DID: did:web:moltable.ai:agent:h002    │
  │   连接码: molt_enroll_xxxxxxxxxx         │
  │   [📋 复制]                              │
  └──────────────────────────────────────────┘

用户操作：
  点"重新生成" → 复制连接码 → 发给 AI
  跟重新生成 API Key 一样简单。
  区别：旧的那个被精确吊销，不是全量重置。
```

---

## 场景 6：吊销单个 Agent

```
用户想停止 Claude Desktop 上的 Agent 访问（手机丢了，或者换了平台）。

当前（API Key）:
  吊销 Key → 所有 Agent 一起断 → 重新配置 Hermes

DID+VC:
  Dashboard → Agents → 找到"Claude助手" → [吊销]
  → 仅吊销该 Agent 的 VC
  → Hermes 不受影响，继续正常使用 ✅

Dashboard 上：
  ┌──────────────────────────────────────────┐
  │ ✅ 我的AI助手 (Hermes)                    │
  │ ❌ Claude助手 (Claude)                   │
  │   已吊销 · 2026-08-15                    │
  │   [恢复]  [永久删除]                     │
  └──────────────────────────────────────────┘
```

---

## 场景 7：匿名用户（零注册体验——现有能力保留）

```
用户不想注册，只想试用。

跟今天完全一样：

AI 检测到没有 ~/.hermes/moltable.json，没有 API Key
  → POST /api/sessions → 获取 mol_xxx token
  → 用 token 调 API → 7 天有效期
  → 记忆到期前提醒注册
  → 注册后: POST /api/sessions/migrate → 记忆合并到新账户
  → 同时自动完成 DID 注册 (像场景 1)

匿名会话这条路径完全不受 DID+VC 影响。保留。
```

---

## 场景 8：Agent 自动跨 Persona 切换

```
用户正在使用"战略顾问"Persona，突然要求换风格：

用户: "切换到保守审核员，审一下这个方案"
AI:
  1. 检测到需要 consult_persona("保守审核员", ...)
  2. 检查本地是否有该 Persona 的委托 VC 缓存
  3. 有 → 直接用 → 调 API  ← 0 延迟
  4. 没有 → GET /api/challenge
         → 构建含 PersonaDelegationCredential 的 VP
         → Ed25519 签名 (50μs)
         → 调 API
         → 多约 0.5 秒 ← 用户可能感觉"等一下"
  5. 答案返回

用户感知的延迟:
  有缓存: LLM 生成答案的时间 (5-15s)，认证开销为零
  无缓存: 多 0.5s，淹没在 LLM 延迟中（LLM 往往 5-20s）

结论: 用户基本感知不到。
```

---

## 全流程对比总结

| 场景 | 今天 (API Key) 用户操作 | DID+VC 后用户操作 | 变化 |
|------|------------------------|-------------------|:---:|
| 新用户 | 注册→生成Key→复制→发给AI | 注册→选平台→生成→复制→发给AI | 多 1 步(选平台) |
| 添加Agent | 把同一个Key复制给新Agent | 生成新连接码→复制→发给AI | 相同 |
| 日常使用 | 无操作 | 无操作 | 无 |
| 续期 | 无 (Key不过期) | 无 (自动) | 无 |
| 丢密钥 | 重新生成Key→全部重配 | 吊销单个Agent→重新生成 | 更好 |
| 吊销Agent | 吊销Key→全部断了 | 只断那一个 | 🚀 大幅改善 |
| 匿名试用 | 无 | 无 (保留) | 无 |
| 切Persona | 无 | 无 (自动缓存) | 无 |

**用户每天的操作变化：零。**
**唯一多出来的是首次注册时多选一个平台，默认值填好就是点一下"继续"。**
