-- P0 修复: persona_versions 跨用户泄露 — 加 user_id 列并回填
ALTER TABLE persona_versions ADD COLUMN IF NOT EXISTS user_id uuid REFERENCES users(id) ON DELETE CASCADE;
UPDATE persona_versions pv SET user_id = p.user_id FROM personas p WHERE pv.persona_id = p.id AND pv.user_id IS NULL;
CREATE INDEX IF NOT EXISTS persona_versions_user_idx ON persona_versions (user_id);
