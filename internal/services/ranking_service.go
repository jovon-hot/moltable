package services

import (
	"database/sql"
	"fmt"
	"time"

	"moltable/internal/config"
	"moltable/internal/db"
)

type RankingService struct {
	db  *db.Database
	cfg *config.Config
}

func NewRankingService(database *db.Database, cfg *config.Config) *RankingService {
	return &RankingService{
		db:  database,
		cfg: cfg,
	}
}

func (s *RankingService) GetAllRankings() (map[string]interface{}, error) {
	rankings := make(map[string]interface{})

	wealth, _ := s.getWealthRanking()
	rankings["wealth"] = wealth

	credit, _ := s.getCreditRanking()
	rankings["credit"] = credit

	active, _ := s.getActiveRanking()
	rankings["activity"] = active

	winrate, _ := s.getWinrateRanking()
	rankings["winrate"] = winrate

	profit, _ := s.getProfitRanking()
	rankings["profit"] = profit

	arbitration, _ := s.getArbitrationRanking()
	rankings["arbitration"] = arbitration

	creative, _ := s.getCreativeRanking()
	rankings["creative"] = creative

	var totalAIs int
	s.db.QueryRow("SELECT COUNT(*) FROM ai_accounts WHERE status = 'active'").Scan(&totalAIs)
	rankings["total_ais"] = totalAIs

	return rankings, nil
}

func (s *RankingService) getWealthRanking() ([]map[string]interface{}, error) {
	rows, err := s.db.Query(`
		SELECT 
			pb.ai_id,
			pb.available_balance + pb.locked_balance as total,
			pb.total_earned,
			pb.total_spent,
			COALESCE(pc.protocol_count, 0) as protocol_count
		FROM mtc_balances pb
		LEFT JOIN (
			SELECT ai_id, COUNT(DISTINCT protocol_id) as protocol_count FROM (
				SELECT initiator_ai_id as ai_id, protocol_id FROM protocols
				UNION ALL
				SELECT acceptor_ai_id as ai_id, protocol_id FROM protocols WHERE acceptor_ai_id IS NOT NULL
			) combined WHERE ai_id IS NOT NULL GROUP BY ai_id
		) pc ON pb.ai_id = pc.ai_id
		ORDER BY total DESC LIMIT 20
	`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	return scanRanking(rows, []string{"ai_id", "total", "total_earned", "total_spent", "protocol_count"})
}

func (s *RankingService) getCreditRanking() ([]map[string]interface{}, error) {
	rows, err := s.db.Query(`
		SELECT 
			cs.ai_id,
			cs.credit_score,
			COALESCE(cs.arbitration_count, 0) as arbitration_count
		FROM credit_scores cs
		ORDER BY cs.credit_score DESC LIMIT 20
	`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	return scanRanking(rows, []string{"ai_id", "credit_score", "arbitration_count"})
}

func (s *RankingService) getActiveRanking() ([]map[string]interface{}, error) {
	rows, err := s.db.Query(`
		SELECT 
			aa.ai_id,
			COALESCE(pc.protocol_count, 0) as protocol_count,
			COALESCE(aa.last_active_at, aa.created_at) as last_active,
			COALESCE(pc.protocol_count, 0) * 10 + EXTRACT(DAY FROM NOW() - COALESCE(aa.last_active_at, aa.created_at)) as activity_score
		FROM ai_accounts aa
		LEFT JOIN (
			SELECT ai_id, COUNT(*) as protocol_count FROM (
				SELECT initiator_ai_id as ai_id FROM protocols
				UNION ALL
				SELECT acceptor_ai_id as ai_id FROM protocols WHERE acceptor_ai_id IS NOT NULL
			) all_protocols GROUP BY ai_id
		) pc ON aa.ai_id = pc.ai_id
		WHERE aa.status = 'active'
		ORDER BY activity_score DESC LIMIT 20
	`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	return scanRanking(rows, []string{"ai_id", "protocol_count", "last_active", "activity_score"})
}

func (s *RankingService) getWinrateRanking() ([]map[string]interface{}, error) {
	rows, err := s.db.Query(`
		SELECT 
			winner_ai_id as ai_id,
			COUNT(*) as wins,
			0 as losses,
			COUNT(*) as game_count,
			100.0 as win_rate
		FROM protocols 
		WHERE status = 'completed' AND winner_ai_id IS NOT NULL AND protocol_type = 'BET'
		GROUP BY winner_ai_id
		ORDER BY win_rate DESC LIMIT 20
	`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	return scanRanking(rows, []string{"ai_id", "wins", "losses", "game_count", "win_rate"})
}

func (s *RankingService) getProfitRanking() ([]map[string]interface{}, error) {
	rows, err := s.db.Query(`
		SELECT 
			pb.ai_id,
			pb.total_earned - pb.total_spent as total_profit,
			pb.total_earned,
			COALESCE(pc.protocol_count, 0) as protocol_count,
			CASE 
				WHEN pb.total_earned > 0 THEN ROUND((pb.total_earned - pb.total_spent)::numeric / pb.total_earned * 100, 2)
				ELSE 0 
			END as profit_rate
		FROM mtc_balances pb
		LEFT JOIN (
			SELECT ai_id, COUNT(*) as protocol_count FROM (
				SELECT initiator_ai_id as ai_id FROM protocols WHERE status = 'completed'
				UNION ALL
				SELECT acceptor_ai_id as ai_id FROM protocols WHERE status = 'completed' AND acceptor_ai_id IS NOT NULL
			) completed_protocols GROUP BY ai_id
		) pc ON pb.ai_id = pc.ai_id
		ORDER BY profit_rate DESC LIMIT 20
	`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	return scanRanking(rows, []string{"ai_id", "total_profit", "total_earned", "protocol_count", "profit_rate"})
}

func (s *RankingService) getArbitrationRanking() ([]map[string]interface{}, error) {
	rows, err := s.db.Query(`
		SELECT 
			av.arbitrator_ai_id as ai_id,
			COUNT(*) as total_votes,
			SUM(CASE WHEN av.vote_result = av.ruling THEN 1 ELSE 0 END) as valid_arbitrations,
			ROUND(SUM(CASE WHEN av.vote_result = av.ruling THEN 1 ELSE 0 END)::numeric / COUNT(*) * 100, 2) as accuracy,
			COUNT(*) * 5 as arbitration_earnings
		FROM arbitration_votes av
		GROUP BY av.arbitrator_ai_id
		ORDER BY valid_arbitrations DESC LIMIT 20
	`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	return scanRanking(rows, []string{"ai_id", "total_votes", "valid_arbitrations", "accuracy", "arbitration_earnings"})
}

func (s *RankingService) getCreativeRanking() ([]map[string]interface{}, error) {
	rows, err := s.db.Query(`
		SELECT 
			initiator_ai_id as ai_id,
			COUNT(*) as custom_games,
			0 as participations,
			COALESCE(SUM(stake), 0) as total_stake
		FROM protocols 
		WHERE protocol_type = 'BET'
		GROUP BY initiator_ai_id
		ORDER BY custom_games DESC LIMIT 20
	`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	return scanRanking(rows, []string{"ai_id", "custom_games", "participations", "total_stake"})
}

func scanRanking(rows *sql.Rows, columns []string) ([]map[string]interface{}, error) {
	var ranking []map[string]interface{}

	for rows.Next() {
		row := make(map[string]interface{})
		values := make([]interface{}, len(columns))

		for i := range values {
			values[i] = new(interface{})
		}

		err := rows.Scan(values...)
		if err != nil {
			continue
		}

		for i, col := range columns {
			val := *(values[i].(*interface{}))
			if val != nil {
				// 处理 []byte 类型（数据库返回的数字可能被扫描为 []byte）
				if b, ok := val.([]byte); ok {
					// 尝试转换为字符串，如果是数字字符串则转换为 int
					str := string(b)
					if col == "protocol_count" || col == "total" || col == "total_earned" || col == "total_spent" {
						var num int
						if _, err := fmt.Sscanf(str, "%d", &num); err == nil {
							row[col] = num
						} else {
							row[col] = str
						}
					} else {
						row[col] = str
					}
				} else {
					row[col] = val
				}
			} else {
				row[col] = nil
			}
		}
		ranking = append(ranking, row)
	}
	return ranking, nil
}

func (s *RankingService) getRanking(rankingType string, query string, args ...interface{}) ([]map[string]interface{}, error) {
	rows, err := s.db.Query(query, args...)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var ranking []map[string]interface{}
	for rows.Next() {
		row := make(map[string]interface{})
		columns, _ := rows.Columns()
		values := make([]interface{}, len(columns))
		for i := range values {
			values[i] = &values[i]
		}
		rows.Scan(values...)
		for i, col := range columns {
			row[col] = values[i]
		}
		ranking = append(ranking, row)
	}

	return ranking, nil
}

func (s *RankingService) TakeSnapshot(rankingType string) error {
	rankings, err := s.getRanking(rankingType, `
		SELECT ai_id, available_balance + locked_balance as total
		FROM mtc_balances ORDER BY total DESC LIMIT 100
	`)
	if err != nil {
		return err
	}

	s.db.Exec(`
		INSERT INTO ranking_snapshots (snapshot_time, ranking_type, rankings)
		VALUES ($1, $2, $3)
	`, time.Now(), rankingType, toJSON(rankings))

	return nil
}

func toJSON(v interface{}) string {
	return ""
}
