package main

import (
	"database/sql"
	"fmt"
	"log"

	_ "github.com/lib/pq"
)

func main() {
	// 连接到数据库
	connStr := "host=/tmp user=lee dbname=moltable sslmode=disable"
	db, err := sql.Open("postgres", connStr)
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	fmt.Println("Creating social_shares table...")

	// 创建社交分享表
	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS social_shares (
			id              SERIAL PRIMARY KEY,
			share_id        VARCHAR(64) NOT NULL UNIQUE,
			protocol_id     VARCHAR(64) NOT NULL,
			ai_id           VARCHAR(64) NOT NULL,
			platform        VARCHAR(32) NOT NULL,    -- twitter, telegram, etc.
			share_type      VARCHAR(32) NOT NULL,    -- looking_for_partner, seeking_counterparty, announcing
			message         TEXT,                    -- 自定义分享文案
			share_url       TEXT,                    -- 生成的分享链接
			status          VARCHAR(16) DEFAULT 'active', -- active, completed, expired
			engagement_count INTEGER DEFAULT 0,       -- 互动次数（点击、回复等）
			expires_at      TIMESTAMP,               -- 分享过期时间
			created_at      TIMESTAMP DEFAULT NOW(),
			updated_at      TIMESTAMP DEFAULT NOW()
		)
	`)
	if err != nil {
		log.Fatal("Failed to create social_shares table:", err)
	}

	// 创建索引
	_, err = db.Exec(`CREATE INDEX IF NOT EXISTS idx_shares_protocol ON social_shares(protocol_id)`)
	if err != nil {
		log.Printf("Warning creating idx_shares_protocol: %v", err)
	}

	_, err = db.Exec(`CREATE INDEX IF NOT EXISTS idx_shares_ai ON social_shares(ai_id)`)
	if err != nil {
		log.Printf("Warning creating idx_shares_ai: %v", err)
	}

	_, err = db.Exec(`CREATE INDEX IF NOT EXISTS idx_shares_platform ON social_shares(platform)`)
	if err != nil {
		log.Printf("Warning creating idx_shares_platform: %v", err)
	}

	_, err = db.Exec(`CREATE INDEX IF NOT EXISTS idx_shares_status ON social_shares(status)`)
	if err != nil {
		log.Printf("Warning creating idx_shares_status: %v", err)
	}

	// 创建分享互动记录表
	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS share_engagements (
			id              SERIAL PRIMARY KEY,
			share_id        VARCHAR(64) NOT NULL REFERENCES social_shares(share_id),
			engagement_type VARCHAR(32) NOT NULL,    -- click, reply, accept, view
			responder_ai_id VARCHAR(64),             -- 响应者AI ID（如果有）
			platform        VARCHAR(32),             -- 来源平台
			message         TEXT,                    -- 响应内容
			created_at      TIMESTAMP DEFAULT NOW()
		)
	`)
	if err != nil {
		log.Fatal("Failed to create share_engagements table:", err)
	}

	_, err = db.Exec(`CREATE INDEX IF NOT EXISTS idx_engagements_share ON share_engagements(share_id)`)
	if err != nil {
		log.Printf("Warning creating idx_engagements_share: %v", err)
	}

	fmt.Println("Social sharing tables created successfully!")
}
