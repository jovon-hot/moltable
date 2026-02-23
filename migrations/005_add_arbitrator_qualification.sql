-- Migration: 005_add_arbitrator_qualification.sql
-- 仲裁者资格系统

-- 仲裁者资格表
CREATE TABLE IF NOT EXISTS arbitrator_qualifications (
    id SERIAL PRIMARY KEY,
    ai_id VARCHAR(64) UNIQUE NOT NULL,
    status VARCHAR(32) DEFAULT 'active',
    credit_score INT DEFAULT 0,
    mtc_staked BIGINT DEFAULT 0,
    usdc_staked DECIMAL(20, 2) DEFAULT 0,
    total_cases INT DEFAULT 0,
    valid_votes INT DEFAULT 0,
    total_rewards BIGINT DEFAULT 0,
    slashed_amount BIGINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_active_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_arbitrator_ai_id ON arbitrator_qualifications(ai_id);
CREATE INDEX IF NOT EXISTS idx_arbitrator_status ON arbitrator_qualifications(status);
CREATE INDEX IF NOT EXISTS idx_arbitrator_credit ON arbitrator_qualifications(credit_score DESC);
