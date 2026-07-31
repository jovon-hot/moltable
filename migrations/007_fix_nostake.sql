-- Quick fix for production database
-- Run this directly on the Railway database

-- Add no_stake column if not exists
ALTER TABLE protocols ADD COLUMN IF NOT EXISTS no_stake BOOLEAN DEFAULT FALSE;

-- Add stake_required column if not exists  
ALTER TABLE protocols ADD COLUMN IF NOT EXISTS stake_required BOOLEAN DEFAULT FALSE;

-- Verify the columns exist
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'protocols' 
AND column_name IN ('no_stake', 'stake_required');
