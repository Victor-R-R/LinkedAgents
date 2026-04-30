#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────
# LinkedAgents — Installer
# ─────────────────────────────────────────────

SKILLS_DIR="${HOME}/.claude/skills"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MCP_PACKAGE="linkedin-scraper-mcp"
MCP_NAME="linkedin"

AGENTS=(
  "post-agent:linkedin-post-agent"
  "jobs-agent:linkedin-jobs-agent"
  "article-agent:linkedin-article-agent"
  "research-agent:linkedin-research-agent"
  "design-agent:linkedin-design-agent"
  "profile-agent:linkedin-profile-agent"
  "messages-agent:linkedin-messages-agent"
  "orchestrator:linkedin-orchestrator"
)

# ─── Helpers ───────────────────────────────────
green()  { echo -e "\033[0;32m$*\033[0m"; }
yellow() { echo -e "\033[0;33m$*\033[0m"; }
red()    { echo -e "\033[0;31m$*\033[0m"; }
bold()   { echo -e "\033[1m$*\033[0m"; }
step()   { echo ""; bold "[$1] $2"; }

# ─── Pre-flight ────────────────────────────────
echo ""
bold "LinkedAgents — Installation"
echo "══════════════════════════════════════════════"

# ─── Step 1: Claude Code ───────────────────────
step "1/4" "Checking Claude Code"

if ! command -v claude &>/dev/null; then
  red "❌  Claude Code not found."
  echo "    Install it: npm install -g @anthropic/claude-code"
  echo "    Or download: https://claude.ai/code"
  exit 1
fi
green "  ✅  Claude Code found ($(claude --version 2>/dev/null || echo 'installed'))"

# ─── Step 2: uv / uvx ─────────────────────────
step "2/4" "Checking uv (Python package runner)"

if ! command -v uvx &>/dev/null; then
  yellow "  ⚠️  uvx not found — installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # Reload PATH for current shell
  export PATH="${HOME}/.cargo/bin:${HOME}/.local/bin:${PATH}"
  if ! command -v uvx &>/dev/null; then
    red "❌  uv installation failed. Install manually: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
  fi
fi
green "  ✅  uvx found ($(uvx --version 2>/dev/null || echo 'installed'))"

# ─── Step 3: LinkedIn MCP server ──────────────
step "3/4" "Setting up LinkedIn MCP server"

echo "  Registering '${MCP_NAME}' MCP server in Claude Code..."

# Check if already registered
if claude mcp list 2>/dev/null | grep -q "^${MCP_NAME}"; then
  green "  ✅  MCP server '${MCP_NAME}' already registered"
else
  claude mcp add "${MCP_NAME}" -- uvx "${MCP_PACKAGE}"
  green "  ✅  MCP server '${MCP_NAME}' registered"
fi

# Check if already authenticated
if [ -f "${HOME}/.linkedin-mcp/cookies.json" ]; then
  green "  ✅  LinkedIn session found (${HOME}/.linkedin-mcp/cookies.json)"
else
  echo ""
  yellow "  ⚠️  No LinkedIn session detected."
  echo "  You need to log in once to create a persistent session."
  echo ""
  echo "  Run this command now (opens a browser window):"
  echo ""
  bold "    uvx ${MCP_PACKAGE} --login"
  echo ""
  read -r -p "  Run it now? [Y/n] " RUN_LOGIN
  RUN_LOGIN="${RUN_LOGIN:-Y}"
  if [[ "$RUN_LOGIN" =~ ^[Yy]$ ]]; then
    echo "  Starting login flow..."
    uvx "${MCP_PACKAGE}" --login
    if [ -f "${HOME}/.linkedin-mcp/cookies.json" ]; then
      green "  ✅  LinkedIn session saved"
    else
      yellow "  ⚠️  Session file not found — login may not have completed."
      echo "    Re-run: uvx ${MCP_PACKAGE} --login"
    fi
  else
    yellow "  ⚠️  Skipped. Run later: uvx ${MCP_PACKAGE} --login"
  fi
fi

# ─── Step 4: Install agents ───────────────────
step "4/4" "Installing agents to Claude Code skills"

mkdir -p "$SKILLS_DIR"
echo ""

INSTALLED=0
SKIPPED=0

for entry in "${AGENTS[@]}"; do
  SRC="${entry%%:*}"
  DEST="${entry##*:}"
  SRC_FILE="${REPO_DIR}/${SRC}/SKILL.md"
  DEST_DIR="${SKILLS_DIR}/${DEST}"

  if [ ! -f "$SRC_FILE" ]; then
    yellow "  ⚠️  Skipping ${DEST} — SKILL.md not found"
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  mkdir -p "$DEST_DIR"
  cp "$SRC_FILE" "${DEST_DIR}/SKILL.md"
  green "  ✅  ${DEST}"
  INSTALLED=$((INSTALLED + 1))
done

# Output directory
mkdir -p "${HOME}/LinkedAgents/output"
green "  ✅  ~/LinkedAgents/output/ (output directory)"

# ─── LinkedIn API (optional) ──────────────────
echo ""
echo "══════════════════════════════════════════════"
bold "Optional — LinkedIn API (post publishing)"
echo ""
echo "The MCP server handles messaging, search, and connections."
echo "To also PUBLISH posts via API, add these to ~/.zshrc:"
echo ""
cat << 'EOF'
  export LINKEDIN_TOKEN="your_access_token"
  export LINKEDIN_PERSON_ID="your_person_id"
  export LINKEDIN_REFRESH_TOKEN="your_refresh_token"
  export LINKEDIN_CLIENT_ID="your_app_client_id"
  export LINKEDIN_CLIENT_SECRET="your_app_secret"
  export LINKEDIN_TOKEN_DATE="$(date +%Y-%m-%d)"
EOF
echo ""
echo "  Get your token: https://www.linkedin.com/developers/tools/oauth/token-generator"
echo "  Required scopes: w_member_social  openid  profile  email"

if [ -n "${LINKEDIN_TOKEN:-}" ] && [ -n "${LINKEDIN_PERSON_ID:-}" ]; then
  echo ""
  green "✅  LINKEDIN_TOKEN and LINKEDIN_PERSON_ID already set."
fi

# ─── Done ─────────────────────────────────────
echo ""
echo "══════════════════════════════════════════════"
bold "Done — ${INSTALLED} agents installed"
[ "$SKIPPED" -gt 0 ] && yellow "Skipped: ${SKIPPED} (SKILL.md missing)"
echo ""
echo "Restart Claude Code, then try:"
echo '  "Prepare my LinkedIn week"'
echo '  "Read my LinkedIn messages"'
echo '  "Draft a LinkedIn post about [your topic]"'
echo ""
