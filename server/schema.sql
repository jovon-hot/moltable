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

-- ============ Projects ============
create table projects (
    id            uuid primary key default gen_random_uuid(),
    user_id       uuid references users(id) on delete cascade,
    name          text not null,
    description   text,
    is_active     boolean default false,
    created_at    timestamptz default now()
);

-- ============ Decisions ============
create table decisions (
    id            uuid primary key default gen_random_uuid(),
    user_id       uuid references users(id) on delete cascade,
    project_id    uuid references projects(id),
    content       text not null,
    decided_at    timestamptz default now()
);

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
