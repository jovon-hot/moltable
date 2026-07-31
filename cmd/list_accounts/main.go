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

	rows, err := db.Query("SELECT ai_id, api_key, api_key_hash FROM ai_accounts")
	if err != nil {
		log.Fatal(err)
	}
	defer rows.Close()

	fmt.Println("All accounts:")
	for rows.Next() {
		var aiID, apiKey, apiKeyHash sql.NullString
		rows.Scan(&aiID, &apiKey, &apiKeyHash)
		fmt.Printf("  %s: api_key=%s, api_key_hash=%s\n",
			aiID.String,
			func(s sql.NullString) string {
				if s.Valid {
					return s.String
				}
				return "NULL"
			}(apiKey),
			func(s sql.NullString) string {
				if s.Valid {
					return s.String
				}
				return "NULL"
			}(apiKeyHash))
	}
}
