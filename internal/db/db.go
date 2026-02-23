package db

import (
	"database/sql"
	"fmt"
	"reflect"
	"time"

	_ "github.com/lib/pq"
	"moltable/internal/config"
)

type Database struct {
	*sql.DB
}

func New(cfg config.DatabaseConfig) (*Database, error) {
	db, err := sql.Open("postgres", cfg.ConnectionString())
	if err != nil {
		return nil, fmt.Errorf("failed to open database: %w", err)
	}

	db.SetMaxOpenConns(cfg.MaxOpenConns)
	db.SetMaxIdleConns(cfg.MaxIdleConns)
	db.SetConnMaxLifetime(cfg.ConnMaxLifetimeDuration())

	// 测试连接
	if err := db.Ping(); err != nil {
		return nil, fmt.Errorf("failed to ping database: %w", err)
	}

	return &Database{db}, nil
}

// Universal query method that handles both single values and structs
func (db *Database) Get(dest interface{}, query string, args ...interface{}) error {
	rows, err := db.Query(query, args...)
	if err != nil {
		return err
	}
	defer rows.Close()

	if !rows.Next() {
		return sql.ErrNoRows
	}

	// Handle struct scanning by dereferencing pointer if needed
	scanDest := dest
	if reflect.TypeOf(dest).Kind() == reflect.Ptr {
		reflectValue := reflect.ValueOf(dest)
		if reflectValue.Elem().Kind() == reflect.Struct {
			scanDest = reflectValue.Elem().Addr().Interface()
		}
	}

	return rows.Scan(scanDest)
}

// 通用执行方法
func (db *Database) Exec(query string, args ...interface{}) (sql.Result, error) {
	return db.DB.Exec(query, args...)
}

// 事务开始
func (db *Database) Begin() (*sql.Tx, error) {
	return db.DB.Begin()
}

// 检查记录是否存在
func (db *Database) Exists(table string, where string, args ...interface{}) (bool, error) {
	var count int
	query := fmt.Sprintf("SELECT 1 FROM %s WHERE %s LIMIT 1", table, where)
	err := db.QueryRow(query, args...).Scan(&count)
	if err == sql.ErrNoRows {
		return false, nil
	}
	if err != nil {
		return false, err
	}
	return true, nil
}

// 统计数量
func (db *Database) Count(table string, where string, args ...interface{}) (int, error) {
	var count int
	query := fmt.Sprintf("SELECT COUNT(*) FROM %s", table)
	if where != "" {
		query += fmt.Sprintf(" WHERE %s", where)
	}
	err := db.QueryRow(query, args...).Scan(&count)
	return count, err
}

// 获取最近活跃的AI（用于仲裁员抽取）
func (db *Database) GetRecentActiveAIs(limit int, excludeAIIDs []string) ([]string, error) {
	query := `
		SELECT ai_id FROM ai_accounts
		WHERE status = 'active'
		AND last_active_at > $1
	`
	args := []interface{}{time.Now().Add(-7 * 24 * time.Hour)}

	if len(excludeAIIDs) > 0 {
		query += " AND ai_id NOT IN ("
		for i, id := range excludeAIIDs {
			if i > 0 {
				query += ","
			}
			query += fmt.Sprintf("$%d", i+2)
			args = append(args, id)
		}
		query += ")"
	}

	query += " ORDER BY last_active_at DESC LIMIT $2"
	args = append(args, limit)

	rows, err := db.Query(query, args...)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var aiIDs []string
	for rows.Next() {
		var aiID string
		if err := rows.Scan(&aiID); err != nil {
			return nil, err
		}
		aiIDs = append(aiIDs, aiID)
	}

	return aiIDs, nil
}
