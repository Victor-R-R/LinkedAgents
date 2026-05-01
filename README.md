# LinkedAgents

> A suite of 7 specialized Claude Code agents + 1 orchestrator for managing your LinkedIn presence — from content creation to inbox management and career discovery.

## Agents

| Agent | Skill | Purpose | Requires MCP |
|-------|-------|---------|:------------:|
| Post Agent | `post-agent/SKILL.md` | Draft and publish LinkedIn posts via API | — |
| Jobs Agent | `jobs-agent/SKILL.md` | Search, score, and act on job listings | ✅ |
| Article Agent | `article-agent/SKILL.md` | Write long-form LinkedIn articles | — |
| Research Agent | `research-agent/SKILL.md` | Curate trending content for your niche | ✅ |
| Design Agent | `design-agent/SKILL.md` | Create visuals, carousels, and brand identity | — |
| Profile Agent | `profile-agent/SKILL.md` | Audit and rewrite your LinkedIn profile | ✅ |
| Messages Agent | `messages-agent/SKILL.md` | Read inbox, draft replies, manage conversations | ✅ |
| Orchestrator | `orchestrator/SKILL.md` | Coordinate the full weekly workflow | ✅ (partial) |

---

## Requirements

- [Claude Code](https://claude.ai/code) installed and authenticated
- [uv](https://docs.astral.sh/uv/) — the install script installs it automatically if missing

> The LinkedIn MCP server (`linkedin-scraper-mcp`) is installed and configured automatically by `install.sh`. No manual setup needed.

> Each person needs their own LinkedIn account credentials. Sessions are stored locally in `~/.linkedin-mcp/` and are not shared.

---

## Installation

### One-liner (recommended)

```bash
git clone https://github.com/Victor-R-R/LinkedAgents.git && cd LinkedAgents && ./install.sh
```

The script handles everything in 4 steps:
1. Checks Claude Code is installed
2. Installs `uv` if missing
3. Registers the LinkedIn MCP server in Claude Code + opens a browser for LinkedIn login
4. Copies all agent skills to `~/.claude/skills/`

After install, **restart Claude Code** to activate the MCP server.

### Manual (pick only the agents you want)

```bash
# Register the MCP server
claude mcp add linkedin -- uvx linkedin-scraper-mcp

# Log in once (opens a browser)
uvx linkedin-scraper-mcp --login

# Copy specific agent skills
mkdir -p ~/.claude/skills/linkedin-post-agent
cp post-agent/SKILL.md ~/.claude/skills/linkedin-post-agent/SKILL.md
```

> Session refresh: if the MCP stops working, re-run `uvx linkedin-scraper-mcp --login`.

---

## LinkedIn API Setup

You need a LinkedIn Developer app to publish posts via API. This is a one-time setup.

### Step 1 — Create a LinkedIn Developer App

1. Go to [LinkedIn Developer Portal](https://developer.linkedin.com/apps)
2. Click **Create app** and fill in the details (your name, a LinkedIn Page, app logo)
3. Under the **Products** tab, add **both** of these products:
   - ✅ **Share on LinkedIn** — enables `w_member_social` (post publishing)
   - ✅ **Sign In with LinkedIn using OpenID Connect** — enables `openid`, `profile`, `email` scopes

> ⚠️ Both products are required. Without OpenID Connect, you cannot retrieve your Person ID.

### Step 2 — Generate an access token

1. Go to [OAuth Token Generator](https://www.linkedin.com/developers/tools/oauth/token-generator)
2. Select your app
3. Check all available scopes: `w_member_social`, `openid`, `profile`, `email`
4. Click **Request access token**

You will receive:
- **Access token** — valid for 60 days
- **Refresh token** — valid for ~1 year (keep it safe for renewal)

### Step 3 — Get your Person ID

```bash
curl -s -H "Authorization: Bearer YOUR_TOKEN" \
     -H "LinkedIn-Version: 202504" \
     https://api.linkedin.com/v2/userinfo | jq '{sub, name}'
# "sub" = your Person ID (looks like: "f-yME4Ji-J")
```

### Step 4 — Set environment variables

Add to `~/.zshrc` (or `~/.bashrc`):

```bash
export LINKEDIN_TOKEN="your_access_token"
export LINKEDIN_PERSON_ID="your_person_id"         # The "sub" field from Step 3
export LINKEDIN_CLIENT_ID="your_app_client_id"     # From app Auth tab
export LINKEDIN_CLIENT_SECRET="your_app_secret"    # From app Auth tab
export LINKEDIN_REFRESH_TOKEN="your_refresh_token" # From Step 2
export LINKEDIN_TOKEN_DATE="2026-04-28"            # Date you generated the token (YYYY-MM-DD)
```

Then reload: `source ~/.zshrc`

### Step 5 — Verify everything works

```bash
# Should print your name and person ID
curl -s -H "Authorization: Bearer $LINKEDIN_TOKEN" \
     -H "LinkedIn-Version: 202504" \
     https://api.linkedin.com/v2/userinfo | jq '{sub, name}'
```

---

## Refresh an expired token

Access tokens expire after 60 days. Use the refresh token to renew without re-authorizing:

```bash
curl -s -X POST "https://www.linkedin.com/oauth/v2/accessToken" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=refresh_token" \
  -d "refresh_token=${LINKEDIN_REFRESH_TOKEN}" \
  -d "client_id=${LINKEDIN_CLIENT_ID}" \
  -d "client_secret=${LINKEDIN_CLIENT_SECRET}" \
  | jq '{access_token, expires_in, refresh_token}'
# Update LINKEDIN_TOKEN and LINKEDIN_TOKEN_DATE with the new values
```

The orchestrator warns you automatically when your token is within 10 days of expiry.

---

## API Reference

| Feature | Status | Notes |
|---------|--------|-------|
| Publish text posts | ✅ | `w_member_social` scope, `/rest/posts` endpoint |
| Publish video posts | ✅ | Multipart upload via `/rest/videos` — see below |
| Read own profile (basic) | ✅ | `/v2/userinfo` — name, sub (Person ID), email |
| Edit profile sections | ❌ | Not available publicly — manual edits only |
| List/read own posts | ❌ | Requires `r_member_social` (partner program only) |
| Job search API | ❌ | Partner Program required — fallback to web search |
| Follower analytics | ❌ | Partner Program required |

**Working API versions (tested May 2026):**
- `/rest/posts` (publish) → `LinkedIn-Version: 202503`
- `/rest/videos` (video upload) → `LinkedIn-Version: 202503`
- `/v2/userinfo` (Person ID) → `LinkedIn-Version: 202504`

> Versions `202504+` return HTTP 426 on `/rest/posts`. Use `202503` exactly.

---

## Video Publishing

LinkedIn video upload uses a **3-step multipart flow** — not a simple PUT. `publish_video.py` handles the full flow automatically.

```bash
python3 publish_video.py
```

### How it works

1. **`initializeUpload`** — LinkedIn returns an array of `uploadInstructions`, each with a pre-signed URL and byte range (typically 3 parts for ~9 MB)
2. **Multipart PUT** — each part is uploaded to its pre-signed URL with only its byte slice; no `Authorization` header needed (auth is embedded in the URL)
3. **`finalizeUpload`** — called with the ETags returned by each part; LinkedIn returns 200 and begins video transcoding
4. **Create post** — post is created referencing the video URN; video becomes visible once transcoding completes (~2–5 min)

### Known gotchas

- `initializeUpload` returns URLs with embedded `\n` (base64 line breaks) — strip them before use
- LinkedIn does **not** return `uploadToken` in the current API version (202503); pass `""` to `finalizeUpload`
- Upload URLs are pre-signed — do **not** pass `Authorization: Bearer` to them
- ETags returned by LinkedIn look like `/ambry-video/signedId/...bin`, not standard HTTP ETags
- Video format: `.mov` (QuickTime) is accepted; transcoding takes 2–5 minutes after `finalizeUpload`
- The post is created immediately after upload; the video thumbnail appears once transcoding is done

---

## Usage

Once installed, trigger agents in Claude Code by describing what you want:

```
"Draft a LinkedIn post about my open source project"
→ Triggers: linkedin-post-agent

"Find full-stack developer jobs in Paris"
→ Triggers: linkedin-jobs-agent

"Write an article about building a SaaS solo"
→ Triggers: linkedin-article-agent

"What's trending in EdTech this week?"
→ Triggers: linkedin-research-agent

"Design a post card with icons for my announcement"
→ Triggers: linkedin-design-agent

"Audit and rewrite my LinkedIn headline"
→ Triggers: linkedin-profile-agent

"Read my LinkedIn messages"
→ Triggers: linkedin-messages-agent

"Reply to [name] on LinkedIn"
→ Triggers: linkedin-messages-agent

"Prepare my LinkedIn week"
→ Triggers: linkedin-orchestrator
```

---

## Output Files

All generated content is saved to `~/LinkedAgents/output/`:

```
~/LinkedAgents/output/
├── research-{YYYY-WNN}.md     # Weekly research digest
├── calendar-{YYYY-WNN}.md     # Content calendar
├── drafts-{YYYY-WNN}.md       # Post drafts
├── article-{slug}-{date}.md   # Article drafts
├── visual-slot*.html          # Design cards (open in browser)
└── session-log.md             # Running activity log
```

---

## Connection Management (bulk invitations)

Two scripts handle incoming connection requests. Both reuse the MCP server's stored cookies — no separate login needed.

### `scripts/process_invitations.py` — Bulk accept in one session (recommended)

Opens a single browser session, loads all pending invitations at once, and clicks Accept on each card directly — no per-profile navigation.

```bash
# Dry run — preview what would be accepted
uvx --from linkedin-scraper-mcp python3 scripts/process_invitations.py --dry-run

# Accept up to 20 (daily hard cap)
uvx --from linkedin-scraper-mcp python3 scripts/process_invitations.py --limit 20

# Accept only profiles matching keywords
uvx --from linkedin-scraper-mcp python3 scripts/process_invitations.py --filter "EdTech,DRH,fondateur"

# Save results
uvx --from linkedin-scraper-mcp python3 scripts/process_invitations.py --output ~/LinkedAgents/output/results.json
```

### `scripts/get_invitations.py` — Inspect only

Fetches the invitation list as JSON without accepting anything.

```bash
uvx --from linkedin-scraper-mcp python3 scripts/get_invitations.py --output ~/LinkedAgents/output/invitations.json
```

> **Rate limit**: LinkedIn allows ~20 connection actions per day. For 200+ invitations, run the script daily — it always picks the next batch.

---

## Project Structure

```
LinkedAgents/
├── README.md
├── install.sh
├── publish_video.py             # Publish a video post via LinkedIn API (multipart upload)
├── post-agent/SKILL.md
├── jobs-agent/SKILL.md
├── article-agent/SKILL.md
├── research-agent/SKILL.md
├── design-agent/SKILL.md
├── profile-agent/SKILL.md
├── messages-agent/SKILL.md
├── orchestrator/SKILL.md
├── scripts/
│   ├── get_invitations.py       # Inspect pending connection requests (read-only)
│   └── process_invitations.py  # Bulk-accept invitations in one session
└── output/                      # Generated files (gitignored)
```

---

Built with ❤️ and Claude Code · [Victor Rubia Rodriguez](https://github.com/Victor-R-R)
