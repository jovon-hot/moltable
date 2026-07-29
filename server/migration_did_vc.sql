-- ============================================
-- DID+VC Agent Identity Layer Migration
-- Run after 001_init.sql base schema
-- ============================================

-- 1. DID Registry: Agent 的去中心化标识符
CREATE TABLE IF NOT EXISTS did_registry (
    did             TEXT PRIMARY KEY,
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
    public_key      TEXT NOT NULL,
    key_type        TEXT DEFAULT 'Ed25519VerificationKey2020',
    platform        TEXT DEFAULT 'unknown',
    agent_name      TEXT DEFAULT '',
    status          TEXT DEFAULT 'active',
    last_seen_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT now(),
    revoked_at      TIMESTAMPTZ
);

CREATE INDEX did_registry_user_idx ON did_registry (user_id);
CREATE INDEX did_registry_status_idx ON did_registry (status);

-- 2. Enrollment Tokens: 一次性连接码
CREATE TABLE IF NOT EXISTS enrollment_tokens (
    token           TEXT PRIMARY KEY,
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
    platform        TEXT DEFAULT 'hermes',
    agent_name      TEXT DEFAULT '',
    consumed_at     TIMESTAMPTZ,
    expires_at      TIMESTAMPTZ NOT NULL DEFAULT (now() + interval '5 minutes'),
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX enrollment_tokens_user_idx ON enrollment_tokens (user_id);

-- 3. Credentials: Verifiable Credentials
CREATE TABLE IF NOT EXISTS credentials (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    credential_jwt  TEXT NOT NULL,
    issuer_did      TEXT NOT NULL,
    subject_did     TEXT NOT NULL,
    credential_type TEXT NOT NULL,
    claims          JSONB NOT NULL DEFAULT '{}',
    replaced_by     UUID REFERENCES credentials(id),
    expires_at      TIMESTAMPTZ,
    revoked_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX credentials_subject_idx ON credentials (subject_did);
CREATE INDEX credentials_type_idx ON credentials (credential_type);

-- 4. Presentations: VP 审计
CREATE TABLE IF NOT EXISTS presentations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_did       TEXT NOT NULL,
    challenge       TEXT NOT NULL,
    expires_at      TIMESTAMPTZ NOT NULL,
    verified_at     TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX presentations_agent_idx ON presentations (agent_did);
CREATE INDEX presentations_challenge_idx ON presentations (challenge);

-- 5. Challenges: 防重放随机数
CREATE TABLE IF NOT EXISTS challenges (
    challenge       TEXT PRIMARY KEY,
    agent_did       TEXT,
    used_at         TIMESTAMPTZ,
    expires_at      TIMESTAMPTZ NOT NULL DEFAULT (now() + interval '5 minutes'),
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- 6. Modify existing tables
ALTER TABLE api_keys ADD COLUMN IF NOT EXISTS migrated_to_did TEXT;
ALTER TABLE personas ADD COLUMN IF NOT EXISTS linked_did TEXT;
ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS agent_did TEXT;
ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS presentation_id UUID;

-- 7. RLS for new tables
ALTER TABLE did_registry ENABLE ROW LEVEL SECURITY;
ALTER TABLE credentials ENABLE ROW LEVEL SECURITY;
ALTER TABLE enrollment_tokens ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can only access their own DIDs"
    ON did_registry FOR ALL
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());
