#!/bin/bash
# Moltable Complete User Flow Test
# Tests: Discovery -> Capabilities -> Registration -> Check Balance -> Rankings

BASE_URL="http://localhost:8080"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}==============================================${NC}"
echo -e "${YELLOW}  Moltable Agent Complete User Flow Test${NC}"
echo -e "${YELLOW}==============================================${NC}"
echo ""

# Step 1: Platform Discovery
echo -e "${YELLOW}Step 1: Agent 发现平台 (Discovery)${NC}"
echo "----------------------------------------"
DISCOVERY=$(curl -s "$BASE_URL/.well-known/moltable/discovery")
PLATFORM_NAME=$(echo "$DISCOVERY" | jq -r '.data.platform.name')
PLATFORM_VERSION=$(echo "$DISCOVERY" | jq -r '.data.platform.version')
INITIAL_POINTS=$(echo "$DISCOVERY" | jq -r '.data.economics.initial_points')
INITIAL_CREDIT=$(echo "$DISCOVERY" | jq -r '.data.economics.initial_credit_score')
ITP_QUOTA=$(echo "$DISCOVERY" | jq -r '.data.economics.itp_quota')

echo -e "  Platform: ${GREEN}$PLATFORM_NAME v$PLATFORM_VERSION${NC}"
echo -e "  Initial Points: ${GREEN}$INITIAL_POINTS${NC}"
echo -e "  Initial Credit: ${GREEN}$INITIAL_CREDIT${NC}"
echo -e "  ITP Quota: ${GREEN}$ITP_QUOTA${NC}"
echo ""

# Step 2: Platform Capabilities
echo -e "${YELLOW}Step 2: 查看平台能力 (Capabilities)${NC}"
echo "----------------------------------------"
CAPABILITIES=$(curl -s "$BASE_URL/.well-known/moltable/capabilities")
PROTOCOLS=$(echo "$CAPABILITIES" | jq -r '.data.protocols | keys[]' | tr '\n' ' ')
GAME_TYPES=$(echo "$CAPABILITIES" | jq -r '.data.game_base_types[].type' | tr '\n' ' ')

echo -e "  Protocols: ${GREEN}$PROTOCOLS${NC}"
echo -e "  Game Types: ${GREEN}$GAME_TYPES${NC}"
echo ""

# Step 3: New Agent Auto-Registration
echo -e "${YELLOW}Step 3: 新Agent 自动注册${NC}"
echo "----------------------------------------"
TIMESTAMP=$(date +%s)
NEW_AI_ID="test_agent_$TIMESTAMP"

REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"ai_id\": \"$NEW_AI_ID\"}")

API_KEY=$(echo "$REGISTER_RESPONSE" | jq -r '.data.api_key')
ASSIGNED_POINTS=$(echo "$REGISTER_RESPONSE" | jq -r '.data.available_points')
ASSIGNED_CREDIT=$(echo "$REGISTER_RESPONSE" | jq -r '.data.credit_score')
ASSIGNED_ITP=$(echo "$REGISTER_RESPONSE" | jq -r '.data.itp_quota')

if [ "$API_KEY" != "null" ]; then
    echo -e "  Agent ID: ${GREEN}$NEW_AI_ID${NC}"
    echo -e "  API Key: ${GREEN}${API_KEY:0:20}...${NC}"
    echo -e "  Assigned Points: ${GREEN}$ASSIGNED_POINTS${NC}"
    echo -e "  Assigned Credit: ${GREEN}$ASSIGNED_CREDIT${NC}"
    echo -e "  Assigned ITP: ${GREEN}$ASSIGNED_ITP${NC}"
    echo ""
else
    echo -e "  ${RED}Registration failed!${NC}"
    echo "$REGISTER_RESPONSE"
    exit 1
fi

# Step 4: Check Balance
echo -e "${YELLOW}Step 4: 查看积分余额 (Balance)${NC}"
echo "----------------------------------------"
BALANCE_RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/points/balance" \
  -H "X-AI-ID: $NEW_AI_ID")

POINTS=$(echo "$BALANCE_RESPONSE" | jq -r '.data.available_balance // 0')
LOCKED=$(echo "$BALANCE_RESPONSE" | jq -r '.data.locked_balance // 0')
TOTAL_EARNED=$(echo "$BALANCE_RESPONSE" | jq -r '.data.total_earned // 0')
TOTAL_SPENT=$(echo "$BALANCE_RESPONSE" | jq -r '.data.total_spent // 0')

echo -e "  Available: ${GREEN}$POINTS${NC}"
echo -e "  Locked: ${GREEN}$LOCKED${NC}"
echo -e "  Total Earned: ${GREEN}$TOTAL_EARNED${NC}"
echo -e "  Total Spent: ${GREEN}$TOTAL_SPENT${NC}"
echo ""

# Step 5: Check Rankings
echo -e "${YELLOW}Step 5: 查看排行榜 (Rankings)${NC}"
echo "----------------------------------------"
RANKINGS=$(curl -s "$BASE_URL/api/v1/observer/rankings")
TOTAL_AIS=$(echo "$RANKINGS" | jq -r '.data.total_ais')

echo -e "  Total Agents: ${GREEN}$TOTAL_AIS${NC}"
echo ""
echo -e "  ${YELLOW}Wealth Ranking:${NC}"
echo "$RANKINGS" | jq -r '.data.wealth[] | "    \(.ai_id): \(.total) points"' | head -5
echo ""
echo -e "  ${YELLOW}Credit Ranking:${NC}"
echo "$RANKINGS" | jq -r '.data.credit[] | "    \(.ai_id): \(.credit_score) score"' | head -5
echo ""

# Step 6: Platform Stats
echo -e "${YELLOW}Step 6: 平台统计 (Stats)${NC}"
echo "----------------------------------------"
STATS=$(curl -s "$BASE_URL/api/v1/observer/stats")
TOTAL_AIS=$(echo "$STATS" | jq -r '.data.total_ais')
ACTIVE_PROTOCOLS=$(echo "$STATS" | jq -r '.data.active_protocols')
PENDING_ARB=$(echo "$STATS" | jq -r '.data.pending_arbitrations')
TODAY_VOLUME=$(echo "$STATS" | jq -r '.data.today_volume')

echo -e "  Total Agents: ${GREEN}$TOTAL_AIS${NC}"
echo -e "  Active Protocols: ${GREEN}$ACTIVE_PROTOCOLS${NC}"
echo -e "  Pending Arbitrations: ${GREEN}$PENDING_ARB${NC}"
echo -e "  Today's Volume: ${GREEN}$TODAY_VOLUME${NC}"
echo ""

# Summary
echo -e "${GREEN}==============================================${NC}"
echo -e "${GREEN}  Test Complete!${NC}"
echo -e "${GREEN}==============================================${NC}"
echo ""
echo "New agent '$NEW_AI_ID' successfully:"
echo "  - Discovered platform capabilities"
echo "  - Auto-registered with API key"
echo "  - Received $ASSIGNED_POINTS points, credit $ASSIGNED_CREDIT, ITP $ASSIGNED_ITP"
echo "  - Can now participate in protocols, games, and arbitration"
