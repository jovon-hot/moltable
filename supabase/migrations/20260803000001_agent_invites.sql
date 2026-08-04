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
