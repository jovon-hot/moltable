package main

import (
	"database/sql"
	"flag"
	"fmt"
	"log"
	"os"

	_ "github.com/lib/pq"
)

func main() {
	// Get DATABASE_URL from environment
	dbURL := os.Getenv("DATABASE_URL")
	if dbURL == "" {
		log.Fatal("DATABASE_URL environment variable not set")
	}

	// Parse command line flags
	aiID := flag.String("ai", "", "AI agent ID")
	mtcBalance := flag.Int64("mtc", -1, "Set MTC balance")
	creditScore := flag.Int("credit", -1, "Set credit score")
	flag.Parse()

	if *aiID == "" {
		log.Fatal("Please specify -ai flag")
	}

	// Connect to database
	db, err := sql.Open("postgres", dbURL)
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Update MTC balance
	if *mtcBalance >= 0 {
		_, err = db.Exec(`
			INSERT INTO mtc_balances (ai_id, available_balance, locked_balance, total_earned, total_spent)
			VALUES ($1, $2, 0, 0, 0)
			ON CONFLICT (ai_id) DO UPDATE SET available_balance = $2
		`, *aiID, *mtcBalance)
		if err != nil {
			log.Fatalf("Failed to update MTC balance: %v", err)
		}
		fmt.Printf("Updated MTC balance for %s to %d\n", *aiID, *mtcBalance)
	}

	// Update credit score
	if *creditScore >= 0 {
		_, err = db.Exec(`
			INSERT INTO credit_scores (ai_id, credit_score, arbitration_count, arbitration_valid_rate, updated_at)
			VALUES ($1, $2, 0, 100.00, NOW())
			ON CONFLICT (ai_id) DO UPDATE SET credit_score = $2, updated_at = NOW()
		`, *aiID, *creditScore)
		if err != nil {
			log.Fatalf("Failed to update credit score: %v", err)
		}
		fmt.Printf("Updated credit score for %s to %d\n", *aiID, *creditScore)
	}

	// If no flags specified, show current balance
	if *mtcBalance < 0 && *creditScore < 0 {
		var mtcAvailable, mtcLocked, mtcEarned, mtcSpent int64
		var credit int
		var creditUpdated sql.NullTime

		err = db.QueryRow(`
			SELECT available_balance, locked_balance, total_earned, total_spent 
			FROM mtc_balances WHERE ai_id = $1
		`, *aiID).Scan(&mtcAvailable, &mtcLocked, &mtcEarned, &mtcSpent)

		if err == sql.ErrNoRows {
			fmt.Printf("No MTC balance found for %s\n", *aiID)
		} else if err != nil {
			log.Printf("Error reading MTC balance: %v\n", err)
		} else {
			fmt.Printf("MTC Balance for %s:\n", *aiID)
			fmt.Printf("  Available: %d\n", mtcAvailable)
			fmt.Printf("  Locked: %d\n", mtcLocked)
			fmt.Printf("  Total Earned: %d\n", mtcEarned)
			fmt.Printf("  Total Spent: %d\n", mtcSpent)
		}

		err = db.QueryRow(`
			SELECT credit_score, updated_at FROM credit_scores WHERE ai_id = $1
		`, *aiID).Scan(&credit, &creditUpdated)

		if err == sql.ErrNoRows {
			fmt.Printf("No credit score found for %s\n", *aiID)
		} else if err != nil {
			log.Printf("Error reading credit score: %v\n", err)
		} else {
			fmt.Printf("Credit Score for %s: %d\n", *aiID, credit)
		}
	}
}
