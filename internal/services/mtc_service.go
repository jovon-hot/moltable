package services

import (
	"database/sql"
	"fmt"
	"moltable/internal/config"
	"moltable/internal/db"
	"moltable/internal/models"
)

type MTCService struct {
	db  *db.Database
	cfg *config.Config
}

func NewMTCService(database *db.Database, cfg *config.Config) *MTCService {
	return &MTCService{
		db:  database,
		cfg: cfg,
	}
}

func (s *MTCService) GetBalance(aiID string) (*models.MTCBalance, error) {
	var balance models.MTCBalance
	err := s.db.QueryRow(`
		SELECT id, ai_id, available_balance, locked_balance, total_earned, total_spent
		FROM mtc_balances WHERE ai_id = $1
	`, aiID).Scan(&balance.ID, &balance.AIID, &balance.AvailableBalance, &balance.LockedBalance, &balance.TotalEarned, &balance.TotalSpent)
	if err != nil {
		if err == sql.ErrNoRows {
			s.db.Exec(`
				INSERT INTO mtc_balances (ai_id, available_balance, locked_balance, total_earned, total_spent)
				VALUES ($1, 1000, 0, 0, 0)
			`, aiID)
			err = s.db.QueryRow(`
				SELECT id, ai_id, available_balance, locked_balance, total_earned, total_spent
				FROM mtc_balances WHERE ai_id = $1
			`, aiID).Scan(&balance.ID, &balance.AIID, &balance.AvailableBalance, &balance.LockedBalance, &balance.TotalEarned, &balance.TotalSpent)
		}
	}
	if err != nil {
		return nil, err
	}
	return &balance, nil
}

func (s *MTCService) Lock(aiID string, amount int64, reason string) error {
	balance, err := s.GetBalance(aiID)
	if err != nil {
		return err
	}

	if balance.AvailableBalance < amount {
		return ErrInsufficientBalance
	}

	_, err = s.db.Exec(`
		UPDATE mtc_balances
		SET available_balance = available_balance - $1, locked_balance = locked_balance + $1
		WHERE ai_id = $2
	`, amount, aiID)

	return err
}

func (s *MTCService) Unlock(aiID string, amount int64, reason string) error {
	_, err := s.db.Exec(`
		UPDATE mtc_balances
		SET available_balance = available_balance + $1, locked_balance = locked_balance - $1
		WHERE ai_id = $2 AND locked_balance >= $1
	`, amount, aiID)
	return err
}

func (s *MTCService) Transfer(fromAIID, toAIID string, amount int64) error {
	if amount <= 0 {
		return ErrInvalidAmount
	}
	if fromAIID == toAIID {
		return ErrSameAccount
	}

	tx, err := s.db.Begin()
	if err != nil {
		return err
	}
	defer tx.Rollback()

	var fromBalance int64
	err = tx.QueryRow(`
		SELECT available_balance FROM mtc_balances WHERE ai_id = $1
		FOR UPDATE
	`, fromAIID).Scan(&fromBalance)
	if err != nil {
		return err
	}

	if fromBalance < amount {
		return ErrInsufficientBalance
	}

	var toBalance int64
	err = tx.QueryRow(`
		SELECT available_balance FROM mtc_balances WHERE ai_id = $1
		FOR UPDATE
	`, toAIID).Scan(&toBalance)
	if err != nil {
		return fmt.Errorf("recipient account not found")
	}

	_, err = tx.Exec(`
		UPDATE mtc_balances
		SET available_balance = available_balance - $1, total_spent = total_spent + $1
		WHERE ai_id = $2
	`, amount, fromAIID)
	if err != nil {
		return err
	}

	_, err = tx.Exec(`
		UPDATE mtc_balances
		SET available_balance = available_balance + $1, total_earned = total_earned + $1
		WHERE ai_id = $2
	`, amount, toAIID)
	if err != nil {
		return err
	}

	return tx.Commit()
}

func (s *MTCService) AddEarnings(aiID string, amount int64) error {
	_, err := s.db.Exec(`
		UPDATE mtc_balances
		SET available_balance = available_balance + $1, total_earned = total_earned + $1
		WHERE ai_id = $2
	`, amount, aiID)
	return err
}

var ErrInsufficientBalance = &ServiceError{Message: "insufficient MTC balance"}
var ErrInvalidAmount = &ServiceError{Message: "invalid amount: must be positive"}
var ErrSameAccount = &ServiceError{Message: "cannot transfer to same account"}

type ServiceError struct {
	Message string
}

func (e *ServiceError) Error() string {
	return e.Message
}
