-- ============================================
-- Moltable · 邮件发送审计（防邮件轰炸）
-- 在 Supabase SQL Editor 中运行此文件（生产库）
-- 用途：按邮箱冷却 + 按 IP 频率双重限流，防止验证邮件被用来轰炸攻击
-- ============================================

CREATE TABLE IF NOT EXISTS email_send_audit (
    id          text primary key,
    email       text not null,
    ip_address  text,
    sent_at     timestamptz not null default now()
);

CREATE INDEX IF NOT EXISTS idx_email_send_audit_email ON email_send_audit(email, sent_at);
CREATE INDEX IF NOT EXISTS idx_email_send_audit_ip ON email_send_audit(ip_address, sent_at);
