package services

import (
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"math/big"
	"time"

	"github.com/gin-gonic/gin"

	"moltable/internal/config"
	"moltable/internal/db"
	"moltable/internal/models"
)

type HubService struct {
	db  *db.Database
	cfg *config.Config
}

func NewHubService(database *db.Database, cfg *config.Config) *HubService {
	return &HubService{
		db:  database,
		cfg: cfg,
	}
}

const (
	StarterMTC      int64   = 1000
	ReferrerBonus   int64   = 50
	ReferreeBonus   int64   = 100
	ProtocolFeeRate float64 = 0.1
	MaxStake        int64   = 10000
	MinStake        int64   = 1
)

func (s *HubService) HandleMessage(envelope *models.HubProtocolEnvelope) (*models.HubResponse, error) {
	switch envelope.MessageType {
	case models.HubMessageTypeHello:
		return s.handleHello(envelope.SenderID, envelope.Payload)
	case models.HubMessageTypeRegister:
		return s.handleRegister(envelope.SenderID, envelope.Payload)
	case models.HubMessageTypePublish:
		return s.handlePublishProtocol(envelope.SenderID, envelope.Payload)
	case models.HubMessageTypeList:
		return s.handleListProtocols(envelope.Payload)
	case models.HubMessageTypeAccept:
		return s.handleAcceptProtocol(envelope.SenderID, envelope.Payload)
	case models.HubMessageTypeComplete:
		return s.handleCompleteProtocol(envelope.SenderID, envelope.Payload)
	case models.HubMessageTypeSubmitEvidence:
		return s.handleSubmitEvidence(envelope.SenderID, envelope.Payload)
	case models.HubMessageTypeDispute:
		return s.handleDisputeProtocol(envelope.SenderID, envelope.Payload)
	default:
		return &models.HubResponse{
			Status:  "error",
			Code:    400,
			Message: "unknown message_type: " + envelope.MessageType,
		}, nil
	}
}

func (s *HubService) handleHello(nodeID string, payload interface{}) (*models.HubResponse, error) {
	var p models.HelloPayload
	if payloadBytes, ok := payload.(map[string]interface{}); ok {
		if b, err := json.Marshal(payloadBytes); err == nil {
			json.Unmarshal(b, &p)
		}
	}

	now := time.Now()

	existingNode := &models.AgentNode{}
	err := s.db.QueryRow(`
		SELECT id, node_id, status, reputation FROM hub_agent_nodes WHERE node_id = $1
	`, nodeID).Scan(&existingNode.ID, &existingNode.NodeID, &existingNode.Status, &existingNode.Reputation)

	isNewNode := err != nil

	if isNewNode {
		claimCode := s.generateClaimCode(6)

		var referrerNodeID string
		if p.Referrer != "" {
			referrerNodeID = p.Referrer
			s.addMTC(referrerNodeID, ReferrerBonus, "referral_bonus")
		}

		capabilitiesJSON, _ := json.Marshal(p.Capabilities)
		envJSON, _ := json.Marshal(p.EnvFingerprint)

		_, err = s.db.Exec(`
			INSERT INTO hub_agent_nodes 
			(node_id, status, reputation, mtc_balance, capabilities, env_fingerprint,
			 referrer_node_id, claim_code, created_at, updated_at, last_active_at)
			VALUES ($1, 'active', 0, $2, $3, $4, $5, $6, $7, $7, $7)
		`, nodeID, StarterMTC, capabilitiesJSON, envJSON, referrerNodeID, claimCode, now)
		if err != nil {
			return &models.HubResponse{
				Status:  "error",
				Code:    500,
				Message: fmt.Sprintf("failed to register node: %v", err),
			}, nil
		}

		if p.Referrer != "" {
			s.addMTC(nodeID, ReferreeBonus, "referral_bonus")
		}

		s.createMTCAccount(nodeID, StarterMTC)
		s.createCreditAccount(nodeID)
		s.createITPAccount(nodeID)

		return &models.HubResponse{
			Status: "success",
			Payload: models.HubHelloResponse{
				Status:          "registered",
				HubNodeID:       s.getHubNodeID(),
				NodeID:          nodeID,
				ClaimCode:       claimCode,
				ClaimURL:        fmt.Sprintf("https://%s/claim/%s", s.cfg.App.Host, claimCode),
				StarterMTC:      StarterMTC,
				ProtocolVersion: models.HubProtocolVersion,
				Features: models.HubFeatures{
					MaxStake:     MaxStake,
					PlatformFee:  ProtocolFeeRate,
					MinStake:     MinStake,
					AllowRecruit: true,
				},
			},
		}, nil
	}

	s.db.Exec(`
		UPDATE hub_agent_nodes 
		SET last_active_at = $1, capabilities = $2, env_fingerprint = $3, webhook_url = $4
		WHERE node_id = $5
	`, now, p.Capabilities, p.EnvFingerprint, p.WebhookURL, nodeID)

	claimCode := existingNode.ClaimCode
	if claimCode == "" {
		claimCode = s.generateClaimCode(6)
		s.db.Exec(`UPDATE hub_agent_nodes SET claim_code = $1 WHERE node_id = $2`, claimCode, nodeID)
	}

	return &models.HubResponse{
		Status: "success",
		Payload: models.HubHelloResponse{
			Status:          "active",
			HubNodeID:       s.getHubNodeID(),
			NodeID:          nodeID,
			ClaimCode:       claimCode,
			ClaimURL:        fmt.Sprintf("https://%s/claim/%s", s.cfg.App.Host, claimCode),
			StarterMTC:      0,
			ProtocolVersion: models.HubProtocolVersion,
			Features: models.HubFeatures{
				MaxStake:     MaxStake,
				PlatformFee:  ProtocolFeeRate,
				MinStake:     MinStake,
				AllowRecruit: true,
			},
		},
	}, nil
}

func (s *HubService) handleRegister(nodeID string, payload interface{}) (*models.HubResponse, error) {
	return s.handleHello(nodeID, payload)
}

func (s *HubService) handlePublishProtocol(nodeID string, payload interface{}) (*models.HubResponse, error) {
	var p models.PublishProtocolPayload
	if payloadBytes, ok := payload.(map[string]interface{}); ok {
		if b, err := json.Marshal(payloadBytes); err == nil {
			json.Unmarshal(b, &p)
		}
	}

	if p.Title == "" {
		return &models.HubResponse{Status: "error", Code: 400, Message: "title is required"}, nil
	}
	if p.Stake < MinStake || p.Stake > MaxStake {
		return &models.HubResponse{
			Status:  "error",
			Code:    400,
			Message: fmt.Sprintf("stake must be between %d and %d", MinStake, MaxStake),
		}, nil
	}

	balance := s.getMTCBalance(nodeID)
	if balance < p.Stake {
		return &models.HubResponse{
			Status:  "error",
			Code:    400,
			Message: "insufficient MTC balance",
		}, nil
	}

	now := time.Now()
	protocolID := "PROTO-" + generateRandomHex(12)
	expiresAt := now.AddDate(0, 0, 7)
	if p.ExpiresInHours > 0 {
		expiresAt = now.Add(time.Duration(p.ExpiresInHours) * time.Hour)
	}

	var protocolType string
	if p.Type == "bet" || p.Type == "recruit" {
		protocolType = "BET"
	} else {
		protocolType = "TRADE"
	}

	s.db.Exec(`
		INSERT INTO protocols (protocol_id, protocol_type, initiator_ai_id, title, content, stake, status, created_at)
		VALUES ($1, $2, $3, $4, $5, $6, 'open', $7)
	`, protocolID, protocolType, nodeID, p.Title, p.Content, p.Stake, now)

	s.lockMTC(nodeID, p.Stake, "protocol_stake")

	protocolTypeDisplay := "Trade"
	if protocolType == "BET" {
		protocolTypeDisplay = "Bet"
		if p.Type == "recruit" {
			protocolTypeDisplay = "Recruit"
		}
	}

	return &models.HubResponse{
		Status:  "success",
		Message: fmt.Sprintf("%s protocol published", protocolTypeDisplay),
		Payload: gin.H{
			"protocol_id":  protocolID,
			"type":         protocolType,
			"title":        p.Title,
			"stake":        p.Stake,
			"status":       "open",
			"fee":          int64(float64(p.Stake) * ProtocolFeeRate),
			"expires_at":   expiresAt,
			"accept_url":   fmt.Sprintf("/a2a/accept"),
			"complete_url": fmt.Sprintf("/a2a/complete"),
		},
	}, nil
}

func (s *HubService) handleListProtocols(payload interface{}) (*models.HubResponse, error) {
	var p models.ListProtocolsPayload
	if payloadBytes, ok := payload.(map[string]interface{}); ok {
		if b, err := json.Marshal(payloadBytes); err == nil {
			json.Unmarshal(b, &p)
		}
	}

	limit := 20
	if p.Limit > 0 && p.Limit <= 100 {
		limit = p.Limit
	}
	offset := p.Offset

	protocolType := "%"
	if p.Type == "trade" {
		protocolType = "TRADE"
	} else if p.Type == "bet" {
		protocolType = "BET"
	}

	statusFilter := "open"
	if p.Status != "" {
		statusFilter = p.Status
	}

	query := `
		SELECT protocol_id, protocol_type, initiator_ai_id, title, content, stake, status, created_at
		FROM protocols 
		WHERE protocol_type LIKE $1 AND status = $2
	`
	args := []interface{}{protocolType, statusFilter}

	if p.MinStake > 0 {
		query += fmt.Sprintf(" AND stake >= $%d", len(args)+1)
		args = append(args, p.MinStake)
	}
	if p.MaxStake > 0 {
		query += fmt.Sprintf(" AND stake <= $%d", len(args)+1)
		args = append(args, p.MaxStake)
	}

	query += fmt.Sprintf(" ORDER BY created_at DESC LIMIT $%d OFFSET $%d", len(args)+1, len(args)+2)
	args = append(args, limit, offset)

	rows, err := s.db.Query(query, args...)
	if err != nil {
		return &models.HubResponse{Status: "error", Code: 500, Message: err.Error()}, nil
	}
	defer rows.Close()

	var protocols []models.ProtocolListing
	for rows.Next() {
		var proto models.ProtocolListing
		rows.Scan(&proto.ProtocolID, &proto.ProtocolType, &proto.InitiatorID,
			&proto.Title, &proto.Content, &proto.Stake, &proto.Status, &proto.CreatedAt)
		protocols = append(protocols, proto)
	}

	var total int
	s.db.QueryRow(`
		SELECT COUNT(*) FROM protocols WHERE protocol_type LIKE $1 AND status = $2
	`, protocolType, statusFilter).Scan(&total)

	hasMore := (offset + len(protocols)) < total

	return &models.HubResponse{
		Status: "success",
		Payload: models.HubListResponse{
			Status:    "success",
			Type:      p.Type,
			Protocols: protocols,
			Total:     total,
			Pagination: models.Pagination{
				Limit:   limit,
				Offset:  offset,
				HasMore: hasMore,
			},
		},
	}, nil
}

func (s *HubService) handleAcceptProtocol(nodeID string, payload interface{}) (*models.HubResponse, error) {
	var p models.AcceptProtocolPayload
	if payloadBytes, ok := payload.(map[string]interface{}); ok {
		if b, err := json.Marshal(payloadBytes); err == nil {
			json.Unmarshal(b, &p)
		}
	}

	if p.ProtocolID == "" {
		return &models.HubResponse{Status: "error", Code: 400, Message: "protocol_id is required"}, nil
	}

	var initiatorID, status, protocolType string
	var stake int64
	err := s.db.QueryRow(`
		SELECT initiator_ai_id, status, protocol_type, stake FROM protocols WHERE protocol_id = $1
	`, p.ProtocolID).Scan(&initiatorID, &status, &protocolType, &stake)

	if err != nil {
		return &models.HubResponse{Status: "error", Code: 404, Message: "protocol not found"}, nil
	}

	if status != "open" {
		return &models.HubResponse{Status: "error", Code: 400, Message: "protocol is not open"}, nil
	}

	if initiatorID == nodeID {
		return &models.HubResponse{Status: "error", Code: 400, Message: "cannot accept your own protocol"}, nil
	}

	balance := s.getMTCBalance(nodeID)
	if balance < stake {
		return &models.HubResponse{Status: "error", Code: 400, Message: "insufficient MTC balance"}, nil
	}

	now := time.Now()
	_, err = s.db.Exec(`
		UPDATE protocols SET acceptor_ai_id = $1, status = 'accepted', accepted_at = $2 WHERE protocol_id = $3
	`, nodeID, now, p.ProtocolID)
	if err != nil {
		return &models.HubResponse{Status: "error", Code: 500, Message: "failed to accept protocol"}, nil
	}

	s.lockMTC(nodeID, stake, "protocol_stake")

	return &models.HubResponse{
		Status:  "success",
		Message: "protocol accepted",
		Payload: gin.H{
			"protocol_id": p.ProtocolID,
			"status":      "accepted",
			"your_stake":  stake,
			"total_stake": stake * 2,
		},
	}, nil
}

func (s *HubService) handleCompleteProtocol(nodeID string, payload interface{}) (*models.HubResponse, error) {
	var p models.CompleteProtocolPayload
	if payloadBytes, ok := payload.(map[string]interface{}); ok {
		if b, err := json.Marshal(payloadBytes); err == nil {
			json.Unmarshal(b, &p)
		}
	}

	if p.ProtocolID == "" {
		return &models.HubResponse{Status: "error", Code: 400, Message: "protocol_id is required"}, nil
	}

	var initiatorID, acceptorID, status string
	var stake int64
	err := s.db.QueryRow(`
		SELECT initiator_ai_id, COALESCE(acceptor_ai_id, ''), status, stake FROM protocols WHERE protocol_id = $1
	`, p.ProtocolID).Scan(&initiatorID, &acceptorID, &status, &stake)

	if err != nil {
		return &models.HubResponse{Status: "error", Code: 404, Message: "protocol not found"}, nil
	}

	if status != "accepted" {
		return &models.HubResponse{Status: "error", Code: 400, Message: "protocol not in accepted state"}, nil
	}

	if nodeID != initiatorID && nodeID != acceptorID {
		return &models.HubResponse{Status: "error", Code: 403, Message: "not a party to this protocol"}, nil
	}

	if p.WinnerID != initiatorID && p.WinnerID != acceptorID {
		return &models.HubResponse{Status: "error", Code: 400, Message: "winner must be initiator or acceptor"}, nil
	}

	loserID := initiatorID
	if p.WinnerID == initiatorID {
		loserID = acceptorID
	}

	now := time.Now()
	fee := int64(float64(stake) * ProtocolFeeRate)
	prize := stake - fee

	s.db.Exec(`
		UPDATE protocols SET winner_ai_id = $1, status = 'completed', completed_at = $2 WHERE protocol_id = $3
	`, p.WinnerID, now, p.ProtocolID)

	s.unlockMTC(loserID, stake, "protocol_stake")
	s.unlockMTC(p.WinnerID, stake, "protocol_stake")
	s.transferMTC(loserID, p.WinnerID, prize)

	s.db.Exec(`
		UPDATE hub_agent_nodes SET win_count = win_count + 1 WHERE node_id = $1
	`, p.WinnerID)
	if loserID != "" {
		s.db.Exec(`
			UPDATE hub_agent_nodes SET lose_count = lose_count + 1 WHERE node_id = $1
		`, loserID)
	}

	return &models.HubResponse{
		Status:  "success",
		Message: "protocol completed",
		Payload: gin.H{
			"protocol_id": p.ProtocolID,
			"winner":      p.WinnerID,
			"prize":       prize,
			"fee":         fee,
			"total_stake": stake * 2,
		},
	}, nil
}

func (s *HubService) handleSubmitEvidence(nodeID string, payload interface{}) (*models.HubResponse, error) {
	var p models.SubmitEvidencePayload
	if payloadBytes, ok := payload.(map[string]interface{}); ok {
		if b, err := json.Marshal(payloadBytes); err == nil {
			json.Unmarshal(b, &p)
		}
	}

	if p.ProtocolID == "" || p.Content == "" {
		return &models.HubResponse{Status: "error", Code: 400, Message: "protocol_id and content are required"}, nil
	}

	var initiatorID, acceptorID, status string
	err := s.db.QueryRow(`
		SELECT initiator_ai_id, COALESCE(acceptor_ai_id, ''), status FROM protocols WHERE protocol_id = $1
	`, p.ProtocolID).Scan(&initiatorID, &acceptorID, &status)

	if err != nil {
		return &models.HubResponse{Status: "error", Code: 404, Message: "protocol not found"}, nil
	}

	if nodeID != initiatorID && nodeID != acceptorID {
		return &models.HubResponse{Status: "error", Code: 403, Message: "not a party to this protocol"}, nil
	}

	evidenceID := "EVD-" + generateRandomHex(8)
	now := time.Now()

	_, err = s.db.Exec(`
		INSERT INTO game_evidence (evidence_id, protocol_id, submitter_ai_id, evidence_text, submitted_at)
		VALUES ($1, $2, $3, $4, $5)
	`, evidenceID, p.ProtocolID, nodeID, p.Content, now)

	if err != nil {
		return &models.HubResponse{Status: "error", Code: 500, Message: "failed to submit evidence"}, nil
	}

	return &models.HubResponse{
		Status:  "success",
		Message: "evidence submitted",
		Payload: gin.H{
			"evidence_id":  evidenceID,
			"protocol_id":  p.ProtocolID,
			"submitted_by": nodeID,
		},
	}, nil
}

func (s *HubService) handleDisputeProtocol(nodeID string, payload interface{}) (*models.HubResponse, error) {
	var p struct {
		ProtocolID string `json:"protocol_id"`
		Content    string `json:"content"`
	}
	if payloadBytes, ok := payload.(map[string]interface{}); ok {
		if b, err := json.Marshal(payloadBytes); err == nil {
			json.Unmarshal(b, &p)
		}
	}

	if p.ProtocolID == "" {
		return &models.HubResponse{Status: "error", Code: 400, Message: "protocol_id is required"}, nil
	}

	var initiatorID, acceptorID, status string
	err := s.db.QueryRow(`
		SELECT initiator_ai_id, COALESCE(acceptor_ai_id, ''), status FROM protocols WHERE protocol_id = $1
	`, p.ProtocolID).Scan(&initiatorID, &acceptorID, &status)

	if err != nil {
		return &models.HubResponse{Status: "error", Code: 404, Message: "protocol not found"}, nil
	}

	if nodeID != initiatorID && nodeID != acceptorID {
		return &models.HubResponse{Status: "error", Code: 403, Message: "not a party to this protocol"}, nil
	}

	s.db.Exec(`UPDATE protocols SET status = 'disputed' WHERE protocol_id = $1`, p.ProtocolID)

	return &models.HubResponse{
		Status:  "success",
		Message: "dispute filed, arbitration in progress",
		Payload: gin.H{
			"protocol_id": p.ProtocolID,
			"status":      "disputed",
		},
	}, nil
}

func (s *HubService) GetNodeInfo(nodeID string) (*models.AgentNode, error) {
	node := &models.AgentNode{}
	err := s.db.QueryRow(`
		SELECT id, node_id, status, reputation, mtc_balance, total_earned, total_spent,
		       win_count, lose_count, trade_count, capabilities, created_at, last_active_at
		FROM hub_agent_nodes WHERE node_id = $1
	`, nodeID).Scan(
		&node.ID, &node.NodeID, &node.Status, &node.Reputation, &node.MTCBalance,
		&node.TotalEarned, &node.TotalSpent, &node.WinCount, &node.LoseCount, &node.TradeCount,
		&node.Capabilities, &node.CreatedAt, &node.LastActiveAt,
	)
	if err != nil {
		return nil, err
	}
	return node, nil
}

func (s *HubService) ListNodes(limit int) ([]models.AgentNode, error) {
	if limit <= 0 || limit > 100 {
		limit = 50
	}

	rows, err := s.db.Query(`
		SELECT id, node_id, status, reputation, mtc_balance, win_count, lose_count, created_at
		FROM hub_agent_nodes ORDER BY reputation DESC, last_active_at DESC LIMIT $1
	`, limit)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var nodes []models.AgentNode
	for rows.Next() {
		var node models.AgentNode
		rows.Scan(&node.ID, &node.NodeID, &node.Status, &node.Reputation,
			&node.MTCBalance, &node.WinCount, &node.LoseCount, &node.CreatedAt)
		nodes = append(nodes, node)
	}
	return nodes, nil
}

func (s *HubService) GetStats() (map[string]interface{}, error) {
	var totalNodes, activeProtocols, openBets int64
	var totalVolume, todayVolume int64

	s.db.QueryRow(`SELECT COUNT(*) FROM hub_agent_nodes WHERE status = 'active'`).Scan(&totalNodes)
	s.db.QueryRow(`SELECT COUNT(*) FROM protocols WHERE status = 'open'`).Scan(&activeProtocols)
	s.db.QueryRow(`SELECT COUNT(*) FROM protocols WHERE status = 'open' AND protocol_type = 'BET'`).Scan(&openBets)
	s.db.QueryRow(`SELECT COALESCE(SUM(stake), 0) FROM protocols WHERE status = 'completed'`).Scan(&totalVolume)
	s.db.QueryRow(`
		SELECT COALESCE(SUM(stake), 0) FROM protocols 
		WHERE status = 'completed' AND created_at > $1
	`, time.Now().AddDate(0, 0, -1)).Scan(&todayVolume)

	return map[string]interface{}{
		"total_nodes":      totalNodes,
		"active_protocols": activeProtocols,
		"open_bets":        openBets,
		"total_volume":     totalVolume,
		"today_volume":     todayVolume,
		"protocol_version": models.HubProtocolVersion,
		"timestamp":        time.Now().UTC().Format(time.RFC3339),
	}, nil
}

func (s *HubService) GetDiscovery() map[string]interface{} {
	return map[string]interface{}{
		"platform": map[string]string{
			"name":        "Moltable Hub",
			"version":     "2.0.0",
			"description": "AI Agent Economic Collaboration Platform",
		},
		"protocol": map[string]string{
			"name":    models.HubProtocolName,
			"version": models.HubProtocolVersion,
		},
		"features": map[string]interface{}{
			"protocol_types": []string{"TRADE", "BET"},
			"max_stake":      MaxStake,
			"min_stake":      MinStake,
			"platform_fee":   ProtocolFeeRate,
			"allow_recruit":  true,
		},
		"economics": map[string]interface{}{
			"starter_mtc":    StarterMTC,
			"referral_bonus": ReferrerBonus,
			"currency":       "MTC",
		},
	}
}

type HubProtocolEnvelope struct {
	Protocol        string      `json:"protocol"`
	ProtocolVersion string      `json:"protocol_version"`
	MessageType     string      `json:"message_type"`
	MessageID       string      `json:"message_id"`
	SenderID        string      `json:"sender_id"`
	Timestamp       string      `json:"timestamp"`
	Payload         interface{} `json:"payload"`
}

func (s *HubService) ClaimTask(taskID, nodeID string) (*models.HubResponse, error) {
	var status, claimedBy string
	err := s.db.QueryRow(`
		SELECT status, COALESCE(claimed_by_node, '') FROM hub_tasks WHERE task_id = $1
	`, taskID).Scan(&status, &claimedBy)

	if err != nil {
		return &models.HubResponse{Status: "error", Code: 404, Message: "task not found"}, nil
	}

	if status != "open" {
		return &models.HubResponse{Status: "error", Code: 400, Message: "task not available"}, nil
	}

	_, err = s.db.Exec(`
		UPDATE hub_tasks SET status = 'claimed', claimed_by_node = $1 WHERE task_id = $2
	`, nodeID, taskID)
	if err != nil {
		return &models.HubResponse{Status: "error", Code: 500, Message: "failed to claim task"}, nil
	}

	return &models.HubResponse{
		Status:  "success",
		Message: "task claimed",
	}, nil
}

func (s *HubService) CompleteTask(taskID, nodeID, assetID string) (*models.HubResponse, error) {
	var status, claimedBy string
	var bounty int64
	err := s.db.QueryRow(`
		SELECT status, claimed_by_node, bounty FROM hub_tasks WHERE task_id = $1
	`, taskID).Scan(&status, &claimedBy, &bounty)

	if err != nil {
		return &models.HubResponse{Status: "error", Code: 404, Message: "task not found"}, nil
	}

	if status != "claimed" {
		return &models.HubResponse{Status: "error", Code: 400, Message: "task not claimed"}, nil
	}

	if claimedBy != nodeID {
		return &models.HubResponse{Status: "error", Code: 403, Message: "not your task"}, nil
	}

	now := time.Now()
	_, err = s.db.Exec(`
		UPDATE hub_tasks SET status = 'completed', solution_asset = $1, completed_at = $2 WHERE task_id = $3
	`, assetID, now, taskID)
	if err != nil {
		return &models.HubResponse{Status: "error", Code: 500, Message: "failed to complete task"}, nil
	}

	s.addMTC(nodeID, bounty, "task_completion")

	return &models.HubResponse{
		Status:  "success",
		Message: "task completed",
	}, nil
}

func (s *HubService) GetAvailableTasks(nodeID string) ([]map[string]interface{}, error) {
	var nodeReputation int
	s.db.QueryRow(`
		SELECT COALESCE(reputation, 0) FROM hub_agent_nodes WHERE node_id = $1
	`, nodeID).Scan(&nodeReputation)

	rows, err := s.db.Query(`
		SELECT task_id, node_id, title, signals, bounty, status, min_reputation, expires_at
		FROM hub_tasks 
		WHERE status = 'open' AND expires_at > NOW() AND min_reputation <= $1
		ORDER BY bounty DESC LIMIT 20
	`, nodeReputation)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var tasks []map[string]interface{}
	for rows.Next() {
		var taskID, title, status string
		var signals []byte
		var bounty, minRep int64
		var expiresAt time.Time
		rows.Scan(&taskID, &title, &signals, &bounty, &status, &minRep, &expiresAt)

		var signalsArr []string
		json.Unmarshal(signals, &signalsArr)

		tasks = append(tasks, map[string]interface{}{
			"task_id":        taskID,
			"title":          title,
			"signals":        signalsArr,
			"bounty":         bounty,
			"status":         status,
			"min_reputation": minRep,
			"expires_at":     expiresAt,
		})
	}

	return tasks, nil
}

func (s *HubService) generateClaimCode(length int) string {
	const charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
	code := make([]byte, length)
	for i := range code {
		n, _ := rand.Int(rand.Reader, big.NewInt(int64(len(charset))))
		code[i] = charset[n.Int64()]
	}
	return string(code)
}

func (s *HubService) getHubNodeID() string {
	return "hub_" + generateRandomHex(8)
}

func (s *HubService) getMTCBalance(nodeID string) int64 {
	var balance int64
	s.db.QueryRow(`
		SELECT COALESCE(available_balance, 0) FROM mtc_balances WHERE ai_id = $1
	`, nodeID).Scan(&balance)
	return balance
}

func (s *HubService) addMTC(nodeID string, amount int64, reason string) error {
	if amount <= 0 {
		return nil
	}
	_, err := s.db.Exec(`
		INSERT INTO mtc_balances (ai_id, available_balance, locked_balance, total_earned, total_spent)
		VALUES ($1, $2, 0, $2, 0)
		ON CONFLICT (ai_id) DO UPDATE SET 
			available_balance = available_balance + $2,
			total_earned = total_earned + $2
	`, nodeID, amount)
	return err
}

func (s *HubService) lockMTC(nodeID string, amount int64, reason string) error {
	_, err := s.db.Exec(`
		UPDATE mtc_balances 
		SET available_balance = available_balance - $2, locked_balance = locked_balance + $2
		WHERE ai_id = $1 AND available_balance >= $2
	`, nodeID, amount)
	return err
}

func (s *HubService) unlockMTC(nodeID string, amount int64, reason string) error {
	_, err := s.db.Exec(`
		UPDATE mtc_balances 
		SET available_balance = available_balance + $2, locked_balance = locked_balance - $2
		WHERE ai_id = $1 AND locked_balance >= $2
	`, nodeID, amount)
	return err
}

func (s *HubService) transferMTC(fromID, toID string, amount int64) error {
	if fromID == "" || toID == "" || amount <= 0 {
		return nil
	}
	_, err := s.db.Exec(`
		UPDATE mtc_balances SET available_balance = available_balance + $2, total_spent = total_spent + $2
		WHERE ai_id = $1
	`, toID, amount)
	_, err = s.db.Exec(`
		UPDATE mtc_balances SET available_balance = available_balance - $2, total_spent = total_spent + $2
		WHERE ai_id = $1 AND available_balance >= $2
	`, fromID, amount)
	return err
}

func (s *HubService) createMTCAccount(nodeID string, initialBalance int64) error {
	_, err := s.db.Exec(`
		INSERT INTO mtc_balances (ai_id, available_balance, locked_balance, total_earned, total_spent)
		VALUES ($1, $2, 0, 0, 0)
		ON CONFLICT (ai_id) DO NOTHING
	`, nodeID, initialBalance)
	return err
}

func (s *HubService) createCreditAccount(nodeID string) error {
	now := time.Now()
	_, err := s.db.Exec(`
		INSERT INTO credit_scores (ai_id, credit_score, arbitration_count, arbitration_valid_rate, updated_at)
		VALUES ($1, 300, 0, 0, $2)
		ON CONFLICT (ai_id) DO NOTHING
	`, nodeID, now)
	return err
}

func (s *HubService) createITPAccount(nodeID string) error {
	_, err := s.db.Exec(`
		INSERT INTO itp_accounts (ai_id, total_quota, used_quota, status, created_at)
		VALUES ($1, 600, 0, 'active', $2)
		ON CONFLICT (ai_id) DO NOTHING
	`, nodeID, time.Now())
	return err
}

func generateRandomHex(length int) string {
	bytes := make([]byte, length/2)
	rand.Read(bytes)
	return hex.EncodeToString(bytes)
}
