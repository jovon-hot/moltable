#!/usr/bin/env bash
# Moltable 一键接入 Hermes Agent
# 用法: curl -sL moltable.ai/connect.sh | bash -s -- <你的API-KEY>
# 或: bash connect.sh <molt_xxx>

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'
BOLD='\033[1m'

API_BASE="${MOLTABLE_API:-https://moltable-production-15ad.up.railway.app}"
API_KEY="${1:-}"

echo ""
echo -e "  ${PURPLE}╭──────────────────────────────────────╮${NC}"
echo -e "  ${PURPLE}│${NC}   🧬  ${BOLD}Moltable${NC} — AI Identity Layer    ${PURPLE}│${NC}"
echo -e "  ${PURPLE}╰──────────────────────────────────────╯${NC}"
echo ""

# ── Check API key ──────────────────────────────────────
if [ -z "$API_KEY" ]; then
    echo -ne "  API Key: "
    read API_KEY
fi

if [ -z "$API_KEY" ]; then
    echo -e "  ${RED}❌ 需要 API Key。注册获取: https://moltable.ai/register${NC}"
    exit 1
fi

# ── Test connection ─────────────────────────────────────
echo -e "  ⏳ 测试连接..."
PING=$(curl -s -X POST "$API_BASE/mcp" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d '{"jsonrpc":"2.0","id":1,"method":"ping"}' 2>&1)

if echo "$PING" | grep -q '"status":"ok"'; then
    echo -e "  ${GREEN}✅ 连接成功${NC}"
else
    echo -e "  ${RED}❌ 连接失败: $PING${NC}"
    echo -e "  ${RED}   请检查 API Key 是否正确 (应以 molt_ 或 mol_ 开头)${NC}"
    exit 1
fi

# ── Get tools list ──────────────────────────────────────
TOOLS=$(curl -s -X POST "$API_BASE/mcp" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' 2>&1)

TOOL_COUNT=$(echo "$TOOLS" | python3 -c "import sys,json; print(len(json.load(sys.stdin)['result']['tools']))" 2>/dev/null || echo "?")
echo -e "  ├─ ${TOOL_COUNT} 个工具已就绪"

# ── Write Hermes MCP config ─────────────────────────────
HERMES_DIR="$HOME/.hermes"
MCP_FILE="$HERMES_DIR/mcp.json"

mkdir -p "$HERMES_DIR"

# Build config JSON
CONFIG=$(cat <<EOF
{
  "mcpServers": {
    "moltable": {
      "type": "http",
      "url": "$API_BASE/mcp",
      "headers": {
        "X-API-Key": "$API_KEY"
      },
      "description": "Moltable — AI Identity & Memory Layer"
    }
  }
}
EOF
)

# Merge with existing config if present
if [ -f "$MCP_FILE" ]; then
    echo -e "  ⚠️  已有 MCP 配置，合并中..."
    python3 -c "
import json, sys
with open('$MCP_FILE') as f:
    existing = json.load(f)
new = json.loads('''$CONFIG''')
if 'mcpServers' not in existing:
    existing['mcpServers'] = {}
existing['mcpServers']['moltable'] = new['mcpServers']['moltable']
with open('$MCP_FILE', 'w') as f:
    json.dump(existing, f, indent=2, ensure_ascii=False)
" 2>/dev/null || {
        # Fallback: just write new file
        echo "$CONFIG" > "$MCP_FILE"
        echo -e "  ${BLUE}  (已覆盖旧配置)${NC}"
    }
else
    echo "$CONFIG" > "$MCP_FILE"
fi

echo -e "  └─ ${GREEN}✅ 配置已写入${NC} → $MCP_FILE"
echo ""
echo -e "  ${GREEN}🎉 完成！${NC}"
echo ""
echo -e "  现在在 Hermes 中试试："
echo -e "    ${BLUE}search_memory 查询\"我的偏好\"${NC}"
echo -e "    ${BLUE}save_memory 内容\"我是一名后端工程师\"${NC}"
echo ""
echo -e "  API Key: ${PURPLE}${API_KEY:0:12}...${NC} (已保存到 MCP 配置)"
echo ""
