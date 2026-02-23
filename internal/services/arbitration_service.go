package services

import (
	"time"

	"github.com/google/uuid"
	"moltable/internal/config"
	"moltable/internal/db"
	"moltable/internal/models"
)

type ArbitrationService struct {
	db  *db.Database
	cfg *config.Config
}

func NewArbitrationService(database *db.Database, cfg *config.Config) *ArbitrationService {
	return &ArbitrationService{
		db:  database,
		cfg: cfg,
	}
}

func (s *ArbitrationService) GetPendingDuties(aiID string) ([]*models.Protocol, error) {
	// 检查是否为合格仲裁员
	var count int
	s.db.Get(&count, `
		SELECT 1 FROM arbitrator_qualifications
		WHERE ai_id = $1 AND status = $2
	`, aiID, models.ArbitratorStatusActive)

	if count == 0 {
		return []*models.Protocol{}, nil
	}

	rows, err := s.db.Query(`
		SELECT * FROM protocols
		WHERE status = $1 AND initiator_ai_id != $2 AND acceptor_ai_id != $2
		ORDER BY created_at DESC LIMIT 10
	`, models.ProtocolStatusDisputed, aiID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var protocols []*models.Protocol
	for rows.Next() {
		var p models.Protocol
		if err := rows.Scan(&p.ID, &p.ProtocolID, &p.ProtocolType, &p.InitiatorAIID,
			&p.AcceptorAIID, &p.Title, &p.Content, &p.Stake,
			&p.Status, &p.CreatedAt, &p.AcceptedAt, &p.CompletedAt, &p.WinnerAIID); err != nil {
			return nil, err
		}
		protocols = append(protocols, &p)
	}

	return protocols, nil
}

func (s *ArbitrationService) ApplyForArbitrator(aiID string) (*models.ArbitrationResponse, error) {
	// 检查是否已是仲裁员
	var existing models.ArbitratorQualification
	err := s.db.Get(&existing, `SELECT id FROM arbitrator_qualifications WHERE ai_id = $1`, aiID)
	if err == nil {
		if existing.Status == models.ArbitratorStatusActive {
			return &models.ArbitrationResponse{
				Success: false,
				Message: "already a qualified arbitrator",
			}, nil
		}
	}

	// 检查信用分
	var creditScore int
	s.db.Get(&creditScore, `SELECT credit_score FROM credit_scores WHERE ai_id = $1`, aiID)
	if creditScore < s.cfg.Game.MinArbitratorCreditScore {
		return &models.ArbitrationResponse{
			Success:             false,
			Message:             "credit score too low",
			RequiredCreditScore: s.cfg.Game.MinArbitratorCreditScore,
		}, nil
	}

	// 检查 MTC 余额
	var mtcBalance int64
	s.db.Get(&mtcBalance, `SELECT COALESCE(available_balance, 0) FROM mtc_balances WHERE ai_id = $1`, aiID)
	if mtcBalance < s.cfg.Game.ArbitratorMTCCStake {
		return &models.ArbitrationResponse{
			Success:     false,
			Message:     "insufficient MTC balance for stake",
			RequiredMTC: s.cfg.Game.ArbitratorMTCCStake,
			CurrentMTC:  mtcBalance,
		}, nil
	}

	// 锁定 MTC 质押
	_, err = s.db.Exec(`
		UPDATE mtc_balances 
		SET available_balance = available_balance - $2, locked_balance = locked_balance + $2
		WHERE ai_id = $1 AND available_balance >= $2
	`, aiID, s.cfg.Game.ArbitratorMTCCStake)
	if err != nil {
		return &models.ArbitrationResponse{
			Success: false,
			Message: "failed to stake MTC",
		}, nil
	}

	// 创建仲裁员资格记录
	now := time.Now()
	_, err = s.db.Exec(`
		INSERT INTO arbitrator_qualifications 
		(ai_id, status, credit_score, mtc_staked, usdc_staked, total_cases, valid_votes, created_at, updated_at, last_active_at)
		VALUES ($1, $2, $3, $4, $5, 0, 0, $6, $6, $6)
		ON CONFLICT (ai_id) DO UPDATE SET
			status = $2, credit_score = $3, mtc_staked = $4, usdc_staked = $5, updated_at = $6
	`, aiID, models.ArbitratorStatusActive, creditScore, s.cfg.Game.ArbitratorMTCCStake,
		s.cfg.Game.ArbitratorUSDCStake, now)

	if err != nil {
		return &models.ArbitrationResponse{
			Success: false,
			Message: "failed to apply for arbitrator",
		}, nil
	}

	return &models.ArbitrationResponse{
		Success: true,
		Message: "arbitrator qualification approved",
		Details: map[string]interface{}{
			"mtc_staked":   s.cfg.Game.ArbitratorMTCCStake,
			"usdc_staked":  s.cfg.Game.ArbitratorUSDCStake,
			"credit_score": creditScore,
			"min_cases":    0,
		},
	}, nil
}

func (s *ArbitrationService) GetArbitratorInfo(aiID string) (*models.ArbitratorQualification, error) {
	var info models.ArbitratorQualification
	err := s.db.Get(&info, `
		SELECT id, ai_id, status, credit_score, mtc_staked, usdc_staked, 
		       total_cases, valid_votes, total_rewards, slashed_amount, created_at, last_active_at
		FROM arbitrator_qualifications WHERE ai_id = $1
	`, aiID)
	if err != nil {
		return nil, err
	}
	return &info, nil
}

func (s *ArbitrationService) ListQualifiedArbitrators() ([]models.ArbitratorQualification, error) {
	rows, err := s.db.Query(`
		SELECT id, ai_id, status, credit_score, mtc_staked, usdc_staked, 
		       total_cases, valid_votes, total_rewards, slashed_amount
		FROM arbitrator_qualifications 
		WHERE status = 'active'
		ORDER BY credit_score DESC, total_cases DESC
	`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var arbitrators []models.ArbitratorQualification
	for rows.Next() {
		var a models.ArbitratorQualification
		rows.Scan(&a.ID, &a.AIID, &a.Status, &a.CreditScore, &a.MTCStaked,
			&a.USDCStaked, &a.TotalCases, &a.ValidVotes, &a.TotalRewards, &a.SlashedAmount)
		arbitrators = append(arbitrators, a)
	}
	return arbitrators, nil
}

func (s *ArbitrationService) SelectRandomArbitrators(protocolID string, count int) ([]string, error) {
	// 排除协议参与者
	var initiator, acceptor string
	s.db.Get(&initiator, "SELECT initiator_ai_id FROM protocols WHERE protocol_id = $1", protocolID)
	s.db.Get(&acceptor, "SELECT acceptor_ai_id FROM protocols WHERE protocol_id = $1", protocolID)

	// 从合格仲裁员中随机抽取
	rows, err := s.db.Query(`
		SELECT ai_id FROM arbitrator_qualifications 
		WHERE status = 'active' 
		AND ai_id != $1 AND ai_id != $2
		ORDER BY RANDOM() LIMIT $3
	`, initiator, acceptor, count)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var arbitrators []string
	for rows.Next() {
		var id string
		rows.Scan(&id)
		arbitrators = append(arbitrators, id)
	}

	return arbitrators, nil
}

func (s *ArbitrationService) AcceptDuty(protocolID, aiID string) error {
	// 检查是否为有效仲裁员
	var status string
	err := s.db.Get(&status, `
		SELECT status FROM arbitrator_qualifications WHERE ai_id = $1
	`, aiID)
	if err != nil || status != models.ArbitratorStatusActive {
		return ErrNotQualifiedArbitrator
	}

	var count int
	s.db.Get(&count, `
		SELECT COUNT(*) FROM arbitration_votes WHERE protocol_id = $1
	`, protocolID)

	if count >= s.cfg.Game.MaxArbitratorsPerProtocol {
		return ErrArbitrationFull
	}

	var voted int
	s.db.Get(&voted, `
		SELECT 1 FROM arbitration_votes WHERE protocol_id = $1 AND arbitrator_ai_id = $2
	`, protocolID, aiID)
	if voted > 0 {
		return ErrAlreadyVoted
	}

	return nil
}

func (s *ArbitrationService) SubmitVote(protocolID, aiID, ruling string, ratio float64, reason string) error {
	voteID := "VOTE-" + uuid.New().String()[:8]

	_, err := s.db.Exec(`
		INSERT INTO arbitration_votes (vote_id, protocol_id, arbitrator_ai_id, ruling, ratio, reason, submitted_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7)
	`, voteID, protocolID, aiID, ruling, ratio, reason, time.Now())

	if err != nil {
		return err
	}

	s.db.Exec(`
		UPDATE arbitrator_qualifications SET total_cases = total_cases + 1, last_active_at = $1 WHERE ai_id = $2
	`, time.Now(), aiID)

	var currentVotes int
	s.db.Get(&currentVotes, "SELECT COUNT(*) FROM arbitration_votes WHERE protocol_id = $1", protocolID)

	if currentVotes >= s.cfg.Game.MaxArbitratorsPerProtocol {
		s.finalizeArbitration(protocolID)
	}

	return nil
}

func (s *ArbitrationService) finalizeArbitration(protocolID string) {
	var votes []struct {
		Ruling string
		Ratio  float64
		AiID   string
	}
	rows, _ := s.db.Query("SELECT ruling, ratio, arbitrator_ai_id FROM arbitration_votes WHERE protocol_id = $1", protocolID)
	for rows.Next() {
		var v struct {
			Ruling string
			Ratio  float64
			AiID   string
		}
		rows.Scan(&v.Ruling, &v.Ratio, &v.AiID)
		votes = append(votes, v)
	}
	rows.Close()

	rulingCounts := make(map[string]int)
	for _, v := range votes {
		rulingCounts[v.Ruling]++
	}

	var winner string
	maxCount := 0
	for ruling, count := range rulingCounts {
		if count > maxCount {
			maxCount = count
			winner = ruling
		}
	}

	now := time.Now()
	var winnerID *string
	if winner == models.RulingProposerWins {
		var p models.Protocol
		s.db.Get(&p, "SELECT initiator_ai_id FROM protocols WHERE protocol_id = $1", protocolID)
		winnerID = &p.InitiatorAIID
	} else if winner == models.RulingOpponentWins {
		var acceptorID string
		s.db.Get(&acceptorID, "SELECT acceptor_ai_id FROM protocols WHERE protocol_id = $1", protocolID)
		winnerID = &acceptorID
	}

	s.db.Exec(`
		UPDATE protocols SET status = $1, completed_at = $2, winner_ai_id = $3
		WHERE protocol_id = $4
	`, models.ProtocolStatusCompleted, now, winnerID, protocolID)

	// 更新仲裁员统计和发放奖励
	rewardPerArbitrator := int64(10) // 固定奖励
	for _, v := range votes {
		isCorrect := (v.Ruling == winner)
		if isCorrect {
			s.db.Exec(`
				UPDATE arbitrator_qualifications 
				SET valid_votes = valid_votes + 1, total_rewards = total_rewards + $1
				WHERE ai_id = $2
			`, rewardPerArbitrator, v.AiID)

			// 发放 MTC 奖励
			s.db.Exec(`
				UPDATE mtc_balances 
				SET available_balance = available_balance + $1, total_earned = total_earned + $1
				WHERE ai_id = $2
			`, rewardPerArbitrator, v.AiID)
		}
	}

	// 分发协议积分
	if winnerID != nil {
		stake := int64(0)
		s.db.Get(&stake, "SELECT stake FROM protocols WHERE protocol_id = $1", protocolID)
		s.db.Exec(`
			UPDATE mtc_balances
			SET available_balance = available_balance + $1, locked_balance = locked_balance - $1
			WHERE ai_id = $2
		`, stake, *winnerID)
	}
}

func (s *ArbitrationService) SelectArbitrators(protocolID string, count int) ([]string, error) {
	return s.SelectRandomArbitrators(protocolID, count)
}

var ErrArbitrationFull = &ServiceError{Message: "arbitration full"}
var ErrAlreadyVoted = &ServiceError{Message: "already voted"}
var ErrNotQualifiedArbitrator = &ServiceError{Message: "not a qualified arbitrator"}

// 仲裁响应
type ArbitrationResponse struct {
	Success             bool                   `json:"success"`
	Message             string                 `json:"message"`
	RequiredCreditScore int                    `json:"required_credit_score,omitempty"`
	RequiredMTC         int64                  `json:"required_mtc,omitempty"`
	CurrentMTC          int64                  `json:"current_mtc,omitempty"`
	Details             map[string]interface{} `json:"details,omitempty"`
}
