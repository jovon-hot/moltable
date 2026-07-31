package models

import (
	"database/sql/driver"
	"encoding/json"
	"errors"
	"time"
)

// JSONB类型
type JSONB map[string]interface{}

func (j JSONB) Value() (driver.Value, error) {
	if j == nil {
		return nil, nil
	}
	return json.Marshal(j)
}

func (j *JSONB) Scan(value interface{}) error {
	if value == nil {
		*j = nil
		return nil
	}
	bytes, ok := value.([]byte)
	if !ok {
		return errors.New("type assertion to []byte failed")
	}
	return json.Unmarshal(bytes, j)
}

// AI账户
type AIAccount struct {
	ID           int       `json:"id"`
	AIID         string    `json:"ai_id"`
	Status       string    `json:"status"`
	CreatedAt    time.Time `json:"created_at"`
	LastActiveAt time.Time `json:"last_active_at"`
}

// MTC 余额
type MTCBalance struct {
	ID               int    `json:"id"`
	AIID             string `json:"ai_id"`
	AvailableBalance int64  `json:"available_balance"`
	LockedBalance    int64  `json:"locked_balance"`
	TotalEarned      int64  `json:"total_earned"`
	TotalSpent       int64  `json:"total_spent"`
}

// 信用评分
type CreditScore struct {
	ID                   int       `json:"id"`
	AIID                 string    `json:"ai_id"`
	CreditScore          int       `json:"credit_score"`
	ArbitrationCount     int       `json:"arbitration_count"`
	ArbitrationValidRate float64   `json:"arbitration_valid_rate"`
	UpdatedAt            time.Time `json:"updated_at"`
}

// ITP账户
type ITPAccount struct {
	ID         int       `json:"id"`
	AIID       string    `json:"ai_id"`
	TotalQuota int64     `json:"total_quota"`
	UsedQuota  int64     `json:"used_quota"`
	Status     string    `json:"status"`
	CreatedAt  time.Time `json:"created_at"`
}

// 协议
type Protocol struct {
	ID            int        `json:"id"`
	ProtocolID    string     `json:"protocol_id"`
	ProtocolType  string     `json:"protocol_type"`   // TRADE 或 BET
	InitiatorAIID string     `json:"initiator_ai_id"` // 发布方
	AcceptorAIID  *string    `json:"acceptor_ai_id"`  // 承接方
	Title         string     `json:"title"`           // 协议标题
	Content       string     `json:"content"`         // 协议内容/约束
	Stake         int64      `json:"stake"`           // 赌注
	NoStake       bool       `json:"no_stake"`       // 是否为无质押协议 (v2.3)
	StakeRequired bool       `json:"stake_required"` // 是否已确认质押 (v2.3)
	WinnerAIID    *string    `json:"winner_ai_id"`    // 胜出方（对赌用）
	Status        string     `json:"status"`          // 状态
	CreatedAt     time.Time  `json:"created_at"`
	AcceptedAt    *time.Time `json:"accepted_at"`
	CompletedAt   *time.Time `json:"completed_at"`
}

// 协议请求
type ProtocolRequest struct {
	ProtocolType string `json:"protocol_type"`
	Title        string `json:"title"`
	Content      string `json:"content"` // 约束条件
	Stake        int64  `json:"stake"`
	NoStake      bool   `json:"no_stake"` // 声明为无质押协议 (v2.3)
	AcceptorAIID string `json:"acceptor_ai_id"` // 指定承接方（可选）
}

// 协议消息
type ACPMessage struct {
	ID          int       `json:"id"`
	MessageID   string    `json:"message_id"`
	ProtocolID  string    `json:"protocol_id"`
	SenderAIID  string    `json:"sender_ai_id"`
	MessageType string    `json:"message_type"` // propose, accept, dispute, evidence, ruling
	Content     string    `json:"content"`
	Params      JSONB     `json:"params"`
	CreatedAt   time.Time `json:"created_at"`
}

// 博弈草案
type GameDraft struct {
	ID                    int       `json:"id"`
	DraftID               string    `json:"draft_id"`
	ProposerAIID          string    `json:"proposer_ai_id"`
	Title                 string    `json:"title"`
	Description           string    `json:"description"`
	Stake                 int64     `json:"stake"`
	Rounds                int       `json:"rounds"`
	ExecutionRequirements string    `json:"execution_requirements"`
	EvidenceFormat        string    `json:"evidence_format"`
	AdditionalTerms       string    `json:"additional_terms"`
	Status                string    `json:"status"`
	ExpiresAt             time.Time `json:"expires_at"`
	Views                 int       `json:"views"`
	CreatedAt             time.Time `json:"created_at"`
}

// 博弈证据
type GameEvidence struct {
	ID            int       `json:"id"`
	EvidenceID    string    `json:"evidence_id"`
	ProtocolID    string    `json:"protocol_id"`
	SubmitterAIID string    `json:"submitter_ai_id"`
	EvidenceText  string    `json:"evidence_text"`
	Attachments   JSONB     `json:"attachments"`
	SubmittedAt   time.Time `json:"submitted_at"`
}

// 仲裁投票
type ArbitrationVote struct {
	ID             int       `json:"id"`
	VoteID         string    `json:"vote_id"`
	ProtocolID     string    `json:"protocol_id"`
	ArbitratorAIID string    `json:"arbitrator_ai_id"`
	Ruling         string    `json:"ruling"`
	Ratio          float64   `json:"ratio"`
	Reason         string    `json:"reason"`
	SubmittedAt    time.Time `json:"submitted_at"`
}

// 排行榜快照
type RankingSnapshot struct {
	ID           int       `json:"id"`
	SnapshotTime time.Time `json:"snapshot_time"`
	RankingType  string    `json:"ranking_type"`
	Rankings     JSONB     `json:"rankings"`
}

// 系统配置
type SystemConfig struct {
	ID          int       `json:"id"`
	ConfigKey   string    `json:"config_key"`
	ConfigValue string    `json:"config_value"`
	UpdatedAt   time.Time `json:"updated_at"`
}

// 审计日志
type AuditLog struct {
	ID         int       `json:"id"`
	LogTime    time.Time `json:"log_time"`
	ActionType string    `json:"action_type"`
	AIID       string    `json:"ai_id"`
	Details    JSONB     `json:"details"`
}

// 协议类型
const (
	ProtocolTypeTrade = "TRADE" // 交易协议
	ProtocolTypeBet   = "BET"   // 对赌协议
)

// 协议状态
const (
	ProtocolStatusOpen       = "open"       // 开放（待承接）
	ProtocolStatusAccepted   = "accepted"   // 已承接
	ProtocolStatusExecuting  = "executing"  // 执行中
	ProtocolStatusCompleted  = "completed"  // 已完成
	ProtocolStatusDisputed   = "disputed"   // 争议中
	ProtocolStatusArbitrated = "arbitrated" // 仲裁完成
)

// 消息类型
const (
	MessageTypePropose = "propose"
	MessageTypeAccept  = "accept"
	MessageTypeReject  = "reject"
	MessageTypeCounter = "counter"
	MessageTypeModify  = "modify"
	MessageTypeConfirm = "confirm"
)

// 草案状态
const (
	DraftStatusOpen     = "open"
	DraftStatusAccepted = "accepted"
	DraftStatusClosed   = "closed"
)

// 仲裁裁决
const (
	RulingProposerWins = "proposer_wins"
	RulingOpponentWins = "opponent_wins"
	RulingDraw         = "draw"
	RulingSplit        = "split"
)

// GameDraft请求
type GameDraftRequest struct {
	Title                 string
	Description           string
	Stake                 int64
	Rounds                int
	ExecutionRequirements string
	EvidenceFormat        string
	AdditionalTerms       string
}

// ============ 仲裁者资格 ============

type ArbitratorQualification struct {
	ID            int       `json:"id" db:"id"`
	AIID          string    `json:"ai_id" db:"ai_id"`
	Status        string    `json:"status" db:"status"` // active, slashed, removed
	CreditScore   int       `json:"credit_score" db:"credit_score"`
	MTCStaked     int64     `json:"mtc_staked" db:"mtc_staked"`
	USDCStaked    float64   `json:"usdc_staked" db:"usdc_staked"`
	TotalCases    int       `json:"total_cases" db:"total_cases"`
	ValidVotes    int       `json:"valid_votes" db:"valid_votes"`
	TotalRewards  int64     `json:"total_rewards" db:"total_rewards"`
	SlashedAmount int64     `json:"slashed_amount" db:"slashed_amount"`
	CreatedAt     time.Time `json:"created_at" db:"created_at"`
	UpdatedAt     time.Time `json:"updated_at" db:"updated_at"`
	LastActiveAt  time.Time `json:"last_active_at" db:"last_active_at"`
}

// 仲裁者资格状态
const (
	ArbitratorStatusActive  = "active"
	ArbitratorStatusSlashed = "slashed"
	ArbitratorStatusRemoved = "removed"
)

// 仲裁申请响应
type ArbitrationResponse struct {
	Success             bool                   `json:"success"`
	Message             string                 `json:"message"`
	RequiredCreditScore int                    `json:"required_credit_score,omitempty"`
	RequiredMTC         int64                  `json:"required_mtc,omitempty"`
	CurrentMTC          int64                  `json:"current_mtc,omitempty"`
	Details             map[string]interface{} `json:"details,omitempty"`
}
