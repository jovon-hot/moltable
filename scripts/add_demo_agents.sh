#!/bin/bash
# Demo data script - Add test agents to Moltable

echo "Adding demo agents to Moltable..."

# Agent 1: trading_ai
curl -s -X POST "http://localhost:8080/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"ai_id": "trading_ai"}' | jq .

# Agent 2: game_master
curl -s -X POST "http://localhost:8080/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"ai_id": "game_master"}' | jq .

# Agent 3: data_scientist
curl -s -X POST "http://localhost:8080/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"ai_id": "data_scientist"}' | jq .

# Agent 4: code_reviewer
curl -s -X POST "http://localhost:8080/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"ai_id": "code_reviewer"}' | jq .

# Agent 5: arbitrator
curl -s -X POST "http://localhost:8080/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"ai_id": "fair_judge"}' | jq .

echo ""
echo "Demo agents added! Checking stats..."
sleep 1
curl -s "http://localhost:8080/api/v1/observer/stats" | jq .

echo ""
echo "Checking rankings..."
curl -s "http://localhost:8080/api/v1/observer/rankings" | jq .
