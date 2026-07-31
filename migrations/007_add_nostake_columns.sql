-- Migration: Add no_stake columns to protocols table
-- Version: 007
-- Date: 2026-02-28

-- Add no_stake column
ALTER TABLE protocols ADD COLUMN IF NOT EXISTS no_stake BOOLEAN DEFAULT FALSE;

-- Add index for daily no-stake protocol counting
CREATE INDEX IF NOT EXISTS idx_protocols_nostake_date 
ON protocols(initiator_ai_id, no_stake, created_at) 
WHERE no_stake = true;

-- Add stake_required column for v2.3
ALTER TABLE protocols ADD COLUMN IF NOT EXISTS stake_required BOOLEAN DEFAULT FALSE;
