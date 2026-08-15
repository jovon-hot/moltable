-- ============================================
-- Moltable · SQLite Schema (开发模式)
-- ============================================

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE,
    name TEXT,
    timezone TEXT DEFAULT 'Asia/Shanghai',
    language TEXT DEFAULT 'zh',
    password_hash TEXT,
    plan TEXT DEFAULT 'free',
    last_active_at TEXT,
    trial_activated_at TEXT,
    expires_at TEXT,
    stripe_customer_id TEXT,
    stripe_subscription_id TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- 迁移：为旧库补充 expires_at 列（新库已在 CREATE TABLE 中定义）
ALTER TABLE users ADD COLUMN expires_at TEXT;

-- API 密钥 (legacy, deprecated)
CREATE TABLE IF NOT EXISTS api_keys (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    name TEXT,
    key_prefix TEXT,
    key_hash TEXT UNIQUE NOT NULL,
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    last_used_at TEXT
);

-- 同步码（molt_sync_xxx — Agent 身份找回，一次性使用）
CREATE TABLE IF NOT EXISTS agent_invites (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    code_hash TEXT UNIQUE NOT NULL,
    code_prefix TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    used_at TEXT,
    expires_at TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    revoked_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_agent_invites_user ON agent_invites(user_id, status);
CREATE INDEX IF NOT EXISTS idx_agent_invites_hash ON agent_invites(code_hash);

-- 匿名会话
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    session_uuid TEXT UNIQUE NOT NULL,
    token TEXT UNIQUE NOT NULL,
    user_id TEXT REFERENCES users(id),
    expires_at TEXT NOT NULL,
    migrated_at TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- 记忆
CREATE TABLE IF NOT EXISTS memories (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT DEFAULT 'fact',
    tags TEXT DEFAULT '[]',
    embedding TEXT DEFAULT '[]',
    source TEXT DEFAULT 'agent',
    confidence REAL DEFAULT 1.0,
    is_archived INTEGER DEFAULT 0,
    source_session_id TEXT,
    -- 同步字段 (Git-style bidirectional sync)
    version INTEGER DEFAULT 1,
    base_content TEXT DEFAULT '',
    updated_at TEXT DEFAULT (datetime('now')),
    created_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_memories_user ON memories(user_id);
CREATE INDEX IF NOT EXISTS idx_memories_category ON memories(category);
CREATE INDEX IF NOT EXISTS idx_memories_user_archived ON memories(user_id, is_archived);
CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(content, content_rowid='rowid');

-- 迁移：为旧库补充同步字段（新库已在 CREATE TABLE 中定义；重复 ALTER 会被跳过）
ALTER TABLE memories ADD COLUMN version INTEGER DEFAULT 1;
ALTER TABLE memories ADD COLUMN base_content TEXT DEFAULT '';
ALTER TABLE memories ADD COLUMN updated_at TEXT DEFAULT '';

-- Persona
CREATE TABLE IF NOT EXISTS personas (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    name TEXT NOT NULL,
    description TEXT,
    type TEXT DEFAULT 'constructed',
    definition TEXT,
    is_active INTEGER DEFAULT 1,
    version INTEGER DEFAULT 1,
    base_content TEXT DEFAULT '',
    updated_at TEXT DEFAULT (datetime('now')),
    created_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_personas_user ON personas(user_id);
ALTER TABLE personas ADD COLUMN version INTEGER DEFAULT 1;
ALTER TABLE personas ADD COLUMN base_content TEXT DEFAULT '';
ALTER TABLE personas ADD COLUMN updated_at TEXT DEFAULT '';

-- 项目 (aligned with schema.sql — persona_id/knowledge_bases/tools/updated_at)
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    name TEXT NOT NULL,
    description TEXT,
    persona_id TEXT,
    knowledge_bases TEXT DEFAULT '[]',
    tools TEXT DEFAULT '[]',
    is_active INTEGER DEFAULT 1,
    version INTEGER DEFAULT 1,
    base_content TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_projects_user ON projects(user_id);
ALTER TABLE projects ADD COLUMN version INTEGER DEFAULT 1;
ALTER TABLE projects ADD COLUMN base_content TEXT DEFAULT '';

-- 决策
CREATE TABLE IF NOT EXISTS decisions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    content TEXT NOT NULL,
    decided_at TEXT DEFAULT (datetime('now')),
    created_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_decisions_user ON decisions(user_id);

-- 审计日志
CREATE TABLE IF NOT EXISTS audit_logs (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    action TEXT NOT NULL,
    ip_address TEXT,
    details TEXT DEFAULT '{}',
    created_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs(user_id);

-- Challenge (DID+VC 防重放)
CREATE TABLE IF NOT EXISTS challenges (
    id TEXT PRIMARY KEY,
    challenge TEXT UNIQUE NOT NULL,
    agent_did TEXT,
    used_at TEXT,
    expires_at TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);

-- DID 注册表
CREATE TABLE IF NOT EXISTS did_registry (
    did TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    public_key TEXT NOT NULL,
    key_type TEXT DEFAULT 'Ed25519',
    platform TEXT,
    agent_name TEXT,
    status TEXT DEFAULT 'active',
    last_seen_at TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_did_user ON did_registry(user_id);
CREATE INDEX IF NOT EXISTS idx_did_status ON did_registry(status);

-- VC 凭证记录
CREATE TABLE IF NOT EXISTS credentials (
    id TEXT PRIMARY KEY,
    credential_jwt TEXT NOT NULL,
    claims TEXT DEFAULT '{}',
    type TEXT,
    subject_did TEXT,
    revoked_at TEXT,
    replaced_by TEXT,
    expires_at TEXT,
    issued_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_cred_did ON credentials(subject_did);

-- 一次性注册 Token
CREATE TABLE IF NOT EXISTS enrollment_tokens (
    token TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    platform TEXT,
    agent_name TEXT,
    consumed_at TEXT,
    expires_at TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);

-- VP 提交记录
CREATE TABLE IF NOT EXISTS presentations (
    id TEXT PRIMARY KEY,
    agent_did TEXT NOT NULL REFERENCES did_registry(did),
    vp_jwt TEXT NOT NULL,
    verified_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_pr_did ON presentations(agent_did);


-- 订阅表
CREATE TABLE IF NOT EXISTS subscriptions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    stripe_subscription_id TEXT,
    plan TEXT NOT NULL DEFAULT 'free',
    status TEXT NOT NULL DEFAULT 'active',
    billing_cycle TEXT DEFAULT 'monthly',
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 每日统计表
CREATE TABLE IF NOT EXISTS daily_stats (
    date TEXT PRIMARY KEY,
    total_users INTEGER DEFAULT 0,
    new_users INTEGER DEFAULT 0,
    active_users INTEGER DEFAULT 0,
    api_calls INTEGER DEFAULT 0,
    errors INTEGER DEFAULT 0,
    trial_activated INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);

-- 推荐码（Referral）
CREATE TABLE IF NOT EXISTS referrals (
    id TEXT PRIMARY KEY,
    referrer_id TEXT NOT NULL,
    code TEXT UNIQUE NOT NULL,
    referred_email TEXT,
    status TEXT DEFAULT 'pending',
    created_at TEXT DEFAULT (datetime('now')),
    claimed_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_referrals_referrer ON referrals(referrer_id, status);
