# Moltable v2 项目全面分析报告

> 分析日期：2025-07-11 | 分析范围：全项目（后端 + 前端 + 扩展 + 文档 + 部署）

---

## 一、产品定位与核心概念

### 1.1 一句话定位

**Moltable 是 AI 时代的身份层（AI Identity Layer）——跨 AI 平台的身份 + 记忆 + Persona 管理。**

来源：`README.md:1` | `PRD_产品需求文档.md:9`

### 1.2 三层架构（Identity → Persona → Agent）

| 层 | 数量 | 拥有什么 | 示例 |
|----|------|---------|------|
| **Identity** | 1 | 用户账户、API Key、所有数据所有权 | Jovon |
| **Persona** | N | 行为模式、思维风格、专业领域 | 战略顾问、保守审核员 |
| **Agent** | N | 工具调用能力、执行任务 | PPT 生成器 |

来源：`PRD_产品需求文档.md:78-93`

### 1.3 Moltable 是 / 不是

**是：** AI 之间的用户身份中间层、跨平台记忆同步基础设施、AI 人格与 Agent 的管理系统
**不是：** AI 聊天界面、模型路由器、Prompt 模板库、Agent 运行时

来源：`PRD_产品需求文档.md:12-35`

### 1.4 核心差异化 vs 竞品

| 能力 | Moltable | mem0 | ChatGPT Memory | Nocturne |
|------|:---:|:---:|:---:|:---:|
| 跨平台 | ✅ 核心 | ⚠️ | ❌ | ✅ |
| 身份层 | ✅ | ❌ | ❌ | ❌ |
| auto_provision | ✅ | ❌ | ⚠️ 自动但不透明 | ❌ |
| Persona 系统 | ✅ | ❌ | ❌ | ❌ |
| 开源 | ✅ MIT | ✅ | ❌ | ✅ |

来源：`PRD_产品需求文档.md:133-142`

---

## 二、server/ 后端目录结构与各模块职责

### 2.1 目录全景

```
server/
├── main.py                     # FastAPI 入口、中间件、路由注册
├── app_state.py                # 共享状态：Supabase 客户端、Rate Limiter、Vector Store 单例
├── mcp_server.py               # MCP stdio 入口（通过 HTTP 代理到 mcp.py）
├── agent_experience.py         # Agent 体验模拟测试脚本
├── schema.sql                  # 数据库 Schema（含 RLS、match_memories RPC）
├── migration.sql               # pgvector 迁移脚本（match_memories 函数）
├── Dockerfile                  # Python 3.11-slim 容器化
├── requirements.txt            # Python 依赖
├── pyproject.toml              # 项目元数据
├── .env.example                # 环境变量模板
├── run_tests.sh                # 测试运行脚本
├── routes/
│   ├── __init__.py
│   ├── auth.py                 # 认证：JWT、API Key、Session Token 三通道
│   ├── memories.py             # 记忆 CRUD + 语义搜索
│   ├── personas.py             # Persona CRUD（Supabase + in-memory fallback）
│   ├── provision.py            # auto_provision REST 端点
│   ├── mcp.py                  # MCP JSON-RPC 2.0 端点（12 个工具 + 批量请求）
│   ├── sessions.py             # 匿名会话（mol_xxx token）
│   ├── billing.py              # Stripe 订阅计费
│   └── v1.py                   # API 版本化代理（/api/v1/* → /api/*）
├── services/
│   ├── __init__.py
│   ├── embedding.py            # 本地 sentence-transformers 嵌入（all-MiniLM-L6-v2）
│   ├── vector_store.py         # 内存向量存储（零依赖 pgvector 替代）
│   ├── provision_service.py    # auto_provision 共享逻辑
│   ├── persona_store.py        # 内存 Persona 存储（含 demo 种子数据）
│   └── repository.py           # Repository 抽象基类（ABC）
├── repositories/
│   └── memory_repo.py          # Supabase pgvector 仓库（含 in-memory fallback）
└── tests/
    ├── conftest.py             # 测试夹具：mock Supabase + mock embed + VectorStore
    ├── test_mcp.py             # MCP JSON-RPC 2.0 集成测试（12 个工具 + 错误处理）
    ├── test_memories_api.py    # Memories API 集成测试（CRUD + 搜索）
    ├── test_personas_api.py    # Personas API 测试
    ├── test_auth_api.py        # Auth API 测试
    ├── test_embedding.py       # Embedding 服务测试
    ├── test_vector_store.py    # VectorStore 单元测试
    ├── test_memory_repo.py     # SupabaseMemoryRepository 测试
    ├── test_provision.py       # Provision 端点测试
    └── fixtures/               # 测试数据（memories.json, personas.json）
```

### 2.2 各模块职责

#### main.py（`server/main.py:1-130`）
- FastAPI 应用创建，挂载 CORS、安全头、速率限制、1MB 请求体限制
- 注册 8 个路由模块（auth, memories, personas, provision, mcp, sessions, billing, v1）
- 注册 MCP 发现端点 `/.well-known/mcp`
- DeepSeek LLM 客户端初始化（可选，失败不阻塞）
- SIGTERM/SIGINT 优雅关闭

#### app_state.py（`server/app_state.py:1-47`）
- Supabase 客户端单例（`SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY`）
- slowapi 速率限制器
- `get_store()` → `SupabaseMemoryRepository(VectorStore())` 延迟初始化
- CORS 白名单（`ALLOWED_ORIGINS` 环境变量）

#### routes/auth.py（`server/routes/auth.py:1-169`）
- JWT Bearer token → Supabase `auth.get_user()` 验证
- API Key → SHA-256 PBKDF2-HMAC + pepper 哈希匹配
- Session Token → `sessions` 表验证（`mol_xxx` 前缀）
- 失败认证记录到 `audit_logs`
- API Key 管理：创建（`molt_` + secrets token）、列表、吊销

#### routes/memories.py（`server/routes/memories.py:1-89`）
- `POST /api/memories/` — 保存记忆（含冲突检测、200 条限制）
- `GET /api/memories/search` — 语义搜索（embed + vector search）
- `GET /api/memories/` — 列表（支持 category 过滤、limit/offset 分页）
- `GET /api/memories/{id}` — 单条获取
- `PUT /api/memories/{id}` — 更新（内容变更时重新 embed）
- `DELETE /api/memories/{id}` — 软删除（is_archived）
- `PATCH /api/memories/{id}/archive` — 归档

#### routes/personas.py（`server/routes/personas.py:1-137`）
- 完整 CRUD（GET list, GET by id, POST, PUT, DELETE）
- Supabase → in-memory 双层 fallback（`_is_offline()` 检测）
- Pydantic 校验（name 1-200 字符，description 2000，system_prompt 10000）

#### routes/provision.py（`server/routes/provision.py:1-23`）
- `POST /api/provision/` — 一键配置端点
- 调用 `provision_service.auto_provision()` 共享逻辑
- 返回 instructions 引导文本

#### routes/mcp.py（`server/routes/mcp.py:1-1100+`）— **核心文件**
- JSON-RPC 2.0 协议实现（单条 + 批量）
- 12 个 MCP 工具定义和实现：

| 工具 | 类别 | 简介 |
|------|------|------|
| `auto_provision` | 核心 | 一键获取用户完整上下文 |
| `search_memory` | 核心 | 语义搜索记忆 |
| `save_memory` | 核心 | 保存单条记忆（冲突检测） |
| `save_memories` | 批量 | 批量保存记忆 |
| `search_by_tag` | 标签 | 按标签搜索 |
| `get_persona` | Persona | 获取 Persona 详情 |
| `list_personas` | Persona | 列出所有 Persona |
| `match_persona` | Persona | 智能推荐最佳 Persona |
| `compare_personas` | Persona | 多 Persona 视角对比 |
| `consult_persona` | Persona | Persona 问答（DeepSeek LLM） |
| `archive_memory` | 管理 | 软删除记忆 |
| `ping` | 系统 | 心跳检测 |

- 无认证方法：`ping`、`tools/list`、`initialize`
- 认证方法：`tools/call`（X-API-Key header 或 Session Token）
- 标准 JSON-RPC 错误码（-32700 ~ -32002）
- MCP 发现端点：`/.well-known/mcp`

#### routes/sessions.py（`server/routes/sessions.py:1-111`）
- `POST /api/sessions/` — 创建匿名会话（7 天有效期，1000 活跃限制）
- `POST /api/sessions/migrate` — 迁移会话记忆到注册用户

#### routes/billing.py（`server/routes/billing.py:1-114`）
- Stripe Checkout 创建（Pro/Team 订阅）
- Stripe Webhook 处理（subscription.created/updated/deleted）
- GET 当前订阅状态

#### services/embedding.py（`server/services/embedding.py:1-103`）
- 可配置模型：`all-MiniLM-L6-v2`（默认，384 维）或 `paraphrase-multilingual-MiniLM-L12-v2`（多语言）
- 输入截断 8000 字符
- 内存缓存（1000 条，LRU 淘汰）
- 批量嵌入 `embed_batch()`

#### services/vector_store.py（`server/services/vector_store.py:1-110`）
- 线程安全内存向量存储
- CRUD + 余弦相似度搜索
- 冲突检测（similarity > 0.85）
- 用户迁移 `migrate_user()`

#### services/provision_service.py（`server/services/provision_service.py:1-97`）
- `auto_provision()` — 组装用户画像、偏好、规则、Persona、项目、决策、核心知识
- 区分匿名会话和注册用户
- 审计日志记录

#### services/persona_store.py（`server/services/persona_store.py:1-99`）
- 内存 Persona 存储（含 demo 种子数据："战略顾问"、"保守审核员"）
- `demo-user` 的预置 Persona 可在离线模式体验

#### repositories/memory_repo.py（`server/repositories/memory_repo.py:1-160`）
- `SupabaseMemoryRepository`：PostgreSQL + pgvector 持久化
- 继承 `Repository` ABC，实现 9 个接口方法
- 降级到 `VectorStore` in-memory fallback

#### mcp_server.py（`server/mcp_server.py:1-112`）
- MCP stdio 入口（`mcp` Python SDK）
- 通过 HTTP 代理到 `mcp.py` JSON-RPC 端点
- 5 个工具：`auto_provision`, `search_memory`, `save_memory`, `list_personas`, `get_current_context`
- **注意**：仅实现 5 个工具，`mcp.py` 有 12 个——存在不一致

---

## 三、schema.sql 数据库设计

来源：`server/schema.sql:1-180`

### 3.1 所有表及用途

| 表名 | 用途 | 关键字段 |
|------|------|---------|
| **users** | 用户账户 | id (uuid PK), email (unique), name, timezone, language |
| **api_keys** | API Key 管理 | user_id (FK), key_hash (SHA-256), key_prefix, permissions[], is_active, revoked_at |
| **personas** | 人格配置 | user_id (FK), name, type, system_prompt, traits (JSONB), parent_id (fork 来源), version |
| **persona_versions** | Entity 版本历史 | persona_id (FK), version, diff (JSONB), changelog, snapshot (JSONB) |
| **memories** | 记忆存储（pgvector） | user_id (FK), content, category, embedding (vector(384)), tags[], is_archived |
| **projects** | 活跃项目 | user_id (FK), name, description, is_active |
| **decisions** | 决策记录 | user_id (FK), project_id (FK), content, decided_at |
| **audit_logs** | 审计日志 | user_id (FK), api_key_id (FK), action, details (JSONB), ip_address |
| **sessions** | 匿名会话 | token (unique), user_id (nullable FK), expires_at, migrated_at |

### 3.2 关键索引与约束

```sql
-- pgvector HNSW 索引（加速语义搜索）
CREATE INDEX ON memories USING hnsw (embedding vector_cosine_ops);

-- 全文搜索索引
CREATE INDEX memories_content_idx ON memories USING gin (to_tsvector('simple', content));

-- 用户+分类组合索引
CREATE INDEX memories_user_cat_idx ON memories (user_id, category);

-- 会话 token 索引
CREATE INDEX sessions_token_idx ON sessions (token);
```

### 3.3 RLS 行级安全

5 张表启用 RLS（`memories`, `personas`, `projects`, `decisions`, `api_keys`），每张表基于 `user_id = auth.uid()` 隔离。

### 3.4 match_memories RPC

```sql
CREATE OR REPLACE FUNCTION match_memories(
    query_embedding vector(384),   -- 与 embedding.py 中 DIM=384 一致
    match_user_id text,
    match_count int DEFAULT 5,
    match_category text DEFAULT NULL,
    match_threshold float DEFAULT 0.5
) RETURNS TABLE(...)
```

**重要**：`migration.sql` 和 `schema.sql` 中的 embedding 维度已统一为 `vector(384)`，与 `embedding.py` 中 `_DIM = 384` 一致。第 1 轮 PDCA 复盘指出的维度不一致问题（1536/1024/4096）已修复。

---

## 四、MCP 协议实现

### 4.1 双入口架构

| 入口 | 位置 | 协议 | 工具数 | 说明 |
|------|------|------|:---:|------|
| HTTP JSON-RPC | `routes/mcp.py` | HTTP POST `/mcp` | 12 | 主入口，支持批量请求 |
| stdio | `mcp_server.py` | stdio (MCP SDK) | 5 | 代理到 HTTP，用于本地 Agent |

### 4.2 HTTP 端点提供的工具（完整 12 个）

来源：`server/routes/mcp.py:92-295`

1. **search_memory** — 语义搜索，支持 category 过滤
2. **save_memory** — 单条保存（含冲突检测，force 参数）
3. **save_memories** — 批量保存
4. **search_by_tag** — 按标签搜索（OR 逻辑）
5. **get_persona** — Persona 详情
6. **list_personas** — Persona 列表
7. **auto_provision** — 一键配置
8. **consult_persona** — Persona 问答（调用 DeepSeek LLM）
9. **match_persona** — 基于 Jaccard 词重叠的智能推荐
10. **compare_personas** — 多 Persona 对比（每个 Persona 调用一次 LLM）
11. **archive_memory** — 软删除记忆
12. **ping** — 心跳检测

### 4.3 MCP 协议合规性

- ✅ JSON-RPC 2.0 规范（单条 + 批量）
- ✅ `.well-known/mcp` 发现端点
- ✅ `initialize` 握手（protocolVersion, capabilities, serverInfo）
- ✅ `tools/list` 免认证
- ✅ `ping` 免认证
- ✅ 标准错误码（-32700 Parse Error ~ -32002 Server Not Initialized）
- ✅ 批量请求支持

### 4.4 stdio 入口（mcp_server.py）

使用 `mcp` Python SDK，通过 `httpx` 代理 HTTP 请求到 `mcp.py` 端点。提供 5 个工具：`auto_provision`, `search_memory`, `save_memory`, `list_personas`, `get_current_context`。

---

## 五、web/ 前端分析

### 5.1 技术栈

```
Next.js 14 + React 18 + TypeScript + Tailwind CSS 3.4
@supabase/ssr + @supabase/supabase-js
lucide-react (图标)
```

来源：`web/package.json:1-20`

### 5.2 页面结构

| 路由 | 文件 | 功能 | 状态 |
|------|------|------|:---:|
| `/` | `src/app/page.tsx` | OnePage Landing：Hero→Features→How It Works→Pricing→About→Privacy | ✅ |
| `/docs` | `src/app/docs/page.tsx` | API 文档中心（12 个 API + MCP 协议 + FAQ） | ✅ |
| `/login` | `src/app/login/page.tsx` | Supabase Auth 登录 | ✅ |
| `/register` | `src/app/register/page.tsx` | Supabase Auth 注册 | ✅ |
| `/dashboard` | `src/app/dashboard/page.tsx` | 仪表盘：统计卡片 + 快速接入指南 + 演示模式 | ✅ |
| `/dashboard/memories` | `src/app/dashboard/memories/page.tsx` | 记忆管理：搜索、分类过滤、CRUD、演示数据 | ✅ |
| `/dashboard/personas` | `src/app/dashboard/personas/page.tsx` | Persona 管理：创建、展开、编辑 Modal、演示数据 | ✅ |
| `/dashboard/settings` | `src/app/dashboard/settings/page.tsx` | API Key 管理 | ✅ |
| `/blog` | `src/app/blog/page.tsx` | 博客占位页 | ⚠️ |
| `/blog/ai-identity-layer` | `...` | 单篇文章 | ⚠️ |
| `/blog/cross-platform-persona` | `...` | 单篇文章 | ⚠️ |
| `/blog/mcp-ai-usb-c` | `...` | 单篇文章 | ⚠️ |

### 5.3 设计系统（Linear 风格暗色主题）

来源：`DESIGN.md:1-120`

- **主色**：`#7170ff`（签名字紫色），克制使用
- **背景层级**：`#08090a`(flat) → `#0f1011`(surface) → `#191a1b`(raised) → `#23252a`(hover)
- **边框替代**：`box-shadow: 0 0 0 1px rgba(255,255,255,0.08)` 取代传统边框
- **字重三级**：400(body) → 510(ui) → 590(heading)
- **圆角标准化**：6px(btn) / 8px(card) / 12px(panel) / 9999px(pill)

### 5.4 前端架构特点

- **演示模式**：无 Supabase 时自动切换，显示 5 条 demo 记忆 + 3 个 demo Persona
- **i18n**：中英文双语言支持（`src/contexts/LanguageContext.tsx` + `src/lib/i18n.ts`）
- **认证中间件**：`src/middleware.ts` — Supabase SSR cookie 自动续期，未登录用户可无阻碍浏览
- **API 客户端**：`src/lib/api.ts` — 自动附加 Bearer token，错误处理统一

---

## 六、extension/ 浏览器插件

### 6.1 功能概览

来源：`extension/manifest.json` | `extension/content.js` | `extension/popup.html`

- **Manifest V3** Chrome 扩展
- **支持站点**：ChatGPT (chatgpt.com)、Claude (claude.ai)、Gemini (gemini.google.com)、DeepSeek (chat.deepseek.com)
- **核心功能**：
  1. 浮动 FAB 按钮（🧠）在右下角
  2. 搜索面板：输入关键词 → 调用 `/api/memories/search` → 显示结果卡片
  3. 一键注入：将记忆内容注入到 AI 输入框（支持 contenteditable/textarea 多种选择器）
  4. API Key 配置面板（popup.html）
- **文件结构**（10 个文件，1227 行）：
  - `manifest.json` — Manifest V3 声明
  - `popup.html` + `popup.js` — 配置 UI
  - `content.js` — 核心注入逻辑（407 行）
  - `toolbar.css` — 暗色主题样式（406 行）
  - `background.js` — Service worker
  - `icons/` — 3 个 SVG 图标

### 6.2 注入机制

`content.js:140-180` 实现了多站点选择器适配：
- ChatGPT: `#prompt-textarea`, `[contenteditable]`
- Claude: `.ProseMirror`, `[contenteditable]`
- Gemini: `textarea`, `[contenteditable]`
- DeepSeek: `#chat-input`, `textarea`
- 通用回退：聚焦元素的最近 textarea

---

## 七、测试覆盖情况

### 7.1 测试文件总览

| 测试文件 | 测试函数数（约） | 覆盖模块 | Mock 策略 |
|---------|:---:|------|------|
| `test_mcp.py` | ~20 | MCP JSON-RPC 端点 | mock Supabase + mock embed |
| `test_memories_api.py` | 14 | Memories REST API | mock Supabase + mock embed |
| `test_personas_api.py` | 5 | Personas API | mock Supabase |
| `test_auth_api.py` | 7 | Auth API | mock Supabase |
| `test_embedding.py` | 5 | Embedding 服务 | mock sentence-transformers |
| `test_vector_store.py` | 14 | VectorStore | 无 mock |
| `test_memory_repo.py` | 8 | SupabaseMemoryRepository | mock Supabase |
| `test_provision.py` | — | Provision 端点 | mock Supabase |
| **合计** | **~73+** | 8 个测试文件 | — |

### 7.2 测试策略

- **conftest.py**（`server/tests/conftest.py:1-60`）：全局 mock Supabase + mock embed + 内存 VectorStore
- 测试可零外部依赖运行：`cd server && python -m pytest tests/ -v`
- CI 已配置（`github/workflows/ci.yml`）：Python 3.12 + pytest + py_compile + Next.js build

### 7.3 测试覆盖缺口

- ✅ MCP 端点：已覆盖（第 1 轮 PDCA 时缺失，第 3 轮已补齐）
- ✅ Provision 端点：已覆盖
- ⚠️ 无真实 Supabase 集成测试（全部 mock）
- ⚠️ 无性能/负载测试
- ⚠️ Chrome 插件未实机测试

---

## 八、部署方式

### 8.1 Docker Compose（`docker-compose.yml:1-58`）

```yaml
services:
  postgres:    # pgvector/pgvector:pg16 + 健康检查 + schema.sql 自动初始化
  api:         # FastAPI（build: ./server），端口 8642→8000，依赖 postgres 健康
  web:         # Next.js（build: ./web），端口 8701→3000，依赖 api 健康
```

### 8.2 Dockerfile（`server/Dockerfile:1-26`）

- Base: `python:3.11-slim`
- 非 root 用户 `moltable`
- 健康检查：`curl -f http://localhost:8000/health`

### 8.3 CI/CD（`.github/workflows/ci.yml:1-26`）

- **Backend**：Python 3.12 → pip install → pytest → py_compile
- **Frontend**：Node 20 → npm ci → next build

### 8.4 环境变量（`server/.env.example:1-40`）

| 变量 | 用途 | 必需 |
|------|------|:---:|
| `SUPABASE_URL` | Supabase 项目 URL | 生产 |
| `SUPABASE_SERVICE_ROLE_KEY` | Admin API Key（绕过 RLS） | 生产 |
| `DEEPSEEK_API_KEY` | LLM API Key | 生产 |
| `API_KEY_PEPPER` | PBKDF2-HMAC 加盐 | 生产 |
| `ALLOWED_ORIGINS` | CORS 白名单 | 生产 |
| `MOLTABLE_EMBED_MODEL` | 嵌入模型名称 | 可选 |
| `STRIPE_SECRET_KEY` | Stripe 支付 | 可选 |

---

## 九、迭代复盘报告关键发现

### 9.1 第 1 轮 PDCA（2026-06-16 ~ 06-18）

来源：`迭代复盘报告_PDCA第1轮.md`

**成就**：
- Phase 0 安全修复 6/6 ✅（CORS、API Key 哈希、输入校验、速率限制、安全头）
- Phase 1 数据持久化 6/6 ✅（Supabase pgvector Repository、RLS、HNSW 索引）
- Phase 2 MCP JSON-RPC 8/10 ⚠️（缺 test_mcp、test_provision）

**致命问题（已修复）**：
- 🔴 `schema.sql` 中 embedding 维度 `vector(1536)` 与 `embedding.py` `4096` 不一致
- 🔴 `migration.sql` 中 `vector(1024)` 也不一致
- 🔴 MCP 端点零测试覆盖
- 🔴 双 MCP 入口（stdio + HTTP）未统一

### 9.2 第 3 轮 PDCA（2026-07-04）

来源：`迭代复盘报告_PDCA第3轮.md`

**成就**：
- 前端设计系统升级（Linear 风格暗色主题）
- Chrome 浏览器插件从 0 到 1（1227 行代码）
- Hermes Skill 升级至 v3.0.0

**未完成**：
- Chrome 插件实机测试
- 生产部署（Railway + Vercel + DNS）
- 后端集成测试（真实 Supabase）

### 9.3 PRD 功能完成度

```
MVP (Phase 1):     10/10 ✅ (100%)
Phase 2 (Persona): 6/7  ⚠️ (86%)  [缺 F14 Persona 对比 → 实际上 compare_personas 已实现]
Phase 2 (插件):    1/1  ✅ (100%)
Phase 3 (进化):    0/6  ❌ (0%)
```

---

## 十、综合评价

### 10.1 优点

1. **产品定位精准** — "AI Identity Layer"概念清晰，三层架构（Identity → Persona → Agent）在竞品中独一无二。不是又一个 AI wrapper，而是基础设施层。

2. **MCP 协议实现完整** — JSON-RPC 2.0 规范完整实现，12 个工具覆盖记忆管理、Persona 系统、配置供给全流程。批量请求、标准错误码、发现端点全部到位。代码位于 `server/routes/mcp.py`（1100+ 行），是项目最核心的交付物。

3. **架构分层清晰** — Routes → Services → Repositories 三层分离。`Repository` ABC 抽象基类 + Supabase/In-memory 双实现，降级优雅。验证：`server/services/repository.py`（ABC） → `server/repositories/memory_repo.py`（Supabase） + `server/services/vector_store.py`（In-memory）

4. **安全底盘扎实** — 10 层防护：速率限制、1MB 请求体限制、Pydantic 输入校验、嵌入截断、200 条记忆上限、PBKDF2-HMAC + pepper 认证、失败审计日志、安全头、CORS 白名单。来源：`上线就绪度评估报告.md:20-50`

5. **前端设计专业** — Linear 风格暗色主题（`DESIGN.md` 定义完整设计系统），shadow-as-border 技术路径，字重三级制度（400/510/590），紫色 accent 克制使用。演示模式 + i18n 双语言 + 中间件免登录浏览，体验闭环完整。

6. **离线友好** — 无 Supabase 时自动切换 in-memory 模式，前端有 demo 数据，后端 Persona 有种子数据。可在 `pip install -r requirements.txt && uvicorn main:app` 后立即体验。

7. **测试体系完善** — 8 个测试文件、73+ 个测试函数、CI 集成。conftest 全局 mock 设计优秀，测试可零外部依赖运行。

8. **文档齐全** — README、PRD、DESIGN、技术架构、3 轮 PDCA 复盘、上线就绪度评估、系统全面评估、Agent 体验分析、竞品调研、ClawHunt 调研。共计 10+ 份文档。

### 10.2 风险与不足

1. **MCP 双入口不一致** — `mcp_server.py`（stdio）仅实现 5 个工具，而 `mcp.py`（HTTP）实现 12 个。如果 Agent 通过 stdio 连接，会缺少 `consult_persona`、`compare_personas`、`save_memories` 等关键功能。来源：`server/mcp_server.py:43-95` vs `server/routes/mcp.py:92-295`

2. **Supabase 强依赖** — 尽管有 in-memory fallback，但注册、API Key 生成、真实 Persona 持久化全部依赖 Supabase。in-memory 模式下只能体验 demo 数据。生产环境若 Supabase 宕机，系统降级为"只读 demo 模式"。

3. **DeepSeek LLM 单点依赖** — `consult_persona` 和 `compare_personas` 依赖 DeepSeek API。如果 API Key 不可用或超时，这两个最酷的 Persona 功能返回本地回退文本。验证：`routes/mcp.py:420-510` 有完整的超时重试（30s timeout, 2 retries）+ 本地回退逻辑。

4. **无数据库连接池** — `app_state.py` 中 Supabase 客户端是单连接，并发 100+ 时可能成为瓶颈。

5. **无缓存层** — 嵌入计算虽有小缓存（1000 条），但无 Redis/分布式缓存。`auto_provision()` 每次都重新查询 5 张表。

6. **前端功能残缺** — 博客为占位页，注册/登录依赖 Supabase（本地不可用），记忆管理和 Persona 管理在演示模式下所有写操作只弹 Toast。

7. **Chrome 插件未实机测试** — 代码结构完整但未在 Chrome 加载测试。AI 输入框注入选择器可能因站点更新失效。

8. **Stripe 计费未与注册流程打通** — `billing.py` 存在但 `/register` 页面不创建 Stripe 客户。

### 10.3 成熟度评估

| 维度 | 评分 | 说明 |
|------|:---:|------|
| 产品定义 | **A** (95) | 定位清晰、差异化明确、三层架构独树一帜 |
| 后端架构 | **A-** (88) | 分层清晰、降级优雅、12 个 MCP 工具完整 |
| 前端体验 | **B+** (85) | 设计专业、演示模式好，但写操作残缺 |
| MCP 协议 | **A** (92) | JSON-RPC 2.0 完整实现，合规性高 |
| 安全 | **A-** (87) | 10 层防护，缺 TLS/WAF 生产层 |
| 测试 | **B+** (83) | 73+ 测试函数，缺真实集成测试 |
| 运维部署 | **B** (82) | Docker + CI 就绪，缺监控/备份/多环境 |
| 文档 | **A** (93) | 10+ 份文档，覆盖 PRD/设计/复盘/评估 |
| Chrome 插件 | **B** (75) | 代码完整，未实机验证 |
| **综合** | **B+ / A- (86)** | **MVP 可演示，生产部署需补齐监控和 Supabase 集成** |

### 10.4 与其他项目的定位关系

本目录下存在配套调研报告：
- `ClawHunt调研.md` / `ClawHunt_深度调研报告.md` / `ClawHunt_任务流程深度分析.md` — 竞品 ClawHunt 分析
- `Moltable_竞品与相关项目调研.md` — mem0、Nocturne、ChatGPT Memory 等竞品对比
- `Agent体验分析报告.md` — 从 Agent 视角评估 Moltable 使用体验

Moltable 与 ClawHunt 的区别：ClawHunt 是 AI Agent 任务执行平台，Moltable 是 AI 身份记忆层。两者互补而非竞争。

---

## 附录：关键文件路径索引

| 文件 | 路径 | 行数（约） |
|------|------|:---:|
| README | `README.md` | 50 |
| PRD | `PRD_产品需求文档.md` | 143 |
| DESIGN | `DESIGN.md` | 120 |
| 技术架构 | `技术架构设计.md` | 250 |
| Schema | `server/schema.sql` | 180 |
| MCP HTTP | `server/routes/mcp.py` | 1100+ |
| MCP stdio | `server/mcp_server.py` | 112 |
| Main | `server/main.py` | 130 |
| App State | `server/app_state.py` | 47 |
| Embedding | `server/services/embedding.py` | 103 |
| Vector Store | `server/services/vector_store.py` | 110 |
| Memory Repo | `server/repositories/memory_repo.py` | 160 |
| Auth | `server/routes/auth.py` | 169 |
| Personas API | `server/routes/personas.py` | 137 |
| Provision | `server/routes/provision.py` | 23 |
| Sessions | `server/routes/sessions.py` | 111 |
| Billing | `server/routes/billing.py` | 114 |
| Landing | `web/src/app/page.tsx` | 320 |
| Dashboard | `web/src/app/dashboard/page.tsx` | 170 |
| Memories Page | `web/src/app/dashboard/memories/page.tsx` | 270 |
| Personas Page | `web/src/app/dashboard/personas/page.tsx` | 240 |
| Extension | `extension/content.js` | 407 |
| Skill | `skills/moltable/SKILL.md` | 130 |
| Docker Compose | `docker-compose.yml` | 58 |
| CI | `.github/workflows/ci.yml` | 26 |
| PDCA 第1轮 | `迭代复盘报告_PDCA第1轮.md` | 220 |
| PDCA 第3轮 | `迭代复盘报告_PDCA第3轮.md` | 120 |
| 上线评估 | `上线就绪度评估报告.md` | 180 |
| 系统评估 | `系统全面评估报告.md` | 160 |
| Agent 体验 | `server/agent_experience.py` | 330 |
