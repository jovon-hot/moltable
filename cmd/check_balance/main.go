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

	agents := []string{"test-agent-001", "test-agent-002"}
	for _, agent := range agents {
		var aiID string
		var balance int64
		err := db.QueryRow("SELECT ai_id, available_balance FROM mtc_balances WHERE ai_id = $1", agent).Scan(&aiID, &balance)
		if err == sql.ErrNoRows {
			fmt.Printf("No balance record for %s\n", agent)
		} else if err != nil {
			fmt.Printf("Error for %s: %v\n", agent, err)
		} else {
			fmt.Printf("%s: balance=%d\n", aiID, balance)
		}
	}
}
