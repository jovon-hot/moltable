# Moltable 线上环境配置说明

> 维护者：阿福 ｜ 移交日期：2026-08-02

---

## 一、架构

```
Browser → Vercel (Next.js 14) → Railway (FastAPI) → Supabase (PostgreSQL + pgvector)
              ↓ 直连 auth             ↓
          Supabase Auth          Supabase (service_role)
```

---

## 二、域名

| 域名 | 指向 | 方式 |
|------|------|:--:|
| `moltable.ai` | Vercel | CNAME → `cname.vercel-dns.com` |
| `www.moltable.ai` | Vercel | CNAME → `cname.vercel-dns.com` |
| `api.moltable.ai` | Railway | CNAME → `moltable-production-15ad.up.railway.app` |

---

## 三、Railway · 后端

| 配置项 | 值 |
|------|------|
| **URL** | `https://moltable-production-15ad.up.railway.app` |
| **Target Port** | **8080** （不是 80！改 80 → 502） |
| **Runtime** | Python 3.11 · Uvicorn |
| **Entry** | `server/main.py` |
| **Dockerfile** | 项目根目录 `/Dockerfile` |
| **依赖** | `requirements-railway.txt` （不加 torch，避免构建超时） |

### 环境变量（Dashboard → Variables）

| 变量 | 说明 |
|------|------|
| `SUPABASE_URL` | `https://wjkyoqbjcxqqsruuutvf.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | service_role 密钥 |
| `API_KEY_PEPPER` | 随机 64 位 hex，密码哈希用 |
| `ALLOWED_ORIGINS` | `https://www.moltable.ai,https://moltable.ai` |

### 健康检查

```bash
curl https://api.moltable.ai/health
# → {"status":"ok","db":true}
```

---

## 四、Vercel · 前端

| 配置项 | 值 |
|------|------|
| **URL** | `https://www.moltable.ai` |
| **GitHub** | `jovon-hot/moltable` · branch `main` |
| **Framework** | Next.js 14 · `web/` 子目录 |
| **构建** | 自动触发（push → `main` → 构建 → 部署） |

### 环境变量（Vercel Dashboard → Settings → Environment Variables）

| 变量 | 说明 |
|------|------|
| `NEXT_PUBLIC_API_URL` | `https://api.moltable.ai` |
| `NEXT_PUBLIC_SUPABASE_URL` | `https://wjkyoqbjcxqqsruuutvf.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | anon key（⚠️ 不是 service_role） |

---

## 五、Supabase · 数据库

| 配置项 | 值 |
|------|------|
| **URL** | `https://wjkyoqbjcxqqsruuutvf.supabase.co` |
| **引擎** | PostgreSQL 15 + pgvector |
| **Schema** | `server/schema.sql` |

### 关键表

| 表 | 用途 |
|------|------|
| `users` | 用户账号（含 `plan`、`password_hash`） |
| `api_keys` | API 密钥（`molt_` 前缀） |
| `sessions` | 会话令牌（`mol_` 前缀·7天有效） |
| `memories` | 记忆（pgvector 搜索） |
| `personas` | 人格配置 |
| `projects` | 项目环境（含 `knowledge_bases`、`tools` JSONB） |

---

## 六、MCP 服务器

| 配置项 | 值 |
|------|------|
| **URL** | `https://api.moltable.ai/mcp` |
| **协议** | JSON-RPC 2.0 |
| **认证** | `X-API-Key` header |
| **工具数** | 14（12 Free + 4 Pro） |

### Hermes 接入

```bash
hermes config set mcp_servers.moltable.url "https://api.moltable.ai/mcp"
hermes config set mcp_servers.moltable.headers.X-API-Key "molt_你的KEY"
hermes mcp test moltable
```

---

## 七、端到端验证

```bash
# 1. 健康检查
curl https://api.moltable.ai/health

# 2. 注册
curl -X POST https://api.moltable.ai/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@moltable.ai","password":"Test2024!"}'

# 3. MCP 工具列表
curl -X POST https://api.moltable.ai/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'

# 4. 前端
curl -o /dev/null -w "%{http_code}" https://www.moltable.ai
# → 200
```

---

## 八、排查速查表

| 症状 | 根因 | 修复 |
|------|------|------|
| Railway 502 | Target Port=80 | 改为 8080 |
| 注册 500 | `api_keys` 缺 `is_active` 列 | `ALTER TABLE ADD COLUMN` |
| 搜索无结果 | embedding 用 trigram hash | 安装 sentence-transformers 或等 keyword fallback |
| Vercel 连不上 API | `NEXT_PUBLIC_API_URL` 未设 | Vercel Dashboard 添加 |
| 构建超时 | torch 下载 2GB | 用 `requirements-railway.txt` |
| 部署后不生效 | Vercel 缓存旧版本 | 等 2-5 分钟或手动 Redeploy |
