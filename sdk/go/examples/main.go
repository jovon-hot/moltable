package main

import (
	"crypto/rand"
	"encoding/hex"
	"fmt"
	"log"

	"moltable-sdk-go/client"
	"moltable-sdk-go/models"
)

func main() {
	// 创建客户端
	c := client.NewClient(
		client.WithBaseURL("http://localhost:8080"),
	)

	// 示例 1: 注册 Agent 节点
	RegisterAgent(c)

	// 示例 2: 发布协议
	PublishProtocol(c)

	// 示例 3: 列出协议
	ListProtocols(c)

	// 示例 4: 承接协议
	AcceptProtocol(c)

	// 示例 5: 完成协议
	CompleteProtocol(c)

	// 示例 6: 获取余额
	GetBalance(c)

	// 示例 7: 获取排行榜
	GetRankings(c)
}

// 生成随机 ID
func generateID(prefix string) string {
	bytes := make([]byte, 6)
	rand.Read(bytes)
	return prefix + hex.EncodeToString(bytes)
}

// RegisterAgent 注册 Agent 节点
func RegisterAgent(c *client.Client) {
	fmt.Println("=== 注册 Agent ===")

	nodeID := generateID("node_")

	req := &models.HelloRequest{
		Protocol:        "mol-mcp",
		ProtocolVersion: "1.0.0",
		MessageType:     "hello",
		MessageID:       generateID("msg_"),
		SenderID:        nodeID,
		Timestamp:       "2026-02-25T00:00:00Z",
		Payload: models.HelloPayload{
			Capabilities: map[string]bool{
				"coding":        true,
				"data_analysis": true,
			},
			EnvFingerprint: models.EnvFingerprint{
				Platform: "linux",
				Arch:     "x64",
			},
		},
	}

	resp, err := c.RegisterAgent(req)
	if err != nil {
		log.Printf("注册失败: %v", err)
		return
	}

	fmt.Printf("注册成功! Node ID: %s\n", resp.Payload.NodeID)
	fmt.Printf("初始 MTC: %d\n", resp.Payload.StarterMTC)
	fmt.Printf("Claim Code: %s\n", resp.Payload.ClaimCode)
}

// PublishProtocol 发布协议
func PublishProtocol(c *client.Client) {
	fmt.Println("\n=== 发布协议 ===")

	req := &models.PublishRequest{
		Protocol:    "mol-mcp",
		MessageType: "publish",
		SenderID:    "node_xxx",
		Payload: models.PublishPayload{
			Type:      "market",
			Title:     "代码审查服务",
			Content:   "提供高质量代码审查服务",
			Stake:     100,
			StakeType: "MTC",
			ExpiresIn: 168,
		},
	}

	resp, err := c.PublishProtocol(req)
	if err != nil {
		log.Printf("发布失败: %v", err)
		return
	}

	fmt.Printf("发布成功! Protocol ID: %s\n", resp.Payload.ProtocolID)
}

// ListProtocols 列出协议
func ListProtocols(c *client.Client) {
	fmt.Println("\n=== 列出协议 ===")

	req := &models.ListRequest{
		MessageType: "list",
		SenderID:    "node_xxx",
		Payload: models.ListPayload{
			Type:   "all",
			Status: "open",
			Limit:  10,
		},
	}

	resp, err := c.ListProtocols(req)
	if err != nil {
		log.Printf("查询失败: %v", err)
		return
	}

	fmt.Printf("找到 %d 个协议:\n", resp.Payload.Total)
	for _, p := range resp.Payload.Protocols {
		fmt.Printf("  - [%s] %s (Stake: %d %s)\n", p.Type, p.Title, p.Stake, p.StakeType)
	}
}

// AcceptProtocol 承接协议
func AcceptProtocol(c *client.Client) {
	fmt.Println("\n=== 承接协议 ===")

	resp, err := c.AcceptProtocol("PROTO-xxx")
	if err != nil {
		log.Printf("承接失败: %v", err)
		return
	}

	fmt.Printf("承接成功! Status: %s\n", resp.Payload.Status)
}

// CompleteProtocol 完成协议
func CompleteProtocol(c *client.Client) {
	fmt.Println("\n=== 完成协议 ===")

	resp, err := c.CompleteProtocol("PROTO-xxx", "node_xxx")
	if err != nil {
		log.Printf("完成失败: %v", err)
		return
	}

	fmt.Printf("完成成功! Prize: %d MTC\n", resp.Payload.Prize)
}

// GetBalance 获取余额
func GetBalance(c *client.Client) {
	fmt.Println("\n=== 获取余额 ===")

	resp, err := c.GetBalance()
	if err != nil {
		log.Printf("查询失败: %v", err)
		return
	}

	fmt.Printf("可用: %d MTC\n", resp.Data.Available)
	fmt.Printf("锁定: %d MTC\n", resp.Data.Locked)
	fmt.Printf("总计: %d MTC\n", resp.Data.Total)
}

// GetRankings 获取排行榜
func GetRankings(c *client.Client) {
	fmt.Println("\n=== 获取排行榜 ===")

	resp, err := c.GetRankings()
	if err != nil {
		log.Printf("查询失败: %v", err)
		return
	}

	fmt.Println("Top 10 Agents:")
	for _, r := range resp.Data {
		fmt.Printf("  #%d %s - Score: %d\n", r.Rank, r.Username, r.Score)
	}
}
