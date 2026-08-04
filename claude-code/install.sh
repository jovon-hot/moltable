#!/usr/bin/env bash
#
# ─────────────────────────────────────────────────────────────────────────────
#  Moltable × Claude Code — one-command installer
#  AI Identity Sync: "iCloud for AI Agents"
#
#  What this does:
#    1. Detects (or lets you pick) the Claude Code project directory
#    2. Writes / merges .mcp.json so Claude Code auto-discovers Moltable
#    3. Collects your Moltable API key (molt_...) if not already set
#    4. Validates connectivity to https://api.moltable.ai/mcp
#    5. Persists MOLTABLE_API_KEY to your shell profile (optional)
#    6. Prints usage examples
#
#  Usage:
#    ./install.sh                          # guided install in current project
#    ./install.sh --project-dir ~/my-app   # install into a specific project
#    ./install.sh --user                   # install into your home directory
#    ./install.sh --key molt_xxx           # pass API key non-interactively
#    ./install.sh --no-profile             # don't touch shell profile
#    ./install.sh --yes                    # accept defaults, no prompts
#
#  Requirements: bash 4+, curl, python3 (or jq) for JSON merging.
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

MCP_URL="https://api.moltable.ai/mcp"
REGISTER_URL="https://moltable.ai/register"
MCP_SERVER_NAME="moltable"

# ── Colors ───────────────────────────────────────────────────────────────────
if [[ -t 1 ]]; then
  C_GREEN=$'\033[32m'; C_YELLOW=$'\033[33m'; C_RED=$'\033[31m'
  C_BOLD=$'\033[1m'; C_DIM=$'\033[2m'; C_RESET=$'\033[0m'
else
  C_GREEN=""; C_YELLOW=""; C_RED=""; C_BOLD=""; C_DIM=""; C_RESET=""
fi
info()  { printf "%s%s%s\n" "$C_GREEN" "$*" "$C_RESET"; }
warn()  { printf "%s%s%s\n" "$C_YELLOW" "$*" "$C_RESET"; }
err()   { printf "%s%s%s\n" "$C_RED" "$*" "$C_RESET" >&2; }
step()  { printf "%s▸ %s%s\n" "$C_BOLD" "$*" "$C_RESET"; }
die()   { err "✗ $*"; exit 1; }

# ── Options ──────────────────────────────────────────────────────────────────
PROJECT_DIR=""
INSTALL_USER=0
NO_PROFILE=0
ASSUME_YES=0
API_KEY="${MOLTABLE_API_KEY:-}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project-dir) PROJECT_DIR="$2"; shift 2 ;;
    --user)        INSTALL_USER=1; shift ;;
    --no-profile)  NO_PROFILE=1; shift ;;
    --key)         API_KEY="$2"; shift 2 ;;
    --yes)         ASSUME_YES=1; shift ;;
    -h|--help)
      sed -n '2,30p' "$0" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *) die "Unknown option: $1 (see --help)" ;;
  esac
done

# ── 0. Prerequisites ─────────────────────────────────────────────────────────
command -v curl >/dev/null 2>&1 || die "curl is required but not found."
PYTHON_OK=0; JQ_OK=0
command -v python3 >/dev/null 2>&1 && PYTHON_OK=1
command -v jq     >/dev/null 2>&1 && JQ_OK=1
if [[ "$PYTHON_OK" -eq 0 && "$JQ_OK" -eq 0 ]]; then
  die "Either python3 or jq is required for JSON merging."
fi

# ── 1. Detect target directory ───────────────────────────────────────────────
detect_project_dir() {
  # Claude Code project = a directory that owns a .claude/ folder,
  # or the current directory (git repos are the common case).
  local d
  if [[ -d ".claude" ]]; then d="$(pwd)"
  elif git rev-parse --is-inside-work-tree >/dev/null 2>&1; then d="$(pwd)"
  else d="$(pwd)"; fi
  printf '%s' "$d"
}

if [[ "$INSTALL_USER" -eq 1 ]]; then
  TARGET_DIR="$HOME"
  INSTALL_MODE="user home ($HOME)"
elif [[ -n "$PROJECT_DIR" ]]; then
  [[ -d "$PROJECT_DIR" ]] || die "Project directory does not exist: $PROJECT_DIR"
  TARGET_DIR="$(cd "$PROJECT_DIR" && pwd)"
  INSTALL_MODE="project ($TARGET_DIR)"
else
  TARGET_DIR="$(detect_project_dir)"
  INSTALL_MODE="project ($TARGET_DIR)"
  if [[ "$ASSUME_YES" -eq 0 ]]; then
    printf "%s Install Moltable for Claude Code in %s%s? [Y/n] " "$C_BOLD" "$TARGET_DIR" "$C_RESET"
    read -r ans || true
    [[ "${ans:-y}" =~ ^[Yy]$ ]] || die "Aborted."
  fi
fi

MCP_JSON="$TARGET_DIR/.mcp.json"

echo
step "1/4  Installing to: $INSTALL_MODE"
echo "      Target file:  $MCP_JSON"

# ── 2. API key ───────────────────────────────────────────────────────────────
if [[ -z "$API_KEY" ]]; then
  if [[ "$ASSUME_YES" -eq 1 ]]; then
    die "No MOLTABLE_API_KEY set and --yes given. Pass it with --key molt_xxx or export MOLTABLE_API_KEY."
  fi
  printf "%s Enter your Moltable API key (molt_...) — get one at %s: %s" \
    "$C_BOLD" "$REGISTER_URL" "$C_RESET"
  read -r -s API_KEY || true
  echo
  [[ -n "$API_KEY" ]] || die "No API key provided."
fi

case "$API_KEY" in
  molt_*) : ;;
  *) warn "⚠ Key does not start with 'molt_' — it may be invalid. Continuing anyway." ;;
esac

# ── 3. Validate connectivity ─────────────────────────────────────────────────
step "2/4  Validating connectivity to $MCP_URL ..."
VALIDATE_RESPONSE="$(
  curl -sS --max-time 15 -o /tmp/moltable_mcp_validate.$$ -w '%{http_code}' \
    -X POST "$MCP_URL" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json, text/event-stream" \
    -H "X-API-Key: $API_KEY" \
    -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"moltable-install","version":"1.0.0"}}}'
)" || true
rm -f /tmp/moltable_mcp_validate.$$

if [[ "$VALIDATE_RESPONSE" =~ ^2[0-9][0-9]$ ]] || [[ "$VALIDATE_RESPONSE" =~ ^4[0-9][0-9]$ ]]; then
  info "      ✓ MCP endpoint reachable (HTTP $VALIDATE_RESPONSE)"
  if [[ "$VALIDATE_RESPONSE" =~ ^40[13]$ ]]; then
    warn "      ⚠ Endpoint returned $VALIDATE_RESPONSE — double-check your API key."
  fi
else
  warn "      ⚠ Could not reach the MCP endpoint (HTTP ${VALIDATE_RESPONSE:-timeout})."
  warn "        Installing anyway — verify connectivity once you're online."
fi

# ── 4. Write / merge .mcp.json ───────────────────────────────────────────────
step "3/4  Writing $MCP_JSON ..."
BACKUP=""
if [[ -f "$MCP_JSON" ]]; then
  BACKUP="$MCP_JSON.bak.$(date +%Y%m%d%H%M%S)"
  cp "$MCP_JSON" "$BACKUP"
  warn "      Existing .mcp.json found — backed up to $BACKUP"
fi

merge_mcp_json() {
  local target="$1"
  local server_json='{"type":"http","url":"https://api.moltable.ai/mcp","headers":{"X-API-Key":"${MOLTABLE_API_KEY}"}}'
  if [[ "$PYTHON_OK" -eq 1 ]]; then
    python3 - "$target" "$server_json" <<'PY'
import json, sys
path, server = sys.argv[1], json.loads(sys.argv[2])
try:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    data = {}
data.setdefault("mcpServers", {})["moltable"] = server
with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write("\n")
PY
  else
    # jq fallback
    local tmp
    tmp="$(mktemp)"
    jq --argjson s "$server_json" \
       '.mcpServers.moltable = $s' "$target" > "$tmp" 2>/dev/null \
      || jq -n --argjson s "$server_json" '{mcpServers:{moltable:$s}}' > "$tmp"
    mv "$tmp" "$target"
  fi
}

if [[ -f "$MCP_JSON" ]]; then
  merge_mcp_json "$MCP_JSON"
  info "      ✓ Merged moltable server into existing $MCP_JSON"
else
  cat > "$MCP_JSON" <<'EOF'
{
  "mcpServers": {
    "moltable": {
      "type": "http",
      "url": "https://api.moltable.ai/mcp",
      "headers": {
        "X-API-Key": "${MOLTABLE_API_KEY}"
      }
    }
  }
}
EOF
  info "      ✓ Created $MCP_JSON"
fi

# ── 5. Persist API key ───────────────────────────────────────────────────────
if [[ "$NO_PROFILE" -eq 0 ]]; then
  step "4/4  Saving MOLTABLE_API_KEY to your shell profile ..."
  case "${SHELL:-}" in
    *zsh) PROFILE="$HOME/.zshrc" ;;
    *bash) [[ -f "$HOME/.bash_profile" ]] && PROFILE="$HOME/.bash_profile" || PROFILE="$HOME/.bashrc" ;;
    *) PROFILE="" ;;
  esac
  if [[ -n "$PROFILE" ]]; then
    touch "$PROFILE"
    if grep -q 'MOLTABLE_API_KEY' "$PROFILE" 2>/dev/null; then
      warn "      MOLTABLE_API_KEY already present in $PROFILE — leaving it untouched."
      warn "      → Make sure it matches your current key; otherwise edit $PROFILE."
    else
      printf '\n# Moltable — AI Identity Sync (added by claude-code/install.sh)\nexport MOLTABLE_API_KEY="%s"\n' "$API_KEY" >> "$PROFILE"
      info "      ✓ Added export to $PROFILE"
      info "      → Run 'source $PROFILE' or open a new terminal to pick it up."
    fi
  else
    warn "      Could not detect a shell profile — set it manually:"
    warn "      export MOLTABLE_API_KEY=\"$API_KEY\""
  fi
else
  warn "4/4  --no-profile given — set the key manually:"
  warn "      export MOLTABLE_API_KEY=\"$API_KEY\""
fi

echo
info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
info "  ✓ Moltable is installed for Claude Code!"
info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
info "  Next steps:"
info "    1. Restart Claude Code (or reload MCP servers) in: $TARGET_DIR"
info "    2. Ask Claude:  \"/moltable\"   → loads the Moltable command guide"
info "    3. First run:   \"Use Moltable to auto-provision my identity\""
info "                    → Claude runs auto_provision and syncs your context"
info "    4. Everyday:    \"Save that as a preference\" / \"Recall what I prefer\""
echo
info "  Example prompts:"
info "    • Provision:      \"Provision my Moltable identity\""
info "    • Save:           \"Remember my preference: always use tabs, 2-space indent\""
info "    • Recall:         \"What do I prefer for code style?\""
info "    • Persona:        \"Switch to my code-review persona\""
info "    • Environment:    \"Discover this project's environment\""
echo
info "  Config:      $MCP_JSON"
info "  Endpoint:    $MCP_URL"
info "  Register:    $REGISTER_URL"
info "  Uninstall:   remove the \"moltable\" entry from $MCP_JSON (backup: ${BACKUP:-none})"
echo
