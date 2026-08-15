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
