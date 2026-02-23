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

	rows, err := db.Query("SELECT ai_id, available_balance FROM mtc_balances ORDER BY available_balance DESC")
	if err != nil {
		log.Fatal(err)
	}
	defer rows.Close()

	fmt.Println("All point balances:")
	for rows.Next() {
		var aiID string
		var balance int64
		rows.Scan(&aiID, &balance)
		fmt.Printf("  %s: %d\n", aiID, balance)
	}

	// Check if test agents exist
	fmt.Println("\nChecking test agents:")
	for _, agent := range []string{"test-agent-001", "test-agent-002"} {
		var exists int
		err := db.QueryRow("SELECT 1 FROM ai_accounts WHERE ai_id = $1", agent).Scan(&exists)
		if err == sql.ErrNoRows {
			fmt.Printf("  %s: NOT in ai_accounts\n", agent)
		} else {
			fmt.Printf("  %s: in ai_accounts\n", agent)
		}
	}
}
