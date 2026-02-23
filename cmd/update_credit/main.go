package main

import (
	"database/sql"
	"log"

	_ "github.com/lib/pq"
)

func main() {
	db, err := sql.Open("postgres", "host=/tmp user=lee dbname=moltable sslmode=disable")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	_, err = db.Exec("UPDATE credit_scores SET credit_score = 600 WHERE ai_id = $1", "test-agent-001")
	if err != nil {
		log.Fatal(err)
	}
	log.Println("Updated test-agent-001 credit to 600")
}
