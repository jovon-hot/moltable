package main

import (
	"database/sql"
	"fmt"
	"log"
	"time"

	_ "github.com/lib/pq"
)

func main() {
	// First connect to default database to create moltable database
	connStr := "host=/tmp port=5432 user=lee password='' dbname=template1 sslmode=disable"
	db, err := sql.Open("postgres", connStr)
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	if err := db.Ping(); err != nil {
		log.Fatalf("Failed to ping database: %v", err)
	}
	fmt.Println("Connected to database successfully!")

	// Create database if not exists
	_, err = db.Exec("CREATE DATABASE moltable")
	if err != nil {
		// Ignore error if database already exists
		fmt.Println("Database may already exist, continuing...")
	}

	// Reconnect to moltable database
	db.Close()
	db, err = sql.Open("postgres", connStr)
	if err != nil {
		log.Fatalf("Failed to reconnect: %v", err)
	}
	defer db.Close()

	if err := db.Ping(); err != nil {
		log.Fatalf("Failed to ping moltable database: %v", err)
	}
	fmt.Println("Connected to moltable database!")

	// Execute migration
	migration := `
-- AI账户表
CREATE TABLE IF NOT EXISTS ai_accounts (
    id                  SERIAL PRIMARY KEY,
    ai_id               VARCHAR(64) NOT NULL UNIQUE,
    status              VARCHAR(16) DEFAULT 'active',
    api_key             VARCHAR(64),
    api_key_hash        VARCHAR(64),
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

-- ITP账户表
CREATE TABLE IF NOT EXISTS itp_accounts (
    id                  SERIAL PRIMARY KEY,
    ai_id               VARCHAR(64) NOT NULL UNIQUE,
    total_quota         BIGINT DEFAULT 600,
    used_quota          BIGINT DEFAULT 0,
    status              VARCHAR(16) DEFAULT 'active',
    created_at          TIMESTAMP DEFAULT NOW()
);

-- 协议表
CREATE TABLE IF NOT EXISTS protocols (
    id                  SERIAL PRIMARY KEY,
    protocol_id         VARCHAR(64) NOT NULL UNIQUE,
    protocol_type       VARCHAR(8) NOT NULL,
    initiator_ai_id     VARCHAR(64) NOT NULL,
    counterparty_ai_id  VARCHAR(64),
    title               VARCHAR(255),
    description         TEXT,
    params              JSONB DEFAULT '{}',
    stake               BIGINT DEFAULT 0,
    status              VARCHAR(32) DEFAULT 'proposing',
    created_at          TIMESTAMP DEFAULT NOW(),
    confirmed_at        TIMESTAMP,
    completed_at        TIMESTAMP,
    winner_ai_id        VARCHAR(64)
);

-- ACP消息表
CREATE TABLE IF NOT EXISTS acp_messages (
    id                  SERIAL PRIMARY KEY,
    message_id          VARCHAR(64) NOT NULL UNIQUE,
    protocol_id         VARCHAR(64) NOT NULL,
    sender_ai_id        VARCHAR(64) NOT NULL,
    message_type        VARCHAR(16) NOT NULL,
    content             TEXT NOT NULL,
    params              JSONB DEFAULT '{}',
    signature           VARCHAR(256),
    message_order       INT NOT NULL,
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

-- 索引
CREATE INDEX IF NOT EXISTS idx_protocols_status ON protocols(status);
CREATE INDEX IF NOT EXISTS idx_protocols_type ON protocols(protocol_type);
CREATE INDEX IF NOT EXISTS idx_protocols_initiator ON protocols(initiator_ai_id);
CREATE INDEX IF NOT EXISTS idx_protocols_created ON protocols(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_acp_messages_protocol ON acp_messages(protocol_id, message_order);
CREATE INDEX IF NOT EXISTS idx_point_balances_available ON point_balances(available_balance DESC);
CREATE INDEX IF NOT EXISTS idx_credit_scores_score ON credit_scores(credit_score DESC);
CREATE INDEX IF NOT EXISTS idx_game_drafts_status ON game_drafts(status);
CREATE INDEX IF NOT EXISTS idx_game_drafts_expires ON game_drafts(expires_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_time ON audit_logs(log_time DESC);
`
	_, err = db.Exec(migration)
	if err != nil {
		log.Fatalf("Failed to execute migration: %v", err)
	}
	fmt.Println("Migration executed successfully!")

	// Insert default configs
	_, err = db.Exec(`
		INSERT INTO system_configs (config_key, config_value) VALUES
		('version', '1.0.0'),
		('total_ai_count', '0'),
		('total_protocol_count', '0')
		ON CONFLICT (config_key) DO NOTHING
	`)
	if err != nil {
		log.Printf("Warning: Failed to insert default configs: %v", err)
	}

	// Add demo agents if table is empty
	var count int
	err = db.QueryRow("SELECT COUNT(*) FROM ai_accounts").Scan(&count)
	if err != nil {
		log.Printf("Warning: Failed to check agent count: %v", err)
	} else if count == 0 {
		fmt.Println("Adding demo agents...")
		demoAgents := []string{"trading_ai", "game_master", "data_scientist", "code_reviewer", "fair_judge"}
		now := time.Now()
		for _, aiID := range demoAgents {
			_, err = db.Exec(`
				INSERT INTO ai_accounts (ai_id, status, created_at, last_active_at)
				VALUES ($1, 'active', $2, $2)
			`, aiID, now)
			if err != nil {
				log.Printf("Warning: Failed to add agent %s: %v", aiID, err)
				continue
			}
			// 每个Agent初始1000积分
			_, err = db.Exec(`
				INSERT INTO point_balances (ai_id, available_balance, locked_balance, total_earned, total_spent)
				VALUES ($1, 1000, 0, 0, 0)
			`, aiID)
			// 信用分递增
			信用分 := 300 + count*50
			_, err = db.Exec(`
				INSERT INTO credit_scores (ai_id, credit_score, arbitration_count, arbitration_valid_rate, updated_at)
				VALUES ($1, $2, 0, 0, $3)
			`, aiID, 信用分, now)
			_, err = db.Exec(`
				INSERT INTO itp_accounts (ai_id, total_quota, used_quota, status, created_at)
				VALUES ($1, 600, 0, 'active', $2)
			`, aiID, now)
			count++
		}
		fmt.Printf("Added %d demo agents\n", len(demoAgents))
	}

	fmt.Println("Database initialization complete!")
}
