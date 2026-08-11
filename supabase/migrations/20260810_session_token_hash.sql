-- Migration: Store session tokens as SHA-256 hashes
-- Created: 2026-08-10
-- Feature: Security hardening — existing sessions.token rows still hold RAW
-- tokens (mol_...). Convert them to their SHA-256 hex digest so a leaked DB
-- dump exposes no usable session tokens, matching hash_session_token().
--
-- The WHERE clause skips rows that are already 64-char hex (i.e. already
-- hashed), making this migration idempotent — re-running is a no-op and never
-- double-hashes. Raw tokens always start with "mol_" so they never match.

update sessions
set token = encode(sha256(token::bytea), 'hex')
where token !~ '^[0-9a-f]{64}$';
