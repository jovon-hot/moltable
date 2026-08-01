#!/bin/bash
# Moltable Stripe 配置脚本
# 用法: bash setup-stripe.sh
# 前置: railway CLI 已登录 (railway login)

set -e

BOLD='\033[1m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${BOLD}Moltable · Stripe 配置${NC}"
echo ""

# ── 凭证 ──────────────────────────────
SK="sk_test_51TzanQ37ZqMGZaD6xh79dMUviyIhq1rC8zRf8LddV6RZHkKBG70FC01SIAuOybfyMKEO1GQ4eGNj24fgaGWlx12l0029ARzB2l"
PK="pk_test_51TzanQ37ZqMGZaD6b9jlbF7jLX4Ne1gAzaqZu4hVwLqyQE8Wdath8LldLhYxDycLJ9HyjpSZ5LxiK4K9AI40fNRb00ug0aqJmp"
WH_SECRET="whsec_jJhOVGPZpIiUi6NcL6p5ZkSexL6tsayX"

# Stripe Price IDs (已创建)
PRICE_PRO_MONTH="price_1Tzau537ZqMGZaD6xAvqK71e"
PRICE_PRO_YEAR="price_1Tzau637ZqMGZaD6NnwjpaV9"
PRICE_TEAM="price_1Tzau737ZqMGZaD6OGhpaeoR"

# ── Railway 环境变量 (需 railway CLI) ──
echo "1. 设置 Railway 环境变量..."
if command -v railway &> /dev/null && railway whoami &> /dev/null; then
    railway variables set \
      STRIPE_SECRET_KEY="$SK" \
      STRIPE_WEBHOOK_SECRET="$WH_SECRET" \
      STRIPE_PRICE_PRO_MONTHLY="$PRICE_PRO_MONTH" \
      STRIPE_PRICE_PRO_YEARLY="$PRICE_PRO_YEAR" \
      STRIPE_PRICE_TEAM="$PRICE_TEAM"
    echo -e "  ${GREEN}✅ Railway 环境变量已设置${NC}"
else
    echo "  ⚠️  Railway CLI 未安装或未登录"
    echo "  手动设置 → Railway Dashboard → moltable → Variables:"
    echo "    STRIPE_SECRET_KEY=$SK"
    echo "    STRIPE_WEBHOOK_SECRET=$WH_SECRET"
    echo "    STRIPE_PRICE_PRO_MONTHLY=$PRICE_PRO_MONTH"
    echo "    STRIPE_PRICE_PRO_YEARLY=$PRICE_PRO_YEAR"
    echo "    STRIPE_PRICE_TEAM=$PRICE_TEAM"
fi

# ── Vercel 前端环境变量 (需 vercel CLI) ──
echo ""
echo "2. 设置 Vercel 环境变量..."
if command -v vercel &> /dev/null; then
    vercel env add NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY production <<< "$PK" 2>/dev/null || true
    echo -e "  ${GREEN}✅ Vercel 环境变量已设置${NC}"
else
    echo "  ⚠️  Vercel CLI 未安装"
    echo "  手动设置 → Vercel Dashboard → moltable → Environment Variables:"
    echo "    NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=$PK"
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  Stripe 配置完成${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "  验证: curl https://moltable-production-15ad.up.railway.app/api/billing/plans"
echo "  支付: POST /api/billing/checkout {\"plan\":\"pro\",\"billing_cycle\":\"monthly\"}"
