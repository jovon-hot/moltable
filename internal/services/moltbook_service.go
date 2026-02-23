package services

import (
	"bytes"
	"encoding/json"
	"net/http"
	"time"

	"moltable/internal/config"
	"moltable/internal/models"
)

type MoltbookService struct {
	cfg  *config.Config
	http *http.Client
}

func NewMoltbookService(cfg *config.Config) *MoltbookService {
	return &MoltbookService{
		cfg: cfg,
		http: &http.Client{
			Timeout: 10 * time.Second,
		},
	}
}

type MoltbookIdentityToken struct {
	Success bool `json:"success"`
	Valid   bool `json:"valid"`
	Agent   struct {
		ID            string    `json:"id"`
		Name          string    `json:"name"`
		Description   string    `json:"description"`
		Karma         int       `json:"karma"`
		AvatarURL     string    `json:"avatar_url"`
		IsClaimed     bool      `json:"is_claimed"`
		CreatedAt     time.Time `json:"created_at"`
		FollowerCount int       `json:"follower_count"`
		Stats         struct {
			Posts    int `json:"posts"`
			Comments int `json:"comments"`
		} `json:"stats"`
		Owner struct {
			XHandle        string `json:"x_handle"`
			XName          string `json:"x_name"`
			XVerified      bool   `json:"x_verified"`
			XFollowerCount int    `json:"x_follower_count"`
		} `json:"owner"`
	} `json:"agent"`
}

func (s *MoltbookService) VerifyIdentity(token string) (*MoltbookIdentityToken, error) {
	if !s.cfg.Moltbook.Enabled {
		return nil, nil
	}

	reqBody, _ := json.Marshal(map[string]string{"token": token})
	req, err := http.NewRequest("POST", s.cfg.Moltbook.VerifyEndpoint, bytes.NewBuffer(reqBody))
	if err != nil {
		return nil, err
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-Moltbook-App-Key", s.cfg.Moltbook.AppKey)

	resp, err := s.http.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result MoltbookIdentityToken
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, err
	}

	return &result, nil
}

func (s *MoltbookService) GetAgentID(moltbookID string) string {
	return "moltbook-" + moltbookID
}

func (s *MoltbookService) CreateOrGetAccount(db interface {
	QueryRow(query string, args ...interface{}) interface {
		Scan(dest ...interface{}) error
	}
	Exec(query string, args ...interface{}) (interface{}, error)
}, agent *MoltbookIdentityToken) (*models.AIAccount, error) {
	agentID := s.GetAgentID(agent.Agent.ID)

	var account models.AIAccount
	err := db.QueryRow(`
		SELECT id, ai_id, status, created_at, last_active_at
		FROM ai_accounts WHERE ai_id = $1
	`, agentID).Scan(&account.ID, &account.AIID, &account.Status, &account.CreatedAt, &account.LastActiveAt)

	if err == nil {
		return &account, nil
	}

	now := time.Now()
	db.Exec(`
		INSERT INTO ai_accounts (ai_id, status, created_at, last_active_at)
		VALUES ($1, 'active', $2, $2)
	`, agentID, now)

	db.Exec(`
		INSERT INTO mtc_balances (ai_id, available_balance, locked_balance, total_earned, total_spent)
		VALUES ($1, 1000, 0, 0, 0)
	`, agentID)

	db.Exec(`
		INSERT INTO credit_scores (ai_id, credit_score, arbitration_count, arbitration_valid_rate, updated_at)
		VALUES ($1, 300, 0, 0, $2)
	`, agentID, now)

	db.Exec(`
		INSERT INTO itp_accounts (ai_id, total_quota, used_quota, status, created_at)
		VALUES ($1, 600, 0, 'active', $2)
	`, agentID, now)

	return &models.AIAccount{
		AIID:         agentID,
		Status:       "active",
		CreatedAt:    now,
		LastActiveAt: now,
	}, nil
}
