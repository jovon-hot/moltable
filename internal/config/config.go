package config

import (
	"fmt"
	"os"
	"time"

	"github.com/spf13/viper"
)

type Config struct {
	App      AppConfig      `mapstructure:"app"`
	Moltbook MoltbookConfig `mapstructure:"moltbook"`
	Database DatabaseConfig `mapstructure:"database"`
	Cache    CacheConfig    `mapstructure:"cache"`
	Game     GameConfig     `mapstructure:"game"`
	Protocol ProtocolConfig `mapstructure:"protocol"`
	ITP      ITPConfig      `mapstructure:"itp"`
	Ranking  RankingConfig  `mapstructure:"ranking"`
	Log      LogConfig      `mapstructure:"log"`
	Observer ObserverConfig `mapstructure:"observer"`
	Telegram TelegramConfig `mapstructure:"telegram"`
	Polygon  PolygonConfig  `mapstructure:"polygon"`
}

type AppConfig struct {
	Name string `mapstructure:"name"`
	Host string `mapstructure:"host"`
	Port string `mapstructure:"port"`
	Mode string `mapstructure:"mode"`
}

type MoltbookConfig struct {
	Enabled        bool   `mapstructure:"enabled"`
	AppKey         string `mapstructure:"app_key"`
	VerifyEndpoint string `mapstructure:"verify_endpoint"`
}

type DatabaseConfig struct {
	URL             string `mapstructure:"url"`
	Host            string `mapstructure:"host"`
	Port            int    `mapstructure:"port"`
	Username        string `mapstructure:"username"`
	Password        string `mapstructure:"password"`
	Name            string `mapstructure:"name"`
	MaxOpenConns    int    `mapstructure:"max_open_conns"`
	MaxIdleConns    int    `mapstructure:"max_idle_conns"`
	ConnMaxLifetime string `mapstructure:"conn_max_lifetime"`
	SocketDir       string `mapstructure:"socket_dir"`
}

// GetURL returns the database URL from environment or config
func (d *DatabaseConfig) GetURL() string {
	// Check DATABASE_URL environment variable first (Railway sets this)
	if url := os.Getenv("DATABASE_URL"); url != "" {
		return url
	}
	return d.URL
}

func (d *DatabaseConfig) ConnectionString() string {
	// Check DATABASE_URL environment variable first (Railway sets this)
	if url := d.GetURL(); url != "" {
		return url
	}
	if d.SocketDir != "" {
		if d.Password != "" {
			return fmt.Sprintf("host=%s user=%s password=%s dbname=%s sslmode=disable",
				d.SocketDir, d.Username, d.Password, d.Name)
		}
		return fmt.Sprintf("host=%s user=%s dbname=%s sslmode=disable",
			d.SocketDir, d.Username, d.Name)
	}
	if d.Password != "" {
		return fmt.Sprintf("host=%s port=%d user=%s password=%s dbname=%s sslmode=disable",
			d.Host, d.Port, d.Username, d.Password, d.Name)
	}
	return fmt.Sprintf("host=%s port=%d user=%s dbname=%s sslmode=disable",
		d.Host, d.Port, d.Username, d.Name)
}

func (d *DatabaseConfig) ConnMaxLifetimeDuration() time.Duration {
	duration, _ := time.ParseDuration(d.ConnMaxLifetime)
	return duration
}

type CacheConfig struct {
	Enabled bool          `mapstructure:"enabled"`
	TTL     time.Duration `mapstructure:"ttl"`
}

type GameConfig struct {
	DefaultStake       int     `mapstructure:"default_stake"`
	MaxStake           int     `mapstructure:"max_stake"`
	ArbitrationFeeRate float64 `mapstructure:"arbitration_fee_rate"`
	MinArbitratorScore int     `mapstructure:"min_arbitrator_score"`
	ArbitratorCount    int     `mapstructure:"arbitrator_count"`
	DraftExpireHours   int     `mapstructure:"draft_expire_hours"`

	// 仲裁者资格要求
	MinArbitratorCreditScore  int     `mapstructure:"min_arbitrator_credit_score"`  // 最低信用分
	ArbitratorMTCCStake       int64   `mapstructure:"arbitrator_mtc_stake"`         // 质押 MTC 数量
	ArbitratorUSDCStake       float64 `mapstructure:"arbitrator_usdc_stake"`        // 质押 USDC 数量
	MaxArbitratorsPerProtocol int     `mapstructure:"max_arbitrators_per_protocol"` // 每协议最大仲裁者
}

type ITPConfig struct {
	Enabled            bool `mapstructure:"enabled"`
	InitialQuota       int  `mapstructure:"initial_quota"`
	MaxBorrow          int  `mapstructure:"max_borrow"`
	DefaultCreditScore int  `mapstructure:"default_credit_score"`
}

type RankingConfig struct {
	SnapshotInterval time.Duration `mapstructure:"snapshot_interval"`
}

type LogConfig struct {
	Level  string `mapstructure:"level"`
	Format string `mapstructure:"format"`
}

type ObserverConfig struct {
	Enabled  bool          `mapstructure:"enabled"`
	CacheTTL time.Duration `mapstructure:"cache_ttl"`
}
type ProtocolConfig struct {
	DailyNoStakeLimit int `mapstructure:"daily_no_stake_limit"` // v2.3: 每个Agent每天最多发布4个无质押任务
}

type PolygonConfig struct {
	Enabled         bool   `mapstructure:"enabled"`
	Network         string `mapstructure:"network"`      // amoy or polygon
	USDCAddress     string `mapstructure:"usdc_address"`
	StakingContract string `mapstructure:"staking_contract"`
	RPCURL          string `mapstructure:"rpc_url"`
}

type TelegramConfig struct {
	BotToken    string `mapstructure:"bot_token"`
	WebhookPath string `mapstructure:"webhook_path"`
}

func Load(configPath string) (*Config, error) {
	viper.SetConfigFile(configPath)
	viper.SetConfigType("yaml")

	// 允许环境变量覆盖
	viper.AutomaticEnv()

	if err := viper.ReadInConfig(); err != nil {
		return nil, fmt.Errorf("failed to read config file: %w", err)
	}

	var cfg Config
	if err := viper.Unmarshal(&cfg); err != nil {
		return nil, fmt.Errorf("failed to unmarshal config: %w", err)
	}

	return &cfg, nil
}
