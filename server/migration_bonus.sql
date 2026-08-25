-- ============================================
-- Moltable · 分享/邀请赠送存储额度 迁移
-- 在 Supabase SQL Editor 运行（生产库）
-- ============================================

-- 1. users 表加 bonus_storage_gb（累计赠送存储额度 GB）
alter table users add column if not exists bonus_storage_gb numeric default 0;

-- 2. referrals 表加 referred_user_id + reward_granted（邀请奖励防重复发放）
alter table referrals add column if not exists referred_user_id uuid;
alter table referrals add column if not exists reward_granted boolean default false;

-- 3. bonus_events 表（发放审计 + 防重复领取）
create table if not exists bonus_events (
    id uuid primary key default gen_random_uuid(),
    user_id uuid references users(id) on delete cascade,
    event_type text not null,          -- 'share' | 'referral'
    amount_gb numeric not null default 1,
    source text,                        -- 帖子链接 / 被邀请人 user_id
    created_at timestamptz default now()
);
create index if not exists bonus_events_user_idx on bonus_events(user_id, event_type);
