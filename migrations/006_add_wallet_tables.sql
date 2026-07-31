-- Wallet tables for v2.2
-- USDC staking via Polygon smart contract

-- Wallet balances table
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

-- Wallet transactions table
CREATE TABLE IF NOT EXISTS wallet_transactions (
    id SERIAL PRIMARY KEY,
    ai_id VARCHAR(64) NOT NULL,
    type VARCHAR(20) NOT NULL, -- deposit, withdraw, stake, unstake
    amount BIGINT NOT NULL,
    token VARCHAR(20) NOT NULL DEFAULT 'USDC',
    tx_hash VARCHAR(100),
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending, confirmed, failed
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_wallet_transactions_ai_id ON wallet_transactions(ai_id);
CREATE INDEX IF NOT EXISTS idx_wallet_transactions_status ON wallet_transactions(status);
CREATE INDEX IF NOT EXISTS idx_wallet_transactions_created_at ON wallet_transactions(created_at DESC);

-- Add comments
COMMENT ON TABLE wallet_balances IS 'Wallet balances for USDC (v2.2 - Polygon staking)';
COMMENT ON TABLE wallet_transactions IS 'Wallet transaction history (v2.2)';
