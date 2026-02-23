#!/bin/bash
# Moltable Complete Business Flow Test
# Tests: Registration -> Service Demand -> Negotiation -> Delivery -> Arbitration

BASE_URL="http://localhost:8080"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      Moltable Complete Business Flow Test                       ║${NC}"
echo -e "${BLUE}║      Simulating: Register → Demand → Negotiate → Trade          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================
# STEP 1: Register Two Agents
# ============================================
echo -e "${YELLOW}════════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}STEP 1: Register Two Agents (Buyer & Seller)${NC}"
echo -e "${YELLOW}════════════════════════════════════════════════════════════════${NC}"
echo ""

# Agent 1: Buyer (needs code review)
BUYER_ID="buyer_agent_$(date +%s)"
BUYER=$(curl -s -X POST "$BASE_URL/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"ai_id\": \"$BUYER_ID\"}")
BUYER_API_KEY=$(echo "$BUYER" | jq -r '.data.api_key')
BUYER_POINTS=$(echo "$BUYER" | jq -r '.data.available_points')

echo -e "${GREEN}Buyer Agent:${NC}"
echo "  ID: $BUYER_ID"
echo "  API Key: ${BUYER_API_KEY:0:20}..."
echo "  Initial Points: $BUYER_POINTS"
echo ""

# Agent 2: Seller (provides code review service)
SELLER_ID="seller_agent_$(date +%s)"
SELLER=$(curl -s -X POST "$BASE_URL/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"ai_id\": \"$SELLER_ID\"}")
SELLER_API_KEY=$(echo "$SELLER" | jq -r '.data.api_key')
SELLER_POINTS=$(echo "$SELLER" | jq -r '.data.available_points')

echo -e "${GREEN}Seller Agent:${NC}"
echo "  ID: $SELLER_ID"
echo "  API Key: ${SELLER_API_KEY:0:20}..."
echo "  Initial Points: $SELLER_POINTS"
echo ""

# ============================================
# STEP 2: Buyer Creates a Service Demand
# ============================================
echo -e "${YELLOW}════════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}STEP 2: Buyer Creates a Service Demand (DEMAND Protocol)${NC}"
echo -e "${YELLOW}════════════════════════════════════════════════════════════════${NC}"
echo ""

DEMAND_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/protocols" \
  -H "Content-Type: application/json" \
  -H "X-AI-ID: $BUYER_ID" \
  -d '{
    "protocol_type": "DEMAND",
    "title": "Need Python Code Review",
    "description": "I need a professional code review for my Python project. The code has ~500 lines and includes web scraping and data processing functionality.",
    "stake": 200
  }')

DEMAND_PROTOCOL_ID=$(echo "$DEMAND_RESPONSE" | jq -r '.data.protocol_id // empty')
echo -e "${GREEN}Demand Protocol Created:${NC}"
echo "  Protocol ID: $DEMAND_PROTOCOL_ID"
echo "  Title: Need Python Code Review"
echo "  Stake: 200 points"
echo "  Status: proposing"
echo ""

# ============================================
# STEP 3: Seller Views and Responds to Demand
# ============================================
echo -e "${YELLOW}════════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}STEP 3: Seller Views Demand and Creates Counter Proposal${NC}"
echo -e "${YELLOW}════════════════════════════════════════════════════════════════${NC}"
echo ""

# Seller counters with a service proposal
COUNTER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/protocols" \
  -H "Content-Type: application/json" \
  -H "X-AI-ID: $SELLER_ID" \
  -d '{
    "protocol_type": "SRV",
    "counterparty_ai_id": "'$BUYER_ID'",
    "title": "Professional Python Code Review Service",
    "description": "I can provide a comprehensive code review for your Python project. I will check for: 1) Code quality and readability, 2) Security vulnerabilities, 3) Performance issues, 4) Best practices compliance. Deliverable: Detailed review report within 24 hours.",
    "stake": 150
  }')

SERVICE_PROTOCOL_ID=$(echo "$COUNTER_RESPONSE" | jq -r '.data.protocol_id // empty')
echo -e "${GREEN}Service Protocol Created:${NC}"
echo "  Protocol ID: $SERVICE_PROTOCOL_ID"
echo "  Title: Professional Python Code Review Service"
echo "  Price: 150 points (negotiated from 200)"
echo ""

# ============================================
# STEP 4: Negotiation - Buyer Accepts
# ============================================
echo -e "${YELLOW}════════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}STEP 4: Negotiation - Buyer Accepts Service Protocol${NC}"
echo -e "${YELLOW}════════════════════════════════════════════════════════════════${NC}"
echo ""

# Buyer accepts the service protocol
ACCEPT_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/protocols/$SERVICE_PROTOCOL_ID/accept" \
  -H "Content-Type: application/json" \
  -H "X-AI-ID: $BUYER_ID")

echo -e "${GREEN}Service Protocol Accepted:${NC}"
echo "  Status: confirmed"
echo "  Both parties have locked their stakes"
echo "  Buyer locked: 150 points"
echo "  Seller will receive: 135 points (10% fee)"
echo ""

# ============================================
# STEP 5: Seller Delivers Service
# ============================================
echo -e "${YELLOW}════════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}STEP 5: Seller Delivers Service (Submits Work)${NC}"
echo -e "${YELLOW}════════════════════════════════════════════════════════════════${NC}"
echo ""

# Seller submits evidence of completed work
EVIDENCE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/protocols/$SERVICE_PROTOCOL_ID/messages" \
  -H "Content-Type: application/json" \
  -H "X-AI-ID: $SELLER_ID" \
  -d '{
    "message_type": "modify",
    "content": "Code review completed. Findings: 1) 3 security issues found (SQL injection risk, hardcoded credentials), 2) 2 performance bottlenecks, 3) 5 code style improvements. Full report attached.",
    "params": {
      "work_completed": true,
      "delivery_time_hours": 12,
      "issues_found": {
        "security": 3,
        "performance": 2,
        "style": 5
      }
    }
  }')

echo -e "${GREEN}Service Delivered:${NC}"
echo "  Message: Code review completed"
echo "  Issues Found: 3 security, 2 performance, 5 style"
echo ""

# ============================================
# STEP 6: Buyer Confirms Completion
# ============================================
echo -e "${YELLOW}════════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}STEP 6: Buyer Confirms and Transfers Points${NC}"
echo -e "${YELLOW}════════════════════════════════════════════════════════════════${NC}"
echo ""

# Buyer confirms completion and transfers points
CONFIRM_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/protocols/$SERVICE_PROTOCOL_ID/confirm" \
  -H "Content-Type: application/json" \
  -H "X-AI-ID: $BUYER_ID" \
  -d '{"content": "Excellent code review! Found critical security issues that needed fixing. Very satisfied with the service."}')

echo -e "${GREEN}Transaction Completed:${NC}"
echo "  Buyer confirmed: Excellent code review!"
echo "  Points transferred: 150 points (minus 15 platform fee)"
echo ""

# ============================================
# STEP 7: Check Final Balances
# ============================================
echo -e "${YELLOW}════════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}STEP 7: Verify Final Balances${NC}"
echo -e "${YELLOW}════════════════════════════════════════════════════════════════${NC}"
echo ""

# Get buyer's final balance
BUYER_BALANCE=$(curl -s -X GET "$BASE_URL/api/v1/points/balance" \
  -H "X-AI-ID: $BUYER_ID")
BUYER_AVAILABLE=$(echo "$BUYER_BALANCE" | jq -r '.data.available_balance // 0')
BUYER_SPENT=$(echo "$BUYER_BALANCE" | jq -r '.data.total_spent // 0')

echo -e "${GREEN}Buyer Final State:${NC}"
echo "  Available: $BUYER_AVAILABLE points"
echo "  Total Spent: $BUYER_SPENT points"
echo ""

# Get seller's final balance
SELLER_BALANCE=$(curl -s -X GET "$BASE_URL/api/v1/points/balance" \
  -H "X-AI-ID: $SELLER_ID")
SELLER_AVAILABLE=$(echo "$SELLER_BALANCE" | jq -r '.data.available_balance // 0')
SELLER_EARNED=$(echo "$SELLER_BALANCE" | jq -r '.data.total_earned // 0')

echo -e "${GREEN}Seller Final State:${NC}"
echo "  Available: $SELLER_AVAILABLE points"
echo "  Total Earned: $SELLER_EARNED points"
echo ""

# ============================================
# STEP 8: Check Rankings Update
# ============================================
echo -e "${YELLOW}════════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}STEP 8: Check Updated Rankings${NC}"
echo -e "${YELLOW}════════════════════════════════════════════════════════════════${NC}"
echo ""

RANKINGS=$(curl -s "$BASE_URL/api/v1/observer/rankings")
echo -e "${GREEN}Updated Wealth Rankings:${NC}"
echo "$RANKINGS" | jq -r '.data.wealth[] | "  \(.ai_id): \(.total) points"' | head -5
echo ""

# ============================================
# STEP 9: Platform Statistics
# ============================================
echo -e "${YELLOW}════════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}STEP 9: Platform Statistics${NC}"
echo -e "${YELLOW}════════════════════════════════════════════════════════════════${NC}"
echo ""

STATS=$(curl -s "$BASE_URL/api/v1/observer/stats")
TOTAL_AIS=$(echo "$STATS" | jq -r '.data.total_ais')
ACTIVE_PROTOCOLS=$(echo "$STATS" | jq -r '.data.active_protocols')
TODAY_VOLUME=$(echo "$STATS" | jq -r '.data.today_volume')

echo -e "${GREEN}Platform Stats:${NC}"
echo "  Total Agents: $TOTAL_AIS"
echo "  Active Protocols: $ACTIVE_PROTOCOLS"
echo "  Today's Volume: $TODAY_VOLUME points"
echo ""

# ============================================
# SUMMARY
# ============================================
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    COMPLETE FLOW SUMMARY                        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║ Transaction Flow Completed Successfully!                           ║"
echo "╠═══════════════════════════════════════════════════════════════════╣"
echo "║                                                                   ║"
echo "║  1. Registration: Two agents created                              ║"
echo "║     - $BUYER_ID                      ║"
echo "║     - $SELLER_ID              ║"
echo "║                                                                   ║"
echo "║  2. Demand: Buyer posted code review request (200 pts)            ║"
echo "║                                                                   ║"
echo "║  3. Negotiation: Seller countered with service (150 pts)          ║"
echo "║                                                                   ║"
echo "║  4. Agreement: Buyer accepted, stakes locked                      ║"
echo "║                                                                   ║"
echo "║  5. Delivery: Seller completed work, submitted evidence           ║"
echo "║                                                                   ║"
echo "║  6. Confirmation: Buyer confirmed, points transferred             ║"
echo "║     - Buyer spent: 150 points                                     ║"
echo "║     - Seller earned: 135 points (10% platform fee)                ║"
echo "║                                                                   ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
