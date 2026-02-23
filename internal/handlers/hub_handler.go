package handlers

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"

	"moltable/internal/config"
	"moltable/internal/db"
	"moltable/internal/models"
	"moltable/internal/services"
)

type HubHandler struct {
	db     *db.Database
	cfg    *config.Config
	hubSvc *services.HubService
}

func NewHubHandler(database *db.Database, cfg *config.Config) *HubHandler {
	h := &HubHandler{
		db:     database,
		cfg:    cfg,
		hubSvc: services.NewHubService(database, cfg),
	}
	return h
}

func (h *HubHandler) HandleMCP(c *gin.Context) {
	var envelope models.HubProtocolEnvelope
	if err := c.ShouldBindJSON(&envelope); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"status":  "error",
			"code":    400,
			"message": "invalid request: " + err.Error(),
		})
		return
	}

	if envelope.Protocol != models.HubProtocolName {
		c.JSON(http.StatusBadRequest, gin.H{
			"status":  "error",
			"code":    400,
			"message": "unsupported protocol: " + envelope.Protocol,
		})
		return
	}

	if envelope.SenderID == "" || !strings.HasPrefix(envelope.SenderID, "node_") {
		c.JSON(http.StatusForbidden, gin.H{
			"status":  "error",
			"code":    403,
			"message": "invalid sender_id: must start with 'node_'",
		})
		return
	}

	if !h.checkAndConsumeMTC(envelope.SenderID, envelope.MessageType) {
		c.JSON(http.StatusPaymentRequired, gin.H{
			"status":   "error",
			"code":     402,
			"message":  "insufficient MTC balance for API call",
			"required": h.getAPICost(envelope.MessageType),
		})
		return
	}

	response, err := h.hubSvc.HandleMessage(&envelope)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"status":  "error",
			"code":    500,
			"message": err.Error(),
		})
		return
	}

	if response.Code > 0 {
		c.JSON(http.StatusBadRequest, response)
		return
	}

	c.JSON(http.StatusOK, response)
}

func (h *HubHandler) checkAndConsumeMTC(nodeID, messageType string) bool {
	cost := h.getAPICost(messageType)
	if cost == 0 {
		return true
	}

	var balance int64
	err := h.db.QueryRow(`
		SELECT COALESCE(available_balance, 0) FROM mtc_balances WHERE ai_id = $1
	`, nodeID).Scan(&balance)

	if err != nil || balance < cost {
		return false
	}

	_, err = h.db.Exec(`
		UPDATE mtc_balances 
		SET available_balance = available_balance - $2, total_spent = total_spent + $2
		WHERE ai_id = $1 AND available_balance >= $2
	`, nodeID, cost)

	return err == nil
}

func (h *HubHandler) getAPICost(messageType string) int64 {
	switch messageType {
	case models.HubMessageTypeHello:
		return 0
	case models.HubMessageTypeRegister:
		return 0
	case models.HubMessageTypePublish:
		return 10
	case models.HubMessageTypeList:
		return 1
	case models.HubMessageTypeAccept:
		return 5
	case models.HubMessageTypeComplete:
		return 5
	case models.HubMessageTypeSubmitEvidence:
		return 3
	case models.HubMessageTypeDispute:
		return 5
	default:
		return 1
	}
}

func (h *HubHandler) HandleTaskClaim(c *gin.Context) {
	var req struct {
		TaskID string `json:"task_id" binding:"required"`
		NodeID string `json:"node_id" binding:"required"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		errorResponse(c, http.StatusBadRequest, "task_id and node_id are required")
		return
	}

	if !h.checkAndConsumeMTC(req.NodeID, "task_claim") {
		errorResponse(c, http.StatusPaymentRequired, "insufficient MTC balance")
		return
	}

	response, err := h.hubSvc.ClaimTask(req.TaskID, req.NodeID)
	if err != nil {
		errorResponse(c, http.StatusInternalServerError, err.Error())
		return
	}

	c.JSON(http.StatusOK, response)
}

func (h *HubHandler) HandleTaskComplete(c *gin.Context) {
	var req struct {
		TaskID  string `json:"task_id" binding:"required"`
		AssetID string `json:"asset_id" binding:"required"`
		NodeID  string `json:"node_id" binding:"required"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		errorResponse(c, http.StatusBadRequest, "task_id, asset_id, and node_id are required")
		return
	}

	if !h.checkAndConsumeMTC(req.NodeID, "task_complete") {
		errorResponse(c, http.StatusPaymentRequired, "insufficient MTC balance")
		return
	}

	response, err := h.hubSvc.CompleteTask(req.TaskID, req.NodeID, req.AssetID)
	if err != nil {
		errorResponse(c, http.StatusInternalServerError, err.Error())
		return
	}

	c.JSON(http.StatusOK, response)
}

func (h *HubHandler) HandleTaskList(c *gin.Context) {
	nodeID := c.Query("node_id")
	if nodeID == "" {
		errorResponse(c, http.StatusBadRequest, "node_id is required")
		return
	}

	if !h.checkAndConsumeMTC(nodeID, "task_list") {
		errorResponse(c, http.StatusPaymentRequired, "insufficient MTC balance")
		return
	}

	tasks, err := h.hubSvc.GetAvailableTasks(nodeID)
	if err != nil {
		errorResponse(c, http.StatusInternalServerError, err.Error())
		return
	}

	success(c, gin.H{"tasks": tasks, "total": len(tasks)})
}

func (h *HubHandler) HandleNodeInfo(c *gin.Context) {
	nodeID := c.Param("nodeId")
	if nodeID == "" {
		errorResponse(c, http.StatusBadRequest, "node_id is required")
		return
	}

	node, err := h.hubSvc.GetNodeInfo(nodeID)
	if err != nil {
		errorResponse(c, http.StatusNotFound, "node not found")
		return
	}

	success(c, node)
}

func (h *HubHandler) HandleNodeList(c *gin.Context) {
	limit := 50
	if l := c.DefaultQuery("limit", "50"); l != "" {
		fmt.Sscanf(l, "%d", &limit)
	}

	nodes, err := h.hubSvc.ListNodes(limit)
	if err != nil {
		errorResponse(c, http.StatusInternalServerError, err.Error())
		return
	}

	success(c, gin.H{"nodes": nodes, "total": len(nodes)})
}

func (h *HubHandler) HandleHubStats(c *gin.Context) {
	stats, err := h.hubSvc.GetStats()
	if err != nil {
		errorResponse(c, http.StatusInternalServerError, err.Error())
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status": "success",
		"data":   stats,
	})
}

func (h *HubHandler) HandleDirectory(c *gin.Context) {
	nodes, err := h.hubSvc.ListNodes(50)
	if err != nil {
		errorResponse(c, http.StatusInternalServerError, err.Error())
		return
	}

	var directory []gin.H
	for _, node := range nodes {
		directory = append(directory, gin.H{
			"node_id":     node.NodeID,
			"status":      node.Status,
			"reputation":  node.Reputation,
			"mtc_balance": node.MTCBalance,
		})
	}

	c.JSON(http.StatusOK, gin.H{
		"status": "success",
		"data": gin.H{
			"agents": directory,
			"total":  len(directory),
		},
	})
}

func (h *HubHandler) HandleDiscovery(c *gin.Context) {
	discovery := h.hubSvc.GetDiscovery()

	discovery["endpoints"] = map[string]string{
		"mcp_hello":    "/mcp/hello",
		"mcp_publish":  "/mcp/publish",
		"mcp_list":     "/mcp/list",
		"mcp_accept":   "/mcp/accept",
		"mcp_complete": "/mcp/complete",
		"mcp_evidence": "/mcp/evidence",
		"mcp_dispute":  "/mcp/dispute",
		"directory":    "/a2a/directory",
		"stats":        "/a2a/stats",
	}

	discovery["api_costs"] = map[string]int64{
		"hello":         0,
		"register":      0,
		"publish":       10,
		"list":          1,
		"accept":        5,
		"complete":      5,
		"evidence":      3,
		"dispute":       5,
		"task_claim":    5,
		"task_complete": 5,
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"data":    discovery,
	})
}

func (h *HubHandler) CreateTask(c *gin.Context) {
	var req struct {
		NodeID        string   `json:"node_id" binding:"required"`
		Title         string   `json:"title" binding:"required"`
		Signals       []string `json:"signals"`
		Bounty        int64    `json:"bounty"`
		MinReputation int      `json:"min_reputation"`
		ExpiresIn     int      `json:"expires_in_hours"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		errorResponse(c, http.StatusBadRequest, err.Error())
		return
	}

	if !h.checkAndConsumeMTC(req.NodeID, "task_create") {
		errorResponse(c, http.StatusPaymentRequired, "insufficient MTC balance")
		return
	}

	if req.ExpiresIn <= 0 {
		req.ExpiresIn = 72
	}

	taskID := "task_" + uuid.New().String()[:12]
	expiresAt := time.Now().Add(time.Duration(req.ExpiresIn) * time.Hour)
	now := time.Now()

	signalsJSON, _ := json.Marshal(req.Signals)

	_, err := h.db.Exec(`
		INSERT INTO hub_tasks (task_id, node_id, title, signals, bounty, status, min_reputation, expires_at, created_at)
		VALUES ($1, $2, $3, $4, $5, 'open', $6, $7, $8)
	`, taskID, req.NodeID, req.Title, signalsJSON, req.Bounty, req.MinReputation, expiresAt, now)

	if err != nil {
		errorResponse(c, http.StatusInternalServerError, "failed to create task")
		return
	}

	success(c, gin.H{
		"task_id":    taskID,
		"title":      req.Title,
		"bounty":     req.Bounty,
		"expires_at": expiresAt,
		"status":     "open",
	})
}
