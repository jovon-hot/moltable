#!/bin/bash
# Moltable — 30秒接入脚本
# curl -sL https://moltable.ai/connect.sh | bash

set -e

MOLTABLE_API="${MOLTABLE_API:-https://api.moltable.ai}"
AUTO_ADD_SKILL="${AUTO_ADD_SKILL:-true}"

echo ""
echo "  █▀▄▀█ █▀█ █   ▀█▀ ▄▀█ █▄▄ █   █▀▀"
echo "  █ ▀ █ █▄█ █▄▄  █  █▀█ █▄█ █▄▄ ██▄"
echo "  Moltable.ai — Switch Agents, Keep Your Soul"
echo "  ─────────────────────────────────"
echo ""

# Check for API key
if [ -z "$MOLTABLE_KEY" ]; then
  echo "🔑  输入你的 Moltable API Key"
  echo "    (注册地址: https://moltable.ai/register)"
  echo ""
  read -p "  API Key: " MOLTABLE_KEY
  echo ""
fi

# Detect Hermes
if command -v hermes &> /dev/null; then
  echo "✓ Hermes 已安装"
  
  # Back up current config
  if [ -f ~/.hermes/config.yaml ]; then
    cp ~/.hermes/config.yaml ~/.hermes/config.yaml.moltable.bak
    echo "✓ 已备份 ~/.hermes/config.yaml"
  fi

  # Configure Moltable MCP server (正确的 MCP 配置格式)
  hermes config set mcp_servers.moltable.url "${MOLTABLE_API}/mcp"
  hermes config set mcp_servers.moltable.headers.X-API-Key "$MOLTABLE_KEY"
  echo "✓ Moltable MCP 已配置"

  if [ "$AUTO_ADD_SKILL" = "true" ]; then
    mkdir -p ~/.hermes/skills/moltable-sync
    if curl -sL --max-time 20 "https://raw.githubusercontent.com/jovon-hot/moltable/main/skill/moltable-sync/SKILL.md" -o ~/.hermes/skills/moltable-sync/SKILL.md 2>/dev/null \
       && grep -q "moltable-sync" ~/.hermes/skills/moltable-sync/SKILL.md 2>/dev/null; then
      echo "✓ 同步 skill 已加载 (~/.hermes/skills/moltable-sync/)"
    else
      echo "⚠  Skill 下载失败(网络?),稍后手动补装或重跑本脚本"
    fi
  fi
else
  echo "⚠  Hermes 未检测到"
  echo "   请先安装 Hermes,或使用其他 MCP 客户端(Claude/Cursor)"
  echo "   接入指引: https://moltable.ai/connect"
fi

echo ""
echo "  ✅ 完成！你的 AI 现在认识你了。"
echo "  接下来对 Hermes 说一句: 同步"
echo ""
