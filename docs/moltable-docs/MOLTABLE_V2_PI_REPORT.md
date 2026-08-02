# Moltable v2 — 项目全面分析报告

> 分析日期: 2025年7月 | 版本: 0.1.0 Alpha | 结论: 架构完整，MVP 就绪，差异化突出

---

## 1. 产品定位

- **一句话**: "AI 时代的身份层 — 在任何 AI 里加载你的 Moltable，AI 就自动认识你"
- **定位**: AI 身份中间层，不是聊天界面、不是模型路由器、不是 Prompt 模板库
- **三层架构**: Identity (唯一) → Persona (多个) → Agent (多个)，共享同一套 Memory
- **核心场景**: 跨 AI 无缝切换（Hermes → Claude 自动加载上下文）、多 Persona 角色切换、Persona 结构化碰撞分析、记忆渐进积累
- **竞品差异**: vs mem0（有 Persona 系统）、vs ChatGPT Memory（用户可控/跨平台）、vs Nocturne（开源）
- **许可证**: MIT，数据归用户所有
- 证据: `README.md` L1-L25, `PRD_产品需求文档.md` L1-L68

---

## 2. server/ 后端架构

- **框架**: Python + FastAPI，入口 `server/main.py`，端口 8642（Docker 映射 8000）
- **目录结构**:
  - `routes/`: 8 个路由模块（auth, memories, personas, provision, mcp, sessions, billing, v1）
  - `services/`: embedding (sentence-transformers)、vector_store (内存向量存储)、persona_store、provision_service、repository (抽象基类)
  - `repositories/`: memory_repo (Supabase pgvector + 内存 fallback 双模式)
- **关键中间件**: CORS、安全 headers（X-Content-Type-Options/X-Frame-Options 等）、1MB body 限制、速率限制（SlowAPI）、API 版本 header
- **认证三通道**: Bearer JWT (Supabase Auth)、X-API-Key、X-Session-Token（匿名会话）
- **LLM 集成**: DeepSeek API（可选），超时 30s + 2 次重试，本地回退模式
- **状态管理**: `app_state.py` 单例模式管理 supabase client、rate limiter、vector store
- 证据: `server/main.py`, `server/app_state.py`, `server/requirements.txt`

---

## 3. MCP 协议工具清单

MCP 端点为 `POST /mcp` (JSON-RPC 2.0)，发现端点为 `GET /.well-known/mcp`。共 12 个工具：

| 工具名 | 功能 |
|--------|------|
| `auto_provision` | 一键获取用户完整上下文（画像/规则/Persona/项目/决策/知识） |
| `search_memory` | 语义搜索记忆，支持 category 过滤和 top_k 控制 |
| `save_memory` | 保存单条记忆，自动冲突检测（相似度>0.9 拦截） |
| `save_memories` | 批量保存多条记忆 |
| `search_by_tag` | 按标签搜索记忆（OR 逻辑） |
| `get_persona` | 获取指定 Persona 完整配置（system_prompt + traits） |
| `list_personas` | 列出所有活跃 Persona |
| `consult_persona` | 用指定 Persona 身份 + 用户记忆上下文回答问题（调用 DeepSeek LLM） |
| `match_persona` | 根据问题语义自动推荐最匹配的 Persona |
| `compare_personas` | 多 Persona 回答同一问题，返回对比视角 |
| `archive_memory` | 软删除记忆 |
| `ping` | 心跳检测 |

另有 stdio 入口 `server/mcp_server.py` (5 个工具代理)。无需认证: ping/initialize/tools/list。
证据: `server/routes/mcp.py` L84-L300, `server/mcp_server.py` L30-L100

---

## 4. 数据库 Schema

8 张核心表（Supabase PostgreSQL + pgvector）：

| 表名 | 用途 |
|------|------|
| `users` | 用户基础信息（email/name/timezone/language） |
| `api_keys` | API Key 管理（PBKDF2 哈希存储，molt_ 前缀） |
| `personas` | Persona 配置（name/system_prompt/traits/model_preference/version） |
| `persona_versions` | Persona 版本历史（diff/changelog/snapshot） |
| `memories` | 记忆存储（content/category/embedding(vector 384)/tags/confidence） |
| `projects` | 活跃项目管理 |
| `decisions` | 决策记录 |
| `audit_logs` | 审计日志（action/details/ip_address） |
| `sessions` | 匿名会话（token/migrated_at/expires_at） |

pgvector RPC: `match_memories()` 函数做余弦相似度语义搜索，HNSW 索引加速。RLS 行级安全策略隔离用户数据。
证据: `server/schema.sql` (全文件 157 行)

---

## 5. web/ 前端

- **技术栈**: Next.js 14 + React 18 + TypeScript + Tailwind CSS 3.4 + Lucide React 图标
- **页面路由**:
  - `/` — Landing Page (功能展示/定价/隐私说明)
  - `/login` — 登录
  - `/register` — 注册
  - `/dashboard` — 仪表盘（记忆数/Persona 数统计）
  - `/dashboard/memories` — 记忆管理
  - `/dashboard/personas` — Persona 管理
  - `/dashboard/settings` — API Key 管理/设置
  - `/blog/*` — 3 篇产品博客
  - `/docs` — 文档页
- **认证**: Supabase SSR + 中间件 (`middleware.ts`)，Bearer token 注入 API 请求
- **国际化**: `LanguageContext` 支持中英文切换
- **支付**: Stripe Checkout 集成（pro/team 订阅计划）
- 证据: `web/package.json`, `web/src/app/page.tsx`, `web/src/lib/api.ts`

---

## 6. extension/ 浏览器插件

- **类型**: Chrome Extension Manifest V3
- **支持站点**: ChatGPT、Claude、Gemini、DeepSeek
- **核心功能**:
  - 浮动记忆工具栏（紫色 FAB 按钮，右下角定位）
  - 记忆搜索（防抖 350ms，调用 `/api/memories/search`）
  - 一键注入记忆到 AI 输入框
  - API Key 存储在 `chrome.storage.local`
  - 零依赖纯 JS 实现，无需构建
- **文件**: `content.js`（内容脚本）、`popup.js`/`popup.html`（配置弹窗）、`background.js`（service worker）、`toolbar.css`（暗色主题）
- 证据: `extension/manifest.json`, `extension/README.md`, `extension/content.js`

---

## 7. tests/ 测试覆盖

8 个测试文件，使用 pytest + pytest-asyncio + FastAPI TestClient，全局 mock Supabase/embedding：

| 测试文件 | 覆盖内容 |
|----------|----------|
| `test_mcp.py` | MCP JSON-RPC 2.0 全量：发现、免认证方法、12 工具调用、错误处理、批量请求 |
| `test_provision.py` | auto_provision REST 端点认证/正常/边界/instructions/速率限制 |
| `test_memories_api.py` | CRUD 全流程、分类过滤、认证、参数校验、搜索 |
| `test_personas_api.py` | Persona CRUD、认证、空列表、必要字段校验 |
| `test_auth_api.py` | JWT/API Key 认证、create/list/revoke API Key、me 端点 |
| `test_vector_store.py` | 余弦相似度、CRUD、搜索/category 过滤/conflict/archived/stats/migrate |
| `test_embedding.py` | embed/embed_batch、归一化、模型缓存、维度 384 |
| `test_memory_repo.py` | SupabaseMemoryRepository online/offline 双模式、fallback 行为 |

CI: `.github/workflows/ci.yml` — 后端 pytest + py_compile 语法检查，前端 next build
证据: `server/tests/*`, `.github/workflows/ci.yml`, `server/conftest.py`

---

## 8. 部署

- **Docker**: `server/Dockerfile` — Python 3.11-slim，非 root 用户运行，HEALTHCHECK
- **Docker Compose**: 三服务编排
  - `postgres`: pgvector/pgvector:pg16，自动执行 schema.sql 初始化
  - `api`: FastAPI 服务，端口 8642→8000
  - `web`: Next.js 前端，端口 8701→3000
- **环境依赖**: Supabase 凭证（SUPABASE_URL/SERVICE_ROLE_KEY）、DEEPSEEK_API_KEY（可选）、API_KEY_PEPPER（安全必需）、STRIPE_SECRET_KEY（可选）
- **无 Kubernetes/Helm 配置**，适合单机部署
- 证据: `docker-compose.yml`, `server/Dockerfile`

---

## 9. 综合评价

### 优势 (⭐⭐⭐⭐⭐)

1. **差异化突出**: auto_provision() 一键配置是杀手级功能，多 Persona 系统在竞品中独一无二
2. **架构务实**: Supabase + 内存 fallback 双模式，无数据库也能运行；pgvector 语义搜索选型正确
3. **MCP 标准合规**: 完整 JSON-RPC 2.0 实现 + 12 个工具 + 批量请求 + 发现端点
4. **零注册体验**: 匿名会话（mol_ token）+ 7 天有效期 + 迁移机制降低使用门槛
5. **测试覆盖扎实**: 8 个测试文件覆盖 API/MCP/向量/嵌入/仓库所有层级
6. **多入口**: REST API + MCP JSON-RPC + MCP stdio + 浏览器插件 + Agent Skill 文件
7. **安全设计**: PBKDF2 API Key 哈希、RLS 行级安全、审计日志、速率限制、安全 headers

### 待改进 (⭐⭐⭐)

1. **无 docker-compose 的 web 端 Dockerfile**: docker-compose 引用 `build: ./web` 但缺少 `web/Dockerfile`（仅 server 有）
2. **embedding 模型**: 默认 all-MiniLM-L6-v2 (384 维，英语优化)，中文需手动切换到 paraphrase-multilingual
3. **无数据持久化备份策略**: 依赖 Supabase 托管，无本地备份/导出方案
4. **内存限制硬编码**: 匿名用户 200 条记忆上限，超额后无渐进式限制（仅 block）
5. **前端缺少 loading/empty/error 三态完整覆盖**: 部分页面仅简单处理
6. **skills/**: 仅 Hermes Agent Skill 文件，缺少 Claude、ChatGPT 等平台的原生适配

### 总评

项目处于 **MVP 完成、差异化验证阶段**。三层架构清晰，MCP 协议实现规范，测试覆盖扎实。auto_provision + Persona 系统是核心壁垒。当前 Alpha 阶段适合早期用户验证，距生产环境尚需补全 web Dockerfile、中文 embedding 默认切换、数据备份方案。

---

*报告生成: PI Coding Agent | 项目路径: /Users/haidong/Desktop/moltable v2*
