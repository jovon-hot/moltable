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

	fmt.Println("Fixing ai_accounts table...")

	// Add missing columns
	cols := []struct {
		name    string
		typ     string
		nullVal string
	}{
		{"api_key", "VARCHAR(64)", "NULL"},
		{"api_key_hash", "VARCHAR(64)", "NULL"},
	}

	for _, col := range cols {
		// Check if column exists
		var exists int
		err := db.QueryRow(`
			SELECT 1 FROM information_schema.columns
			WHERE table_name = 'ai_accounts' AND column_name = $1
		`, col.name).Scan(&exists)

		if err == sql.ErrNoRows {
			fmt.Printf("Adding column %s...\n", col.name)
			_, err := db.Exec(fmt.Sprintf("ALTER TABLE ai_accounts ADD COLUMN %s %s", col.name, col.typ))
			if err != nil {
				log.Printf("Warning: %v", err)
			}
		} else {
			fmt.Printf("Column %s already exists\n", col.name)
		}
	}

	// Also ensure point_balances has all required columns
	fmt.Println("\nChecking point_balances columns...")
	rows, err := db.Query("SELECT column_name FROM information_schema.columns WHERE table_name = 'point_balances'")
	if err != nil {
		log.Fatal(err)
	}
	defer rows.Close()

	fmt.Println("point_balances columns:")
	for rows.Next() {
		var col string
		rows.Scan(&col)
		fmt.Println("  -", col)
	}

	fmt.Println("\nDone!")
}
