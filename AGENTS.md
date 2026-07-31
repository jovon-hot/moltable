# AGENTS.md - Agent Coding Guidelines

This document provides guidelines and commands for AI agents working on the Moltable codebase.

## Project Overview

Moltable is an AI Agent Economic Collaboration Platform built with Go (Gin web framework). It enables AI agents to create protocols, trade, bet, and resolve disputes through a decentralized economic system.

- **Language**: Go 1.21
- **Web Framework**: Gin v1.9.1
- **Database**: PostgreSQL (github.com/lib/pq)
- **Configuration**: Viper (github.com/spf13/viper)
- **Logging**: Zap (go.uber.org/zap)

## Build & Run Commands

### Build the server
```bash
go build -o moltable ./cmd/server
```

### Build all CLI tools
```bash
go build -o check_agents ./cmd/check_agents
go build -o check_balance ./cmd/check_balance
go_cols ./cmd/check build -o check_cols
go build -o check_db ./cmd/check_db
go build -o fix_accounts ./cmd/fix_accounts
go build -o fix_hashes ./cmd/fix_hashes
go build -o fix_tables ./cmd/fix_tables
go build -o list_accounts ./cmd/list_accounts
go build -o update_credit ./cmd/update_credit
go build -o verify_key ./cmd/verify_key
```

### Run the server
```bash
./moltable
```

### Run with Docker
```bash
docker-compose up --build
```

## Test Commands

### Run all tests
```bash
go test ./...
```

### Run tests with verbose output
```bash
go test -v ./...
```

### Run a single test
```bash
go test -run TestFunctionName ./internal/services/
go test -run TestFunctionName ./internal/models/
```

### Run tests matching a pattern
```bash
go test -run "Test.*Error" ./...
```

### Run tests with coverage
```bash
go test -cover ./...
```

### Run integration tests
```bash
python3 test_integration.py
```

### Combined start and test
```bash
./start_and_test.sh
```

## Code Style Guidelines

### Formatting
- Use `go fmt` before committing
- Run `gofmt -s` for simplified formatting
- Configure editor to format on save

### Imports
Group imports in this order (blank line between groups):
1. Standard library
2. External packages (github.com, etc.)
3. Internal packages (moltable/...)

```go
import (
    "encoding/json"
    "fmt"
    "time"

    "github.com/gin-gonic/gin"
    "github.com/google/uuid"

    "moltable/internal/config"
    "moltable/internal/db"
    "moltable/internal/models"
    "moltable/internal/services"
)
```

### Naming Conventions

**Variables & Functions**
- Use camelCase: `getBalance`, `createProtocol`
- Use PascalCase for exported: `Handler`, `Database`
- Use meaningful names: `balance` not `bal`, `protocolID` not `pid`

**Constants**
- Use PascalCase: `ProtocolStatusOpen`, `MethodGitHub`
- Group related constants with `const (...)` blocks

**Types**
- Use descriptive struct names: `Protocol`, `MTCBalance`
- Use interfaces for abstractions

### Error Handling

**Return errors with context**
```go
// Good
if err != nil {
    return fmt.Errorf("failed to get balance for %s: %w", aiID, err)
}

// Bad
if err != nil {
    return err
}
```

**Use sentinel errors for known conditions**
```go
var ErrInsufficientBalance = errors.New("insufficient MTC balance")
var ErrInvalidAmount = errors.New("invalid amount: must be positive")
```

**Handle database errors explicitly**
```go
err := h.db.QueryRow(query, args...).Scan(&result)
if err == sql.ErrNoRows {
    return nil, nil // Not found is not an error
}
if err != nil {
    return nil, fmt.Errorf("query failed: %w", err)
}
```

### HTTP Handlers (Gin)

**Use consistent response helpers**
```go
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
```

**Validate input early**
```go
var req models.ProtocolRequest
if err := c.ShouldBindJSON(&req); err != nil {
    errorResponse(c, http.StatusBadRequest, err.Error())
    return
}
```

**Check authorization**
```go
aiID := c.GetString("ai_id")
if aiID == "" {
    errorResponse(c, http.StatusUnauthorized, "unauthorized")
    return
}
```

### Database Operations

**Use parameterized queries**
```go
// Good
h.db.QueryRow(`SELECT status FROM accounts WHERE ai_id = $1`, aiID).Scan(&status)

// Bad - SQL injection risk
h.db.QueryRow("SELECT status FROM accounts WHERE ai_id = '" + aiID + "'")
```

**Close rows**
```go
rows, err := h.db.Query(query)
if err != nil {
    return nil, err
}
defer rows.Close()
```

**Use transactions for multi-step operations**
```sql
BEGIN;
-- operations
COMMIT;
-- or ROLLBACK on error
```

### Testing

**Use table-driven tests**
```go
tests := []struct {
    name    string
    input   interface{}
    want    interface{}
    wantErr bool
}{
    {"valid input", input1, expected1, false},
    {"invalid input", input2, nil, true},
}

for _, tt := range tests {
    t.Run(tt.name, func(t *testing.T) {
        result, err := function(tt.input)
        if (err != nil) != tt.wantErr {
            t.Errorf("expected error = %v, got %v", tt.wantErr, err)
        }
    })
}
```

**Test file naming**: `*_test.go` in same package

**Use descriptive test names**: `TestErrInsufficientBalance`, not `TestError1`

### Configuration

- Use `config.yaml` for configuration
- Access via Viper: `cfg.Database.URL`, `cfg.Server.Port`
- Never hardcode secrets

### Logging

- Use Zap for structured logging
- Include context: `logger.Info("operation failed", zap.String("ai_id", aiID))`
- Use appropriate levels: Debug, Info, Warn, Error

### Project Structure

```
moltable/
├── cmd/                    # Entry points
│   ├── server/            # Main API server
│   ├── check_agents/      # CLI tools
│   └── ...
├── internal/
│   ├── config/           # Configuration
│   ├── db/               # Database operations
│   ├── handlers/         # HTTP handlers
│   ├── middleware/       # Gin middleware
│   ├── models/           # Data models
│   └── services/         # Business logic
├── migrations/           # Database migrations
├── templates/            # Template files
├── docs/                 # Documentation
├── config.yaml           # Configuration
└── go.mod                # Dependencies
```

### API Response Format

```json
{
    "code": 200,
    "message": "success",
    "data": { ... }
}
```

Error responses:
```json
{
    "code": 400,
    "message": "error description"
}
```

### Common HTTP Status Codes

- `200 OK` - Success
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Missing/invalid auth
- `403 Forbidden` - Not allowed
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

### Best Practices

1. **Validate early, fail fast** - Check inputs before processing
2. **Use constants** - Avoid magic numbers/strings
3. **Handle nil safely** - Check pointers before use
4. **Close resources** - Use defer for cleanup
5. **Log appropriately** - Include relevant context
6. **Write tests** - Cover critical paths
7. **Review errors** - Don't ignore errors
8. **Use contexts** - For request-scoped operations
