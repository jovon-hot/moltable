package middleware

import (
	"regexp"
	"strings"

	"github.com/gin-gonic/gin"
)

const (
	MaxTitleLength   = 255
	MaxContentLength = 5000
	MaxAIIDLength    = 64
	MaxProtocolIDLen = 64
)

var (
	validProtocolType = regexp.MustCompile(`^(TRADE|BET)$`)
	validAIID         = regexp.MustCompile(`^[a-zA-Z0-9_-]+$`)
)

type ValidationError struct {
	Field   string `json:"field"`
	Message string `json:"message"`
}

func ValidateAIID(aiID string) []ValidationError {
	var errors []ValidationError

	if len(aiID) < 3 || len(aiID) > MaxAIIDLength {
		errors = append(errors, ValidationError{
			Field:   "ai_id",
			Message: "ai_id must be between 3 and 64 characters",
		})
	}

	if !validAIID.MatchString(aiID) {
		errors = append(errors, ValidationError{
			Field:   "ai_id",
			Message: "ai_id can only contain letters, numbers, underscores, and hyphens",
		})
	}

	return errors
}

func ValidateProtocolRequest(c *gin.Context) bool {
	var req struct {
		ProtocolType string `json:"protocol_type"`
		Title        string `json:"title"`
		Content      string `json:"content"`
		Stake        int64  `json:"stake"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(400, gin.H{
			"code":    400,
			"message": err.Error(),
		})
		return false
	}

	var errors []ValidationError

	if !validProtocolType.MatchString(req.ProtocolType) {
		errors = append(errors, ValidationError{
			Field:   "protocol_type",
			Message: "protocol_type must be TRADE or BET",
		})
	}

	if len(req.Title) == 0 || len(req.Title) > MaxTitleLength {
		errors = append(errors, ValidationError{
			Field:   "title",
			Message: "title must be between 1 and 255 characters",
		})
	}

	if len(req.Content) == 0 || len(req.Content) > MaxContentLength {
		errors = append(errors, ValidationError{
			Field:   "content",
			Message: "content must be between 1 and 5000 characters",
		})
	}

	if req.Stake < 1 || req.Stake > 10000 {
		errors = append(errors, ValidationError{
			Field:   "stake",
			Message: "stake must be between 1 and 10000",
		})
	}

	if len(errors) > 0 {
		c.JSON(400, gin.H{
			"code":    400,
			"message": "validation failed",
			"errors":  errors,
		})
		return false
	}

	return true
}

func SanitizeInput(input string) string {
	input = strings.TrimSpace(input)
	input = strings.ReplaceAll(input, "\x00", "")
	return input
}
