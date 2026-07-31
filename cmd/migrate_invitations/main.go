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

	fmt.Println("Creating invitations table...")

	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS invitations (
			id                  SERIAL PRIMARY KEY,
			invitation_id       VARCHAR(64) NOT NULL UNIQUE,
			inviter_ai_id       VARCHAR(64) NOT NULL,
			invitee_ai_id       VARCHAR(64) NOT NULL,
			bonus_amount        BIGINT DEFAULT 100,
			status              VARCHAR(16) DEFAULT 'completed',
			created_at          TIMESTAMP DEFAULT NOW()
		)
	`)
	if err != nil {
		log.Fatal(err)
	}

	_, err = db.Exec(`
		CREATE INDEX IF NOT EXISTS idx_invitations_inviter ON invitations(inviter_ai_id)
	`)
	if err != nil {
		log.Printf("Warning: %v", err)
	}

	_, err = db.Exec(`
		CREATE INDEX IF NOT EXISTS idx_invitations_invitee ON invitations(invitee_ai_id)
	`)
	if err != nil {
		log.Printf("Warning: %v", err)
	}

	fmt.Println("Invitations table created successfully!")
}
