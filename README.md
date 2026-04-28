# LinkedAgents

> A suite of 6 specialized Claude Code agents for managing your LinkedIn presence — from content creation to career discovery.

## Agents

| Agent | File | Purpose |
|-------|------|---------|
| Post Agent | `post-agent/SKILL.md` | Draft and publish LinkedIn posts via API |
| Jobs Agent | `jobs-agent/SKILL.md` | Search, score, and act on job listings |
| Article Agent | `article-agent/SKILL.md` | Write long-form LinkedIn articles |
| Research Agent | `research-agent/SKILL.md` | Curate trending content for your niche |
| Design Agent | `design-agent/SKILL.md` | Create visuals, carousels, and brand identity |
| Profile Agent | `profile-agent/SKILL.md` | Audit and rewrite your LinkedIn profile |
| Orchestrator | `orchestrator/SKILL.md` | Coordinate the full weekly workflow |

## Installation (Claude Code)

### Option 1 — Script (recommended)

```bash
git clone https://github.com/Victor-R-R/LinkedAgents.git
cd LinkedAgents
./install.sh
```

The script checks for Claude Code, installs all agents to `~/.claude/skills/`, and guides you through the LinkedIn API setup.

### Option 2 — One-liner

```bash
git clone https://github.com/Victor-R-R/LinkedAgents.git && cd LinkedAgents && ./install.sh
```

### Option 3 — Manual (install only the agents you want)

```bash
mkdir -p ~/.claude/skills/linkedin-post-agent
cp post-agent/SKILL.md ~/.claude/skills/linkedin-post-agent/SKILL.md
```

Repeat for any agent you want.

---

## LinkedIn API Setup

### 1. Create your app

1. Go to [LinkedIn Developer Portal](https://developer.linkedin.com/)
2. Create a new app and add the **"Share on LinkedIn"** product
3. Under OAuth 2.0, set your redirect URI (e.g. `http://localhost:3000/callback`)

### 2. Required OAuth scopes

| Scope | Purpose |
|-------|---------|
| `w_member_social` | Publish posts on your behalf |
| `r_basicprofile` | Read your profile (name, headline) |
| `openid` | OAuth 2.0 identity |
| `profile` | Extended profile fields |
| `email` | Your email address |

### 3. Generate a token

Go to: `https://www.linkedin.com/developers/tools/oauth/token-generator`

Select scopes: `w_member_social`, `r_basicprofile`, `openid`, `profile`, `email`

You will receive:
- **Access token** — valid for 60 days
- **Refresh token** — valid for ~1 year (keep it safe)

### 4. Get your Person ID

```bash
curl -s -H "Authorization: Bearer $LINKEDIN_TOKEN" \
     -H "LinkedIn-Version: 202410" \
     https://api.linkedin.com/v2/userinfo | jq '{sub, name}'
# "sub" = your Person ID
```

### 5. Set environment variables

Add to `~/.zshrc`:

```bash
export LINKEDIN_TOKEN="your_access_token"
export LINKEDIN_PERSON_ID="your_person_id"         # The "sub" field from /v2/userinfo
export LINKEDIN_REFRESH_TOKEN="your_refresh_token"
export LINKEDIN_CLIENT_ID="your_app_client_id"
export LINKEDIN_CLIENT_SECRET="your_app_secret"
export LINKEDIN_TOKEN_DATE="2025-03-15"            # Date you generated the token
```

Then reload: `source ~/.zshrc`

### 6. Refresh an expired token (before 60 days)

```bash
curl -s -X POST "https://www.linkedin.com/oauth/v2/accessToken" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=refresh_token&refresh_token=${LINKEDIN_REFRESH_TOKEN}&client_id=${LINKEDIN_CLIENT_ID}&client_secret=${LINKEDIN_CLIENT_SECRET}" \
  | jq '{access_token, expires_in, refresh_token}'
# Update LINKEDIN_TOKEN and LINKEDIN_TOKEN_DATE with the new values
```

---

## API Limitations

| Feature | Available | Notes |
|---------|-----------|-------|
| Publish posts | ✅ | `w_member_social` scope, `/rest/posts` endpoint |
| Read own profile (basic) | ✅ | `/v2/userinfo` — name, headline, email |
| Edit profile sections | ❌ | Not available publicly — manual edits only |
| Job search API | ❌ | Partner Program required — fallback to web search |
| Follower analytics | ❌ | Partner Program required |
| Publish articles | ✅ | Via post with article URL |

> **API note**: This project uses the **Posts API** (`/rest/posts` with `LinkedIn-Version: 202410`).
> The legacy `ugcPosts` endpoint is officially deprecated and no longer used.

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

## Project Structure

```
LinkedAgents/
├── README.md
├── post-agent/
│   └── SKILL.md
├── jobs-agent/
│   └── SKILL.md
├── article-agent/
│   └── SKILL.md
├── research-agent/
│   └── SKILL.md
├── design-agent/
│   └── SKILL.md
├── profile-agent/
│   └── SKILL.md
├── orchestrator/
│   └── SKILL.md
└── output/              # Generated files (gitignored)
```

---

## Usage Examples

```
"Draft a LinkedIn post about Appel Internat for CPEs"
→ Triggers: linkedin-post-agent

"Find full-stack developer jobs in Île-de-France"
→ Triggers: linkedin-jobs-agent

"Write an article about building a SaaS as an AED"
→ Triggers: linkedin-article-agent

"What's trending in EdTech this week?"
→ Triggers: linkedin-research-agent

"Design a post card for Appel Internat"
→ Triggers: linkedin-design-agent

"Audit and rewrite my LinkedIn headline"
→ Triggers: linkedin-profile-agent

"Prepare my LinkedIn week"
→ Triggers: linkedin-orchestrator
```

---

Built for [Appel Internat](https://appel-internat.com) · Victor · Seine-et-Marne, France
