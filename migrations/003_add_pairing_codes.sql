-- Moltable Pairing Code Migration
-- Used for Telegram verification during agent registration

-- Pairing codes table
CREATE TABLE IF NOT EXISTS pairing_codes (
    id SERIAL PRIMARY KEY,
    pairing_code VARCHAR(6) NOT NULL UNIQUE,
    ai_id VARCHAR(64) NOT NULL,
    status VARCHAR(16) DEFAULT 'pending',
    telegram_user_id BIGINT,
    telegram_chat_id BIGINT,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Index for quick lookup
CREATE INDEX IF NOT EXISTS idx_pairing_codes_code ON pairing_codes(pairing_code);
CREATE INDEX IF NOT EXISTS idx_pairing_codes_status ON pairing_codes(status);
CREATE INDEX IF NOT EXISTS idx_pairing_codes_expires ON pairing_codes(expires_at);
