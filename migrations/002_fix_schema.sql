-- Moltable Schema Fix Migration
-- Run this script to fix missing columns and inconsistencies

-- Rename point_balances to mtc_balances (if not already renamed)
ALTER TABLE IF EXISTS point_balances RENAME TO mtc_balances;

-- Add vote_result column to arbitration_votes table
ALTER TABLE IF EXISTS arbitration_votes ADD COLUMN IF NOT EXISTS vote_result VARCHAR(32);

-- Fix duplicate credit_scores for test accounts
DELETE FROM credit_scores WHERE ai_id IN (
    SELECT ai_id FROM credit_scores GROUP BY ai_id HAVING COUNT(*) > 1
) AND ctid NOT IN (
    SELECT MIN(ctid) FROM credit_scores GROUP BY ai_id HAVING COUNT(*) > 1
);

-- Create unique constraint if not exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'credit_scores_ai_id_key'
    ) THEN
        ALTER TABLE credit_scores ADD CONSTRAINT credit_scores_ai_id_key UNIQUE (ai_id);
    END IF;
END $$;
