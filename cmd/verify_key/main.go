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

	apiKey := "mol_4b585801-8d50-4e1f-ad6f-"
	hash := sha256.Sum256([]byte(apiKey))
	apiKeyHash := hex.EncodeToString(hash[:])

	fmt.Println("API Key:", apiKey)
	fmt.Println("Hash:", apiKeyHash)

	var agentID string
	err = db.QueryRow(
		"SELECT ai_id FROM ai_accounts WHERE api_key_hash = $1 AND status = 'active'",
		apiKeyHash,
	).Scan(&agentID)

	if err != nil {
		fmt.Println("Error:", err)
	} else {
		fmt.Println("Agent ID:", agentID)
	}

	// Check what api_key_hash is stored
	var storedHash string
	db.QueryRow("SELECT api_key_hash FROM ai_accounts WHERE ai_id = $1", "test-agent-001").Scan(&storedHash)
	fmt.Println("Stored hash for test-agent-001:", storedHash)
}
