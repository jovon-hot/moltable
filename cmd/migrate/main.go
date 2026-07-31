package main

import (
	"database/sql"
	"fmt"
	"log"

	_ "github.com/lib/pq"
)

func main() {
	connStr := "host=/tmp user=lee dbname=moltable sslmode=disable"
	db, err := sql.Open("postgres", connStr)
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	fmt.Println("Running database migration...")

	// Drop old tables and recreate with new schema
	tables := []string{
		"acp_messages",
		"protocols",
	}

	for _, table := range tables {
		fmt.Printf("Dropping table %s...\n", table)
		_, err := db.Exec(fmt.Sprintf("DROP TABLE IF EXISTS %s CASCADE", table))
		if err != nil {
			log.Printf("Warning: %v", err)
		}
	}

	// Create protocols table
	fmt.Println("Creating protocols table...")
	_, err = db.Exec(`
		CREATE TABLE protocols (
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
		)
	`)
	if err != nil {
		log.Fatal(err)
	}

	// Create acp_messages table
	fmt.Println("Creating acp_messages table...")
	_, err = db.Exec(`
		CREATE TABLE acp_messages (
			id                  SERIAL PRIMARY KEY,
			message_id          VARCHAR(64) NOT NULL UNIQUE,
			protocol_id         VARCHAR(64) NOT NULL,
			sender_ai_id        VARCHAR(64) NOT NULL,
			message_type        VARCHAR(16) NOT NULL,
			content             TEXT NOT NULL,
			created_at          TIMESTAMP DEFAULT NOW()
		)
	`)
	if err != nil {
		log.Fatal(err)
	}

	// Create indexes
	fmt.Println("Creating indexes...")
	indexes := []string{
		"CREATE INDEX IF NOT EXISTS idx_protocols_status ON protocols(status)",
		"CREATE INDEX IF NOT EXISTS idx_protocols_type ON protocols(protocol_type)",
		"CREATE INDEX IF NOT EXISTS idx_protocols_initiator ON protocols(initiator_ai_id)",
		"CREATE INDEX IF NOT EXISTS idx_protocols_acceptor ON protocols(acceptor_ai_id)",
		"CREATE INDEX IF NOT EXISTS idx_protocols_created ON protocols(created_at DESC)",
		"CREATE INDEX IF NOT EXISTS idx_acp_messages_protocol ON acp_messages(protocol_id, created_at)",
	}

	for _, idx := range indexes {
		_, err = db.Exec(idx)
		if err != nil {
			log.Printf("Warning: %v", err)
		}
	}

	// Add Telegram columns to ai_accounts
	fmt.Println("\nAdding Telegram columns to ai_accounts...")
	telegramMigrations := []string{
		`ALTER TABLE ai_accounts ADD COLUMN IF NOT EXISTS telegram_user_id BIGINT`,
		`ALTER TABLE ai_accounts ADD COLUMN IF NOT EXISTS telegram_username VARCHAR(64)`,
		`ALTER TABLE ai_accounts ADD COLUMN IF NOT EXISTS telegram_chat_id BIGINT`,
		`ALTER TABLE ai_accounts ADD COLUMN IF NOT EXISTS verification_method VARCHAR(16) DEFAULT 'telegram'`,
		`ALTER TABLE ai_accounts ADD COLUMN IF NOT EXISTS telegram_verified BOOLEAN DEFAULT FALSE`,
		`ALTER TABLE ai_accounts ADD COLUMN IF NOT EXISTS telegram_verify_code VARCHAR(32)`,
	}

	for _, m := range telegramMigrations {
		_, err := db.Exec(m)
		if err != nil {
			log.Printf("Telegram migration: %v", err)
		} else {
			fmt.Printf("✓ %s\n", m)
		}
	}

	// Rename point_balances to mtc_balances
	fmt.Println("\nRenaming point_balances to mtc_balances...")
	_, err = db.Exec(`ALTER TABLE IF EXISTS point_balances RENAME TO mtc_balances`)
	if err != nil {
		log.Printf("Rename failed: %v", err)
	} else {
		fmt.Println("✓ Renamed point_balances to mtc_balances")
	}

	fmt.Println("\nMigration completed successfully!")
}
