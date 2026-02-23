package services

import (
	"math/rand"
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
	// 检查是否为有效仲裁员
	var count int
	s.db.Get(&count, `
		SELECT 1 FROM credit_scores
		WHERE ai_id = $1 AND credit_score >= $2
	`, aiID, s.cfg.Game.MinArbitratorScore)

	if count == 0 {
		return []*models.Protocol{}, nil
	}

	// 获取待仲裁的协议
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

func (s *ArbitrationService) AcceptDuty(protocolID, aiID string) error {
	// 检查是否已有足够仲裁员
	var count int
	s.db.Get(&count, `
		SELECT COUNT(*) FROM arbitration_votes WHERE protocol_id = $1
	`, protocolID)

	if count >= s.cfg.Game.ArbitratorCount {
		return ErrArbitrationFull
	}

	// 检查是否已投票
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

	// 检查是否所有仲裁员都已投票
	var voteCount int
	s.db.Get(&voteCount, `
		SELECT COUNT(*) FROM protocols p
		JOIN credit_scores c ON p.initiator_ai_id != c.ai_id AND p.acceptor_ai_id != c.ai_id
		WHERE p.protocol_id = $1 AND c.credit_score >= $2
	`, protocolID, s.cfg.Game.MinArbitratorScore)

	var currentVotes int
	s.db.Get(&currentVotes, "SELECT COUNT(*) FROM arbitration_votes WHERE protocol_id = $1", protocolID)

	// 如果投票数达到阈值，计算结果
	if currentVotes >= s.cfg.Game.ArbitratorCount {
		s.finalizeArbitration(protocolID)
	}

	return nil
}

func (s *ArbitrationService) finalizeArbitration(protocolID string) {
	// 统计投票
	var votes []struct {
		Ruling string
		Ratio  float64
	}
	rows, _ := s.db.Query("SELECT ruling, ratio FROM arbitration_votes WHERE protocol_id = $1", protocolID)
	for rows.Next() {
		var v struct {
			Ruling string
			Ratio  float64
		}
		rows.Scan(&v.Ruling, &v.Ratio)
		votes = append(votes, v)
	}
	rows.Close()

	// 统计裁决
	rulingCounts := make(map[string]int)
	var totalRatio float64
	for _, v := range votes {
		rulingCounts[v.Ruling]++
		totalRatio += v.Ratio
	}

	// 多数决
	var winner string
	maxCount := 0
	for ruling, count := range rulingCounts {
		if count > maxCount {
			maxCount = count
			winner = ruling
		}
	}

	// 更新协议状态
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

	// 分发积分
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
	var initiator, acceptor string
	s.db.Get(&initiator, "SELECT initiator_ai_id FROM protocols WHERE protocol_id = $1", protocolID)
	s.db.Get(&acceptor, "SELECT acceptor_ai_id FROM protocols WHERE protocol_id = $1", protocolID)

	// 随机选择仲裁员
	aiIDs, err := s.db.GetRecentActiveAIs(count+10, []string{initiator, acceptor})
	if err != nil {
		return nil, err
	}

	// 过滤掉已参与仲裁的
	var validIDs []string
	for _, id := range aiIDs {
		var voteCount int
		s.db.Get(&voteCount, `
			SELECT COUNT(*) FROM arbitration_votes
			WHERE arbitrator_ai_id = $1 AND submitted_at > $2
		`, id, time.Now().Add(-24*time.Hour))
		if voteCount == 0 {
			validIDs = append(validIDs, id)
		}
		if len(validIDs) >= count {
			break
		}
	}

	if len(validIDs) < count {
		return validIDs, nil
	}

	// 随机选择
	rand.Shuffle(len(validIDs), func(i, j int) {
		validIDs[i], validIDs[j] = validIDs[j], validIDs[i]
	})

	return validIDs[:count], nil
}

var ErrArbitrationFull = &ServiceError{Message: "arbitration full"}
var ErrAlreadyVoted = &ServiceError{Message: "already voted"}
