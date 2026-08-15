-- Stripe subscription: add customer + subscription id to users
alter table users add column if not exists stripe_customer_id text;
alter table users add column if not exists stripe_subscription_id text;
