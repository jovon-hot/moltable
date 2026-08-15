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
