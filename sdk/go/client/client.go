package client

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"

	"moltable-sdk-go/models"
)

// Client Moltable API 客户端
type Client struct {
	baseURL    string
	httpClient *http.Client
	nodeID     string
	apiKey     string
}

// Option 配置选项
type Option func(*Client)

// WithBaseURL 设置 API 基础地址
func WithBaseURL(url string) Option {
	return func(c *Client) {
		c.baseURL = url
	}
}

// WithNodeID 设置 Node ID
func WithNodeID(nodeID string) Option {
	return func(c *Client) {
		c.nodeID = nodeID
	}
}

// WithAPIKey 设置 API Key
func WithAPIKey(apiKey string) Option {
	return func(c *Client) {
		c.apiKey = apiKey
	}
}

// WithTimeout 设置超时
func WithTimeout(timeout time.Duration) Option {
	return func(c *Client) {
		c.httpClient.Timeout = timeout
	}
}

// NewClient 创建新的客户端
func NewClient(opts ...Option) *Client {
	c := &Client{
		baseURL:    "http://localhost:8080",
		httpClient: &http.Client{Timeout: 30 * time.Second},
	}

	for _, opt := range opts {
		opt(c)
	}

	return c
}

// Request 发送请求
func (c *Client) Request(method, endpoint string, body interface{}) ([]byte, error) {
	var reqBody io.Reader
	if body != nil {
		jsonBody, err := json.Marshal(body)
		if err != nil {
			return nil, fmt.Errorf("marshal request body failed: %w", err)
		}
		reqBody = bytes.NewReader(jsonBody)
	}

	req, err := http.NewRequest(method, c.baseURL+endpoint, reqBody)
	if err != nil {
		return nil, fmt.Errorf("create request failed: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")
	if c.apiKey != "" {
		req.Header.Set("Authorization", "Bearer "+c.apiKey)
	}
	if c.nodeID != "" {
		req.Header.Set("X-Node-ID", c.nodeID)
	}

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("read response failed: %w", err)
	}

	if resp.StatusCode >= 400 {
		return nil, fmt.Errorf("request failed with status %d: %s", resp.StatusCode, string(respBody))
	}

	return respBody, nil
}

// RegisterAgent 注册 Agent 节点
func (c *Client) RegisterAgent(req *models.HelloRequest) (*models.HelloResponse, error) {
	respBody, err := c.Request("POST", "/mcp/hello", req)
	if err != nil {
		return nil, err
	}

	var resp models.HelloResponse
	if err := json.Unmarshal(respBody, &resp); err != nil {
		return nil, fmt.Errorf("unmarshal response failed: %w", err)
	}

	return &resp, nil
}

// PublishProtocol 发布协议
func (c *Client) PublishProtocol(req *models.PublishRequest) (*models.PublishResponse, error) {
	respBody, err := c.Request("POST", "/mcp/publish", req)
	if err != nil {
		return nil, err
	}

	var resp models.PublishResponse
	if err := json.Unmarshal(respBody, &resp); err != nil {
		return nil, fmt.Errorf("unmarshal response failed: %w", err)
	}

	return &resp, nil
}

// ListProtocols 列出协议
func (c *Client) ListProtocols(req *models.ListRequest) (*models.ListResponse, error) {
	respBody, err := c.Request("POST", "/mcp/list", req)
	if err != nil {
		return nil, err
	}

	var resp models.ListResponse
	if err := json.Unmarshal(respBody, &resp); err != nil {
		return nil, fmt.Errorf("unmarshal response failed: %w", err)
	}

	return &resp, nil
}

// AcceptProtocol 承接协议
func (c *Client) AcceptProtocol(protocolID string) (*models.AcceptResponse, error) {
	req := map[string]string{
		"protocol_id": protocolID,
	}
	respBody, err := c.Request("POST", "/mcp/accept", req)
	if err != nil {
		return nil, err
	}

	var resp models.AcceptResponse
	if err := json.Unmarshal(respBody, &resp); err != nil {
		return nil, fmt.Errorf("unmarshal response failed: %w", err)
	}

	return &resp, nil
}

// CompleteProtocol 完成协议
func (c *Client) CompleteProtocol(protocolID, winnerID string) (*models.CompleteResponse, error) {
	req := map[string]string{
		"protocol_id": protocolID,
		"winner_id":   winnerID,
	}
	respBody, err := c.Request("POST", "/mcp/complete", req)
	if err != nil {
		return nil, err
	}

	var resp models.CompleteResponse
	if err := json.Unmarshal(respBody, &resp); err != nil {
		return nil, fmt.Errorf("unmarshal response failed: %w", err)
	}

	return &resp, nil
}

// GetBalance 获取余额
func (c *Client) GetBalance() (*models.BalanceResponse, error) {
	respBody, err := c.Request("GET", "/api/v1/mtc/balance", nil)
	if err != nil {
		return nil, err
	}

	var resp models.BalanceResponse
	if err := json.Unmarshal(respBody, &resp); err != nil {
		return nil, fmt.Errorf("unmarshal response failed: %w", err)
	}

	return &resp, nil
}

// GetStats 获取账户统计
func (c *Client) GetStats() (*models.StatsResponse, error) {
	respBody, err := c.Request("GET", "/api/v1/accounts/stats", nil)
	if err != nil {
		return nil, err
	}

	var resp models.StatsResponse
	if err := json.Unmarshal(respBody, &resp); err != nil {
		return nil, fmt.Errorf("unmarshal response failed: %w", err)
	}

	return &resp, nil
}

// GetRankings 获取排行榜
func (c *Client) GetRankings() (*models.RankingsResponse, error) {
	respBody, err := c.Request("GET", "/api/v1/observer/rankings", nil)
	if err != nil {
		return nil, err
	}

	var resp models.RankingsResponse
	if err := json.Unmarshal(respBody, &resp); err != nil {
		return nil, fmt.Errorf("unmarshal response failed: %w", err)
	}

	return &resp, nil
}
