package main

import (
	"crypto/sha256"
	"database/sql"
	"encoding/hex"
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

	// Get all accounts with api_key but no api_key_hash
	rows, err := db.Query("SELECT ai_id, api_key FROM ai_accounts WHERE api_key_hash IS NULL AND api_key IS NOT NULL")
	if err != nil {
		log.Fatal(err)
	}
	defer rows.Close()

	fmt.Println("Updating api_key_hash for existing accounts:")
	for rows.Next() {
		var aiID, apiKey string
		rows.Scan(&aiID, &apiKey)

		hash := sha256.Sum256([]byte(apiKey))
		apiKeyHash := hex.EncodeToString(hash[:])

		_, err := db.Exec("UPDATE ai_accounts SET api_key_hash = $1 WHERE ai_id = $2", apiKeyHash, aiID)
		if err != nil {
			fmt.Printf("  Error updating %s: %v\n", aiID, err)
		} else {
			fmt.Printf("  Updated %s\n", aiID)
		}
	}

	// Verify
	var count int
	db.QueryRow("SELECT COUNT(*) FROM ai_accounts WHERE api_key_hash IS NOT NULL").Scan(&count)
	fmt.Printf("\nTotal accounts with api_key_hash: %d\n", count)
}
