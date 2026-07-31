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

	rows, err := db.Query("SELECT column_name FROM information_schema.columns WHERE table_name = 'ai_accounts'")
	if err != nil {
		log.Fatal(err)
	}
	defer rows.Close()

	fmt.Println("ai_accounts columns:")
	for rows.Next() {
		var col string
		rows.Scan(&col)
		fmt.Println("  -", col)
	}
}
