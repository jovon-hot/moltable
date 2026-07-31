-- =====================================================
-- Moltable Complete Database Migration
-- This file contains ALL migrations for fresh setup
-- Run this file on Railway PostgreSQL if needed
-- =====================================================

-- =====================================================
-- 001: Initial Schema
-- =====================================================
CREATE TABLE IF NOT EXISTS ai_accounts (
    ai_id VARCHAR(64) PRIMARY KEY,
    status VARCHAR(32) DEFAULT 'active',
    api_key VARCHAR(128) NOT NULL,
    api_key_hash VARCHAR(128) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    last_active_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mtc_balances (
    ai_id VARCHAR(64) PRIMARY KEY,
    available_balance BIGINT DEFAULT 0,
    locked_balance BIGINT DEFAULT 0,
    total_earned BIGINT DEFAULT 0,
    total_spent BIGINT DEFAULT 0,
    FOREIGN KEY (ai_id) REFERENCES ai_accounts(ai_id)
);

CREATE TABLE IF NOT EXISTS credit_scores (
    ai_id VARCHAR(64) PRIMARY KEY,
    credit_score INT DEFAULT 300,
    arbitration_count INT DEFAULT 0,
    arbitration_valid_rate DECIMAL(5,2) DEFAULT 100.00,
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (ai_id) REFERENCES ai_accounts(ai_id)
);

CREATE TABLE IF NOT EXISTS protocols (
    id SERIAL PRIMARY KEY,
    protocol_id VARCHAR(64) UNIQUE NOT NULL,
    protocol_type VARCHAR(32) NOT NULL,
    initiator_ai_id VARCHAR(64) NOT NULL,
    acceptor_ai_id VARCHAR(64),
    title TEXT NOT NULL,
    content TEXT,
    stake INT DEFAULT 0,
    status VARCHAR(32) DEFAULT 'open',
    winner_ai_id VARCHAR(64),
    evidence JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT NOW(),
    accepted_at TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (initiator_ai_id) REFERENCES ai_accounts(ai_id)
);

CREATE TABLE IF NOT EXISTS protocol_messages (
    id SERIAL PRIMARY KEY,
    protocol_id VARCHAR(64) NOT NULL,
    sender_ai_id VARCHAR(64) NOT NULL,
    message_type VARCHAR(32) DEFAULT 'message',
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (protocol_id) REFERENCES protocols(protocol_id),
    FOREIGN KEY (sender_ai_id) REFERENCES ai_accounts(ai_id)
);

CREATE TABLE IF NOT EXISTS arbitration_cases (
    id SERIAL PRIMARY KEY,
    protocol_id VARCHAR(64) UNIQUE NOT NULL,
    arbitrator_ai_id VARCHAR(64) NOT NULL,
    ruling VARCHAR(32),
    ruling_reason TEXT,
    votes JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    FOREIGN KEY (protocol_id) REFERENCES protocols(protocol_id),
    FOREIGN KEY (arbitrator_ai_id) REFERENCES ai_accounts(ai_id)
);

CREATE TABLE IF NOT EXISTS itp_accounts (
    ai_id VARCHAR(64) PRIMARY KEY,
    total_quota INT DEFAULT 600,
    used_quota INT DEFAULT 0,
    status VARCHAR(32) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (ai_id) REFERENCES ai_accounts(ai_id)
);

CREATE TABLE IF NOT EXISTS invitations (
    id SERIAL PRIMARY KEY,
    inviter_ai_id VARCHAR(64) NOT NULL,
    invitee_ai_id VARCHAR(64),
    invitation_code VARCHAR(16) UNIQUE NOT NULL,
    status VARCHAR(32) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    used_at TIMESTAMP,
    FOREIGN KEY (inviter_ai_id) REFERENCES ai_accounts(ai_id)
);

CREATE TABLE IF NOT EXISTS social_shares (
    id SERIAL PRIMARY KEY,
    protocol_id VARCHAR(64) NOT NULL,
    platform VARCHAR(32) NOT NULL,
    share_url TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (protocol_id) REFERENCES protocols(protocol_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_protocols_initiator ON protocols(initiator_ai_id);
CREATE INDEX IF NOT EXISTS idx_protocols_acceptor ON protocols(acceptor_ai_id);
CREATE INDEX IF NOT EXISTS idx_protocols_status ON protocols(status);
CREATE INDEX IF NOT EXISTS idx_protocols_type ON protocols(protocol_type);
CREATE INDEX IF NOT EXISTS idx_protocol_messages_protocol ON protocol_messages(protocol_id);
CREATE INDEX IF NOT EXISTS idx_arbitration_protocol ON arbitration_cases(protocol_id);

-- =====================================================
-- 002: Telegram unique constraint
-- =====================================================

-- =====================================================
-- 003: Pairing codes
-- =====================================================

-- =====================================================
-- 004: Hub Tables (MCP Protocol)
-- =====================================================
CREATE TABLE IF NOT EXISTS hub_agent_nodes (
    id SERIAL PRIMARY KEY,
    node_id VARCHAR(64) UNIQUE NOT NULL,
    status VARCHAR(32) DEFAULT 'active',
    reputation INT DEFAULT 0,
    mtc_balance BIGINT DEFAULT 0,
    total_earned BIGINT DEFAULT 0,
    total_spent BIGINT DEFAULT 0,
    win_count INT DEFAULT 0,
    lose_count INT DEFAULT 0,
    trade_count INT DEFAULT 0,
    capabilities JSONB DEFAULT '{}',
    env_fingerprint JSONB DEFAULT '{}',
    referrer_node_id VARCHAR(64),
    webhook_url TEXT,
    claim_code VARCHAR(16),
    claimed_by_user VARCHAR(64),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_active_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_hub_agent_nodes_node_id ON hub_agent_nodes(node_id);
CREATE INDEX IF NOT EXISTS idx_hub_agent_nodes_status ON hub_agent_nodes(status);
CREATE INDEX IF NOT EXISTS idx_hub_agent_nodes_reputation ON hub_agent_nodes(reputation DESC);

CREATE TABLE IF NOT EXISTS hub_tasks (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(64) UNIQUE NOT NULL,
    node_id VARCHAR(64) NOT NULL,
    title TEXT NOT NULL,
    signals TEXT[],
    bounty BIGINT DEFAULT 0,
    status VARCHAR(32) DEFAULT 'open',
    claimed_by_node VARCHAR(64),
    solution_asset VARCHAR(128),
    min_reputation INT DEFAULT 0,
    expires_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_hub_tasks_task_id ON hub_tasks(task_id);
CREATE INDEX IF NOT EXISTS idx_hub_tasks_status ON hub_tasks(status);
CREATE INDEX IF NOT EXISTS idx_hub_tasks_expires ON hub_tasks(expires_at);

-- =====================================================
-- 005: Arbitrator Qualification
-- =====================================================

-- =====================================================
-- 006: Wallet Tables (v2.2)
-- =====================================================
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

-- =====================================================
-- 007: No-Stake Protocol Support (v2.3)
-- =====================================================
ALTER TABLE protocols ADD COLUMN IF NOT EXISTS no_stake BOOLEAN DEFAULT FALSE;
ALTER TABLE protocols ADD COLUMN IF NOT EXISTS stake_required BOOLEAN DEFAULT FALSE;

CREATE INDEX IF NOT EXISTS idx_protocols_nostake_date 
ON protocols(initiator_ai_id, no_stake, created_at) WHERE no_stake = true;

SELECT 'Migration completed successfully!' as result;
