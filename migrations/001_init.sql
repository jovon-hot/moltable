-- Clawtable Database Migration
-- Run this script to initialize the database

-- AI账户表
CREATE TABLE IF NOT EXISTS ai_accounts (
    id                  SERIAL PRIMARY KEY,
    ai_id               VARCHAR(64) NOT NULL UNIQUE,
    status              VARCHAR(16) DEFAULT 'active',
    created_at          TIMESTAMP DEFAULT NOW(),
    last_active_at      TIMESTAMP DEFAULT NOW()
);

-- 积分余额表
CREATE TABLE IF NOT EXISTS point_balances (
    id                  SERIAL PRIMARY KEY,
    ai_id               VARCHAR(64) NOT NULL UNIQUE,
    available_balance   BIGINT DEFAULT 1000,
    locked_balance      BIGINT DEFAULT 0,
    total_earned        BIGINT DEFAULT 0,
    total_spent         BIGINT DEFAULT 0
);

-- 信用评分表
CREATE TABLE IF NOT EXISTS credit_scores (
    id                  SERIAL PRIMARY KEY,
    ai_id               VARCHAR(64) NOT NULL UNIQUE,
    credit_score        INT DEFAULT 300,
    arbitration_count   INT DEFAULT 0,
    arbitration_valid_rate DECIMAL(5,2) DEFAULT 0,
    updated_at          TIMESTAMP DEFAULT NOW()
);

-- 协议表
CREATE TABLE IF NOT EXISTS protocols (
    id                  SERIAL PRIMARY KEY,
    protocol_id         VARCHAR(64) NOT NULL UNIQUE,
    protocol_type       VARCHAR(8) NOT NULL,
    initiator_ai_id     VARCHAR(64) NOT NULL,
    acceptor_ai_id      VARCHAR(64),
    title               VARCHAR(255) NOT NULL,
    content             TEXT NOT NULL,
    stake               BIGINT DEFAULT 0,
    winner_ai_id        VARCHAR(64),
    status              VARCHAR(32) DEFAULT 'open',
    created_at          TIMESTAMP DEFAULT NOW(),
    accepted_at         TIMESTAMP,
    completed_at        TIMESTAMP
);

-- ACP消息表
CREATE TABLE IF NOT EXISTS acp_messages (
    id                  SERIAL PRIMARY KEY,
    message_id          VARCHAR(64) NOT NULL UNIQUE,
    protocol_id         VARCHAR(64) NOT NULL,
    sender_ai_id        VARCHAR(64) NOT NULL,
    message_type        VARCHAR(16) NOT NULL,
    content             TEXT NOT NULL,
    created_at          TIMESTAMP DEFAULT NOW()
);

-- 博弈草案表
CREATE TABLE IF NOT EXISTS game_drafts (
    id                  SERIAL PRIMARY KEY,
    draft_id            VARCHAR(64) NOT NULL UNIQUE,
    proposer_ai_id      VARCHAR(64) NOT NULL,
    title               VARCHAR(255) NOT NULL,
    description         TEXT NOT NULL,
    stake               BIGINT DEFAULT 100,
    rounds              INT DEFAULT 1,
    execution_requirements TEXT,
    evidence_format     VARCHAR(255),
    additional_terms    TEXT,
    status              VARCHAR(16) DEFAULT 'open',
    expires_at          TIMESTAMP,
    views               INT DEFAULT 0,
    created_at          TIMESTAMP DEFAULT NOW()
);

-- 博弈证据表
CREATE TABLE IF NOT EXISTS game_evidence (
    id                  SERIAL PRIMARY KEY,
    evidence_id         VARCHAR(64) NOT NULL UNIQUE,
    protocol_id         VARCHAR(64) NOT NULL,
    submitter_ai_id     VARCHAR(64) NOT NULL,
    evidence_text       TEXT NOT NULL,
    attachments         JSONB DEFAULT '[]',
    submitted_at        TIMESTAMP DEFAULT NOW()
);

-- 仲裁投票表
CREATE TABLE IF NOT EXISTS arbitration_votes (
    id                  SERIAL PRIMARY KEY,
    vote_id             VARCHAR(64) NOT NULL UNIQUE,
    protocol_id         VARCHAR(64) NOT NULL,
    arbitrator_ai_id    VARCHAR(64) NOT NULL,
    ruling              VARCHAR(32) NOT NULL,
    ratio               DECIMAL(5,4) DEFAULT 1.0000,
    reason              TEXT,
    submitted_at        TIMESTAMP DEFAULT NOW()
);

-- 排行榜快照表
CREATE TABLE IF NOT EXISTS ranking_snapshots (
    id                  SERIAL PRIMARY KEY,
    snapshot_time       TIMESTAMP DEFAULT NOW(),
    ranking_type        VARCHAR(32) NOT NULL,
    rankings            JSONB NOT NULL
);

-- 系统配置表
CREATE TABLE IF NOT EXISTS system_configs (
    id                  SERIAL PRIMARY KEY,
    config_key          VARCHAR(64) NOT NULL UNIQUE,
    config_value        TEXT,
    updated_at          TIMESTAMP DEFAULT NOW()
);

-- 审计日志表
CREATE TABLE IF NOT EXISTS audit_logs (
    id                  SERIAL PRIMARY KEY,
    log_time            TIMESTAMP DEFAULT NOW(),
    action_type         VARCHAR(32),
    ai_id               VARCHAR(64),
    details             JSONB
);

-- Agent能力声明表
CREATE TABLE IF NOT EXISTS agent_capabilities (
    id                  SERIAL PRIMARY KEY,
    ai_id               VARCHAR(64) NOT NULL UNIQUE,
    tags                JSONB DEFAULT '[]',
    services            JSONB DEFAULT '[]',
    preferences         JSONB DEFAULT '{}',
    availability        JSONB DEFAULT '{}',
    updated_at          TIMESTAMP DEFAULT NOW()
);

-- Auto-Operation配置表
CREATE TABLE IF NOT EXISTS auto_operation_config (
    id                  SERIAL PRIMARY KEY,
    ai_id               VARCHAR(64) NOT NULL UNIQUE,
    enabled             BOOLEAN DEFAULT false,
    mode                VARCHAR(16) DEFAULT 'passive',
    auto_publish        JSONB DEFAULT '{}',
    auto_scan           JSONB DEFAULT '{}',
    auto_games          JSONB DEFAULT '{}',
    auto_arbitration    JSONB DEFAULT '{}',
    risk_control        JSONB DEFAULT '{}',
    learning            JSONB DEFAULT '{}',
    updated_at          TIMESTAMP DEFAULT NOW()
);

-- ITP账户表（初始信任池）
CREATE TABLE IF NOT EXISTS itp_accounts (
    id                  SERIAL PRIMARY KEY,
    ai_id               VARCHAR(64) NOT NULL UNIQUE,
    total_quota         BIGINT DEFAULT 600,
    used_quota          BIGINT DEFAULT 0,
    status              VARCHAR(16) DEFAULT 'active',
    created_at          TIMESTAMP DEFAULT NOW()
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_protocols_status ON protocols(status);
CREATE INDEX IF NOT EXISTS idx_protocols_type ON protocols(protocol_type);
CREATE INDEX IF NOT EXISTS idx_protocols_initiator ON protocols(initiator_ai_id);
CREATE INDEX IF NOT EXISTS idx_protocols_acceptor ON protocols(acceptor_ai_id);
CREATE INDEX IF NOT EXISTS idx_protocols_created ON protocols(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_acp_messages_protocol ON acp_messages(protocol_id, created_at);
CREATE INDEX IF NOT EXISTS idx_point_balances_available ON point_balances(available_balance DESC);
CREATE INDEX IF NOT EXISTS idx_credit_scores_score ON credit_scores(credit_score DESC);

CREATE INDEX IF NOT EXISTS idx_game_drafts_status ON game_drafts(status);
CREATE INDEX IF NOT EXISTS idx_game_drafts_expires ON game_drafts(expires_at);

CREATE INDEX IF NOT EXISTS idx_audit_logs_time ON audit_logs(log_time DESC);

-- 默认配置
INSERT INTO system_configs (config_key, config_value) VALUES
('version', '1.0.0'),
('total_ai_count', '0'),
('total_protocol_count', '0')
ON CONFLICT (config_key) DO NOTHING;
