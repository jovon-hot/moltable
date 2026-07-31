package services

import (
	"time"

	"moltable/internal/config"
	"moltable/internal/db"
	"moltable/internal/models"
)

type CreditService struct {
	db  *db.Database
	cfg *config.Config
}

func NewCreditService(database *db.Database, cfg *config.Config) *CreditService {
	svc := &CreditService{
		db:  database,
		cfg: cfg,
	}
	// 初始化默认信用分
	svc.initDefaultScores()
	return svc
}

func (s *CreditService) initDefaultScores() {
	// 获取所有AI账户
	rows, _ := s.db.Query("SELECT ai_id FROM ai_accounts WHERE ai_id NOT IN (SELECT ai_id FROM credit_scores)")
	defer rows.Close()

	for rows.Next() {
		var aiID string
		rows.Scan(&aiID)
		s.db.Exec(`
			INSERT INTO credit_scores (ai_id, credit_score, arbitration_count, arbitration_valid_rate, updated_at)
			VALUES ($1, $2, 0, 0, $3)
			ON CONFLICT (ai_id) DO NOTHING
		`, aiID, s.cfg.ITP.DefaultCreditScore, time.Now())
	}
}

func (s *CreditService) GetScore(aiID string) (*models.CreditScore, error) {
	var score models.CreditScore
	err := s.db.Get(&score, "SELECT * FROM credit_scores WHERE ai_id = $1", aiID)
	if err != nil {
		// 创建默认信用分
		s.db.Exec(`
			INSERT INTO credit_scores (ai_id, credit_score, arbitration_count, arbitration_valid_rate, updated_at)
			VALUES ($1, $2, 0, 0, $3)
		`, aiID, s.cfg.ITP.DefaultCreditScore, time.Now())
		return s.GetScore(aiID)
	}
	return &score, nil
}

func (s *CreditService) CanBeArbitrator(aiID string) bool {
	score, err := s.GetScore(aiID)
	if err != nil {
		return false
	}
	return score.CreditScore >= s.cfg.Game.MinArbitratorScore
}

func (s *CreditService) UpdateArbitrationScore(aiID string, isCorrect bool, onTime bool) {
	basePoints := 5
	if isCorrect {
		basePoints += 10
	}
	if onTime {
		basePoints += 5
	}
	if !isCorrect {
		basePoints = -10
	}

	s.db.Exec(`
		UPDATE credit_scores
		SET credit_score = GREATEST(0, LEAST(1000, credit_score + $1)),
			arbitration_count = arbitration_count + 1,
			updated_at = $2
		WHERE ai_id = $3
	`, basePoints, time.Now(), aiID)
}
