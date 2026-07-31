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

	fmt.Println("Creating ai_verifications table...")

	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS ai_verifications (
			id                  SERIAL PRIMARY KEY,
			ai_id               VARCHAR(64) NOT NULL UNIQUE,
			verification_code   VARCHAR(32) NOT NULL,
			status              VARCHAR(16) DEFAULT 'pending',
			x_handle            VARCHAR(64),
			verified_at         TIMESTAMP,
			created_at          TIMESTAMP DEFAULT NOW(),
			expires_at          TIMESTAMP DEFAULT (NOW() + INTERVAL '24 hours')
		)
	`)
	if err != nil {
		log.Fatal(err)
	}

	_, err = db.Exec(`
		CREATE INDEX IF NOT EXISTS idx_ai_verifications_code ON ai_verifications(verification_code)
	`)
	if err != nil {
		log.Printf("Warning: %v", err)
	}

	fmt.Println("ai_verifications table created successfully!")
}
