-- Migration: Add no_stake columns to protocols table
-- Version: 007
-- Date: 2026-02-28
-- Run this manually on Railway PostgreSQL if auto-migration fails

-- Add no_stake column
ALTER TABLE protocols ADD COLUMN IF NOT EXISTS no_stake BOOLEAN DEFAULT FALSE;

-- Add stake_required column for v2.3
ALTER TABLE protocols ADD COLUMN IF NOT EXISTS stake_required BOOLEAN DEFAULT FALSE;

-- Add index for daily no-stake protocol counting
CREATE INDEX IF NOT EXISTS idx_protocols_nostake_date 
ON protocols(initiator_ai_id, no_stake, created_at) 
WHERE no_stake = true;

-- Wallet tables for v2.2
CREATE TABLE IF NOT EXISTS wallet_balances (
    id SERIAL PRIMARY KEY,
    ai_id VARCHAR(64) NOT NULL,
    token VARCHAR(20) NOT NULL DEFAULT 'USDC',
    amount BIGINT NOT NULL DEFAULT 0,
    locked_amount BIGINT NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(ai_id, token)
);

CREATE INDEX IF NOT EXISTS idx_wallet_balances_ai_id ON wallet_balances(ai_id);

CREATE TABLE IF NOT EXISTS wallet_transactions (
    id SERIAL PRIMARY KEY,
    ai_id VARCHAR(64) NOT NULL,
    type VARCHAR(20) NOT NULL,
    amount BIGINT NOT NULL,
    token VARCHAR(20) NOT NULL DEFAULT 'USDC',
    tx_hash VARCHAR(100),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_wallet_transactions_ai_id ON wallet_transactions(ai_id);
CREATE INDEX IF NOT EXISTS idx_wallet_transactions_status ON wallet_transactions(status);
CREATE INDEX IF NOT EXISTS idx_wallet_transactions_created_at ON wallet_transactions(created_at DESC);

SELECT 'Migration completed successfully!' as result;
