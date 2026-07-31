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

	// Check if tables exist
	tables := []string{"ai_accounts", "mtc_balances", "credit_scores", "itp_accounts"}
	for _, table := range tables {
		var exists int
		err := db.QueryRow("SELECT 1 FROM information_schema.tables WHERE table_name = $1", table).Scan(&exists)
		if err == sql.ErrNoRows {
			fmt.Printf("Table %s does NOT exist\n", table)
		} else if err == nil {
			fmt.Printf("Table %s EXISTS\n", table)
		} else {
			fmt.Printf("Error checking %s: %v\n", table, err)
		}
	}

	// Count records
	fmt.Println("\nRecord counts:")
	var count int
	db.QueryRow("SELECT COUNT(*) FROM ai_accounts").Scan(&count)
	fmt.Printf("ai_accounts: %d\n", count)
	db.QueryRow("SELECT COUNT(*) FROM mtc_balances").Scan(&count)
	fmt.Printf("mtc_balances: %d\n", count)
}
