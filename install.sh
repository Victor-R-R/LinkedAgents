#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────
# LinkedAgents — Installer
# ─────────────────────────────────────────────

SKILLS_DIR="${HOME}/.claude/skills"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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

# ─── Pre-flight ────────────────────────────────
echo ""
bold "LinkedAgents — Installation"
echo "──────────────────────────────────────────────"

# Check Claude Code is installed
if ! command -v claude &>/dev/null; then
  red "❌  Claude Code not found."
  echo "    Install it first: https://claude.ai/code"
  exit 1
fi

# Create skills directory if needed
mkdir -p "$SKILLS_DIR"

# ─── Install agents ────────────────────────────
echo ""
echo "Installing agents to: $SKILLS_DIR"
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

# ─── Output directory ──────────────────────────
mkdir -p "${HOME}/LinkedAgents/output"
green "  ✅  ~/LinkedAgents/output/ (output directory)"

# ─── Summary ───────────────────────────────────
echo ""
echo "──────────────────────────────────────────────"
bold "Installed: ${INSTALLED} agents"
[ "$SKIPPED" -gt 0 ] && yellow "Skipped:   ${SKIPPED} (SKILL.md missing)"

# ─── Environment variables ─────────────────────
echo ""
bold "Next step — LinkedIn API setup"
echo ""
echo "Add these to your ~/.zshrc (or ~/.bashrc):"
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
echo "Get your token at:"
echo "  https://www.linkedin.com/developers/tools/oauth/token-generator"
echo ""
echo "Required scopes: w_member_social  r_basicprofile  openid  profile  email"
echo ""

# ─── Check if vars are already set ─────────────
if [ -n "${LINKEDIN_TOKEN:-}" ] && [ -n "${LINKEDIN_PERSON_ID:-}" ]; then
  green "✅  LINKEDIN_TOKEN and LINKEDIN_PERSON_ID are already set."
else
  yellow "⚠️   LINKEDIN_TOKEN / LINKEDIN_PERSON_ID not detected in current shell."
  echo "    Set them and run: source ~/.zshrc"
fi

echo ""
bold "Done. Open Claude Code and try:"
echo '  "Prepare my LinkedIn week"'
echo '  "Draft a LinkedIn post about Appel Internat"'
echo ""
