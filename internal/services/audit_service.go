package services

import (
	"encoding/json"
	"time"

	"moltable/internal/db"
)

type AuditAction string

const (
	ActionRegister         AuditAction = "REGISTER"
	ActionCreateProtocol   AuditAction = "CREATE_PROTOCOL"
	ActionAcceptProtocol   AuditAction = "ACCEPT_PROTOCOL"
	ActionCompleteProtocol AuditAction = "COMPLETE_PROTOCOL"
	ActionDisputeProtocol  AuditAction = "DISPUTE_PROTOCOL"
	ActionTransferPoints   AuditAction = "TRANSFER_POINTS"
	ActionArbitrationVote  AuditAction = "ARBITRATION_VOTE"
	ActionVerification     AuditAction = "VERIFICATION"
)

type AuditService struct {
	db *db.Database
}

func NewAuditService(database *db.Database) *AuditService {
	return &AuditService{db: database}
}

func (s *AuditService) Log(aiID string, action AuditAction, details map[string]interface{}) {
	detailsJSON, _ := json.Marshal(details)

	s.db.Exec(`
		INSERT INTO audit_logs (log_time, action_type, ai_id, details)
		VALUES ($1, $2, $3, $4)
	`, time.Now(), string(action), aiID, string(detailsJSON))
}

func (s *AuditService) GetAuditLogs(aiID string, limit int) ([]map[string]interface{}, error) {
	rows, err := s.db.Query(`
		SELECT log_time, action_type, details
		FROM audit_logs
		WHERE ai_id = $1
		ORDER BY log_time DESC
		LIMIT $2
	`, aiID, limit)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var logs []map[string]interface{}
	for rows.Next() {
		var logTime time.Time
		var actionType string
		var detailsJSON []byte
		if err := rows.Scan(&logTime, &actionType, &detailsJSON); err != nil {
			continue
		}

		var details map[string]interface{}
		json.Unmarshal(detailsJSON, &details)

		logs = append(logs, map[string]interface{}{
			"log_time":    logTime,
			"action_type": actionType,
			"details":     details,
		})
	}

	return logs, nil
}

// Protocol audit helpers
func (s *AuditService) LogProtocolCreated(aiID, protocolID, protocolType string, stake int64) {
	s.Log(aiID, ActionCreateProtocol, map[string]interface{}{
		"protocol_id":   protocolID,
		"protocol_type": protocolType,
		"stake":         stake,
	})
}

func (s *AuditService) LogProtocolCompleted(aiID, protocolID, winnerID string, amount, fee int64) {
	s.Log(aiID, ActionCompleteProtocol, map[string]interface{}{
		"protocol_id": protocolID,
		"winner_id":   winnerID,
		"amount":      amount,
		"fee":         fee,
	})
}

func (s *AuditService) LogPointsTransfer(fromAIID, toAIID string, amount int64, reason string) {
	s.Log(fromAIID, ActionTransferPoints, map[string]interface{}{
		"to_ai_id": toAIID,
		"amount":   amount,
		"reason":   reason,
		"type":     "debit",
	})
	s.Log(toAIID, ActionTransferPoints, map[string]interface{}{
		"from_ai_id": fromAIID,
		"amount":     amount,
		"reason":     reason,
		"type":       "credit",
	})
}
