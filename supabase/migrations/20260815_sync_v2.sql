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
