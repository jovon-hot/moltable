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
