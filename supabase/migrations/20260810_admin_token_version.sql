-- Migration: Admin auth hardening — token-versioned JWTs
-- Created: 2026-08-10
-- Feature: Admin auth secrets separation + immediate revocation of admin tokens
--
-- token_version is bumped every time an admin account is disabled/enabled so
-- that already-issued JWTs are invalidated immediately (checked on every
-- authenticated admin request alongside is_active).

ALTER TABLE admin_users ADD COLUMN IF NOT EXISTS token_version integer DEFAULT 1;
