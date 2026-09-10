-- ============================================================
-- Moltable · Supabase 全量重建 SQL (自动生成, 请勿手改)
-- 生成时间: 2026-09-10 · 来源: 16 个 DDL 文件按依赖顺序合并
-- 用法: 新建 Supabase 项目 → SQL Editor 粘贴本文件全文 → Run
-- 验证: 2026-09-10 在全新 PG16 + pgvector 上单文件执行通过 → 28 张表
-- 重新生成: python3 ~/.hermes/scripts/gen_rebuild_all.py
-- ============================================================



-- ---------- >>> server/schema.sql ----------
-- ============================================
-- Moltable · Supabase 数据库 Schema
-- 在 Supabase SQL Editor 中运行此文件
-- ============================================

-- 启用 pgvector 扩展
create extension if not exists vector;

-- ============ 用户表 ============
create table users (
    id            uuid primary key default gen_random_uuid(),
    email         text unique not null,
    name          text,
    password_hash text,
    plan          text default 'free',
    timezone      text default 'Asia/Shanghai',
    language      text default 'zh',
    last_active_at        timestamptz,
    trial_activated_at    timestamptz,
    expires_at            timestamptz,
    stripe_customer_id     text,
    stripe_subscription_id text,
    email_verified         boolean default false,
    email_verify_token     text,
    email_verify_token_expires timestamptz,
    bonus_storage_gb       numeric default 0,
    created_at    timestamptz default now(),
    updated_at    timestamptz default now()
);

-- ============ API Keys ============
create table api_keys (
    id            uuid primary key default gen_random_uuid(),
    user_id       uuid references users(id) on delete cascade,
    key_hash      text not null,
    key_prefix    text not null,
    name          text,
    permissions   text[] default '{read,write}',
    is_active     boolean default true,
    last_used_at  timestamptz,
    expires_at    timestamptz,
    created_at    timestamptz default now(),
    revoked_at    timestamptz
);
create index api_keys_user_id_idx on api_keys (user_id);
create index api_keys_key_hash_idx on api_keys (key_hash);

-- ============ Agent Invites (同步码, molt_sync_xxx) ============
create table agent_invites (
    id            uuid primary key default gen_random_uuid(),
    user_id       uuid references users(id) on delete cascade,
    code_hash     text not null,                   -- PBKDF2(molt_sync_xxx) — 同 hash_api_key()
    code_prefix   text not null,                   -- 前 12 位用于展示
    status        text not null default 'pending', -- pending | used | revoked | expired
    used_at       timestamptz,
    expires_at    timestamptz not null,            -- 默认 7 天（应用层写入）
    created_at    timestamptz default now(),
    revoked_at    timestamptz
);
create index agent_invites_user_status_idx on agent_invites (user_id, status);
create index agent_invites_code_hash_idx on agent_invites (code_hash);

-- ============ Personas ============
create table personas (
    id              uuid primary key default gen_random_uuid(),
    user_id         uuid references users(id) on delete cascade,
    name            text not null,
    type            text default 'constructed',
    description     text,
    system_prompt   text,
    traits          jsonb default '{}',
    model_preference text,
    version         integer default 1,
    base_content    text default '',
    parent_id       uuid references personas(id),
    is_active       boolean default true,
    memory_count    integer default 0,
    created_at      timestamptz default now(),
    updated_at      timestamptz default now()
);

-- Entity 版本历史
create table persona_versions (
    id            uuid primary key default gen_random_uuid(),
    persona_id    uuid references personas(id) on delete cascade,
    version       integer not null,
    diff          jsonb,
    changelog     text,
    snapshot      jsonb not null,
    created_at    timestamptz default now()
);
create index persona_versions_persona_id_idx on persona_versions (persona_id);

create index personas_user_id_idx on personas (user_id);
create index personas_parent_id_idx on personas (parent_id);

-- ============ Memories (pgvector) ============
-- category 取值: preference, decision, fact, project, insight, task, relationship
create table memories (
    id            uuid primary key default gen_random_uuid(),
    user_id       uuid references users(id) on delete cascade,
    content       text not null,
    category      text not null,
    source        text default 'manual',
    confidence    real default 1.0,
    embedding     vector(384),
    tags          text[] default '{}',
    is_archived   boolean default false,
    version       integer default 1,
    base_content  text default '',
    created_at    timestamptz default now(),
    updated_at    timestamptz default now()
);

-- HNSW 向量索引
create index on memories using hnsw (embedding vector_cosine_ops);

-- 全文搜索索引
create index memories_content_idx on memories using gin (to_tsvector('simple', content));

-- 按用户+分类查询
create index memories_user_cat_idx on memories (user_id, category);
create index memories_user_id_idx on memories (user_id);

-- ============ Projects ============
create table projects (
    id            uuid primary key default gen_random_uuid(),
    user_id       uuid references users(id) on delete cascade,
    name          text not null,
    description   text,
    persona_id    uuid references personas(id) on delete set null,
    knowledge_bases jsonb default '[]',
    tools         jsonb default '[]',
    is_active     boolean default true,
    version       integer default 1,
    base_content  text default '',
    created_at    timestamptz default now(),
    updated_at    timestamptz default now()
);
create index projects_user_id_idx on projects (user_id);

-- ============ Decisions ============
create table decisions (
    id            uuid primary key default gen_random_uuid(),
    user_id       uuid references users(id) on delete cascade,
    project_id    uuid references projects(id) on delete cascade,
    content       text not null,
    decided_at    timestamptz default now()
);
create index decisions_user_id_idx on decisions (user_id);
create index decisions_project_id_idx on decisions (project_id);

-- ============ 审计日志 ============
create table audit_logs (
    id            uuid primary key default gen_random_uuid(),
    user_id       uuid references users(id) on delete cascade,
    api_key_id    uuid references api_keys(id),
    action        text not null,
    details       jsonb,
    ip_address    text,
    created_at    timestamptz default now()
);
create index audit_logs_user_id_idx on audit_logs (user_id);
create index audit_logs_api_key_id_idx on audit_logs (api_key_id);

-- ============ Sessions (Anonymous) ============
create table if not exists sessions (
    id            uuid primary key default gen_random_uuid(),
    session_uuid  uuid unique not null default gen_random_uuid(),
    token         text unique not null,
    user_id       uuid references users(id) on delete set null,
    created_at    timestamptz default now(),
    expires_at    timestamptz not null,
    migrated_at   timestamptz
);

create index sessions_token_idx on sessions (token);
create index sessions_user_id_idx on sessions (user_id);

-- ============================================
-- DID+VC Agent Identity Layer (merged from migration_did_vc.sql)
-- ============================================

create table did_registry (
    did             text primary key,
    user_id         uuid references users(id) on delete cascade,
    public_key      text not null,
    key_type        text default 'Ed25519VerificationKey2020',
    platform        text default 'unknown',
    agent_name      text default '',
    status          text default 'active',
    last_seen_at    timestamptz,
    created_at      timestamptz default now(),
    revoked_at      timestamptz
);
create index did_registry_user_idx on did_registry (user_id);
create index did_registry_status_idx on did_registry (status);

create table enrollment_tokens (
    token           text primary key,
    user_id         uuid references users(id) on delete cascade,
    platform        text default 'hermes',
    agent_name      text default '',
    consumed_at     timestamptz,
    expires_at      timestamptz not null default (now() + interval '5 minutes'),
    created_at      timestamptz default now()
);
create index enrollment_tokens_user_idx on enrollment_tokens (user_id);

create table credentials (
    id              uuid primary key default gen_random_uuid(),
    credential_jwt  text not null,
    issuer_did      text not null,
    subject_did     text not null,
    credential_type text not null,
    claims          jsonb not null default '{}',
    replaced_by     uuid references credentials(id),
    expires_at      timestamptz,
    revoked_at      timestamptz,
    created_at      timestamptz default now()
);
create index credentials_subject_idx on credentials (subject_did);
create index credentials_type_idx on credentials (credential_type);

create table presentations (
    id              uuid primary key default gen_random_uuid(),
    agent_did       text not null,
    challenge       text not null,
    expires_at      timestamptz not null,
    verified_at     timestamptz default now()
);
create index presentations_agent_idx on presentations (agent_did);
create index presentations_challenge_idx on presentations (challenge);

create table challenges (
    challenge       text primary key,
    agent_did       text,
    used_at         timestamptz,
    expires_at      timestamptz not null default (now() + interval '5 minutes'),
    created_at      timestamptz default now()
);

-- DID+VC 扩展列
alter table api_keys add column if not exists migrated_to_did text;
alter table personas add column if not exists linked_did text;
alter table audit_logs add column if not exists agent_did text;
alter table audit_logs add column if not exists presentation_id uuid;

-- DID+VC RLS
alter table did_registry enable row level security;
alter table credentials enable row level security;
alter table enrollment_tokens enable row level security;

create policy "Users can only access their own DIDs"
    on did_registry for all
    using (user_id = auth.uid())
    with check (user_id = auth.uid());

-- ============================================
-- pgvector RPC：语义搜索
-- ============================================
create or replace function match_memories(
    query_embedding vector(384),
    match_user_id text,
    match_count int default 5,
    match_category text default null,
    match_threshold float default 0.5
)
returns table (
    id uuid,
    content text,
    category text,
    source text,
    tags text[],
    similarity float,
    created_at timestamptz
)
language plpgsql
as $$
begin
    return query
    select
        m.id,
        m.content,
        m.category,
        m.source,
        m.tags,
        1 - (m.embedding <=> query_embedding) as similarity,
        m.created_at
    from memories m
    where m.user_id::text = match_user_id
      and m.is_archived = false
      and (match_category is null or m.category = match_category)
      and 1 - (m.embedding <=> query_embedding) > match_threshold
    order by m.embedding <=> query_embedding
    limit match_count;
end;
$$;

-- ============================================
-- 关键词搜索 RPC（pgvector 回退方案）
-- ============================================
create or replace function match_memories_keyword(
    query_text text,
    match_user_id text,
    match_count int default 5,
    match_category text default null
)
returns table (
    id uuid,
    content text,
    category text,
    source text,
    tags text[],
    rank float,
    created_at timestamptz
)
language plpgsql
as $$
begin
    return query
    select
        m.id,
        m.content,
        m.category,
        m.source,
        m.tags,
        ts_rank_cd(to_tsvector('simple', m.content), plainto_tsquery('simple', query_text)) as rank,
        m.created_at
    from memories m
    where m.user_id::text = match_user_id
      and m.is_archived = false
      and (match_category is null or m.category = match_category)
      and to_tsvector('simple', m.content) @@ plainto_tsquery('simple', query_text)
    order by rank desc
    limit match_count;
end;
$$;

-- ============ 记忆 Persona 隔离 ============
alter table memories add column if not exists persona_id uuid references personas(id) on delete set null;
create index if not exists memories_persona_id_idx on memories (persona_id);

-- ============================================
-- 每日统计表
-- ============================================
create table if not exists daily_stats (
    date            date primary key,
    total_users     integer default 0,
    new_users       integer default 0,
    active_users    integer default 0,
    api_calls       integer default 0,
    errors          integer default 0,
    trial_activated integer default 0,
    created_at      timestamptz default now()
);

-- ============================================
-- RLS: 用户数据隔离
-- ============================================
alter table memories enable row level security;
alter table personas enable row level security;
alter table projects enable row level security;
alter table decisions enable row level security;
alter table api_keys enable row level security;

-- 每个用户只能访问自己的数据
create policy "Users can only access their own memories"
    on memories for all
    using (user_id = auth.uid())
    with check (user_id = auth.uid());

create policy "Users can only access their own personas"
    on personas for all
    using (user_id = auth.uid());

create policy "Users can only access their own projects"
    on projects for all
    using (user_id = auth.uid());

create policy "Users can only access their own api_keys"
    on api_keys for all
    using (user_id = auth.uid());

-- ── 运营统计表 ──────────────────────────────────
create table if not exists daily_stats (
    date            date primary key,
    total_users     integer default 0,
    new_users       integer default 0,
    active_users    integer default 0,
    api_calls       integer default 0,
    errors          integer default 0,
    trial_activated integer default 0,
    created_at      timestamptz default now()
);

-- ── 用户活跃度追踪 ──────────────────────────────
alter table users add column if not exists last_active_at timestamptz;
alter table users add column if not exists trial_activated_at timestamptz;
alter table users add column if not exists expires_at timestamptz;

-- ── Admin accounts (email+password auth) ───────
create table if not exists admin_users (
    email           text primary key,
    name            text default '',
    password_hash   text not null,
    role            text not null default 'operator' check (role in ('admin', 'operator')),
    is_active       boolean default true,
    token_version   integer default 1,
    last_login_at   timestamptz,
    created_at      timestamptz default now()
);

-- ── Stripe webhook 事件去重表 ───────
create table if not exists webhook_events (
    event_id      text primary key,
    processed_at  timestamptz default now()
);

-- sync v2: 同步协议扩展 — decisions/did_registry/credentials/persona_versions 纳入同步
-- 补协议列: version / base_content / updated_at

ALTER TABLE decisions ADD COLUMN IF NOT EXISTS created_at timestamptz DEFAULT now();
ALTER TABLE decisions ADD COLUMN IF NOT EXISTS version integer DEFAULT 1;
ALTER TABLE decisions ADD COLUMN IF NOT EXISTS base_content text DEFAULT '';
ALTER TABLE decisions ADD COLUMN IF NOT EXISTS updated_at timestamptz;

ALTER TABLE did_registry ADD COLUMN IF NOT EXISTS version integer DEFAULT 1;
ALTER TABLE did_registry ADD COLUMN IF NOT EXISTS base_content text DEFAULT '';
ALTER TABLE did_registry ADD COLUMN IF NOT EXISTS updated_at timestamptz;

ALTER TABLE credentials ADD COLUMN IF NOT EXISTS version integer DEFAULT 1;
ALTER TABLE credentials ADD COLUMN IF NOT EXISTS base_content text DEFAULT '';
ALTER TABLE credentials ADD COLUMN IF NOT EXISTS updated_at timestamptz;

ALTER TABLE persona_versions ADD COLUMN IF NOT EXISTS updated_at timestamptz;

-- P1: profiles 表 — 身份深层字段(1:1, PII 分级, phone 加密不进同步)
CREATE TABLE IF NOT EXISTS profiles (
    user_id         uuid primary key references users(id) on delete cascade,
    nickname        text,
    phone_encrypted text,
    location        text,
    education       jsonb default '[]',
    career          jsonb default '[]',
    values          jsonb default '[]',
    history         jsonb default '[]',
    version         integer default 1,
    base_content    text default '',
    updated_at      timestamptz,
    created_at      timestamptz default now()
);

-- P1: Agent 备份源同步 — 灵魂资产文件级快照 + CAS 内容寻址
-- 只备份「记忆/灵魂资产」，不备份「流水账」(对话日志 db / FTS 索引)

CREATE TABLE IF NOT EXISTS backup_sources (
    id             uuid primary key default gen_random_uuid(),
    user_id        uuid references users(id) on delete cascade,
    agent_type     text not null,
    name           text not null,
    latest_version integer default 0,
    created_at     timestamptz default now()
);
CREATE INDEX IF NOT EXISTS backup_sources_user_idx ON backup_sources(user_id);

CREATE TABLE IF NOT EXISTS snapshots (
    id             uuid primary key default gen_random_uuid(),
    source_id      uuid references backup_sources(id) on delete cascade,
    version        integer not null,
    manifest       jsonb not null default '{}',
    parent_version integer,
    created_at     timestamptz default now()
);
CREATE INDEX IF NOT EXISTS snapshots_source_version_idx ON snapshots(source_id, version);

-- 邮箱验证邮件发送审计（防邮件轰炸：按邮箱冷却 + 按 IP 频率）
CREATE TABLE IF NOT EXISTS email_send_audit (
    id          text primary key,
    email       text not null,
    ip_address  text,
    sent_at     timestamptz not null default now()
);
CREATE INDEX IF NOT EXISTS idx_email_send_audit_email ON email_send_audit(email, sent_at);
CREATE INDEX IF NOT EXISTS idx_email_send_audit_ip ON email_send_audit(ip_address, sent_at);


-- ---------- >>> supabase/migrations/20260803000001_agent_invites.sql ----------
create table if not exists agent_invites (
    id uuid primary key default gen_random_uuid(),
    user_id uuid references users(id) on delete cascade,
    code_hash text not null,
    code_prefix text not null,
    status text not null default 'pending',
    used_at timestamptz,
    expires_at timestamptz not null,
    created_at timestamptz default now(),
    revoked_at timestamptz
);
create index if not exists agent_invites_user_status_idx on agent_invites (user_id, status);
create index if not exists agent_invites_code_hash_idx on agent_invites (code_hash);


-- ---------- >>> supabase/migrations/20260806_referrals.sql ----------
-- Migration: Add referrals table for the referral / invite program
-- Created: 2026-08-06
-- Feature: Users generate unique invite codes, track pending/claimed referrals
--
-- Each row is one invite code issued by a referrer. `code` is an 8-char
-- alphanumeric string (UUID-derived, generated by the backend) and is unique.
-- `status` transitions pending → claimed when a new user signs up with the code.

-- Enable pgcrypto for UUID generation (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Main referrals table
CREATE TABLE IF NOT EXISTS referrals (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    referrer_id     TEXT NOT NULL,              -- users.id of the inviter
    code            TEXT NOT NULL UNIQUE,       -- 8-char alphanumeric invite code
    referred_email  TEXT,                       -- email of the invited person (set on claim)
    status          TEXT NOT NULL DEFAULT 'pending',  -- pending | claimed
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    claimed_at      TIMESTAMPTZ                 -- set when the code is claimed
);

-- Stats per referrer (invites sent, claimed/pending breakdown)
CREATE INDEX IF NOT EXISTS idx_referrals_referrer_status
    ON referrals (referrer_id, status, created_at DESC);

-- Fast claim lookup by referred email (optional)
CREATE INDEX IF NOT EXISTS idx_referrals_referred_email
    ON referrals (referred_email);

-- Enable Row-Level Security
ALTER TABLE referrals ENABLE ROW LEVEL SECURITY;

-- Users can view their own referral codes
CREATE POLICY "Users can view own referrals"
    ON referrals FOR SELECT
    USING (auth.uid()::text = referrer_id);


-- ---------- >>> supabase/migrations/20260806_temporal_facts.sql ----------
-- Migration: Add temporal_facts table for fact-change timeline tracking
-- Created: 2026-08-06
-- Feature: Temporal Memory Timeline (Zep competitive feature gap)
--
-- This table stores fact change events to build per-entity timelines.
-- Each row represents one fact transition (old_value → new_value).

-- Enable pgcrypto for UUID generation (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Main temporal facts table
CREATE TABLE IF NOT EXISTS temporal_facts (
    id          TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id     TEXT NOT NULL,
    entity      TEXT NOT NULL,              -- e.g. "preferred_language", "current_role"
    attribute   TEXT NOT NULL DEFAULT 'value', -- e.g. "value", "status", "version"
    old_value   TEXT,                       -- NULL = first time tracking
    new_value   TEXT NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    source_memory_id TEXT,                  -- FK to memories.id if auto-detected
    confidence  REAL NOT NULL DEFAULT 0.8,  -- 0.0-1.0
    persona_id  TEXT                        -- FK to personas.id if persona-scoped
);
-- 2026-09-10 fix: 原文件同时有列级 PRIMARY KEY 和 CONSTRAINT temporal_facts_pkey PRIMARY KEY,
-- 在空库上执行报 "multiple primary keys for table temporal_facts are not allowed"
-- → 任何全新项目的重建都会卡在这一步。删除重复约束, 保留列级 PRIMARY KEY。

-- Fast lookup: get timeline for a specific entity
CREATE INDEX IF NOT EXISTS idx_temporal_user_entity
    ON temporal_facts (user_id, entity, attribute, recorded_at);

-- Recent changes feed
CREATE INDEX IF NOT EXISTS idx_temporal_user_recent
    ON temporal_facts (user_id, recorded_at DESC);

-- Look up by source memory
CREATE INDEX IF NOT EXISTS idx_temporal_source_memory
    ON temporal_facts (source_memory_id);

-- Persona-scoped queries
CREATE INDEX IF NOT EXISTS idx_temporal_persona
    ON temporal_facts (user_id, persona_id, recorded_at DESC);

-- Enable Row-Level Security
ALTER TABLE temporal_facts ENABLE ROW LEVEL SECURITY;

-- Users can only see their own temporal facts
CREATE POLICY "Users can view own temporal facts"
    ON temporal_facts FOR SELECT
    USING (auth.uid()::text = user_id);

-- Users can insert their own temporal facts
CREATE POLICY "Users can insert own temporal facts"
    ON temporal_facts FOR INSERT
    WITH CHECK (auth.uid()::text = user_id);


-- ---------- >>> supabase/migrations/20260810_admin_token_version.sql ----------
-- Migration: Admin auth hardening — token-versioned JWTs
-- Created: 2026-08-10
-- Feature: Admin auth secrets separation + immediate revocation of admin tokens
--
-- token_version is bumped every time an admin account is disabled/enabled so
-- that already-issued JWTs are invalidated immediately (checked on every
-- authenticated admin request alongside is_active).

ALTER TABLE admin_users ADD COLUMN IF NOT EXISTS token_version integer DEFAULT 1;


-- ---------- >>> supabase/migrations/20260810_session_token_hash.sql ----------
-- Migration: Store session tokens as SHA-256 hashes
-- Created: 2026-08-10
-- Feature: Security hardening — existing sessions.token rows still hold RAW
-- tokens (mol_...). Convert them to their SHA-256 hex digest so a leaked DB
-- dump exposes no usable session tokens, matching hash_session_token().
--
-- The WHERE clause skips rows that are already 64-char hex (i.e. already
-- hashed), making this migration idempotent — re-running is a no-op and never
-- double-hashes. Raw tokens always start with "mol_" so they never match.

update sessions
set token = encode(sha256(token::bytea), 'hex')
where token !~ '^[0-9a-f]{64}$';


-- ---------- >>> supabase/migrations/20260814_stripe_subscription.sql ----------
-- Stripe subscription: add customer + subscription id to users
alter table users add column if not exists stripe_customer_id text;
alter table users add column if not exists stripe_subscription_id text;


-- ---------- >>> supabase/migrations/20260815_p0_persona_versions_user_id.sql ----------
-- P0 修复: persona_versions 跨用户泄露 — 加 user_id 列并回填
ALTER TABLE persona_versions ADD COLUMN IF NOT EXISTS user_id uuid REFERENCES users(id) ON DELETE CASCADE;
UPDATE persona_versions pv SET user_id = p.user_id FROM personas p WHERE pv.persona_id = p.id AND pv.user_id IS NULL;
CREATE INDEX IF NOT EXISTS persona_versions_user_idx ON persona_versions (user_id);


-- ---------- >>> supabase/migrations/20260815_schema_drift_fix.sql ----------
-- 生产 schema 漂移修复:补同步协议列 + 试用期列
-- 1. 同步协议列(memories/personas/projects 生产缺 version/base_content)
ALTER TABLE memories ADD COLUMN IF NOT EXISTS version integer DEFAULT 1;
ALTER TABLE memories ADD COLUMN IF NOT EXISTS base_content text DEFAULT '';
ALTER TABLE personas ADD COLUMN IF NOT EXISTS base_content text DEFAULT '';
ALTER TABLE projects ADD COLUMN IF NOT EXISTS version integer DEFAULT 1;
ALTER TABLE projects ADD COLUMN IF NOT EXISTS base_content text DEFAULT '';
-- 2. 试用期列(users 生产缺 trial_activated_at/expires_at)
ALTER TABLE users ADD COLUMN IF NOT EXISTS trial_activated_at timestamptz;
ALTER TABLE users ADD COLUMN IF NOT EXISTS expires_at timestamptz;


-- ---------- >>> supabase/migrations/20260815_sync_v2.sql ----------
-- sync v2: 同步协议扩展 — decisions/did_registry/credentials/persona_versions 纳入同步
-- 补协议列: version / base_content / updated_at

ALTER TABLE decisions ADD COLUMN IF NOT EXISTS created_at timestamptz DEFAULT now();
ALTER TABLE decisions ADD COLUMN IF NOT EXISTS version integer DEFAULT 1;
ALTER TABLE decisions ADD COLUMN IF NOT EXISTS base_content text DEFAULT '';
ALTER TABLE decisions ADD COLUMN IF NOT EXISTS updated_at timestamptz;

ALTER TABLE did_registry ADD COLUMN IF NOT EXISTS version integer DEFAULT 1;
ALTER TABLE did_registry ADD COLUMN IF NOT EXISTS base_content text DEFAULT '';
ALTER TABLE did_registry ADD COLUMN IF NOT EXISTS updated_at timestamptz;

ALTER TABLE credentials ADD COLUMN IF NOT EXISTS version integer DEFAULT 1;
ALTER TABLE credentials ADD COLUMN IF NOT EXISTS base_content text DEFAULT '';
ALTER TABLE credentials ADD COLUMN IF NOT EXISTS updated_at timestamptz;

ALTER TABLE persona_versions ADD COLUMN IF NOT EXISTS updated_at timestamptz;


-- ---------- >>> supabase/migrations/20260815_sync_v2_did_vc.sql ----------
-- sync v2 前置：DID/VC 相关表（生产缺失，补齐）+ 协议列

CREATE TABLE IF NOT EXISTS did_registry (
    did             text primary key,
    user_id         uuid references users(id) on delete cascade,
    public_key      text not null,
    key_type        text default 'Ed25519VerificationKey2020',
    platform        text default 'unknown',
    agent_name      text default '',
    status          text default 'active',
    last_seen_at    timestamptz,
    created_at      timestamptz default now(),
    revoked_at      timestamptz
);
CREATE INDEX IF NOT EXISTS did_registry_user_idx ON did_registry (user_id);
CREATE INDEX IF NOT EXISTS did_registry_status_idx ON did_registry (status);

CREATE TABLE IF NOT EXISTS enrollment_tokens (
    token           text primary key,
    user_id         uuid references users(id) on delete cascade,
    platform        text default 'hermes',
    agent_name      text default '',
    consumed_at     timestamptz,
    expires_at      timestamptz not null default (now() + interval '5 minutes'),
    created_at      timestamptz default now()
);
CREATE INDEX IF NOT EXISTS enrollment_tokens_user_idx ON enrollment_tokens (user_id);

CREATE TABLE IF NOT EXISTS credentials (
    id              uuid primary key default gen_random_uuid(),
    credential_jwt  text not null,
    issuer_did      text not null,
    subject_did     text not null,
    credential_type text not null,
    claims          jsonb not null default '{}',
    replaced_by     uuid references credentials(id),
    expires_at      timestamptz,
    revoked_at      timestamptz,
    created_at      timestamptz default now()
);
CREATE INDEX IF NOT EXISTS credentials_subject_idx ON credentials (subject_did);
CREATE INDEX IF NOT EXISTS credentials_type_idx ON credentials (credential_type);

CREATE TABLE IF NOT EXISTS presentations (
    id              uuid primary key default gen_random_uuid(),
    agent_did       text not null,
    challenge       text not null,
    expires_at      timestamptz not null,
    verified_at     timestamptz default now()
);
CREATE INDEX IF NOT EXISTS presentations_agent_idx ON presentations (agent_did);
CREATE INDEX IF NOT EXISTS presentations_challenge_idx ON presentations (challenge);

CREATE TABLE IF NOT EXISTS challenges (
    challenge       text primary key,
    agent_did       text,
    used_at         timestamptz,
    expires_at      timestamptz not null default (now() + interval '5 minutes'),
    created_at      timestamptz default now()
);

-- DID+VC 扩展列
ALTER TABLE api_keys ADD COLUMN IF NOT EXISTS migrated_to_did text;
ALTER TABLE personas ADD COLUMN IF NOT EXISTS linked_did text;
ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS agent_did text;
ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS presentation_id uuid;

-- sync v2 协议列
ALTER TABLE decisions ADD COLUMN IF NOT EXISTS created_at timestamptz DEFAULT now();
ALTER TABLE decisions ADD COLUMN IF NOT EXISTS version integer DEFAULT 1;
ALTER TABLE decisions ADD COLUMN IF NOT EXISTS base_content text DEFAULT '';
ALTER TABLE decisions ADD COLUMN IF NOT EXISTS updated_at timestamptz;

ALTER TABLE did_registry ADD COLUMN IF NOT EXISTS version integer DEFAULT 1;
ALTER TABLE did_registry ADD COLUMN IF NOT EXISTS base_content text DEFAULT '';
ALTER TABLE did_registry ADD COLUMN IF NOT EXISTS updated_at timestamptz;

ALTER TABLE credentials ADD COLUMN IF NOT EXISTS version integer DEFAULT 1;
ALTER TABLE credentials ADD COLUMN IF NOT EXISTS base_content text DEFAULT '';
ALTER TABLE credentials ADD COLUMN IF NOT EXISTS updated_at timestamptz;

ALTER TABLE persona_versions ADD COLUMN IF NOT EXISTS updated_at timestamptz;


-- ---------- >>> supabase/migrations/20260815_sync_v2_profiles.sql ----------
-- P1: profiles 表 — 身份深层字段(1:1, PII 分级, phone 加密不进同步)
CREATE TABLE IF NOT EXISTS profiles (
    user_id         uuid primary key references users(id) on delete cascade,
    nickname        text,
    phone_encrypted text,
    location        text,
    education       jsonb default '[]',
    career          jsonb default '[]',
    values          jsonb default '[]',
    history         jsonb default '[]',
    version         integer default 1,
    base_content    text default '',
    updated_at      timestamptz,
    created_at      timestamptz default now()
);


-- ---------- >>> server/migrations/001_experiments.sql ----------
-- Moltable A/B Testing Framework — Database Schema
-- Run this in your Supabase SQL Editor or it auto-creates in SQLite mode.

-- Experiments table
CREATE TABLE IF NOT EXISTS experiments (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    variants TEXT NOT NULL DEFAULT '[]',  -- JSON array of {key, name, weight, description}
    goal TEXT DEFAULT 'conversion',
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'running', 'paused', 'completed')),
    traffic_pct REAL DEFAULT 100.0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- User-to-variant assignments
CREATE TABLE IF NOT EXISTS experiment_assignments (
    id SERIAL PRIMARY KEY,
    experiment_id TEXT NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,
    variant TEXT NOT NULL,
    assigned_at TEXT NOT NULL,
    UNIQUE(experiment_id, user_id)
);

-- Conversion events
CREATE TABLE IF NOT EXISTS experiment_conversions (
    id SERIAL PRIMARY KEY,
    experiment_id TEXT NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,
    variant TEXT NOT NULL,
    goal TEXT DEFAULT 'conversion',
    converted_at TEXT NOT NULL
);

-- Indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_exp_assignments_exp ON experiment_assignments(experiment_id);
CREATE INDEX IF NOT EXISTS idx_exp_assignments_user ON experiment_assignments(experiment_id, user_id);
CREATE INDEX IF NOT EXISTS idx_exp_conversions_exp ON experiment_conversions(experiment_id);
CREATE INDEX IF NOT EXISTS idx_exp_conversions_variant ON experiment_conversions(experiment_id, variant);


-- ---------- >>> server/migration_bonus.sql ----------
-- ============================================
-- Moltable · 分享/邀请赠送存储额度 迁移
-- 在 Supabase SQL Editor 运行（生产库）
-- ============================================

-- 1. users 表加 bonus_storage_gb（累计赠送存储额度 GB）
alter table users add column if not exists bonus_storage_gb numeric default 0;

-- 2. referrals 表加 referred_user_id + reward_granted（邀请奖励防重复发放）
alter table referrals add column if not exists referred_user_id uuid;
alter table referrals add column if not exists reward_granted boolean default false;

-- 3. bonus_events 表（发放审计 + 防重复领取）
create table if not exists bonus_events (
    id uuid primary key default gen_random_uuid(),
    user_id uuid references users(id) on delete cascade,
    event_type text not null,          -- 'share' | 'referral'
    amount_gb numeric not null default 1,
    source text,                        -- 帖子链接 / 被邀请人 user_id
    created_at timestamptz default now()
);
create index if not exists bonus_events_user_idx on bonus_events(user_id, event_type);


-- ---------- >>> server/migration_email_rate_limit.sql ----------
-- ============================================
-- Moltable · 邮件发送审计（防邮件轰炸）
-- 在 Supabase SQL Editor 中运行此文件（生产库）
-- 用途：按邮箱冷却 + 按 IP 频率双重限流，防止验证邮件被用来轰炸攻击
-- ============================================

CREATE TABLE IF NOT EXISTS email_send_audit (
    id          text primary key,
    email       text not null,
    ip_address  text,
    sent_at     timestamptz not null default now()
);

CREATE INDEX IF NOT EXISTS idx_email_send_audit_email ON email_send_audit(email, sent_at);
CREATE INDEX IF NOT EXISTS idx_email_send_audit_ip ON email_send_audit(ip_address, sent_at);


-- ---------- >>> server/migration_email_verify.sql ----------
-- ============================================
-- Moltable · 邮箱验证迁移
-- 在 Supabase SQL Editor 中运行此文件（生产库）
-- 为 users 表补充邮箱验证列
-- ============================================

ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified boolean default false;
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verify_token text;
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verify_token_expires timestamptz;

-- 已有用户视为已验证（避免历史用户被误标未验证）
UPDATE users SET email_verified = true WHERE email_verified IS NULL;
