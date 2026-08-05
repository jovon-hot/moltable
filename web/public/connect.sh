#!/bin/bash
# Moltable — 30秒接入脚本
# curl -sL https://moltable.ai/connect.sh | bash

set -e

MOLTABLE_API="${MOLTABLE_API:-https://api.moltable.ai}"
AUTO_ADD_SKILL="${AUTO_ADD_SKILL:-true}"

echo ""
echo "  █▀▄▀█ █▀█ █   ▀█▀ ▄▀█ █▄▄ █   █▀▀"
echo "  █ ▀ █ █▄█ █▄▄  █  █▀█ █▄█ █▄▄ ██▄"
echo "  Moltable.ai — AI Identity Sync"
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

  # Configure Moltable tool
  hermes config set moltable.api_key "$MOLTABLE_KEY"
  hermes config set moltable.api_url "$MOLTABLE_API"
  echo "✓ Moltable API 已配置"

  if [ "$AUTO_ADD_SKILL" = "true" ]; then
    if hermes skills install moltable/skills 2>/dev/null; then
      echo "✓ Moltable Skill 已加载"
    else
      echo "⚠  Skill 安装需要手动完成: hermes skills install moltable/skills"
    fi
  fi
else
  echo "⚠  Hermes 未检测到"
  echo "   手动配置:"
  echo "   export MOLTABLE_KEY='$MOLTABLE_KEY'"
  echo "   安装: pip install moltable-connect  (即将发布)"
fi

echo ""
echo "  ✅ 完成！你的 AI 现在认识你了。"
echo "  测试: hermes run 'who am i'"
echo ""
