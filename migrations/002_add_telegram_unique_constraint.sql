-- Add unique constraint for Telegram user ID to prevent duplicate registrations

-- Add unique constraint on telegram_user_id
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'ai_accounts_telegram_user_id_key'
    ) THEN
        ALTER TABLE ai_accounts ADD CONSTRAINT ai_accounts_telegram_user_id_key UNIQUE (telegram_user_id);
    END IF;
END $$;

-- Rename point_balances to mtc_balances
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'point_balances') THEN
        ALTER TABLE point_balances RENAME TO mtc_balances;
    END IF;
END $$;
