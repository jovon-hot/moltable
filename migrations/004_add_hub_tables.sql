-- Migration: 004_add_hub_tables.sql
-- Hub/MCP Protocol tables for agent onboarding

-- Agent Nodes table
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

-- Hub Tasks table (for bounty system)
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
