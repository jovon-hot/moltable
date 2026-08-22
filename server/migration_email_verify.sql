-- ============================================
-- Moltable · 邮箱验证迁移
-- 在 Supabase SQL Editor 中运行此文件（生产库）
-- 为 users 表补充邮箱验证列
-- ============================================

ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified boolean default false;
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verify_token text;

-- 已有用户视为已验证（避免历史用户被误标未验证）
UPDATE users SET email_verified = true WHERE email_verified IS NULL;
