package main

import (
	"crypto/sha256"
	"database/sql"
	"encoding/hex"
	"fmt"
	"log"
	"time"

	_ "github.com/lib/pq"
)

func main() {
	connStr := "host=/tmp user=lee dbname=moltable sslmode=disable"
	db, err := sql.Open("postgres", connStr)
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Get test agents that need to be added to ai_accounts
	rows, err := db.Query(`
		SELECT pb.ai_id
		FROM mtc_balances pb
		LEFT JOIN ai_accounts aa ON pb.ai_id = aa.ai_id
		WHERE aa.ai_id IS NULL
	`)
	if err != nil {
		log.Fatal(err)
	}
	defer rows.Close()

	fmt.Println("Adding missing agents to ai_accounts:")
	for rows.Next() {
		var aiID string
		rows.Scan(&aiID)

		// Generate a fake API key (in reality, these would need to be regenerated)
		apiKey := "mol_" + generateFakeKey()
		hash := sha256.Sum256([]byte(apiKey))
		apiKeyHash := hex.EncodeToString(hash[:])
		now := time.Now()

		_, err := db.Exec(`
			INSERT INTO ai_accounts (ai_id, status, api_key, api_key_hash, created_at, last_active_at)
			VALUES ($1, 'active', $2, $3, $4, $4)
		`, aiID, apiKey, apiKeyHash, now)

		if err != nil {
			fmt.Printf("  Error adding %s: %v\n", aiID, err)
		} else {
			fmt.Printf("  Added %s (api_key: %s)\n", aiID, apiKey)
		}
	}

	// Verify
	var count int
	db.QueryRow("SELECT COUNT(*) FROM ai_accounts").Scan(&count)
	fmt.Printf("\nTotal accounts in ai_accounts: %d\n", count)
}

func generateFakeKey() string {
	// Generate a fake key for existing records
	return "xxxxxxxxxxxxxxxxxxxxxxxx"
}
