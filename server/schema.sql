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
    is_active     boolean default false,
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

-- ── Admin accounts (email+password auth) ───────
create table if not exists admin_users (
    email           text primary key,
    name            text default '',
    password_hash   text not null,
    role            text not null default 'operator' check (role in ('admin', 'operator')),
    is_active       boolean default true,
    last_login_at   timestamptz,
    created_at      timestamptz default now()
);
