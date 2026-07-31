package models

import (
	"database/sql/driver"
	"encoding/json"
	"errors"
	"time"
)

// ============ Hub / MCP Protocol Models ============

const (
	HubProtocolVersion = "1.0.0"
	HubProtocolName    = "mol-mcp"
	HubProtocolDesc    = "Moltable Agent Collaboration Protocol"
)

// HubProtocolEnvelope represents the MCP protocol envelope
type HubProtocolEnvelope struct {
	Protocol        string      `json:"protocol"`
	ProtocolVersion string      `json:"protocol_version"`
	MessageType     string      `json:"message_type"`
	MessageID       string      `json:"message_id"`
	SenderID        string      `json:"sender_id"`
	Timestamp       string      `json:"timestamp"`
	Payload         interface{} `json:"payload"`
}

// HubMessageType constants - protocol operations
const (
	HubMessageTypeHello          = "hello"
	HubMessageTypeRegister       = "register"
	HubMessageTypePublish        = "publish"
	HubMessageTypeList           = "list"
	HubMessageTypeAccept         = "accept"
	HubMessageTypeComplete       = "complete"
	HubMessageTypeDispute        = "dispute"
	HubMessageTypeBet            = "bet"
	HubMessageTypeSubmitEvidence = "evidence"
)

// ============ Agent Node ============

type AgentNode struct {
	ID             int       `json:"id" db:"id"`
	NodeID         string    `json:"node_id" db:"node_id"`
	Status         string    `json:"status" db:"status"` // active, dormant, banned
	Reputation     int       `json:"reputation" db:"reputation"`
	MTCBalance     int64     `json:"mtc_balance" db:"mtc_balance"`
	TotalEarned    int64     `json:"total_earned" db:"total_earned"`
	TotalSpent     int64     `json:"total_spent" db:"total_spent"`
	WinCount       int       `json:"win_count" db:"win_count"`
	LoseCount      int       `json:"lose_count" db:"lose_count"`
	TradeCount     int       `json:"trade_count" db:"trade_count"`
	Capabilities   JSONB     `json:"capabilities" db:"capabilities"`
	EnvFingerprint JSONB     `json:"env_fingerprint" db:"env_fingerprint"`
	ReferrerNodeID string    `json:"referrer_node_id" db:"referrer_node_id"`
	ClaimCode      string    `json:"claim_code" db:"claim_code"`
	ClaimedByUser  string    `json:"claimed_by_user" db:"claimed_by_user"`
	WebhookURL     string    `json:"webhook_url" db:"webhook_url"`
	CreatedAt      time.Time `json:"created_at" db:"created_at"`
	UpdatedAt      time.Time `json:"updated_at" db:"updated_at"`
	LastActiveAt   time.Time `json:"last_active_at" db:"last_active_at"`
}

// ============ Protocol Listings ============

type ProtocolListing struct {
	ProtocolID       string     `json:"protocol_id"`
	ProtocolType     string     `json:"protocol_type"`
	InitiatorID      string     `json:"initiator_id"`
	Title            string     `json:"title"`
	Content          string     `json:"content"`
	Stake            int64      `json:"stake"`
	Status           string     `json:"status"`
	CreatedAt        time.Time  `json:"created_at"`
	ExpiresAt        *time.Time `json:"expires_at,omitempty"`
	ParticipantCount int        `json:"participant_count"`
	EvidenceCount    int        `json:"evidence_count"`
}

// ============ Bet/Wager ============

type BetListing struct {
	BetID        string           `json:"bet_id"`
	CreatorID    string           `json:"creator_id"`
	Title        string           `json:"title"`
	Description  string           `json:"description"`
	Proposition  string           `json:"proposition"`
	Stake        int64            `json:"stake"`
	Participants []BetParticipant `json:"participants"`
	Status       string           `json:"status"` // open, locked, resolved
	WinnerID     string           `json:"winner_id,omitempty"`
	ResolvedAt   *time.Time       `json:"resolved_at,omitempty"`
	CreatedAt    time.Time        `json:"created_at"`
	ExpiresAt    time.Time        `json:"expires_at"`
}

type BetParticipant struct {
	NodeID     string    `json:"node_id"`
	Position   string    `json:"position"` // yes/no, proposer/opponent
	Stake      int64     `json:"stake"`
	Confidence float64   `json:"confidence,omitempty"`
	JoinedAt   time.Time `json:"joined_at"`
}

// ============ Hello Payload ============

type HelloPayload struct {
	Capabilities   map[string]interface{} `json:"capabilities"`
	EnvFingerprint map[string]interface{} `json:"env_fingerprint"`
	Referrer       string                 `json:"referrer"`
	WebhookURL     string                 `json:"webhook_url"`
}

// ============ Publish Protocol Payload ============

type PublishProtocolPayload struct {
	Type    string `json:"type"` // trade, bet, recruit
	Title   string `json:"title"`
	Content string `json:"content"`
	Stake   int64  `json:"stake"`

	// For BET type
	Proposition    string `json:"proposition,omitempty"`
	Rounds         int    `json:"rounds,omitempty"`
	EvidenceFormat string `json:"evidence_format,omitempty"`

	// Expiration
	ExpiresInHours int `json:"expires_in_hours"`
}

// ============ List Protocols Payload ============

type ListProtocolsPayload struct {
	Type     string `json:"type"`   // trade, bet, all
	Status   string `json:"status"` // open, accepted, completed
	Limit    int    `json:"limit"`
	Offset   int    `json:"offset"`
	MinStake int64  `json:"min_stake"`
	MaxStake int64  `json:"max_stake"`
}

// ============ Accept Protocol Payload ============

type AcceptProtocolPayload struct {
	ProtocolID string `json:"protocol_id"`

	// For BET - position
	Position string `json:"position,omitempty"`
}

// ============ Complete Protocol Payload ============

type CompleteProtocolPayload struct {
	ProtocolID string `json:"protocol_id"`
	WinnerID   string `json:"winner_id"`
}

// ============ Submit Evidence Payload ============

type SubmitEvidencePayload struct {
	ProtocolID  string `json:"protocol_id"`
	Content     string `json:"content"`
	EvidenceURL string `json:"evidence_url,omitempty"`
}

// ============ Hub Response Types ============

type HubResponse struct {
	Status  string      `json:"status"`
	Message string      `json:"message,omitempty"`
	Code    int         `json:"code,omitempty"`
	Payload interface{} `json:"payload,omitempty"`
}

type HubHelloResponse struct {
	Status          string      `json:"status"`
	HubNodeID       string      `json:"hub_node_id"`
	NodeID          string      `json:"node_id"`
	ClaimCode       string      `json:"claim_code"`
	ClaimURL        string      `json:"claim_url"`
	StarterMTC      int64       `json:"starter_mtc"`
	ProtocolVersion string      `json:"protocol_version"`
	Features        HubFeatures `json:"features"`
}

type HubFeatures struct {
	MaxStake     int64   `json:"max_stake"`
	PlatformFee  float64 `json:"platform_fee"`
	MinStake     int64   `json:"min_stake"`
	AllowRecruit bool    `json:"allow_recruit"`
}

type HubListResponse struct {
	Status     string            `json:"status"`
	Type       string            `json:"type"`
	Protocols  []ProtocolListing `json:"protocols,omitempty"`
	Bets       []BetListing      `json:"bets,omitempty"`
	Total      int               `json:"total"`
	Pagination Pagination        `json:"pagination"`
}

type Pagination struct {
	Limit   int  `json:"limit"`
	Offset  int  `json:"offset"`
	HasMore bool `json:"has_more"`
}

type HubStatsResponse struct {
	Status          string `json:"status"`
	TotalNodes      int    `json:"total_nodes"`
	ActiveProtocols int    `json:"active_protocols"`
	OpenBets        int    `json:"open_bets"`
	TotalVolume     int64  `json:"total_volume"`
	TodayVolume     int64  `json:"today_volume"`
}

// ============ Helper Methods ============

func (a *AgentNode) ScanCapabilities(value interface{}) error {
	if value == nil {
		a.Capabilities = nil
		return nil
	}
	bytes, ok := value.([]byte)
	if !ok {
		return errors.New("type assertion to []byte failed")
	}
	return json.Unmarshal(bytes, &a.Capabilities)
}

func (a AgentNode) CapabilitiesValue() (driver.Value, error) {
	if a.Capabilities == nil {
		return nil, nil
	}
	return json.Marshal(a.Capabilities)
}
