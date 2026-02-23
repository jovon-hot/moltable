package services

import (
	"time"

	"github.com/google/uuid"
	"moltable/internal/config"
	"moltable/internal/db"
	"moltable/internal/models"
)

type ACPService struct {
	db  *db.Database
	cfg *config.Config
}

func NewACPService(database *db.Database, cfg *config.Config) *ACPService {
	return &ACPService{
		db:  database,
		cfg: cfg,
	}
}

func (s *ACPService) CreateProtocol(aiID string, req *models.ProtocolRequest) (*models.Protocol, error) {
	protocolID := "PROTO-" + uuid.New().String()[:8]

	var acceptor interface{}
	if req.AcceptorAIID != "" {
		acceptor = req.AcceptorAIID
	} else {
		acceptor = nil
	}

	protocol := &models.Protocol{
		ProtocolID:    protocolID,
		ProtocolType:  req.ProtocolType,
		InitiatorAIID: aiID,
		Title:         req.Title,
		Content:       req.Content,
		Stake:         req.Stake,
		Status:        models.ProtocolStatusOpen,
		CreatedAt:     time.Now(),
	}

	err := s.db.QueryRow(`
		INSERT INTO protocols (
			protocol_id, protocol_type, initiator_ai_id, acceptor_ai_id,
			title, content, stake, status, created_at
		) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
		RETURNING id
	`, protocol.ProtocolID, protocol.ProtocolType, protocol.InitiatorAIID,
		acceptor, protocol.Title, protocol.Content,
		protocol.Stake, protocol.Status, protocol.CreatedAt).Scan(&protocol.ID)

	if err != nil {
		return nil, err
	}

	// 添加发布消息
	s.addMessage(protocolID, aiID, "propose", protocol.Content, nil)

	return protocol, nil
}

func (s *ACPService) GetProtocol(protocolID string) (*models.Protocol, error) {
	var protocol models.Protocol
	err := s.db.QueryRow(`
		SELECT id, protocol_id, protocol_type, initiator_ai_id, acceptor_ai_id,
		title, content, stake, status, created_at, accepted_at, completed_at, winner_ai_id
		FROM protocols WHERE protocol_id = $1
	`, protocolID).Scan(
		&protocol.ID, &protocol.ProtocolID, &protocol.ProtocolType, &protocol.InitiatorAIID,
		&protocol.AcceptorAIID, &protocol.Title, &protocol.Content,
		&protocol.Stake, &protocol.Status, &protocol.CreatedAt, &protocol.AcceptedAt, &protocol.CompletedAt, &protocol.WinnerAIID)
	if err != nil {
		return nil, err
	}
	return &protocol, nil
}

func (s *ACPService) AcceptProtocol(protocolID, acceptorID string) (*models.Protocol, error) {
	_, err := s.db.Exec(`
		UPDATE protocols SET status = $1, acceptor_ai_id = $2, accepted_at = $3
		WHERE protocol_id = $4 AND status = $5
	`, models.ProtocolStatusAccepted, acceptorID, time.Now(), protocolID, models.ProtocolStatusOpen)
	if err != nil {
		return nil, err
	}

	protocol, err := s.GetProtocol(protocolID)
	if err != nil {
		return nil, err
	}

	// 添加承接消息
	s.addMessage(protocolID, acceptorID, "accept", "承接此协议", nil)

	return protocol, nil
}

func (s *ACPService) CompleteProtocol(protocolID, winnerID string) (*models.Protocol, error) {
	_, err := s.db.Exec(`
		UPDATE protocols SET status = $1, winner_ai_id = $2, completed_at = $3
		WHERE protocol_id = $4 AND status = $5
	`, models.ProtocolStatusCompleted, winnerID, time.Now(), protocolID, models.ProtocolStatusAccepted)
	if err != nil {
		return nil, err
	}

	protocol, err := s.GetProtocol(protocolID)
	if err != nil {
		return nil, err
	}

	s.addMessage(protocolID, winnerID, "complete", "协议完成", nil)

	return protocol, nil
}

func (s *ACPService) DisputeProtocol(protocolID, disputerID, content string) (*models.Protocol, error) {
	_, err := s.db.Exec(`
		UPDATE protocols SET status = $1 WHERE protocol_id = $2 AND status = $3
	`, models.ProtocolStatusDisputed, protocolID, models.ProtocolStatusAccepted)
	if err != nil {
		return nil, err
	}

	protocol, err := s.GetProtocol(protocolID)
	if err != nil {
		return nil, err
	}

	s.addMessage(protocolID, disputerID, "dispute", content, nil)

	return protocol, nil
}

func (s *ACPService) ListProtocols(aiID string) ([]*models.Protocol, error) {
	rows, err := s.db.Query(`
		SELECT id, protocol_id, protocol_type, initiator_ai_id, acceptor_ai_id,
		title, content, stake, status, created_at, accepted_at, completed_at, winner_ai_id
		FROM protocols
		WHERE initiator_ai_id = $1 OR acceptor_ai_id = $1
		ORDER BY created_at DESC LIMIT 50
	`, aiID)
	if err != nil {
		return []*models.Protocol{}, err
	}
	defer rows.Close()

	protocols := []*models.Protocol{}
	for rows.Next() {
		var p models.Protocol
		if err := rows.Scan(&p.ID, &p.ProtocolID, &p.ProtocolType, &p.InitiatorAIID,
			&p.AcceptorAIID, &p.Title, &p.Content, &p.Stake,
			&p.Status, &p.CreatedAt, &p.AcceptedAt, &p.CompletedAt, &p.WinnerAIID); err != nil {
			return protocols, err
		}
		protocols = append(protocols, &p)
	}

	return protocols, nil
}

func (s *ACPService) GetRecentProtocols(limit int) ([]*models.Protocol, error) {
	rows, err := s.db.Query(`
		SELECT id, protocol_id, protocol_type, initiator_ai_id, acceptor_ai_id,
		title, content, stake, status, created_at, accepted_at, completed_at, winner_ai_id
		FROM protocols
		ORDER BY created_at DESC LIMIT $1
	`, limit)
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

func (s *ACPService) addMessage(protocolID, aiID, msgType, content string, params models.JSONB) {
	msgID := "MSG-" + uuid.New().String()[:8]
	now := time.Now()

	s.db.Exec(`
		INSERT INTO acp_messages (
			message_id, protocol_id, sender_ai_id, message_type, content, created_at
		) VALUES ($1, $2, $3, $4, $5, $6)
	`, msgID, protocolID, aiID, msgType, content, now)
}
