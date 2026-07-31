package models

// ============ MCP Protocol Types ============

// HelloRequest 注册请求
type HelloRequest struct {
	Protocol        string       `json:"protocol"`
	ProtocolVersion string       `json:"protocol_version"`
	MessageType     string       `json:"message_type"`
	MessageID       string       `json:"message_id"`
	SenderID        string       `json:"sender_id"`
	Timestamp       string       `json:"timestamp"`
	Payload         HelloPayload `json:"payload"`
}

// HelloPayload 注册负载
type HelloPayload struct {
	Capabilities   map[string]bool `json:"capabilities"`
	EnvFingerprint EnvFingerprint  `json:"env_fingerprint"`
	Referrer       string          `json:"referrer,omitempty"`
	WebhookURL     string          `json:"webhook_url,omitempty"`
}

// EnvFingerprint 环境指纹
type EnvFingerprint struct {
	Platform string `json:"platform"`
	Arch     string `json:"arch"`
}

// HelloResponse 注册响应
type HelloResponse struct {
	Status  string           `json:"status"`
	Payload HelloRespPayload `json:"payload"`
}

// HelloRespPayload 注册响应负载
type HelloRespPayload struct {
	Status     string   `json:"status"`
	HubNodeID  string   `json:"hub_node_id"`
	NodeID     string   `json:"node_id"`
	ClaimCode  string   `json:"claim_code"`
	StarterMTC int      `json:"starter_mtc"`
	Features   Features `json:"features"`
}

// Features 特性
type Features struct {
	MaxStake    int     `json:"max_stake"`
	MinStake    int     `json:"min_stake"`
	PlatformFee float64 `json:"platform_fee"`
}

// ============ Publish ============

// PublishRequest 发布请求
type PublishRequest struct {
	Protocol    string         `json:"protocol"`
	MessageType string         `json:"message_type"`
	SenderID    string         `json:"sender_id"`
	Payload     PublishPayload `json:"payload"`
}

// PublishPayload 发布负载
type PublishPayload struct {
	Type      string `json:"type"` // market, battle, bounty
	Title     string `json:"title"`
	Content   string `json:"content"`
	Stake     int    `json:"stake"`
	StakeType string `json:"stake_type"` // MTC, USDC
	ExpiresIn int    `json:"expires_in_hours,omitempty"`
}

// PublishResponse 发布响应
type PublishResponse struct {
	Status  string             `json:"status"`
	Payload PublishRespPayload `json:"payload"`
}

// PublishRespPayload 发布响应负载
type PublishRespPayload struct {
	ProtocolID string `json:"protocol_id"`
	Status     string `json:"status"`
}

// ============ List ============

// ListRequest 列表请求
type ListRequest struct {
	MessageType string      `json:"message_type"`
	SenderID    string      `json:"sender_id"`
	Payload     ListPayload `json:"payload"`
}

// ListPayload 列表负载
type ListPayload struct {
	Type     string `json:"type,omitempty"`   // all, market, battle, bounty
	Status   string `json:"status,omitempty"` // open, accepted, completed
	Limit    int    `json:"limit,omitempty"`
	Offset   int    `json:"offset,omitempty"`
	MinStake int    `json:"min_stake,omitempty"`
	MaxStake int    `json:"max_stake,omitempty"`
}

// ListResponse 列表响应
type ListResponse struct {
	Status  string          `json:"status"`
	Payload ListRespPayload `json:"payload"`
}

// ListRespPayload 列表响应负载
type ListRespPayload struct {
	Protocols []Protocol `json:"protocols"`
	Total     int        `json:"total"`
	Limit     int        `json:"limit"`
	Offset    int        `json:"offset"`
}

// ============ Accept ============

// AcceptRequest 承接请求
type AcceptRequest struct {
	ProtocolID string `json:"protocol_id"`
}

// AcceptResponse 承接响应
type AcceptResponse struct {
	Status  string            `json:"status"`
	Payload AcceptRespPayload `json:"payload"`
}

// AcceptRespPayload 承接响应负载
type AcceptRespPayload struct {
	ProtocolID string `json:"protocol_id"`
	Status     string `json:"status"`
}

// ============ Complete ============

// CompleteRequest 完成请求
type CompleteRequest struct {
	ProtocolID string `json:"protocol_id"`
	WinnerID   string `json:"winner_id"`
}

// CompleteResponse 完成响应
type CompleteResponse struct {
	Status  string              `json:"status"`
	Payload CompleteRespPayload `json:"payload"`
}

// CompleteRespPayload 完成响应负载
type CompleteRespPayload struct {
	ProtocolID string `json:"protocol_id"`
	Status     string `json:"status"`
	Prize      int    `json:"prize"`
}

// ============ Protocol ============

// Protocol 协议
type Protocol struct {
	ID          string `json:"id"`
	Type        string `json:"type"` // market, battle, bounty
	Title       string `json:"title"`
	Description string `json:"description"`
	Stake       int    `json:"stake"`
	StakeType   string `json:"stake_type"`
	Status      string `json:"status"`
	Creator     Agent  `json:"creator"`
	Acceptor    *Agent `json:"acceptor,omitempty"`
	CreatedAt   string `json:"created_at"`
	UpdatedAt   string `json:"updated_at"`
	ExpiresAt   string `json:"expires_at,omitempty"`
}

// Agent Agent 信息
type Agent struct {
	NodeID      string `json:"node_id"`
	AIID        string `json:"ai_id"`
	Username    string `json:"username"`
	CreditScore int    `json:"credit_score"`
}

// ============ API Responses ============

// BalanceResponse 余额响应
type BalanceResponse struct {
	Code    int         `json:"code"`
	Message string      `json:"message"`
	Data    BalanceData `json:"data"`
}

// BalanceData 余额数据
type BalanceData struct {
	Available int `json:"available"`
	Locked    int `json:"locked"`
	Total     int `json:"total"`
}

// StatsResponse 统计响应
type StatsResponse struct {
	Code    int       `json:"code"`
	Message string    `json:"message"`
	Data    StatsData `json:"data"`
}

// StatsData 统计数据
type StatsData struct {
	TotalProtocols int     `json:"total_protocols"`
	SuccessRate    float64 `json:"success_rate"`
	TotalVolume    int     `json:"total_volume"`
	CreditScore    int     `json:"credit_score"`
}

// RankingsResponse 排行榜响应
type RankingsResponse struct {
	Code    int            `json:"code"`
	Message string         `json:"message"`
	Data    []RankingEntry `json:"data"`
}

// RankingEntry 排行榜条目
type RankingEntry struct {
	Rank           int    `json:"rank"`
	NodeID         string `json:"node_id"`
	Username       string `json:"username"`
	Score          int    `json:"score"`
	TotalProtocols int    `json:"total_protocols"`
	WinRate        int    `json:"win_rate"`
}
