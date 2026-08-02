# Moltable v2 生产部署指南

> 目标：Vercel（前端）+ Supabase（数据库）+ Railway（后端）

---

## 架构概览

```
用户浏览器 → Vercel (web/, Next.js) → Railway (server/, FastAPI) → Supabase (PostgreSQL+pgvector)
                     ↓ 直连                           ↓
              Supabase Auth (JWT)              Supabase (service_role key)
```

---

## 一、Supabase 数据库（先做）

### 1.1 创建项目
1. 打开 [supabase.com](https://supabase.com) → New Project
2. 记下 `Project URL` 和 `anon key` / `service_role key`
3. 进入 SQL Editor

### 1.2 执行 Schema
打开 `server/schema.sql`，**逐段执行**：

```sql
-- 第1段：启用扩展
create extension if not exists vector;

-- 第2段：建表（users → api_keys → personas → memories → projects → decisions → audit_logs → sessions）
-- 复制 schema.sql 中所有 CREATE TABLE 语句

-- 第3段：创建索引和 RPC 函数
-- match_memories() 函数 + HNSW 索引

-- 第4段：启用 RLS
-- 复制所有 ALTER TABLE ... ENABLE ROW LEVEL SECURITY + CREATE POLICY 语句
```

### 1.3 验证
```sql
SELECT * FROM pg_extension WHERE extname = 'vector';  -- 应返回一行
SELECT * FROM users LIMIT 1;  -- 空表但结构存在
```

---

## 二、Railway 部署后端

### 2.1 前置
- Railway 账号 + CLI 安装（`brew install railway`）
- 本项目已包含 `server/Dockerfile` + `server/railway.json`

### 2.2 环境变量（在 Railway Dashboard 设置）

| 变量 | 说明 | 从哪里获取 |
|------|------|-----------|
| `SUPABASE_URL` | Supabase 项目 URL | Supabase Settings → API |
| `SUPABASE_SERVICE_ROLE_KEY` | service_role key | Supabase Settings → API |
| `API_KEY_PEPPER` | PBKDF2 pepper salt | 用 `python3 -c "import secrets; print(secrets.token_hex(32))"` 生成 |
| `DEEPSEEK_API_KEY` | LLM API key（可选） | deepseek.com |
| `ALLOWED_ORIGINS` | CORS 白名单 | Vercel 域名，如 `https://moltable.vercel.app` |
| `MOLTABLE_ISSUER_KEY` | Ed25519 私钥（DID+VC） | `python3 -c "from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey; print(Ed25519PrivateKey.generate().private_bytes_raw().hex())"` |
| `MOLTABLE_DOMAIN` | DID 域名 | `moltable.io` 或你的域名 |
| `STRIPE_SECRET_KEY` | Stripe 密钥（可选） | Stripe Dashboard |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook（可选） | Stripe Dashboard |
| `STRIPE_PRICE_PRO` | Pro 价格 ID（可选） | Stripe Dashboard |
| `STRIPE_PRICE_TEAM` | Team 价格 ID（可选） | Stripe Dashboard |

> ⚠️ `MOLTABLE_ISSUER_KEY` 必须持久化——重启后 VC 签名仍一致。在 Railway 中设置一次后不要改。

### 2.3 部署
```bash
cd ~/Desktop/moltable\ v2/server
railway login
railway init
railway up
```

Railway 自动检测 Dockerfile 并构建。首次构建约 5-8 分钟（含 torch CPU 版下载）。

### 2.4 验证
```bash
curl https://你的项目.railway.app/health
# → {"status":"ok","db":true,"db_required":true}
```

记下 Railway 分配的域名（如 `moltable-api.up.railway.app`）。

---

## 三、Vercel 部署前端

### 3.1 环境变量（在 Vercel Dashboard 设置）

| 变量 | 说明 | 值 |
|------|------|----|
| `NEXT_PUBLIC_API_URL` | 后端地址 | Railway 域名，如 `https://moltable-api.up.railway.app` |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase URL | Supabase Project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anon key | Supabase anon/public key |

> ⚠️ `NEXT_PUBLIC_` 前缀的变量会暴露到浏览器——只用 anon key，不要用 service_role key！

### 3.2 部署
```bash
cd ~/Desktop/moltable\ v2/web
vercel --prod
```

或通过 Vercel Dashboard：
1. Import Git Repository → 选择 `~/Desktop/moltable v2/web` 目录
2. Framework 选 Next.js
3. 设置上述环境变量
4. Deploy

### 3.3 验证
```bash
curl https://moltable.vercel.app
# → 应该返回 Landing 页 HTML
```

---

## 四、部署后验证清单

### 4.1 后端健康检查
```bash
curl https://api.你的域名/health
# → {"status":"ok","db":true}
```

### 4.2 注册流程
```bash
# 注册
curl -X POST https://api.你的域名/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test1234"}'

# 登录
curl -X POST https://api.你的域名/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test1234"}'
```

### 4.3 MCP 工具
```bash
# 用登录返回的 API key
curl -X POST https://api.你的域名/mcp \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
# → 应返回 12 个工具
```

### 4.4 前端检查
- [ ] 首页正常加载
- [ ] 注册/登录可用（Supabase Auth 或本地模式）
- [ ] Dashboard 正常
- [ ] Docs 页 curl 示例显示正确 API 地址
- [ ] 定价页正常

### 4.5 CORS 检查
```bash
curl -I -X OPTIONS https://api.你的域名/health \
  -H "Origin: https://你的前端.vercel.app" \
  -H "Access-Control-Request-Method: GET"
# → Access-Control-Allow-Origin 应返回前端域名
```

---

## 五、已知限制 & 后续工作

| 项目 | 状态 | 说明 |
|------|:---:|------|
| sentence-transformers | ⚠️ | Dockerfile 已安装 torch CPU 版（~1.5GB），语义搜索可用 |
| Stripe 支付 | ⚪ | 配置 STRIPE_* 变量后自动启用 |
| Chrome 插件 | ❌ | 未部署到 Chrome Web Store |
| 邮件验证 | ❌ | 未配置 Supabase 邮件模板 |
| 监控 | ❌ | 未配置 Prometheus/Grafana |
| HTTPS | ✅ | Vercel + Railway 自动 HTTPS |
| 数据库备份 | ⚠️ | Supabase 有自动备份，确认 Pro plan |

---

## 六、回滚方案

```bash
# Railway 回滚到上一个部署
railway rollback

# Vercel 回滚
vercel rollback
```
