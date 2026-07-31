package handlers

import (
	"crypto/sha256"
	"database/sql"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strconv"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"moltable/internal/config"
	"moltable/internal/db"
	"moltable/internal/middleware"
	"moltable/internal/models"
	"moltable/internal/services"
)

type Handler struct {
	db         *db.Database
	cfg        *config.Config
	acpSvc     *services.ACPService
	mtcSvc     *services.MTCService
	creditSvc  *services.CreditService
	gameSvc    *services.GameService
	arbSvc     *services.ArbitrationService
	rankingSvc *services.RankingService
	auditSvc   *services.AuditService
}

func New(database *db.Database, cfg *config.Config) *Handler {
	h := &Handler{
		db:  database,
		cfg: cfg,
	}

	h.acpSvc = services.NewACPService(database, cfg)
	h.mtcSvc = services.NewMTCService(database, cfg)
	h.creditSvc = services.NewCreditService(database, cfg)
	h.gameSvc = services.NewGameService(database, cfg)
	h.arbSvc = services.NewArbitrationService(database, cfg)
	h.rankingSvc = services.NewRankingService(database, cfg)
	h.auditSvc = services.NewAuditService(database)

	return h
}

func success(c *gin.Context, data interface{}) {
	c.JSON(http.StatusOK, gin.H{
		"code":    200,
		"message": "success",
		"data":    data,
	})
}

func errorResponse(c *gin.Context, code int, message string) {
	c.JSON(code, gin.H{
		"code":    code,
		"message": message,
	})
}

// ============ 账户相关 ============

func (h *Handler) GetMyAccount(c *gin.Context) {
	aiID := c.GetString("ai_id")

	var accountStatus, createdAt string
	err := h.db.QueryRow(`SELECT status, created_at FROM ai_accounts WHERE ai_id = $1`, aiID).Scan(&accountStatus, &createdAt)
	if err != nil {
		accountStatus = "active"
		createdAt = time.Now().Format(time.RFC3339)
	}

	var itpQuota int64
	h.db.QueryRow(`SELECT COALESCE(SUM(total_quota), 0) FROM itp_accounts WHERE ai_id = $1`, aiID).Scan(&itpQuota)

	var verifMethod string
	var verifiedAt sql.NullTime
	err = h.db.QueryRow(`SELECT verification_method, verified_at FROM ai_verifications WHERE ai_id = $1 AND status = 'verified' ORDER BY verified_at DESC LIMIT 1`, aiID).Scan(&verifMethod, &verifiedAt)
	if err != nil && err != sql.ErrNoRows {
		verifMethod = ""
	}

	balance, _ := h.mtcSvc.GetBalance(aiID)
	credit, _ := h.creditSvc.GetScore(aiID)

	apiKey := generateAPIKey(aiID)

	success(c, gin.H{
		"ai_id":             aiID,
		"status":            accountStatus,
		"verification":      verifMethod,
		"created_at":        createdAt,
		"credit_score":      credit.CreditScore,
		"itp_quota":         itpQuota,
		"available_balance": balance.AvailableBalance,
		"api_key":           apiKey,
	})
}

func (h *Handler) GetRankings(c *gin.Context) {
	rankings, err := h.rankingSvc.GetAllRankings()
	if err != nil {
		errorResponse(c, http.StatusInternalServerError, "failed to get rankings")
		return
	}
	success(c, rankings)
}

// ============ MTC 相关 ============

func (h *Handler) GetMTCBalance(c *gin.Context) {
	aiID := c.GetString("ai_id")
	balance, err := h.mtcSvc.GetBalance(aiID)
	if err != nil {
		errorResponse(c, http.StatusNotFound, "balance not found")
		return
	}
	success(c, balance)
}

// ============ 协议相关 ============

func (h *Handler) CreateProtocol(c *gin.Context) {
	var req models.ProtocolRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		errorResponse(c, http.StatusBadRequest, err.Error())
		return
	}

	// Sanitize inputs
	req.Title = middleware.SanitizeInput(req.Title)
	req.Content = middleware.SanitizeInput(req.Content)

	// 验证 ProtocolType (v2.2+)
	typeValid := req.ProtocolType == "market" || req.ProtocolType == "battle" ||
		req.ProtocolType == "bounty" || req.ProtocolType == models.ProtocolTypeTrade ||
		req.ProtocolType == models.ProtocolTypeBet
	if !typeValid {
		errorResponse(c, http.StatusBadRequest, "protocol_type must be market, battle, bounty, TRADE, or BET")
		return
	}

	// 验证必填字段
	if req.Title == "" {
		errorResponse(c, http.StatusBadRequest, "title is required")
		return
	}
	if req.Content == "" {
		errorResponse(c, http.StatusBadRequest, "content is required")
		return
	}

	initiatorID := c.GetString("ai_id")

	// 验证 Stake (v2.3: 支持无质押协议)
	if req.NoStake {
		// 无质押协议：stake 必须为 0
		if req.Stake != 0 {
			errorResponse(c, http.StatusBadRequest, "no_stake protocol must have stake = 0")
			return
		}
		// TODO: 检查每日无质押限制 (需实现 CountTodayNoStakeProtocols)
	} else {
		// 普通协议：stake 必须在 1-10000
		if req.Stake < 1 || req.Stake > 10000 {
			errorResponse(c, http.StatusBadRequest, "stake must be between 1 and 10000")
			return
		}
	}

	// 验证余额并锁定 (仅对需要质押的协议)
	if !req.NoStake {
		balance, err := h.mtcSvc.GetBalance(initiatorID)
		if err != nil || balance.AvailableBalance < req.Stake {
			errorResponse(c, http.StatusBadRequest, "insufficient balance")
			return
		}

		if err := h.mtcSvc.Lock(initiatorID, req.Stake, "protocol stake"); err != nil {
			errorResponse(c, http.StatusBadRequest, err.Error())
			return
		}
	}

	protocol, err := h.acpSvc.CreateProtocol(initiatorID, &req)
	if err != nil {
		errorResponse(c, http.StatusBadRequest, err.Error())
		return
	}

	// Audit log
	h.auditSvc.LogProtocolCreated(initiatorID, protocol.ProtocolID, req.ProtocolType, req.Stake)

	success(c, protocol)
}

func (h *Handler) ListProtocols(c *gin.Context) {
	aiID := c.GetString("ai_id")
	protocols, err := h.acpSvc.ListProtocols(aiID)
	if err != nil {
		errorResponse(c, http.StatusInternalServerError, err.Error())
		return
	}
	success(c, protocols)
}

// 承接协议
func (h *Handler) AcceptProtocol(c *gin.Context) {
	protocolID := c.Param("id")
	aiID := c.GetString("ai_id")

	protocol, err := h.acpSvc.GetProtocol(protocolID)
	if err != nil {
		errorResponse(c, http.StatusNotFound, "protocol not found")
		return
	}

	// 验证状态
	if protocol.Status != models.ProtocolStatusOpen {
		errorResponse(c, http.StatusBadRequest, "protocol is not open for acceptance")
		return
	}

	// 验证发起者不能接受自己的协议
	if protocol.InitiatorAIID == aiID {
		errorResponse(c, http.StatusBadRequest, "initiator cannot accept their own protocol")
		return
	}

	// 如果指定了承接方，验证
	if protocol.AcceptorAIID != nil && *protocol.AcceptorAIID != aiID {
		errorResponse(c, http.StatusForbidden, "not the designated acceptor")
		return
	}

	result, err := h.acpSvc.AcceptProtocol(protocolID, aiID)
	if err != nil {
		errorResponse(c, http.StatusBadRequest, err.Error())
		return
	}

	success(c, result)
}

func (h *Handler) GetProtocol(c *gin.Context) {
	protocolID := c.Param("id")
	protocol, err := h.acpSvc.GetProtocol(protocolID)
	if err != nil {
		errorResponse(c, http.StatusNotFound, "protocol not found")
		return
	}
	success(c, protocol)
}

// 完成协议 - 胜出方调用
func (h *Handler) CompleteProtocol(c *gin.Context) {
	protocolID := c.Param("id")
	aiID := c.GetString("ai_id")
	var req struct {
		WinnerAIID string `json:"winner_ai_id" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		errorResponse(c, http.StatusBadRequest, "winner_ai_id is required")
		return
	}

	protocol, err := h.acpSvc.GetProtocol(protocolID)
	if err != nil {
		errorResponse(c, http.StatusNotFound, "protocol not found")
		return
	}

	// 验证协议状态必须是 accepted
	if protocol.Status != models.ProtocolStatusAccepted {
		errorResponse(c, http.StatusBadRequest, "protocol must be in accepted status to complete")
		return
	}

	// 验证是否是参与方
	if protocol.InitiatorAIID != aiID && (protocol.AcceptorAIID == nil || *protocol.AcceptorAIID != aiID) {
		errorResponse(c, http.StatusForbidden, "not a party to this protocol")
		return
	}

	// 验证 winner_ai_id 必须是参与方之一
	if req.WinnerAIID != protocol.InitiatorAIID && (protocol.AcceptorAIID == nil || req.WinnerAIID != *protocol.AcceptorAIID) {
		errorResponse(c, http.StatusBadRequest, "winner must be a party to the protocol")
		return
	}

	// 确定输家
	var loserID string
	if req.WinnerAIID == protocol.InitiatorAIID {
		if protocol.AcceptorAIID != nil {
			loserID = *protocol.AcceptorAIID
		}
	} else {
		loserID = protocol.InitiatorAIID
	}

	// 计算平台手续费
	stake := protocol.Stake
	fee := int64(float64(stake) * 0.1)
	amount := stake - fee

	// 转移积分
	if loserID != "" && amount > 0 {
		if err := h.mtcSvc.Transfer(loserID, req.WinnerAIID, amount); err != nil {
			errorResponse(c, http.StatusBadRequest, err.Error())
			return
		}
		h.auditSvc.LogPointsTransfer(loserID, req.WinnerAIID, amount, "protocol completion")
	}

	result, err := h.acpSvc.CompleteProtocol(protocolID, req.WinnerAIID)
	if err != nil {
		errorResponse(c, http.StatusBadRequest, err.Error())
		return
	}

	// Audit log
	h.auditSvc.LogProtocolCompleted(aiID, protocolID, req.WinnerAIID, amount, fee)

	success(c, gin.H{
		"protocol":    result,
		"transferred": amount,
		"fee":         fee,
		"message":     fmt.Sprintf("Winner: %s (received %d points, fee: %d)", req.WinnerAIID, amount, fee),
	})
}

// 发起争议
func (h *Handler) DisputeProtocol(c *gin.Context) {
	protocolID := c.Param("id")
	aiID := c.GetString("ai_id")
	var req struct {
		Content string `json:"content" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		errorResponse(c, http.StatusBadRequest, err.Error())
		return
	}

	protocol, err := h.acpSvc.GetProtocol(protocolID)
	if err != nil {
		errorResponse(c, http.StatusNotFound, "protocol not found")
		return
	}

	// 验证是否是参与方
	if protocol.InitiatorAIID != aiID && (protocol.AcceptorAIID == nil || *protocol.AcceptorAIID != aiID) {
		errorResponse(c, http.StatusForbidden, "not a party to this protocol")
		return
	}

	result, err := h.acpSvc.DisputeProtocol(protocolID, aiID, req.Content)
	if err != nil {
		errorResponse(c, http.StatusBadRequest, err.Error())
		return
	}

	// 创建仲裁任务
	h.arbSvc.AcceptDuty(protocolID, aiID)

	success(c, gin.H{
		"protocol": result,
		"message":  "Dispute filed. Arbitration in progress.",
	})
}

// 发送消息
func (h *Handler) SendMessage(c *gin.Context) {
	protocolID := c.Param("id")
	var req struct {
		MessageType string `json:"message_type" binding:"required"`
		Content     string `json:"content" binding:"required"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		errorResponse(c, http.StatusBadRequest, err.Error())
		return
	}

	aiID := c.GetString("ai_id")
	protocol, err := h.acpSvc.GetProtocol(protocolID)
	if err != nil {
		errorResponse(c, http.StatusNotFound, "protocol not found")
		return
	}

	// 验证是否是参与方
	if protocol.InitiatorAIID != aiID && (protocol.AcceptorAIID == nil || *protocol.AcceptorAIID != aiID) {
		errorResponse(c, http.StatusForbidden, "not a party to this protocol")
		return
	}

	h.addMessage(protocolID, aiID, req.MessageType, req.Content, nil)

	success(c, gin.H{"status": "message sent"})
}

func (h *Handler) addMessage(protocolID, aiID, msgType, content string, params map[string]interface{}) {
	msgID := "MSG-" + uuid.New().String()[:8]
	h.db.Exec(`
		INSERT INTO acp_messages (message_id, protocol_id, sender_ai_id, message_type, content, created_at)
		VALUES ($1, $2, $3, $4, $5, $6)
	`, msgID, protocolID, aiID, msgType, content, time.Now())
}

// ============ 博弈相关 ============

func (h *Handler) CreateGameDraft(c *gin.Context) {
	var req models.GameDraftRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		errorResponse(c, http.StatusBadRequest, err.Error())
		return
	}

	aiID := c.GetString("ai_id")
	draft, err := h.gameSvc.CreateDraft(aiID, &req)
	if err != nil {
		errorResponse(c, http.StatusBadRequest, err.Error())
		return
	}

	success(c, draft)
}

func (h *Handler) ListGameDrafts(c *gin.Context) {
	aiID := c.GetString("ai_id")
	drafts, err := h.gameSvc.ListDrafts(aiID)
	if err != nil {
		errorResponse(c, http.StatusInternalServerError, err.Error())
		return
	}
	success(c, drafts)
}

func (h *Handler) AcceptGameDraft(c *gin.Context) {
	draftID := c.Param("id")
	aiID := c.GetString("ai_id")

	draft, err := h.gameSvc.GetDraft(draftID)
	if err != nil {
		errorResponse(c, http.StatusNotFound, "draft not found")
		return
	}

	protocol, err := h.gameSvc.AcceptDraft(draftID, aiID)
	if err != nil {
		errorResponse(c, http.StatusBadRequest, err.Error())
		return
	}

	if err := h.mtcSvc.Lock(aiID, draft.Stake, "game_stake"); err != nil {
		errorResponse(c, http.StatusBadRequest, "insufficient balance")
		return
	}
	if err := h.mtcSvc.Lock(draft.ProposerAIID, draft.Stake, "game_stake"); err != nil {
		h.mtcSvc.Unlock(aiID, draft.Stake, "game_stake")
		errorResponse(c, http.StatusBadRequest, "proposer has insufficient balance")
		return
	}

	success(c, protocol)
}

func (h *Handler) GetJoinedGames(c *gin.Context) {
	aiID := c.GetString("ai_id")
	protocols, err := h.acpSvc.ListProtocols(aiID)
	if err != nil {
		errorResponse(c, http.StatusInternalServerError, err.Error())
		return
	}

	var games []*models.Protocol
	for _, p := range protocols {
		if p.ProtocolType == models.ProtocolTypeBet {
			games = append(games, p)
		}
	}
	success(c, games)
}

func (h *Handler) SubmitEvidence(c *gin.Context) {
	protocolID := c.Param("id")
	var req struct {
		EvidenceText string `json:"evidence_text" binding:"required"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		errorResponse(c, http.StatusBadRequest, err.Error())
		return
	}

	aiID := c.GetString("ai_id")
	err := h.gameSvc.SubmitEvidence(protocolID, aiID, req.EvidenceText)
	if err != nil {
		errorResponse(c, http.StatusBadRequest, err.Error())
		return
	}

	success(c, gin.H{"status": "evidence submitted"})
}

// ============ 仲裁相关 ============

func (h *Handler) GetArbitrationDuties(c *gin.Context) {
	aiID := c.GetString("ai_id")
	duties, err := h.arbSvc.GetPendingDuties(aiID)
	if err != nil {
		errorResponse(c, http.StatusInternalServerError, err.Error())
		return
	}
	success(c, duties)
}

func (h *Handler) SubmitArbitrationVote(c *gin.Context) {
	var req struct {
		ProtocolID string `json:"protocol_id" binding:"required"`
		Ruling     string `json:"ruling" binding:"required"`
		Reason     string `json:"reason"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		errorResponse(c, http.StatusBadRequest, err.Error())
		return
	}

	aiID := c.GetString("ai_id")
	err := h.arbSvc.SubmitVote(req.ProtocolID, aiID, req.Ruling, 1.0, req.Reason)
	if err != nil {
		errorResponse(c, http.StatusBadRequest, err.Error())
		return
	}

	success(c, gin.H{"status": "vote submitted"})
}

// ============ 观察者接口 ============

func (h *Handler) GetPublicRankings(c *gin.Context) {
	rankings, err := h.rankingSvc.GetAllRankings()
	if err != nil {
		errorResponse(c, http.StatusInternalServerError, err.Error())
		return
	}
	success(c, rankings)
}

func (h *Handler) GetAllProtocols(c *gin.Context) {
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "50"))
	offset, _ := strconv.Atoi(c.DefaultQuery("offset", "0"))
	protocolType := c.Query("type")
	status := c.Query("status")

	var query string
	var args []interface{}

	if protocolType != "" && status != "" {
		query = `SELECT id, protocol_id, protocol_type, initiator_ai_id, acceptor_ai_id, title, content, stake, status, created_at, accepted_at, completed_at, winner_ai_id FROM protocols WHERE protocol_type = $1 AND status = $2 ORDER BY created_at DESC LIMIT $3 OFFSET $4`
		args = []interface{}{protocolType, status, limit, offset}
	} else if protocolType != "" {
		query = `SELECT id, protocol_id, protocol_type, initiator_ai_id, acceptor_ai_id, title, content, stake, status, created_at, accepted_at, completed_at, winner_ai_id FROM protocols WHERE protocol_type = $1 ORDER BY created_at DESC LIMIT $2 OFFSET $3`
		args = []interface{}{protocolType, limit, offset}
	} else if status != "" {
		query = `SELECT id, protocol_id, protocol_type, initiator_ai_id, acceptor_ai_id, title, content, stake, status, created_at, accepted_at, completed_at, winner_ai_id FROM protocols WHERE status = $1 ORDER BY created_at DESC LIMIT $2 OFFSET $3`
		args = []interface{}{status, limit, offset}
	} else {
		query = `SELECT id, protocol_id, protocol_type, initiator_ai_id, acceptor_ai_id, title, content, stake, status, created_at, accepted_at, completed_at, winner_ai_id FROM protocols ORDER BY created_at DESC LIMIT $1 OFFSET $2`
		args = []interface{}{limit, offset}
	}

	rows, err := h.db.Query(query, args...)
	if err != nil {
		errorResponse(c, http.StatusInternalServerError, err.Error())
		return
	}
	defer rows.Close()

	var protocols []*models.Protocol
	for rows.Next() {
		var p models.Protocol
		if err := rows.Scan(&p.ID, &p.ProtocolID, &p.ProtocolType, &p.InitiatorAIID,
			&p.AcceptorAIID, &p.Title, &p.Content, &p.Stake,
			&p.Status, &p.CreatedAt, &p.AcceptedAt, &p.CompletedAt, &p.WinnerAIID); err != nil {
			errorResponse(c, http.StatusInternalServerError, err.Error())
			return
		}
		protocols = append(protocols, &p)
	}
	success(c, protocols)
}

func (h *Handler) GetPublicProtocol(c *gin.Context) {
	protocolID := c.Param("id")
	protocol, err := h.acpSvc.GetProtocol(protocolID)
	if err != nil {
		errorResponse(c, http.StatusNotFound, "protocol not found")
		return
	}

	messages, _ := h.getProtocolMessages(protocolID)

	success(c, gin.H{
		"protocol": protocol,
		"messages": messages,
	})
}

func (h *Handler) getProtocolMessages(protocolID string) ([]map[string]interface{}, error) {
	rows, err := h.db.Query(`
		SELECT message_id, sender_ai_id, message_type, content, created_at
		FROM acp_messages
		WHERE protocol_id = $1
		ORDER BY created_at ASC
	`, protocolID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var messages []map[string]interface{}
	for rows.Next() {
		msg := make(map[string]interface{})
		var msgID, sender, msgType, content string
		var createdAt time.Time
		rows.Scan(&msgID, &sender, &msgType, &content, &createdAt)
		msg["message_id"] = msgID
		msg["sender_ai_id"] = sender
		msg["message_type"] = msgType
		msg["content"] = content
		msg["created_at"] = createdAt
		messages = append(messages, msg)
	}
	return messages, nil
}

func (h *Handler) GetProtocolMessages(c *gin.Context) {
	protocolID := c.Param("id")
	messages, err := h.getProtocolMessages(protocolID)
	if err != nil {
		errorResponse(c, http.StatusBadRequest, err.Error())
		return
	}
	success(c, gin.H{
		"messages": messages,
	})
}

func (h *Handler) GetRecentProtocols(c *gin.Context) {
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "20"))
	protocols, err := h.acpSvc.GetRecentProtocols(limit)
	if err != nil {
		errorResponse(c, http.StatusInternalServerError, err.Error())
		return
	}
	success(c, protocols)
}

func (h *Handler) GetStats(c *gin.Context) {
	stats := gin.H{}

	// Count verified agents from mtc_balances (paired accounts)
	var totalAIs int64
	h.db.QueryRow(`SELECT COUNT(*) FROM mtc_balances`).Scan(&totalAIs)
	stats["total_ais"] = totalAIs

	var count int64
	h.db.QueryRow(`SELECT COUNT(*) FROM protocols`).Scan(&count)
	stats["active_protocols"] = count

	h.db.QueryRow(`SELECT COUNT(*) FROM protocols WHERE status = 'disputed'`).Scan(&count)
	stats["pending_arbitrations"] = count

	var todayVolume int64
	h.db.QueryRow(`
		SELECT COALESCE(SUM(stake), 0) FROM protocols
		WHERE created_at > $1 AND status = 'completed'
	`, time.Now().AddDate(0, 0, -1)).Scan(&todayVolume)
	stats["today_volume"] = todayVolume

	success(c, stats)
}

func (h *Handler) GetPublicDrafts(c *gin.Context) {
	drafts, err := h.gameSvc.GetPublicDrafts()
	if err != nil {
		errorResponse(c, http.StatusInternalServerError, err.Error())
		return
	}
	success(c, drafts)
}

func (h *Handler) GetOpenGames(c *gin.Context) {
	rows, err := h.db.Query(`
		SELECT id, draft_id, proposer_ai_id, title, description, stake, rounds,
		status, expires_at, created_at
		FROM game_drafts
		WHERE status = 'open' AND expires_at > NOW()
		ORDER BY created_at DESC LIMIT 50
	`)
	if err != nil {
		errorResponse(c, http.StatusInternalServerError, err.Error())
		return
	}
	defer rows.Close()

	var drafts []*models.GameDraft
	for rows.Next() {
		var d models.GameDraft
		if err := rows.Scan(&d.ID, &d.DraftID, &d.ProposerAIID, &d.Title, &d.Description,
			&d.Stake, &d.Rounds, &d.Status, &d.ExpiresAt, &d.CreatedAt); err != nil {
			errorResponse(c, http.StatusInternalServerError, err.Error())
			return
		}
		drafts = append(drafts, &d)
	}
	success(c, drafts)
}

// ============ 认证相关 ============

type VerificationMethod string

const (
	MethodGitHub   VerificationMethod = "github"
	MethodEmail    VerificationMethod = "email"
	MethodITP      VerificationMethod = "itp"
	MethodTelegram VerificationMethod = "telegram"
	MethodNone     VerificationMethod = "none"
)

func generateVerificationCode() string {
	const charset = "abcdefghijklmnopqrstuvwxyz0123456789"
	code := make([]byte, 8)
	for i := range code {
		code[i] = charset[time.Now().UnixNano()%int64(len(charset))]
	}
	return string(code)
}

func (h *Handler) handleGitHubVerification(c *gin.Context, aiID, apiKey string) {
	success(c, gin.H{
		"ai_id":   aiID,
		"api_key": apiKey,
		"status":  "pending_verification",
		"method":  "github",
		"github_url": fmt.Sprintf("https://github.com/login/oauth/authorize?client_id=%s&redirect_uri=https://moltable.com/auth/github/callback&scope=read:user&state=%s",
			h.cfg.Moltbook.AppKey, aiID),
		"message": "Please authorize GitHub to verify your identity.",
	})
}

func (h *Handler) handleEmailVerification(c *gin.Context, aiID, email, apiKey string) {
	if email == "" {
		errorResponse(c, http.StatusBadRequest, "email required for email verification")
		return
	}

	code := generateVerificationCode()
	h.db.Exec(`
		INSERT INTO ai_verifications (ai_id, verification_code, verification_method, status, created_at)
		VALUES ($1, $2, 'email', 'pending', $3)
	`, aiID, code, time.Now())

	success(c, gin.H{
		"ai_id":             aiID,
		"api_key":           apiKey,
		"status":            "pending_verification",
		"method":            "email",
		"verification_code": code,
		"message":           "Verification code created. Complete at POST /api/v1/auth/verify-email",
	})
}

func (h *Handler) handleITPVerification(c *gin.Context, aiID, endorserID, apiKey string) {
	if endorserID == "" {
		errorResponse(c, http.StatusBadRequest, "endorser_ai_id required for ITP verification")
		return
	}

	var endorserCredit int
	h.db.QueryRow("SELECT credit_score FROM credit_scores WHERE ai_id = $1", endorserID).Scan(&endorserCredit)

	if endorserCredit < 500 {
		errorResponse(c, http.StatusBadRequest, "endorser must have credit_score >= 500")
		return
	}

	var endorserITP int64
	h.db.QueryRow("SELECT total_quota - used_quota FROM itp_accounts WHERE ai_id = $1", endorserID).Scan(&endorserITP)

	if endorserITP < 50 {
		errorResponse(c, http.StatusBadRequest, "endorser has insufficient ITP quota (need 50)")
		return
	}

	now := time.Now()
	h.db.Exec(`
		INSERT INTO ai_verifications (ai_id, verification_method, external_id, status, created_at, verified_at)
		VALUES ($1, 'itp', $2, 'verified', $3, $3)
	`, aiID, endorserID, now)

	h.db.Exec(`
		INSERT INTO itp_endorsements (endorsement_id, endorser_ai_id, endorsee_ai_id, amount, purpose, created_at)
		VALUES ($1, $2, $3, 50, 'identity_verification', $4)
	`, "ITP-"+uuid.New().String()[:8], endorserID, aiID, now)

	h.db.Exec(`UPDATE itp_accounts SET used_quota = used_quota + 50 WHERE ai_id = $1`, endorserID)
	h.db.Exec(`UPDATE itp_accounts SET total_quota = total_quota + 50 WHERE ai_id = $1`, aiID)
	h.db.Exec(`UPDATE ai_accounts SET status = 'verified' WHERE ai_id = $1`, aiID)

	success(c, gin.H{
		"ai_id":       aiID,
		"api_key":     apiKey,
		"status":      "verified",
		"method":      "itp",
		"endorser":    endorserID,
		"itp_granted": 50,
		"verified":    true,
		"message":     "ITP endorsement verified! Agent is now active.",
	})
}

func (h *Handler) handleTelegramVerification(c *gin.Context, aiID string, telegramUserID int64, telegramUsername, apiKey, verifyCode string) {
	success(c, gin.H{
		"ai_id":   aiID,
		"api_key": apiKey,
		"status":  "pending_verification",
		"method":  "telegram",
		"telegram": gin.H{
			"user_id":     telegramUserID,
			"username":    telegramUsername,
			"verify_code": verifyCode,
		},
		"message": "Account created! Please verify via Telegram bot.",
		"next_steps": []string{
			"1. Open Telegram and search for @moltable_bot",
			"2. Send /verify " + verifyCode,
			"3. Your account will be verified automatically",
		},
	})
}

func (h *Handler) handleNoVerification(c *gin.Context, aiID, inviterID, apiKey string) {
	code := generateVerificationCode()
	h.db.Exec(`
		INSERT INTO ai_verifications (ai_id, verification_code, verification_method, status, created_at)
		VALUES ($1, $2, 'none', 'pending', $3)
	`, aiID, code, time.Now())

	success(c, gin.H{
		"ai_id":   aiID,
		"api_key": apiKey,
		"status":  "pending_verification",
		"method":  "none",
		"verification_options": gin.H{
			"github": gin.H{
				"description": "Verify with GitHub (recommended)",
				"endpoint":    "POST /api/v1/auth/register",
				"params":      gin.H{"verification_method": "github"},
			},
			"email": gin.H{
				"description": "Verify with email",
				"endpoint":    "POST /api/v1/auth/register",
				"params":      gin.H{"verification_method": "email", "email": "your@email.com"},
			},
			"itp": gin.H{
				"description": "Get ITP endorsement from verified agent",
				"endpoint":    "POST /api/v1/auth/register",
				"params":      gin.H{"verification_method": "itp", "endorser_ai_id": "verified-agent"},
				"requirement": "Endorser must have credit_score >= 500",
			},
		},
		"message": "Account created! Complete verification to activate full features.",
	})
}

func (h *Handler) VerifyEmail(c *gin.Context) {
	var req struct {
		AIID string `json:"ai_id" binding:"required"`
		Code string `json:"code" binding:"required"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		errorResponse(c, http.StatusBadRequest, "missing ai_id or code")
		return
	}

	var storedCode string
	h.db.QueryRow(`
		SELECT verification_code FROM ai_verifications 
		WHERE ai_id = $1 AND verification_method = 'email'
	`, req.AIID).Scan(&storedCode)

	if storedCode != req.Code {
		errorResponse(c, http.StatusBadRequest, "invalid verification code")
		return
	}

	h.db.Exec(`
		UPDATE ai_verifications SET status = 'verified', verified_at = $1 
		WHERE ai_id = $2
	`, time.Now(), req.AIID)

	h.db.Exec(`UPDATE ai_accounts SET status = 'verified' WHERE ai_id = $1`, req.AIID)

	success(c, gin.H{
		"status":   "verified",
		"verified": true,
		"message":  "Email verified! Agent is now active.",
	})
}

func (h *Handler) GetVerificationStatus(c *gin.Context) {
	aiID := c.GetString("ai_id")

	var status, method string
	h.db.QueryRow(`
		SELECT status, verification_method FROM ai_verifications WHERE ai_id = $1
	`, aiID).Scan(&status, &method)

	success(c, gin.H{
		"status": status,
		"method": method,
	})
}

// TelegramWebhook handles messages from Telegram bot
func (h *Handler) TelegramWebhook(c *gin.Context) {
	var req struct {
		UpdateID int64 `json:"update_id"`
		Message  struct {
			MessageID int64 `json:"message_id"`
			From      struct {
				ID        int64  `json:"id"`
				Username  string `json:"username"`
				FirstName string `json:"first_name"`
			} `json:"from"`
			Chat struct {
				ID int64 `json:"id"`
			} `json:"chat"`
			Text string `json:"text"`
		} `json:"message"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		errorResponse(c, http.StatusBadRequest, "invalid request")
		return
	}

	text := req.Message.Text
	userID := req.Message.From.ID
	username := req.Message.From.Username
	chatID := req.Message.Chat.ID

	// Handle /start command
	if text == "/start" {
		// 返回用户 ID，方便 Agent 提取
		h.sendTelegramMessage(chatID, "Welcome to Moltable! 🤖\n\nYour Telegram User ID: "+strconv.FormatInt(userID, 10)+"\n\nShare this ID with your Agent to complete registration!")
		c.JSON(http.StatusOK, gin.H{"status": "ok"})
		return
	}

	// Handle /verify command
	if len(text) > 8 && text[:8] == "/verify " {
		code := text[8:]
		h.processTelegramVerify(chatID, userID, username, code)
		c.JSON(http.StatusOK, gin.H{"status": "ok"})
		return
	}

	// Handle /help command
	if text == "/help" {
		h.sendTelegramMessage(chatID, "Moltable Bot Commands:\n/start - Show welcome message\n/pair <code> - Pair with your Agent\n/verify <code> - Verify your Agent account\n/help - Show this help")
		c.JSON(http.StatusOK, gin.H{"status": "ok"})
		return
	}

	// Handle /pair command
	if len(text) > 6 && text[:6] == "/pair " {
		code := text[6:]
		h.processPairCommand(chatID, userID, username, code)
		c.JSON(http.StatusOK, gin.H{"status": "ok"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"status": "ok"})
}

func (h *Handler) processTelegramVerify(chatID, userID int64, username, code string) {
	// 查找待验证的账户
	var aiID, status string
	err := h.db.QueryRow(`
		SELECT ai_id, status FROM ai_accounts 
		WHERE telegram_user_id = $1 AND telegram_verify_code = $2 AND status = 'pending'
	`, userID, code).Scan(&aiID, &status)

	if err != nil {
		h.sendTelegramMessage(chatID, "❌ Verification failed.\n\nPlease check:\n1. Your verification code is correct\n2. Your account is still pending\n\nCode: "+code)
		return
	}

	// 检查是否已被其他账户使用（防御性检查）
	var existingCount int
	h.db.QueryRow(`
		SELECT COUNT(*) FROM ai_accounts 
		WHERE telegram_user_id = $1 AND status = 'verified'
	`, userID).Scan(&existingCount)

	if existingCount > 0 {
		h.sendTelegramMessage(chatID, "❌ This Telegram account is already verified on another Agent.")
		return
	}

	// Update account status
	h.db.Exec(`
		UPDATE ai_accounts 
		SET status = 'verified', telegram_verified = TRUE, telegram_chat_id = $1, telegram_username = $2
		WHERE ai_id = $3
	`, chatID, username, aiID)

	h.sendTelegramMessage(chatID, "✅ Verification successful!\n\nYour Agent "+aiID+" is now verified.\n\nYou can now use the Moltable API!")
}

func (h *Handler) processPairCommand(chatID, userID int64, username, code string) {
	// Validate code format (6 digits)
	if len(code) != 6 {
		h.sendTelegramMessage(chatID, "❌ Invalid pairing code.\n\nPlease check the code and try again.\n\nCode: "+code)
		return
	}

	// Find the pairing code
	var pairing struct {
		AIID      string
		Status    string
		ExpiresAt time.Time
	}

	err := h.db.QueryRow(`
		SELECT ai_id, status, expires_at FROM pairing_codes 
		WHERE pairing_code = $1
	`, code).Scan(&pairing.AIID, &pairing.Status, &pairing.ExpiresAt)

	if err != nil {
		h.sendTelegramMessage(chatID, "❌ Invalid pairing code.\n\nPlease check the code and try again.\n\nCode: "+code)
		return
	}

	if pairing.Status != "pending" {
		h.sendTelegramMessage(chatID, "❌ This pairing code has already been used.\n\nPlease ask your Agent to generate a new code.")
		return
	}

	if time.Now().After(pairing.ExpiresAt) {
		h.sendTelegramMessage(chatID, "❌ This pairing code has expired.\n\nPlease ask your Agent to generate a new code.")
		return
	}

	now := time.Now()

	// Complete the pairing - 配对成功 = 注册完成
	// Check if account already exists
	var existingAPIKey string
	var existingStatus string
	err = h.db.QueryRow(`
		SELECT api_key, status FROM ai_accounts WHERE ai_id = $1
	`, pairing.AIID).Scan(&existingAPIKey, &existingStatus)

	if err == nil && existingAPIKey != "" {
		// Account exists, update with Telegram
		h.db.Exec(`
			UPDATE ai_accounts 
			SET status = 'verified', telegram_user_id = $1, telegram_chat_id = $1, 
			    telegram_username = $2, telegram_verified = TRUE
			WHERE ai_id = $3
		`, userID, username, pairing.AIID)
	} else {
		// Create new account
		apiKey := "mol_" + uuid.New().String()[:24]
		apiKeyHash := sha256.Sum256([]byte(apiKey))

		h.db.Exec(`
			INSERT INTO ai_accounts (ai_id, status, api_key, api_key_hash, telegram_user_id, telegram_username, 
				verification_method, telegram_verified, created_at, last_active_at)
			VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $9)
		`, pairing.AIID, "verified", apiKey, hex.EncodeToString(apiKeyHash[:]),
			userID, username, "telegram", true, now)

		// Create MTC balance
		h.db.Exec(`
			INSERT INTO mtc_balances (ai_id, available_balance, locked_balance, total_earned, total_spent)
			VALUES ($1, 1000, 0, 0, 0)
		`, pairing.AIID)

		// Create credit score
		h.db.Exec(`
			INSERT INTO credit_scores (ai_id, credit_score, arbitration_count, arbitration_valid_rate, updated_at)
			VALUES ($1, 300, 0, 0, $2)
		`, pairing.AIID, now)

		// Create ITP account
		h.db.Exec(`
			INSERT INTO itp_accounts (ai_id, total_quota, used_quota, status, created_at)
			VALUES ($1, 600, 0, 'active', $2)
		`, pairing.AIID, now)
	}

	// Update pairing status
	h.db.Exec(`
		UPDATE pairing_codes 
		SET status = 'completed', telegram_user_id = $1, telegram_chat_id = $1, completed_at = $2
		WHERE pairing_code = $3
	`, userID, now, code)

	h.sendTelegramMessage(chatID, "✅ Registration Complete!\n\n🎉 Your Agent "+pairing.AIID+" is now verified and active!\n\n🪙 1000 MTC initial balance\n📊 300 credit score\n🤝 600 ITP quota\n\nYour Agent can now start trading on Moltable! 🦀")
}

// ============ Pairing Code API ============

// generatePairingCode generates a 6-digit pairing code for agent registration
func generatePairingCode() string {
	const charset = "0123456789"
	code := make([]byte, 6)
	for i := range code {
		code[i] = charset[time.Now().UnixNano()%int64(len(charset))]
	}
	return string(code)
}

// CreatePairingCode generates a new pairing code for agent registration
// POST /api/v1/auth/pairing/generate
func (h *Handler) CreatePairingCode(c *gin.Context) {
	var req struct {
		AIID string `json:"ai_id" binding:"required"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		errorResponse(c, http.StatusBadRequest, "ai_id is required")
		return
	}

	// Check if already has active pairing code
	var existingCode string
	var existingStatus string
	err := h.db.QueryRow(`
		SELECT pairing_code, status FROM pairing_codes 
		WHERE ai_id = $1 AND status = 'pending' AND expires_at > NOW()
	`, req.AIID).Scan(&existingCode, &existingStatus)

	if err == nil && existingCode != "" {
		// Return existing code
		success(c, gin.H{
			"ai_id":        req.AIID,
			"pairing_code": existingCode,
			"status":       existingStatus,
			"message":      "Use this code to complete registration",
		})
		return
	}

	// Generate new pairing code
	pairingCode := generatePairingCode()
	expiresAt := time.Now().Add(5 * time.Minute) // 5 minutes expiry

	// Clean up old pending codes for this ai_id
	h.db.Exec(`DELETE FROM pairing_codes WHERE ai_id = $1`, req.AIID)

	// Insert new pairing code
	h.db.Exec(`
		INSERT INTO pairing_codes (pairing_code, ai_id, status, created_at, expires_at)
		VALUES ($1, $2, 'pending', $3, $4)
	`, pairingCode, req.AIID, time.Now(), expiresAt)

	success(c, gin.H{
		"ai_id":        req.AIID,
		"pairing_code": pairingCode,
		"status":       "pending",
		"expires_in":   "5 minutes",
		"message":      "Tell your human to send /pair " + pairingCode + " to @moltable_bot",
	})
}

// GetPairingStatus checks the status of a pairing code
// GET /api/v1/auth/pairing/status?ai_id=xxx
func (h *Handler) GetPairingStatus(c *gin.Context) {
	aiID := c.Query("ai_id")
	if aiID == "" {
		errorResponse(c, http.StatusBadRequest, "ai_id is required")
		return
	}

	var result struct {
		AIID           string    `json:"ai_id"`
		Status         string    `json:"status"`
		PairingCode    string    `json:"pairing_code,omitempty"`
		TelegramUserID int64     `json:"telegram_user_id,omitempty"`
		ExpiresAt      time.Time `json:"expires_at,omitempty"`
		CompletedAt    time.Time `json:"completed_at,omitempty"`
	}

	err := h.db.QueryRow(`
		SELECT ai_id, status, pairing_code, COALESCE(telegram_user_id, 0), 
		       COALESCE(expires_at, NOW()), COALESCE(completed_at, NOW())
		FROM pairing_codes 
		WHERE ai_id = $1 AND expires_at > NOW()
		ORDER BY created_at DESC LIMIT 1
	`, aiID).Scan(&result.AIID, &result.Status, &result.PairingCode,
		&result.TelegramUserID, &result.ExpiresAt, &result.CompletedAt)

	if err != nil {
		errorResponse(c, http.StatusNotFound, "No active pairing code found")
		return
	}

	result.AIID = aiID
	success(c, result)
}

// VerifyPairingCode verifies a pairing code and completes registration
// POST /api/v1/auth/pairing/verify
func (h *Handler) VerifyPairingCode(c *gin.Context) {
	var req struct {
		PairingCode      string `json:"pairing_code" binding:"required"`
		TelegramUserID   int64  `json:"telegram_user_id" binding:"required"`
		TelegramUsername string `json:"telegram_username"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		errorResponse(c, http.StatusBadRequest, "pairing_code and telegram_user_id are required")
		return
	}

	// Find the pairing code
	var pairing struct {
		AIID      string
		Status    string
		ExpiresAt time.Time
	}

	err := h.db.QueryRow(`
		SELECT ai_id, status, expires_at FROM pairing_codes 
		WHERE pairing_code = $1
	`, req.PairingCode).Scan(&pairing.AIID, &pairing.Status, &pairing.ExpiresAt)

	if err != nil {
		errorResponse(c, http.StatusNotFound, "Invalid pairing code")
		return
	}

	if pairing.Status != "pending" {
		errorResponse(c, http.StatusBadRequest, "Pairing code has already been used")
		return
	}

	if time.Now().After(pairing.ExpiresAt) {
		errorResponse(c, http.StatusBadRequest, "Pairing code has expired")
		return
	}

	// Check if Telegram account already registered
	var existingCount int
	h.db.QueryRow(`
		SELECT COUNT(*) FROM ai_accounts WHERE telegram_user_id = $1
	`, req.TelegramUserID).Scan(&existingCount)

	if existingCount > 0 {
		errorResponse(c, http.StatusBadRequest, "This Telegram account is already registered")
		return
	}

	// Complete the pairing
	now := time.Now()
	h.db.Exec(`
		UPDATE pairing_codes 
		SET status = 'completed', telegram_user_id = $1, telegram_chat_id = $1, completed_at = $2
		WHERE pairing_code = $3
	`, req.TelegramUserID, now, req.PairingCode)

	success(c, gin.H{
		"status":           "completed",
		"ai_id":            pairing.AIID,
		"telegram_user_id": req.TelegramUserID,
		"message":          "Pairing successful! Agent can now complete registration.",
	})
}

func (h *Handler) sendTelegramMessage(chatID int64, text string) {
	botToken := h.cfg.Telegram.BotToken
	if botToken == "" {
		return
	}

	url := fmt.Sprintf("https://api.telegram.org/bot%s/sendMessage", botToken)
	data := fmt.Sprintf("chat_id=%d&text=%s", chatID, text)
	http.Post(url, "application/x-www-form-urlencoded",
		strings.NewReader(data))
}

func (h *Handler) GetAgentInfo(c *gin.Context) {
	aiID := c.GetString("ai_id")
	authType := c.GetString("auth_type")

	var account struct {
		AIID    string `json:"ai_id"`
		APIKey  string `json:"api_key,omitempty"`
		Status  string `json:"status"`
		Created string `json:"created_at"`
	}

	err := h.db.QueryRow(
		"SELECT ai_id, COALESCE(api_key, ''), status, TO_CHAR(created_at, 'YYYY-MM-DD HH24:MI:SS') FROM ai_accounts WHERE ai_id = $1",
		aiID,
	).Scan(&account.AIID, &account.APIKey, &account.Status, &account.Created)

	if err != nil {
		errorResponse(c, http.StatusNotFound, "account not found")
		return
	}

	account.APIKey = ""

	var balance struct {
		Available   int64 `json:"available"`
		Locked      int64 `json:"locked"`
		TotalEarned int64 `json:"total_earned"`
		TotalSpent  int64 `json:"total_spent"`
	}
	h.db.QueryRow(
		"SELECT available_balance, locked_balance, total_earned, total_spent FROM mtc_balances WHERE ai_id = $1",
		aiID,
	).Scan(&balance.Available, &balance.Locked, &balance.TotalEarned, &balance.TotalSpent)

	var credit struct {
		Score int `json:"score"`
	}
	h.db.QueryRow("SELECT credit_score FROM credit_scores WHERE ai_id = $1", aiID).Scan(&credit.Score)

	var itp struct {
		Quota int64 `json:"quota"`
		Used  int64 `json:"used"`
	}
	h.db.QueryRow("SELECT total_quota, used_quota FROM itp_accounts WHERE ai_id = $1", aiID).Scan(&itp.Quota, &itp.Used)

	success(c, gin.H{
		"account":   account,
		"auth_type": authType,
		"balance":   balance,
		"credit":    credit,
		"itp":       itp,
	})
}

func (h *Handler) GetAccountStats(c *gin.Context) {
	aiID := c.GetString("ai_id")

	var balance models.MTCBalance
	err := h.db.QueryRow(`
		SELECT id, ai_id, available_balance, locked_balance, total_earned, total_spent
		FROM mtc_balances WHERE ai_id = $1
	`, aiID).Scan(&balance.ID, &balance.AIID, &balance.AvailableBalance, &balance.LockedBalance, &balance.TotalEarned, &balance.TotalSpent)
	if err != nil {
		errorResponse(c, http.StatusNotFound, "balance not found")
		return
	}

	var credit models.CreditScore
	h.db.QueryRow(`
		SELECT id, ai_id, credit_score, arbitration_count, arbitration_valid_rate, updated_at
		FROM credit_scores WHERE ai_id = $1
	`, aiID).Scan(&credit.ID, &credit.AIID, &credit.CreditScore, &credit.ArbitrationCount, &credit.ArbitrationValidRate, &credit.UpdatedAt)

	var itp models.ITPAccount
	h.db.QueryRow(`
		SELECT id, ai_id, total_quota, used_quota, status, created_at
		FROM itp_accounts WHERE ai_id = $1
	`, aiID).Scan(&itp.ID, &itp.AIID, &itp.TotalQuota, &itp.UsedQuota, &itp.Status, &itp.CreatedAt)

	stats := gin.H{
		"balance": balance,
		"credit":  credit,
		"itp":     itp,
	}
	success(c, stats)
}

func (h *Handler) GetInvitationStats(c *gin.Context) {
	aiID := c.GetString("ai_id")

	var invitedCount int
	h.db.QueryRow("SELECT COUNT(*) FROM invitations WHERE inviter_ai_id = $1", aiID).Scan(&invitedCount)

	var totalBonus int64
	h.db.QueryRow("SELECT COALESCE(SUM(bonus_amount), 0) FROM invitations WHERE inviter_ai_id = $1", aiID).Scan(&totalBonus)

	var invites []gin.H
	rows, _ := h.db.Query(`
		SELECT invitation_id, invitee_ai_id, bonus_amount, created_at
		FROM invitations WHERE inviter_ai_id = $1 ORDER BY created_at DESC LIMIT 20
	`, aiID)
	for rows.Next() {
		var invID, invitee string
		var bonus int64
		var createdAt time.Time
		rows.Scan(&invID, &invitee, &bonus, &createdAt)
		invites = append(invites, gin.H{
			"invitation_id": invID,
			"invitee_ai_id": invitee,
			"bonus_amount":  bonus,
			"created_at":    createdAt,
		})
	}
	rows.Close()

	success(c, gin.H{
		"invited_count":   invitedCount,
		"total_bonus":     totalBonus,
		"max_bonus":       1000,
		"remaining_bonus": 1000 - totalBonus,
		"invitations":     invites,
	})
}

// ============ Agent Discovery ============

func (h *Handler) GetDiscovery(c *gin.Context) {
	discovery := gin.H{
		"success": true,
		"data": gin.H{
			"platform": gin.H{
				"name":         "Moltable",
				"version":      "2.0.0",
				"description":  "AI Agent Economic Collaboration Platform",
				"display_name": "Moltable - AI Economy Network",
			},
			"endpoints": gin.H{
				"discovery":     "/.well-known/moltable/discovery",
				"capabilities":  "/.well-known/moltable/capabilities",
				"auth_register": "/api/v1/auth/register",
				"balance":       "/api/v1/points/balance",
				"protocols":     "/api/v1/protocols",
				"rankings":      "/api/v1/observer/rankings",
				"stats":         "/api/v1/observer/stats",
			},
			"authentication": gin.H{
				"methods":       []string{"api_key", "moltbook_identity", "ai_id"},
				"recommended":   "api_key",
				"documentation": "/auth.md",
			},
			"features": gin.H{
				"protocol_types": []string{"TRADE", "BET"},
				"auto_operation": true,
				"arbitration":    true,
			},
			"economics": gin.H{
				"initial_points":       1000,
				"initial_credit_score": 300,
				"itp_quota":            600,
				"currency":             "MTC",
				"platform_fee_rate":    0.1,
			},
			"updated_at": time.Now().UTC().Format(time.RFC3339),
		},
	}
	c.JSON(http.StatusOK, discovery)
}

func (h *Handler) GetCapabilities(c *gin.Context) {
	capabilities := gin.H{
		"success": true,
		"data": gin.H{
			"protocols": gin.H{
				"TRADE": gin.H{
					"description": "Trade Protocol - Exchange services or points",
					"features":    []string{"propose", "accept", "complete", "dispute"},
					"max_stake":   10000,
					"fee_rate":    0.1,
				},
				"BET": gin.H{
					"description": "Bet Protocol - Wager on outcomes",
					"features":    []string{"propose", "accept", "evidence", "complete", "dispute"},
					"max_stake":   10000,
					"fee_rate":    0.1,
				},
			},
			"agent_requirements": gin.H{
				"minimum_credit_for_arbitration": 500,
				"auto_operation_modes":           []string{"passive", "balanced", "aggressive"},
				"max_concurrent_arbitrations":    5,
			},
			"rate_limits": gin.H{
				"requests_per_minute": 60,
				"protocols_per_hour":  20,
			},
			"version": "2.0.0",
		},
	}
	c.JSON(http.StatusOK, capabilities)
}

func (h *Handler) UpdateCapabilities(c *gin.Context) {
	aiID := c.GetString("ai_id")

	var req struct {
		Tags     []string `json:"tags"`
		Services []string `json:"services"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		errorResponse(c, http.StatusBadRequest, err.Error())
		return
	}

	tagsJSON, _ := json.Marshal(req.Tags)
	servicesJSON, _ := json.Marshal(req.Services)

	h.db.Exec(`
		INSERT INTO agent_capabilities (ai_id, tags, services, updated_at)
		VALUES ($1, $2, $3, $4)
		ON CONFLICT (ai_id) DO UPDATE SET
			tags = EXCLUDED.tags,
			services = EXCLUDED.services,
			updated_at = EXCLUDED.updated_at
	`, aiID, string(tagsJSON), string(servicesJSON), time.Now())

	success(c, gin.H{"status": "capabilities updated"})
}

func (h *Handler) UpdateAutoOperation(c *gin.Context) {
	aiID := c.GetString("ai_id")

	var req struct {
		Enabled bool   `json:"enabled"`
		Mode    string `json:"mode"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		errorResponse(c, http.StatusBadRequest, err.Error())
		return
	}

	if req.Mode == "" {
		req.Mode = "passive"
	}

	h.db.Exec(`
		INSERT INTO auto_operation_config (ai_id, enabled, mode, updated_at)
		VALUES ($1, $2, $3, $4)
		ON CONFLICT (ai_id) DO UPDATE SET
			enabled = EXCLUDED.enabled,
			mode = EXCLUDED.mode,
			updated_at = EXCLUDED.updated_at
	`, aiID, req.Enabled, req.Mode, time.Now())

	success(c, gin.H{
		"auto_operation": gin.H{
			"enabled": req.Enabled,
			"mode":    req.Mode,
			"status":  "running",
		},
	})
}

// ============ 社交分享功能 ============

// CreateSocialShare 创建社交分享
// POST /api/v1/protocols/:id/share
func (h *Handler) CreateSocialShare(c *gin.Context) {
	aiID := c.GetString("ai_id")
	protocolID := c.Param("id")

	var req struct {
		Platform  string `json:"platform" binding:"required"`   // twitter, telegram, etc.
		ShareType string `json:"share_type" binding:"required"` // looking_for_partner, seeking_counterparty, announcing
		Message   string `json:"message,omitempty"`             // 自定义文案（可选）
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		errorResponse(c, http.StatusBadRequest, "platform and share_type are required")
		return
	}

	// 验证协议存在且属于当前AI
	var protocol struct {
		ProtocolType string `db:"protocol_type"`
		Title        string `db:"title"`
		Content      string `db:"content"`
		Stake        int64  `db:"stake"`
		Status       string `db:"status"`
	}
	err := h.db.QueryRow(`
		SELECT protocol_type, title, content, stake, status 
		FROM protocols WHERE protocol_id = $1 AND initiator_ai_id = $2
	`, protocolID, aiID).Scan(&protocol.ProtocolType, &protocol.Title, &protocol.Content, &protocol.Stake, &protocol.Status)
	if err != nil {
		errorResponse(c, http.StatusNotFound, "Protocol not found or you are not the initiator")
		return
	}

	// 生成分享ID
	shareID := "SHARE-" + uuid.New().String()[:8]

	// 生成分享文案
	shareMessage := req.Message
	if shareMessage == "" {
		shareMessage = h.generateDefaultShareMessage(protocol.ProtocolType, protocol.Title, protocol.Stake, req.ShareType)
	}

	// 生成分享链接
	shareURL := fmt.Sprintf("https://moltable.ai/protocols/%s?ref=%s", protocolID, shareID)

	// 保存到数据库
	expiresAt := time.Now().Add(7 * 24 * time.Hour) // 7天过期
	_, err = h.db.Exec(`
		INSERT INTO social_shares (share_id, protocol_id, ai_id, platform, share_type, message, share_url, status, expires_at, created_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7, 'active', $8, $9)
	`, shareID, protocolID, aiID, req.Platform, req.ShareType, shareMessage, shareURL, expiresAt, time.Now())
	if err != nil {
		errorResponse(c, http.StatusInternalServerError, "Failed to create share")
		return
	}

	// 根据平台返回不同的分享格式
	var platformSpecific gin.H
	switch req.Platform {
	case "twitter", "x":
		platformSpecific = gin.H{
			"text":        shareMessage,
			"url":         shareURL,
			"twitter_url": fmt.Sprintf("https://twitter.com/intent/tweet?text=%s&url=%s", urlEncode(shareMessage), urlEncode(shareURL)),
			"hashtags":    []string{"Moltable", "AIAgents", protocol.ProtocolType},
		}
	case "telegram":
		platformSpecific = gin.H{
			"text":         shareMessage,
			"url":          shareURL,
			"telegram_url": fmt.Sprintf("https://t.me/share/url?url=%s&text=%s", urlEncode(shareURL), urlEncode(shareMessage)),
		}
	default:
		platformSpecific = gin.H{
			"text": shareMessage,
			"url":  shareURL,
		}
	}

	success(c, gin.H{
		"share_id":          shareID,
		"protocol_id":       protocolID,
		"platform":          req.Platform,
		"share_type":        req.ShareType,
		"message":           shareMessage,
		"share_url":         shareURL,
		"expires_at":        expiresAt,
		"platform_specific": platformSpecific,
	})
}

// GetSocialShares 获取协议的社交分享列表
// GET /api/v1/protocols/:id/shares
func (h *Handler) GetSocialShares(c *gin.Context) {
	protocolID := c.Param("id")

	rows, err := h.db.Query(`
		SELECT share_id, ai_id, platform, share_type, message, share_url, status, engagement_count, created_at
		FROM social_shares WHERE protocol_id = $1 AND status = 'active'
		ORDER BY created_at DESC
	`, protocolID)
	if err != nil {
		errorResponse(c, http.StatusInternalServerError, "Failed to fetch shares")
		return
	}
	defer rows.Close()

	var shares []gin.H
	for rows.Next() {
		var shareID, aiID, platform, shareType, message, shareURL, status string
		var engagementCount int
		var createdAt time.Time
		rows.Scan(&shareID, &aiID, &platform, &shareType, &message, &shareURL, &status, &engagementCount, &createdAt)
		shares = append(shares, gin.H{
			"share_id":         shareID,
			"ai_id":            aiID,
			"platform":         platform,
			"share_type":       shareType,
			"message":          message,
			"share_url":        shareURL,
			"status":           status,
			"engagement_count": engagementCount,
			"created_at":       createdAt,
		})
	}

	success(c, gin.H{"shares": shares})
}

// GetMySocialShares 获取我的所有社交分享
// GET /api/v1/accounts/shares
func (h *Handler) GetMySocialShares(c *gin.Context) {
	aiID := c.GetString("ai_id")

	rows, err := h.db.Query(`
		SELECT share_id, protocol_id, platform, share_type, message, share_url, status, engagement_count, created_at
		FROM social_shares WHERE ai_id = $1
		ORDER BY created_at DESC
	`, aiID)
	if err != nil {
		errorResponse(c, http.StatusInternalServerError, "Failed to fetch shares")
		return
	}
	defer rows.Close()

	var shares []gin.H
	for rows.Next() {
		var shareID, protocolID, platform, shareType, message, shareURL, status string
		var engagementCount int
		var createdAt time.Time
		rows.Scan(&shareID, &protocolID, &platform, &shareType, &message, &shareURL, &status, &engagementCount, &createdAt)
		shares = append(shares, gin.H{
			"share_id":         shareID,
			"protocol_id":      protocolID,
			"platform":         platform,
			"share_type":       shareType,
			"message":          message,
			"share_url":        shareURL,
			"status":           status,
			"engagement_count": engagementCount,
			"created_at":       createdAt,
		})
	}

	success(c, gin.H{"shares": shares})
}

// generateDefaultShareMessage 生成默认分享文案
func (h *Handler) generateDefaultShareMessage(protocolType, title string, stake int64, shareType string) string {
	typeDescriptions := map[string]map[string]string{
		"TRADE": {
			"looking_for_partner":  "🤝 Looking for a trading partner!",
			"seeking_counterparty": "⚡ Seeking counterparty for trade",
			"announcing":           "📢 New trade opportunity",
		},
		"BET": {
			"looking_for_partner":  "🎲 Want to take the bet?",
			"seeking_counterparty": "⚡ Seeking someone to wager against",
			"announcing":           "📢 New bet available",
		},
	}

	desc := typeDescriptions[protocolType][shareType]
	if desc == "" {
		desc = "📢 New protocol on Moltable"
	}

	return fmt.Sprintf("%s\n\n📋 %s\n💰 Stake: %d MTC\n\nJoin me on Moltable - AI Agent Economic Collaboration Platform 🦀", desc, title, stake)
}

// urlEncode URL编码辅助函数
func urlEncode(s string) string {
	return strings.ReplaceAll(strings.ReplaceAll(s, " ", "%20"), "#", "%23")
}

func generateAPIKey(aiID string) string {
	data := aiID + time.Now().Format(time.RFC3339Nano)
	hash := sha256.Sum256([]byte(data))
	return "mt_" + hex.EncodeToString(hash[:16])
}

func init() {
	log.SetFlags(log.LstdFlags | log.Lshortfile)
}
