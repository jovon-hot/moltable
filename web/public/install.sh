#!/bin/bash
# Moltable — Agent 灵魂资产备份 CLI 安装脚本
# curl -sL https://moltable.ai/install.sh | bash
#
# 下载 moltable backup CLI（纯 Python stdlib，无第三方依赖）到 ~/.moltable/，
# 并添加 `moltable` 命令到 shell（alias 或 PATH）。

set -e

INSTALL_DIR="${MOLTABLE_INSTALL_DIR:-$HOME/.moltable}"
API_BASE="https://moltable.ai"
BIN_DIR="$INSTALL_DIR/bin"

# ── 打印 banner ──────────────────────────────────
echo ""
echo "  █▀▄▀█ █▀█ █   ▀█▀ ▄▀█ █▄▄ █   █▀▀"
echo "  █ ▀ █ █▄█ █▄▄  █  █▀█ █▄█ █▄▄ ██▄"
echo "  Moltable — Switch Agents, Keep Your Soul"
echo "  ─────────────────────────────────────────"
echo ""

# ── 检测 python3 ──────────────────────────────────
if ! command -v python3 &> /dev/null; then
  echo "❌ 未检测到 python3，请先安装 Python 3.8+"
  exit 1
fi
PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✓ Python $PY_VERSION"

# ── 创建安装目录 ──────────────────────────────────
mkdir -p "$INSTALL_DIR" "$BIN_DIR"

# ── 下载 CLI（两个文件：主命令 + hermes adapter）──
echo "↓ 下载 moltable backup CLI ..."
curl -fsSL "$API_BASE/cli/moltable_backup.py" -o "$INSTALL_DIR/moltable_backup.py"
curl -fsSL "$API_BASE/cli/hermes_adapter.py" -o "$INSTALL_DIR/hermes_adapter.py"
echo "✓ 已下载到 $INSTALL_DIR/"

# ── 创建 moltable 命令 ─────────────────────────────
cat > "$BIN_DIR/moltable" << 'EOF'
#!/bin/bash
# moltable — Agent 灵魂资产备份 CLI
# 用法: moltable backup <init|push|pull|sources> [options]
#       moltable <init|push|pull|sources> [options]  （backup 可省略）
args=("$@")
if [ "${args[0]}" = "backup" ]; then
  args=("${args[@]:1}")
fi
exec python3 "$HOME/.moltable/moltable_backup.py" "${args[@]}"
EOF
chmod +x "$BIN_DIR/moltable"
echo "✓ 已创建命令 $BIN_DIR/moltable"

# ── 添加到 PATH ────────────────────────────────────
SHELL_RC=""
case "$SHELL" in
  */zsh) SHELL_RC="$HOME/.zshrc" ;;
  */bash) SHELL_RC="$HOME/.bashrc" ;;
  *) SHELL_RC="$HOME/.profile" ;;
esac

PATH_LINE="export PATH=\"\$HOME/.moltable/bin:\$PATH\""
if ! grep -qF '.moltable/bin' "$SHELL_RC" 2>/dev/null; then
  echo "" >> "$SHELL_RC"
  echo "# Moltable CLI" >> "$SHELL_RC"
  echo "$PATH_LINE" >> "$SHELL_RC"
  echo "✓ 已添加 PATH 到 $SHELL_RC"
else
  echo "✓ PATH 已配置"
fi

echo ""
echo "  ✅ 安装完成！"
echo ""
echo "  下一步："
echo "    1. 重开终端，或执行:  source $SHELL_RC"
echo "    2. 初始化配置:        moltable backup init"
echo "    3. 设置 API Key:      编辑 ~/.moltable/backup.json 写入 api_key"
echo "    4. 首次备份:          moltable backup push"
echo ""
echo "  获取 API Key: https://moltable.ai/register"
echo ""
