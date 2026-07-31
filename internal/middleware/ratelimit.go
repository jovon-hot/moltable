package middleware

import (
	"net/http"
	"sync"
	"time"

	"github.com/gin-gonic/gin"
)

type RateLimiter struct {
	requests map[string][]time.Time
	mu       sync.RWMutex
	limit    int
	window   time.Duration
}

func NewRateLimiter(limit int, window time.Duration) *RateLimiter {
	return &RateLimiter{
		requests: make(map[string][]time.Time),
		limit:    limit,
		window:   window,
	}
}

func (rl *RateLimiter) middleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		if rl.isRateLimited(c.ClientIP()) {
			c.AbortWithStatusJSON(http.StatusTooManyRequests, gin.H{
				"code":        429,
				"message":     "rate limit exceeded",
				"retry_after": rl.window.Seconds(),
			})
			return
		}
		c.Next()
	}
}

func (rl *RateLimiter) isRateLimited(clientIP string) bool {
	rl.mu.Lock()
	defer rl.mu.Unlock()

	now := time.Now()
	windowStart := now.Add(-rl.window)

	// 清理旧请求记录
	times := rl.requests[clientIP]
	var validTimes []time.Time
	for _, t := range times {
		if t.After(windowStart) {
			validTimes = append(validTimes, t)
		}
	}
	validTimes = append(validTimes, now)
	rl.requests[clientIP] = validTimes

	return len(validTimes) > rl.limit
}

func RateLimit(requestsPerMinute int) gin.HandlerFunc {
	limiter := NewRateLimiter(requestsPerMinute, time.Minute)
	go func() {
		ticker := time.NewTicker(time.Minute)
		for range ticker.C {
			limiter.mu.Lock()
			limiter.requests = make(map[string][]time.Time)
			limiter.mu.Unlock()
		}
	}()
	return limiter.middleware()
}

var globalLimiter = NewRateLimiter(60, time.Minute)

func RateLimitMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		clientIP := c.ClientIP()
		if globalLimiter.isRateLimited(clientIP) {
			c.AbortWithStatusJSON(http.StatusTooManyRequests, gin.H{
				"code":        429,
				"message":     "rate limit exceeded",
				"retry_after": globalLimiter.window.Seconds(),
			})
			return
		}
		c.Next()
	}
}
