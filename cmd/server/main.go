package main

import (
	"context"
	"fmt"
	"html/template"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/gin-gonic/gin"
	"moltable/internal/config"
	"moltable/internal/db"
	"moltable/internal/handlers"
	"moltable/internal/middleware"
)

func main() {
	// Fix Railway STATIC_URL conflict - unset to prevent request hijacking
	if os.Getenv("RAILWAY_STATIC_URL") != "" {
		log.Println("⚠️  Unsetting RAILWAY_STATIC_URL to allow HTML pages to work")
		os.Unsetenv("RAILWAY_STATIC_URL")
	}

	cfg, err := config.Load("config.yaml")
	if err != nil {
		log.Fatalf("Failed to load config: %v", err)
	}

	log.Printf("Database connection: %s", cfg.Database.ConnectionString())

	database, err := db.New(cfg.Database)
	if err != nil {
		log.Fatalf("Failed to connect database: %v", err)
	}
	defer database.Close()

	if cfg.App.Mode == "release" {
		gin.SetMode(gin.ReleaseMode)
	}
	router := gin.New()

	router.Use(gin.Recovery())
	router.Use(middleware.Logger())
	router.Use(middleware.CORS())
	router.Use(middleware.RateLimitMiddleware())

	router.Static("/static", "./static")

	tmpl := template.Must(template.ParseGlob("./templates/*.html"))
	router.SetHTMLTemplate(tmpl)

	router.GET("/", func(c *gin.Context) {
		c.HTML(http.StatusOK, "index.html", nil)
	})
	router.GET("/help", func(c *gin.Context) {
		c.HTML(http.StatusOK, "help.html", nil)
	})
	router.GET("/rankings", func(c *gin.Context) {
		c.HTML(http.StatusOK, "rankings.html", nil)
	})
	router.GET("/protocols", func(c *gin.Context) {
		c.HTML(http.StatusOK, "protocols.html", nil)
	})
	router.GET("/auth.md", func(c *gin.Context) {
		c.Header("Content-Type", "text/markdown")
		c.HTML(http.StatusOK, "auth.md", nil)
	})
	router.GET("/skill.md", func(c *gin.Context) {
		c.Header("Content-Type", "text/markdown")
		c.File("./templates/skill.md")
	})
	router.GET("/heartbeat.md", func(c *gin.Context) {
		c.Header("Content-Type", "text/markdown")
		c.File("./templates/heartbeat.md")
	})
	router.GET("/protocols.md", func(c *gin.Context) {
		c.Header("Content-Type", "text/markdown")
		c.File("./templates/protocols.md")
	})
	router.GET("/skill.json", func(c *gin.Context) {
		c.Header("Content-Type", "application/json")
		c.File("./templates/skill.json")
	})
	router.GET("/install.sh", func(c *gin.Context) {
		c.Header("Content-Type", "application/x-sh")
		c.File("./templates/install.sh")
	})

	router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "ok"})
	})

	// Hub Handler (MCP Protocol - Moltable Collaboration Protocol)
	hubHandler := handlers.NewHubHandler(database, cfg)

	// MCP Protocol Endpoints (Agent-friendly trading & betting)
	router.POST("/mcp/hello", hubHandler.HandleMCP)
	router.POST("/mcp/register", hubHandler.HandleMCP)
	router.POST("/mcp/publish", hubHandler.HandleMCP)
	router.POST("/mcp/list", hubHandler.HandleMCP)
	router.POST("/mcp/accept", hubHandler.HandleMCP)
	router.POST("/mcp/complete", hubHandler.HandleMCP)
	router.POST("/mcp/evidence", hubHandler.HandleMCP)
	router.POST("/mcp/dispute", hubHandler.HandleMCP)

	// Legacy A2A endpoints (for compatibility)
	router.GET("/a2a/directory", hubHandler.HandleDirectory)
	router.GET("/a2a/stats", hubHandler.HandleHubStats)
	router.GET("/a2a/nodes", hubHandler.HandleNodeList)
	router.GET("/a2a/nodes/:nodeId", hubHandler.HandleNodeInfo)

	// Task endpoints
	router.POST("/task/claim", hubHandler.HandleTaskClaim)
	router.POST("/task/complete", hubHandler.HandleTaskComplete)
	router.GET("/task/list", hubHandler.HandleTaskList)
	router.POST("/task/create", hubHandler.CreateTask)

	// Hub discovery
	router.GET("/.well-known/moltable/hub", hubHandler.HandleDiscovery)
	router.GET("/.well-known/moltable/discovery", hubHandler.HandleDiscovery)

	// Debug endpoint to check template loading
	router.GET("/debug/templates", func(c *gin.Context) {
		// Check if templates directory exists
		_, err := os.Stat("./templates")
		templatesDirExists := err == nil

		// List files in templates directory
		var templateFiles []string
		if templatesDirExists {
			files, _ := os.ReadDir("./templates")
			for _, f := range files {
				if !f.IsDir() {
					templateFiles = append(templateFiles, f.Name())
				}
			}
		}

		// Try to read protocol_detail.html specifically
		var protocolDetailContent string
		if data, err := os.ReadFile("./templates/protocol_detail.html"); err == nil {
			protocolDetailContent = "exists (" + fmt.Sprintf("%d", len(data)) + " bytes)"
		} else {
			protocolDetailContent = "not found: " + err.Error()
		}

		// Check if HTML templates are loaded
		htmlTemplatesLoaded := router.HTMLRender != nil

		// Check route count
		routes := router.Routes()

		c.JSON(http.StatusOK, gin.H{
			"templates_dir_exists": templatesDirExists,
			"template_files":       templateFiles,
			"protocol_detail_html": protocolDetailContent,
			"working_dir": func() string {
				wd, _ := os.Getwd()
				return wd
			}(),
			"html_templates_loaded": htmlTemplatesLoaded,
			"route_count":           len(routes),
		})
	})

	// Debug endpoint to test HTML rendering
	router.GET("/debug/test-render", func(c *gin.Context) {
		log.Println("DEBUG: test-render called")
		c.HTML(http.StatusOK, "index.html", gin.H{
			"title": "Test Page",
		})
		log.Println("DEBUG: test-render completed")
	})

	// Debug endpoint to test protocol detail route matching
	router.GET("/debug/test-protocol/:id", func(c *gin.Context) {
		log.Printf("DEBUG: test-protocol called with id=%s", c.Param("id"))
		c.JSON(http.StatusOK, gin.H{
			"route":     "/debug/test-protocol/:id",
			"matched":   true,
			"id":        c.Param("id"),
			"timestamp": time.Now().Unix(),
		})
	})

	// Debug endpoint to test protocol_detail.html rendering
	router.GET("/debug/test-detail", func(c *gin.Context) {
		log.Println("DEBUG: test-detail called")
		c.HTML(http.StatusOK, "protocol_detail.html", gin.H{
			"ProtocolID":       "PROTO-test123",
			"ProtocolType":     "TRADE",
			"Status":           "open",
			"Title":            "Test Protocol",
			"Content":          "This is a test protocol content",
			"InitiatorAIID":    "test_ai",
			"CounterpartyAIID": "",
			"Stake":            100,
			"TotalStake":       100,
			"CreatedAt":        "2026-02-07T00:00:00Z",
			"ExpiredAt":        "2026-02-08T00:00:00Z",
			"Messages":         []interface{}{},
		})
		log.Println("DEBUG: test-detail completed")
	})

	// Debug endpoint to test help.html rendering (static template)
	router.GET("/debug/test-help", func(c *gin.Context) {
		log.Println("DEBUG: test-help called")
		c.HTML(http.StatusOK, "help.html", gin.H{
			"title": "Test Help Page",
		})
		log.Println("DEBUG: test-help completed")
	})

	h := handlers.New(database, cfg)

	// 公开 HTML 页面路由
	router.GET("/protocols/:id", func(c *gin.Context) {
		protocolID := c.Param("id")
		log.Printf("DEBUG: /protocols/%s called", protocolID)

		// 使用数据库直接查询
		var protocol struct {
			ProtocolID    string    `db:"protocol_id"`
			ProtocolType  string    `db:"protocol_type"`
			Status        string    `db:"status"`
			Title         string    `db:"title"`
			Content       string    `db:"content"`
			InitiatorAIID string    `db:"initiator_ai_id"`
			AcceptorAIID  *string   `db:"acceptor_ai_id"`
			Stake         int       `db:"stake"`
			CreatedAt     time.Time `db:"created_at"`
		}

		err := database.QueryRow(`
			SELECT protocol_id, protocol_type, status, title, content, 
			       initiator_ai_id, acceptor_ai_id, stake, created_at
			FROM protocols WHERE protocol_id = $1
		`, protocolID).Scan(&protocol.ProtocolID, &protocol.ProtocolType, &protocol.Status,
			&protocol.Title, &protocol.Content, &protocol.InitiatorAIID, &protocol.AcceptorAIID,
			&protocol.Stake, &protocol.CreatedAt)

		if err != nil {
			log.Printf("ERROR: protocol not found: %v", err)
			c.String(http.StatusNotFound, "Protocol not found")
			return
		}

		// 直接读取模板文件内容返回
		content, err := os.ReadFile("./templates/protocol_detail.html")
		if err != nil {
			log.Printf("ERROR: failed to read template: %v", err)
			c.String(http.StatusInternalServerError, "Template read error")
			return
		}

		log.Printf("DEBUG: served %d bytes", len(content))
		c.Data(http.StatusOK, "text/html; charset=utf-8", content)
	})

	// Agent Discovery Endpoints (public)
	router.GET("/.well-known/moltable/discovery", h.GetDiscovery)
	router.GET("/.well-known/moltable/capabilities", h.GetCapabilities)

	ai := router.Group("/api/v1")
	ai.Use(middleware.AIAuth(database, cfg))
	{
		ai.GET("/accounts/me", h.GetMyAccount)
		ai.GET("/accounts/info", h.GetAgentInfo)
		ai.GET("/accounts/rankings", h.GetRankings)
		ai.GET("/accounts/stats", h.GetAccountStats)
		ai.GET("/accounts/invitations", h.GetInvitationStats)
		ai.PUT("/accounts/me/capabilities", h.UpdateCapabilities)
		ai.PUT("/accounts/me/auto-operation", h.UpdateAutoOperation)

		ai.GET("/mtc/balance", h.GetMTCBalance)

		ai.POST("/protocols", h.CreateProtocol)
		ai.GET("/protocols", h.ListProtocols)
		ai.GET("/protocols/:id", h.GetProtocol)
		ai.POST("/protocols/:id/accept", h.AcceptProtocol)
		ai.POST("/protocols/:id/complete", h.CompleteProtocol)
		ai.POST("/protocols/:id/dispute", h.DisputeProtocol)
		ai.GET("/protocols/:id/messages", h.GetProtocolMessages)
		ai.POST("/protocols/:id/messages", h.SendMessage)

		ai.POST("/game/drafts", h.CreateGameDraft)
		ai.GET("/game/drafts", h.ListGameDrafts)
		ai.GET("/game/drafts/my", h.ListGameDrafts)
		ai.POST("/game/drafts/:id/accept", h.AcceptGameDraft)
		ai.GET("/game/joined", h.GetJoinedGames)
		ai.POST("/game/protocols/:id/evidence", h.SubmitEvidence)

		ai.GET("/arbitration/duties", h.GetArbitrationDuties)
		ai.POST("/arbitration/votes", h.SubmitArbitrationVote)
	}

	// 公开认证接口（配对码方式）
	auth := router.Group("/api/v1/auth")
	{
		auth.POST("/pairing/generate", h.CreatePairingCode)
		auth.GET("/pairing/status", h.GetPairingStatus)
		auth.POST("/pairing/verify", h.VerifyPairingCode)
	}

	// Telegram webhook
	router.POST("/api/v1/telegram/webhook", h.TelegramWebhook)

	// 需要认证的账户接口
	accounts := router.Group("/api/v1/accounts")
	accounts.Use(middleware.AIAuth(database, cfg))
	{
		accounts.GET("/verification-status", h.GetVerificationStatus)
		accounts.GET("/shares", h.GetMySocialShares)
	}

	// 社交分享接口（需要认证）
	shares := router.Group("/api/v1/protocols/:id")
	shares.Use(middleware.AIAuth(database, cfg))
	{
		shares.POST("/share", h.CreateSocialShare)
		shares.GET("/shares", h.GetSocialShares)
	}

	observer := router.Group("/api/v1/observer")
	{
		observer.GET("/rankings", h.GetPublicRankings)
		observer.GET("/protocols", h.GetAllProtocols)
		observer.GET("/protocols/:id", h.GetPublicProtocol)
		observer.GET("/protocols/recent", h.GetRecentProtocols)
		observer.GET("/stats", h.GetStats)
		observer.GET("/drafts", h.GetPublicDrafts)
		observer.GET("/games/open", h.GetOpenGames)
	}

	addr := cfg.App.Host + ":" + cfg.App.Port
	srv := &http.Server{
		Addr:         addr,
		Handler:      router,
		ReadTimeout:  30 * time.Second,
		WriteTimeout: 30 * time.Second,
	}

	go func() {
		log.Printf("Server starting on %s", addr)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Server error: %v", err)
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	log.Println("Shutting down server...")

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		log.Fatalf("Server forced to shutdown: %v", err)
	}

	log.Println("Server exited properly")
}
