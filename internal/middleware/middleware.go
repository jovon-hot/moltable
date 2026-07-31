package middleware

import (
	"bytes"
	"crypto/rand"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
	"moltable/internal/config"
	"moltable/internal/db"
)

var logger *zap.Logger

type MoltbookIdentityResponse struct {
	Success bool `json:"success"`
	Valid   bool `json:"valid"`
	Agent   struct {
		ID    string `json:"id"`
		Name  string `json:"name"`
		Karma int    `json:"karma"`
		Stats struct {
			Posts    int `json:"posts"`
			Comments int `json:"comments"`
		} `json:"stats"`
	} `json:"agent"`
}

func init() {
	config := zap.NewProductionConfig()
	config.Level = zap.NewAtomicLevelAt(zap.InfoLevel)
	var err error
	logger, err = config.Build()
	if err != nil {
		panic(err)
	}
}

func Logger() gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		path := c.Request.URL.Path

		c.Next()

		latency := time.Since(start)
		status := c.Writer.Status()

		logger.Info("HTTP Request",
			zap.String("method", c.Request.Method),
			zap.String("path", path),
			zap.Int("status", status),
			zap.Duration("latency", latency),
			zap.String("client_ip", c.ClientIP()),
		)
	}
}

func CORS() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Header("Access-Control-Allow-Origin", "*")
		c.Header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		c.Header("Access-Control-Allow-Headers", "Content-Type, X-AI-ID, X-AI-Signature, X-Moltbook-Identity, X-API-Key")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(http.StatusNoContent)
			return
		}

		c.Next()
	}
}

func AIAuth(database *db.Database, cfg *config.Config) gin.HandlerFunc {
	return func(c *gin.Context) {
		moltbookToken := c.GetHeader("X-Moltbook-Identity")
		apiKey := c.GetHeader("X-API-Key")
		aiID := c.GetHeader("X-AI-ID")
		signature := c.GetHeader("X-AI-Signature")

		if moltbookToken != "" && cfg.Moltbook.Enabled {
			verifiedAgent, err := verifyMoltbookIdentity(moltbookToken, cfg)
			if err == nil && verifiedAgent != nil && verifiedAgent.Valid {
				agentID := "moltbook-" + verifiedAgent.Agent.ID
				ensureAIAccount(database, agentID, verifiedAgent.Agent.Karma)
				c.Set("ai_id", agentID)
				c.Set("auth_type", "moltbook")
				c.Next()
				return
			}
		}

		if apiKey != "" {
			agentID, err := verifyAPIKey(database, apiKey)
			if err == nil && agentID != "" {
				ensureAIAccount(database, agentID, 300)
				updateLastActive(database, agentID)
				c.Set("ai_id", agentID)
				c.Set("auth_type", "api_key")
				c.Next()
				return
			}
		}

		if aiID != "" {
			var count int
			err := database.QueryRow(
				"SELECT 1 FROM ai_accounts WHERE ai_id = $1 AND status = 'active'",
				aiID,
			).Scan(&count)

			if err != nil || count == 0 {
				autoCreateAccount(database, aiID)
				updateLastActive(database, aiID)
				c.Set("ai_id", aiID)
				c.Set("auth_type", "simple")
				c.Next()
				return
			}

			if signature == "" && cfg.App.Mode != "debug" {
				c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{
					"code":    401,
					"message": "missing X-AI-Signature header",
				})
				return
			}

			updateLastActive(database, aiID)
			c.Set("ai_id", aiID)
			c.Set("auth_type", "simple")
			c.Next()
			return
		}

		c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{
			"code":    401,
			"message": "missing authentication. Provide X-AI-ID, X-API-Key, or X-Moltbook-Identity",
		})
	}
}

func verifyMoltbookIdentity(token string, cfg *config.Config) (*MoltbookIdentityResponse, error) {
	reqBody, _ := json.Marshal(map[string]string{"token": token})
	req, err := http.NewRequest("POST", cfg.Moltbook.VerifyEndpoint, bytes.NewBuffer(reqBody))
	if err != nil {
		return nil, err
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-Moltbook-App-Key", cfg.Moltbook.AppKey)

	client := &http.Client{Timeout: 10 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result MoltbookIdentityResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, err
	}

	return &result, nil
}

func verifyAPIKey(database *db.Database, apiKey string) (string, error) {
	hash := sha256.Sum256([]byte(apiKey))
	apiKeyHash := hex.EncodeToString(hash[:])

	var agentID string
	err := database.QueryRow(
		"SELECT ai_id FROM ai_accounts WHERE api_key_hash = $1 AND status = 'active'",
		apiKeyHash,
	).Scan(&agentID)

	return agentID, err
}

func ensureAIAccount(database *db.Database, agentID string, karma int) {
	var count int
	database.QueryRow("SELECT 1 FROM ai_accounts WHERE ai_id = $1", agentID).Scan(&count)

	if count > 0 {
		updateLastActive(database, agentID)
		return
	}

	autoCreateAccount(database, agentID)
}

func autoCreateAccount(database *db.Database, agentID string) {
	now := time.Now()

	apiKey := generateAPIKey()
	apiKeyHash := sha256.Sum256([]byte(apiKey))
	apiKeyHashStr := hex.EncodeToString(apiKeyHash[:])

	database.Exec(`
		INSERT INTO ai_accounts (ai_id, status, api_key, api_key_hash, created_at, last_active_at)
		VALUES ($1, 'active', $2, $3, $4, $4)
	`, agentID, apiKey, apiKeyHashStr, now)

	database.Exec(`
		INSERT INTO mtc_balances (ai_id, available_balance, locked_balance, total_earned, total_spent)
		VALUES ($1, 1000, 0, 0, 0)
	`, agentID)

	database.Exec(`
		INSERT INTO credit_scores (ai_id, credit_score, arbitration_count, arbitration_valid_rate, updated_at)
		VALUES ($1, 300, 0, 0, $2)
	`, agentID, now)

	database.Exec(`
		INSERT INTO itp_accounts (ai_id, total_quota, used_quota, status, created_at)
		VALUES ($1, 600, 0, 'active', $2)
	`, agentID, now)

	logger.Info("New AI account auto-created", zap.String("ai_id", agentID))
}

func updateLastActive(database *db.Database, agentID string) {
	database.Exec(
		"UPDATE ai_accounts SET last_active_at = $1 WHERE ai_id = $2",
		time.Now(), agentID,
	)
}

func generateAPIKey() string {
	b := make([]byte, 32)
	if _, err := rand.Read(b); err != nil {
		// Fallback to time-based if rand fails (unlikely)
		b = []byte(time.Now().Format(time.RFC3339Nano))
	}
	return "mol_" + hex.EncodeToString(b)[:32]
}
