# Moltable Stripe 上线配置

> 按顺序复制粘贴到对应平台即可。两端配好后自动生效。

---

## 一、Railway 环境变量（后端）

打开 https://railway.app/project/moltable-production/variables

逐个添加以下 5 个变量：

```
STRIPE_SECRET_KEY
```
```
sk_test_51TzanQ37ZqMGZaD6xh79dMUviyIhq1rC8zRf8LddV6RZHkKBG70FC01SIAuOybfyMKEO1GQ4eGNj24fgaGWlx12l0029ARzB2l
```
```
STRIPE_WEBHOOK_SECRET
```
```
whsec_jJhOVGPZpIiUi6NcL6p5ZkSexL6tsayX
```
```
STRIPE_PRICE_PRO_MONTHLY
```
```
price_1Tzau537ZqMGZaD6xAvqK71e
```
```
STRIPE_PRICE_PRO_YEARLY
```
```
price_1Tzau637ZqMGZaD6NnwjpaV9
```
```
STRIPE_PRICE_TEAM
```
```
price_1Tzau737ZqMGZaD6OGhpaeoR
```

添加后 Railway 自动重新部署，约 30 秒生效。

---

## 二、Vercel 环境变量（前端）

打开 Vercel Dashboard → moltable → Settings → Environment Variables

添加：

```
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY
```
```
pk_test_51TzanQ37ZqMGZaD6b9jlbF7jLX4Ne1gAzaqZu4hVwLqyQE8Wdath8LldLhYxDycLJ9HyjpSZ5LxiK4K9AI40fNRb00ug0aqJmp
```

添加后 Vercel 自动重新部署。

---

## 三、验证

两端部署完成后：

```bash
# 1. 定价页
curl https://moltable-production-15ad.up.railway.app/api/billing/plans

# 2. 创建订阅（应返回 Stripe Checkout URL）
curl -X POST https://moltable-production-15ad.up.railway.app/api/billing/checkout \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <你的API-Key>" \
  -d '{"plan":"pro","billing_cycle":"monthly"}'

# 应返回: {"url": "https://checkout.stripe.com/..."}

# 3. Stripe 测试卡号
# 卡号: 4242 4242 4242 4242
# 日期: 任意未来日期
# CVC: 任意3位
# 用于测试订阅购买，不会真实扣费
```

---

## 四、Stripe 侧已就绪

| 资源 | ID | 说明 |
|------|-----|------|
| Pro Monthly | `price_1Tzau537ZqMGZaD6xAvqK71e` | ¥19/月 |
| Pro Yearly | `price_1Tzau637ZqMGZaD6NnwjpaV9` | ¥149/年 |
| Team Monthly | `price_1Tzau737ZqMGZaD6OGhpaeoR` | ¥39/月 |
| Webhook | `we_1TzauQ37ZqMGZaD68GRiwMvX` | → `https://moltable-production-15ad.up.railway.app/api/billing/webhook` |
| Webhook Secret | `whsec_jJhOVGP...` | 验证 Stripe 事件签名 |

Webhook 订阅事件：`customer.subscription.created` · `updated` · `deleted`

---

## 五、billing.py 订阅流程

```
用户点击"升级 Pro"
  → POST /api/billing/checkout {"plan":"pro","billing_cycle":"monthly"}
  → 后端调用 stripe.checkout.Session.create(mode="subscription")
  → 返回 Stripe Checkout URL
  → 用户跳转到 Stripe 页面填写卡信息
  → 订阅成功 → Stripe 发送 webhook (customer.subscription.created)
  → 后端接收 → 写入 subscriptions 表 (user_id, stripe_subscription_id, status=active, plan=pro)
  → GET /api/auth/me 返回 plan=pro

续费:
  → Stripe 每月自动扣款
  → 成功: customer.subscription.updated (status=active)
  → 失败: customer.subscription.updated (status=past_due)

取消:
  → 用户在 Stripe 取消或后端调用取消
  → webhook: customer.subscription.deleted
  → status → canceled
  → plan → free (回退)
```
