---
name: linkedin-orchestrator
description: Master orchestrator for the full LinkedIn weekly workflow. Use this skill when the user wants to plan their LinkedIn week, run a full LinkedIn session, get a weekly content plan, or coordinate multiple LinkedIn tasks at once. Trigger for phrases like "prepare my LinkedIn week", "run my LinkedIn session", "what should I post this week", "LinkedIn weekly plan", "full LinkedIn workflow", or "orchestrate my LinkedIn". Coordinates the research, post, article, design, and profile agents in a structured sequence and outputs a complete weekly action plan.
---

# LinkedIn Orchestrator

Master coordinator for the LinkedAgents suite. Runs a full weekly LinkedIn workflow by sequencing the 5 specialist agents in the right order and producing a unified, actionable output.

> This agent does not replace the specialists — it directs them.
> For any single task (just a post, just a carousel), trigger the specialist agent directly.
> Use the orchestrator when you want the **full weekly picture**.

---

## When to trigger this agent

| User says | Orchestrator response |
|-----------|-----------------------|
| "Prepare my LinkedIn week" | Full 5-phase workflow |
| "What should I post this week?" | Research → Post Calendar only |
| "Run a full LinkedIn session" | Full 5-phase workflow |
| "I have 30 minutes for LinkedIn" | Abbreviated run, phases 2 + 3 only |
| "LinkedIn status check" | Token check + profile score only |

---

## Pre-flight Checks

Before starting any workflow, run these silently:

### 1. Output directory (persistent)
```bash
mkdir -p ~/LinkedAgents/output
```

> Files are saved to `~/LinkedAgents/output/` — persistent across reboots.
> Do NOT use `/tmp/` — it is cleared on every restart.

### 2. Token status check
```bash
# Check if LINKEDIN_TOKEN is set
if [ -z "$LINKEDIN_TOKEN" ]; then
  echo "⚠️  LINKEDIN_TOKEN not set. Publishing will be disabled."
  echo "    Set it with: export LINKEDIN_TOKEN='your_token_here'"
fi

# Check if LINKEDIN_PERSON_ID is set
if [ -z "$LINKEDIN_PERSON_ID" ]; then
  echo "⚠️  LINKEDIN_PERSON_ID not set."
  echo "    Get it with: curl -s -H \"Authorization: Bearer \$LINKEDIN_TOKEN\" -H \"LinkedIn-Version: 202503\" https://api.linkedin.com/v2/userinfo | jq '.sub'"
fi

# Check token age if LINKEDIN_TOKEN_DATE is set (macOS-compatible)
if [ -n "$LINKEDIN_TOKEN_DATE" ]; then
  TOKEN_AGE=$(python3 -c "
from datetime import datetime
delta = datetime.now() - datetime.fromisoformat('$LINKEDIN_TOKEN_DATE')
print(delta.days)
" 2>/dev/null || echo "0")
  if [ "$TOKEN_AGE" -gt 50 ]; then
    echo "⚠️  LinkedIn token is ${TOKEN_AGE} days old — expires in $((60 - TOKEN_AGE)) days."
    echo "    Renew at: https://www.linkedin.com/developers/tools/oauth/token-generator"
    echo "    Or refresh automatically with: linkedin-post-agent refresh token"
  fi
fi
```

### 3. Confirm week + context
Ask the user (once, concisely):
- What week / date range are we planning for?
- Any specific topic, launch, or event this week? (or "nothing special")
- Posting frequency target: 2×/week, 3×/week, or daily?
- Language: FR, EN, or bilingual?

---

## The 5-Phase Weekly Workflow

```
Phase 1 — RESEARCH        linkedin-research-agent   ~10 min
Phase 2 — CALENDAR        Orchestrator logic         ~5 min
Phase 3 — CONTENT         linkedin-post-agent        ~15 min
Phase 4 — VISUALS         linkedin-design-agent      ~10 min
Phase 5 — PUBLISH / LOG   Orchestrator logic         ~5 min
```

---

### Phase 1 — Research

**Delegate to**: `linkedin-research-agent`

**Instruction to pass**:
> "Run a weekly research session for the week of {date}. Topics: EdTech France, internats, SaaS solo founder, Next.js ecosystem, RGPD éducation. Return: top 5 curated items with relevance scores, 3 trending themes, and 3 post ideas inspired by this week's content."

**Output expected**: Weekly digest (5 items + themes + post ideas)

```bash
WEEK=$(date +%Y-W%V)
OUTPUT_DIR=~/LinkedAgents/output
cat > "${OUTPUT_DIR}/research-${WEEK}.md" << 'ENDOFFILE'
{research output here}
ENDOFFILE
echo "✅ Research saved to ${OUTPUT_DIR}/research-${WEEK}.md"
```

---

### Phase 2 — Content Calendar

**Orchestrator builds this** from Phase 1 output + user preferences.

**Calendar format**:

```markdown
# LinkedIn Calendar — Week of {date}

| Slot | Day & Time | Format | Theme | Angle | Status |
|------|-----------|--------|-------|-------|--------|
| 1 | {Day} 07h45 | Post (text) | {theme} | {angle} | 🔲 Draft |
| 2 | {Day} 12h15 | Post + visual | {theme} | {angle} | 🔲 Draft |
| 3 | {Day} 17h30 | Reshare + take | {article from research} | {your take} | 🔲 Draft |
```

**Slot assignment rules**:
- Best days: Tuesday → Thursday
- Best times: 07:30–09:00 / 12:00–13:00 / 17:30–18:30
- For 2×/week: Tuesday 07h45 + Thursday 12h15
- For 3×/week: add Wednesday 17h30
- Never schedule 2 posts on the same day
- Alternate formats: text-only → visual → reshare → article

**Theme rotation** (cycle weekly):
1. Product update / feature reveal
2. Founder story / behind the scenes
3. Industry insight / market data
4. Social proof / user quote
5. Educational / how-to
6. Engagement question

```bash
WEEK=$(date +%Y-W%V)
OUTPUT_DIR=~/LinkedAgents/output
cat > "${OUTPUT_DIR}/calendar-${WEEK}.md" << 'ENDOFFILE'
{calendar here}
ENDOFFILE
echo "✅ Calendar saved to ${OUTPUT_DIR}/calendar-${WEEK}.md"
```

---

### Phase 3 — Content Drafting

**Delegate to**: `linkedin-post-agent` (once per post slot)

**Instruction to pass** (repeat for each slot):
> "Draft 3 variants for slot {N}: theme is '{theme}', angle is '{angle}', audience is '{audience}', language is '{FR/EN}', tone is '{tone}'. Apply Appel Internat context."

**For reshare slots**: ask research-agent for the draft commentary (3–5 lines + question).

**Output**: All drafts saved to `~/LinkedAgents/output/drafts-{YYYY-WNN}.md`

After all slots: present a summary table for the user to choose:

```
Slot 1: A / B / C ?
Slot 2: A / B / C ?
Slot 3: A / B / C ?
```

Wait for user input before proceeding to Phase 4.

---

### Phase 4 — Visuals

**Delegate to**: `linkedin-design-agent` (only for slots marked "Post + visual" or "Carousel")

**Instruction to pass**:
> "Create a post card for slot {N}. Text: '{approved draft headline}'. Format: 1200×627 post image. Brand: Appel Internat. Language: {FR/EN}. Save to ~/LinkedAgents/output/visual-slot{N}.html"

**For text-only posts**: skip this phase for that slot.
**For reshares**: no visual needed (LinkedIn auto-generates link preview).

After each visual:
```bash
open ~/LinkedAgents/output/visual-slot1.html
```

---

### Phase 5 — Publish & Log

> Uses the **Posts API** (current). The legacy `ugcPosts` endpoint is no longer used.

**For each approved slot**:

```bash
# Escape the post text for JSON
POST_TEXT_ESCAPED=$(echo "$POST_TEXT" | python3 -c "import sys, json; print(json.dumps(sys.stdin.read().strip()))" | sed 's/^"//;s/"$//')

RESPONSE=$(curl -s --fail -X POST "https://api.linkedin.com/rest/posts" \
  -H "Authorization: Bearer $LINKEDIN_TOKEN" \
  -H "Content-Type: application/json" \
  -H "LinkedIn-Version: 202503" \
  -H "X-Restli-Protocol-Version: 2.0.0" \
  -d "{
    \"author\": \"urn:li:person:${LINKEDIN_PERSON_ID}\",
    \"commentary\": \"${POST_TEXT_ESCAPED}\",
    \"visibility\": \"PUBLIC\",
    \"distribution\": {
      \"feedDistribution\": \"MAIN_FEED\",
      \"targetEntities\": [],
      \"thirdPartyDistributionChannels\": []
    },
    \"lifecycleState\": \"PUBLISHED\",
    \"isReshareDisabledByAuthor\": false
  }")

HTTP_CODE=$(echo "$RESPONSE_FULL" | grep "^HTTP" | awk '{print $2}')
# Post URN is in x-restli-id header — NOT in response body
POST_URN=$(echo "$RESPONSE_FULL" | grep -i "x-restli-id:" | awk '{print $2}' | tr -d '\r')

if [ "$HTTP_CODE" != "201" ]; then
  echo "❌ Publish failed — HTTP $HTTP_CODE"
  echo "   Check LINKEDIN_TOKEN (expires after 60 days) and LINKEDIN_PERSON_ID."
else
  echo "✅ Published — Post URN: $POST_URN"
  echo "   Save URN to delete later: $POST_URN"
fi
```

**Always confirm before publishing**:
> Show exact post text → ask "Confirmer la publication ? (oui/non)"
> Never auto-publish.

**Session log**:
```bash
OUTPUT_DIR=~/LinkedAgents/output
cat >> "${OUTPUT_DIR}/session-log.md" << ENDOFFILE

## Session — $(date '+%Y-%m-%d %H:%M')
- Week: $(date +%Y-W%V)
- Posts drafted: {N}
- Posts approved: {N}
- Posts published: {N}
- Visuals created: {N}
- Token status: {OK / ⚠️ expiring in N days / ❌ not set}
- Notes: {any user notes}
ENDOFFILE
```

---

## Abbreviated Flows

### "I have 30 minutes"
Run phases 2 + 3 only:
- Skip research (use last week's if available in `~/LinkedAgents/output/`)
- Build calendar for 2 slots max
- Draft 1 variant per slot (not 3)
- No visuals
- No publishing

### "Just give me post ideas"
Run phase 1 only (research-agent weekly digest).

### "Status check"
- Check token expiry
- Show last session log entry (`tail -30 ~/LinkedAgents/output/session-log.md`)
- Show what's scheduled this week (if calendar exists)
- Score: how many posts were published vs planned last week?

---

## Master Output Summary

At the end of a full session, print:

```
╔══════════════════════════════════════════════════════╗
║         LinkedIn Weekly Summary — W{NN} {YYYY}       ║
╠══════════════════════════════════════════════════════╣
║  📰 Research    5 items curated · 3 themes identified ║
║  📅 Calendar    {N} slots planned                     ║
║  ✍️  Drafts      {N} posts drafted and approved        ║
║  🎨 Visuals     {N} cards generated                   ║
║  🚀 Published   {N} posts live                        ║
║  🔑 Token       {OK / ⚠️ renew in N days}              ║
╠══════════════════════════════════════════════════════╣
║  Files: ~/LinkedAgents/output/                       ║
║  · research-{W}.md                                   ║
║  · calendar-{W}.md                                   ║
║  · drafts-{W}.md                                     ║
║  · visual-slot*.html                                 ║
║  · session-log.md                                    ║
╚══════════════════════════════════════════════════════╝
```

---

## Agent Dependency Map

```
linkedin-orchestrator
├── linkedin-research-agent   (Phase 1)
├── linkedin-post-agent       (Phase 3, once per slot)
├── linkedin-design-agent     (Phase 4, visual slots only)
└── [linkedin-article-agent]  (optional, if long-form planned)
    └── linkedin-profile-agent (standalone, not in weekly flow)
```

`linkedin-jobs-agent` is standalone — trigger directly, not via orchestrator.
`linkedin-profile-agent` is quarterly — run on demand, not weekly.

---

## Environment Variables Reference

```bash
# Required for publishing
export LINKEDIN_TOKEN="your_access_token"         # Expires in 60 days
export LINKEDIN_PERSON_ID="your_person_id"        # The "sub" field from GET /v2/userinfo
export LINKEDIN_REFRESH_TOKEN="your_refresh"      # Expires in 1 year — use to renew access token
export LINKEDIN_CLIENT_ID="your_app_client_id"
export LINKEDIN_CLIENT_SECRET="your_app_secret"

# Optional but recommended
export LINKEDIN_TOKEN_DATE="2025-03-15"           # Set when you regenerate — orchestrator warns at day 50+
```

Add to `~/.zshrc` to persist across sessions.
