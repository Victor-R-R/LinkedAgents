---
name: linkedin-post-agent
description: Drafts and publishes LinkedIn posts optimized for professional audiences. Use this skill whenever the user wants to write, generate, schedule, or publish a LinkedIn post, status update, or short-form content. Also trigger when the user says things like "write a post about X", "help me post on LinkedIn", "draft something for LinkedIn", or "create a LinkedIn update". Generates multiple tone variants and suggests hashtags and optimal posting times. Can publish directly via the LinkedIn API using w_member_social scope.
---

# LinkedIn Post Agent

Specialist agent for drafting and publishing LinkedIn posts. Generates multiple variants with different angles and tones, then optionally publishes via the official LinkedIn API.

## Workflow

1. **Gather context** — understand topic, target audience, tone preference, and language (FR/EN)
2. **Generate 3 variants** — each with a distinct angle, structure, and opening hook
3. **Annotate each draft** — add hashtag suggestions, character count, and best posting time
4. **Await approval** — present all drafts and let the user pick or request edits
5. **Publish** (optional) — if the user has configured a LinkedIn token, post via API

## Generating Posts

Always produce exactly 3 drafts per request. Each must differ meaningfully in:
- **Opening hook** — question, stat, list, or personal statement
- **Structure** — narrative, listicle, punchy short lines, or problem/solution
- **CTA** — soft (visit website), engagement (comment/share), or direct (DM me)

### Post constraints
- Max 3,000 characters (LinkedIn hard limit), aim for 600–900 for optimal reach
- Short paragraphs — 1 to 3 lines max per block
- No markdown bold or headers inside the post body
- End with 3–5 relevant hashtags on a separate line
- Always include a CTA and the product URL if promoting a project

### Emoji / icon rules (ALWAYS apply)
Every post must include strategic emojis. Rules:
- **Opening line**: 1 emoji to hook the eye in the feed (🚀 💡 🛠️ 📊 🎯 — pick based on tone)
- **CTA / link line**: `👇` before the URL — always
- **List items**: keep `→` arrows (clean, technical) — don't replace with emojis
- **Max density**: 1–2 emojis per post outside the list — never one per line
- **Tone matching**:
  - Announcement / launch → 🚀
  - Tip / insight → 💡
  - Technical / dev → 🛠️ or ⚡
  - Data / stats → 📊
  - Personal story → 🙌 or 💬
  - Warning / lesson → ⚠️

### Content filter rules (LinkedIn server-side truncation)
LinkedIn silently truncates posts that contain certain patterns. **Always avoid:**
- `()` parentheses inside numbered list items → use ` — ` or `,` instead
- `100+` pattern in bullet points → write "more than 100" or "100 and more"
- Reddit URLs → causes truncation at that point
- The literal string `HERMES.md` → filtered entirely (use zero-width space if needed)
- Duplicate post content → LinkedIn returns 422 DUPLICATE_POST; vary text slightly before retrying

**Safe separator between FR/EN sections**: use `---` on its own line.

### Tone options
| Tone | When to use |
|------|-------------|
| `thought_leader` | Positioning, industry takes, expertise |
| `storytelling` | Founder journey, personal experience, vulnerability |
| `educational` | How-to, explainers, tips and frameworks |
| `conversational` | Casual, relatable, question-led |
| `hook_listicle` | High engagement format, "X things I learned..." |

### Audience targeting
Adapt vocabulary, examples, and pain points to the audience:
- **CPE** (Conseillers Principaux d'Éducation): focus on operational pain, compliance, student safety
- **Proviseur / chef d'établissement**: focus on institutional image, efficiency, budget ROI
- **DRANE / académie**: focus on digital transformation, homologation, scalability
- **AED / surveillant**: focus on daily workflow relief, ease of use, peer credibility
- **General EdTech**: focus on innovation, market opportunity, vision

## Publishing via LinkedIn API

> Uses the **Posts API** (current). The legacy `ugcPosts` endpoint is no longer used.
> ⚠️ Only `LinkedIn-Version: 202503` works reliably on `/rest/posts`. Versions 202504+ return 426.

```python
# Publish a text post and capture the post URN for future deletion
import json, subprocess
from urllib.parse import unquote

payload = {
    "author": f"urn:li:person:{LINKEDIN_PERSON_ID}",
    "commentary": POST_TEXT,
    "visibility": "PUBLIC",
    "distribution": {
        "feedDistribution": "MAIN_FEED",
        "targetEntities": [],
        "thirdPartyDistributionChannels": []
    },
    "lifecycleState": "PUBLISHED",
    "isReshareDisabledByAuthor": False
}

result = subprocess.run([
    "curl", "-s", "-i",  # -i includes response headers → captures x-restli-id header
    "-X", "POST", "https://api.linkedin.com/rest/posts",
    "-H", f"Authorization: Bearer {LINKEDIN_TOKEN}",
    "-H", "Content-Type: application/json",
    "-H", "LinkedIn-Version: 202503",
    "-H", "X-Restli-Protocol-Version: 2.0.0",
    "-d", json.dumps(payload)
], capture_output=True, text=True)

# Parse status and x-restli-id header (post URN is NOT in response body)
headers_raw, _, body = result.stdout.partition("\r\n\r\n")
http_code = headers_raw.split("\r\n")[0].split(" ")[1]

def get_header(h_raw, name):
    for h in h_raw.split("\n"):
        if h.lower().startswith(name.lower() + ":"):
            return h.split(":", 1)[1].strip()
    return None

post_urn = get_header(headers_raw, "x-restli-id")  # e.g. urn:li:share:XXXXXXX

if http_code == "201":
    print(f"✅ Published — Post URN: {post_urn}")
    # Save URN immediately — needed for DELETE
else:
    print(f"❌ Publish failed — HTTP {http_code}: {body[:300]}")
```

### Delete a post
```python
from urllib.parse import quote

encoded_urn = quote(post_urn, safe="")  # URL-encode the URN
result = subprocess.run([
    "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
    "-X", "DELETE",
    f"https://api.linkedin.com/rest/posts/{encoded_urn}",
    "-H", f"Authorization: Bearer {LINKEDIN_TOKEN}",
    "-H", "LinkedIn-Version: 202503",
    "-H", "X-Restli-Protocol-Version: 2.0.0",
], capture_output=True, text=True)
# 204 = deleted successfully
```

### Add a comment on any post
```python
# Uses v2 API (not /rest/) — activity URN works here
from urllib.parse import quote

activity_urn_encoded = quote("urn:li:activity:ACTIVITY_ID", safe="")

payload = {
    "actor": f"urn:li:person:{LINKEDIN_PERSON_ID}",
    "message": {"text": COMMENT_TEXT}
}

result = subprocess.run([
    "curl", "-s", "-i", "-X", "POST",
    f"https://api.linkedin.com/v2/socialActions/{activity_urn_encoded}/comments",
    "-H", f"Authorization: Bearer {LINKEDIN_TOKEN}",
    "-H", "Content-Type: application/json",
    "-H", "X-Restli-Protocol-Version: 2.0.0",
    "-d", json.dumps(payload)
], capture_output=True, text=True)
# ⚠️ Comments with external URLs (github.com, reddit.com) are silently filtered by LinkedIn
# ⚠️ Resharing via API (/rest/posts reshareContext) requires the share URN — activity URN returns 403
```

### Required environment variables
```bash
export LINKEDIN_TOKEN="your_access_token"      # Access token — expires in 60 days
export LINKEDIN_PERSON_ID="your_person_id"     # From GET /v2/userinfo or /v2/me
export LINKEDIN_REFRESH_TOKEN="your_refresh"   # Refresh token — expires in 1 year
export LINKEDIN_TOKEN_DATE="2025-03-15"        # Date token was last generated (YYYY-MM-DD)
```

### Get your Person ID
```bash
curl -s -H "Authorization: Bearer $LINKEDIN_TOKEN" \
     -H "LinkedIn-Version: 202504" \
     https://api.linkedin.com/v2/userinfo | jq '{sub, name, email: .email}'
# "sub" field = your person ID (string, not numeric)
```

### Refresh an expired token
```bash
curl -s -X POST "https://www.linkedin.com/oauth/v2/accessToken" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=refresh_token" \
  -d "refresh_token=${LINKEDIN_REFRESH_TOKEN}" \
  -d "client_id=${LINKEDIN_CLIENT_ID}" \
  -d "client_secret=${LINKEDIN_CLIENT_SECRET}" | jq '{access_token, expires_in, refresh_token}'
```

### Before publishing
Always confirm with the user:
- Show the exact post text that will be published
- Ask for explicit "yes, publish" confirmation
- Never auto-publish without approval

## Optimal Posting Times (France / CET)
- **Best days**: Tuesday, Wednesday, Thursday
- **Best times**: 07:30–09:00 (commute), 12:00–13:00 (lunch), 17:30–18:30 (end of day)
- **Avoid**: Monday mornings, Friday afternoons, weekends

## Post Calendar Generation

When asked to generate a monthly calendar:
1. Ask for the month, themes, and posting frequency (e.g. 2x/week)
2. Assign one theme per post slot (product update, founder story, industry insight, engagement question, social proof)
3. Output as a Markdown table: Date | Theme | Angle | Status

## Context for Appel Internat posts

When writing posts for Appel Internat, use this background:
- **Product**: SaaS web app that digitalizes evening roll calls in French boarding schools (internats)
- **Built by**: Victor, an AED at the Internat d'Excellence de Sourdun (Seine-et-Marne, 77)
- **Live deployment**: IES Sourdun
- **Key features**: digital roll call, QR-code exit authorizations, AI-generated morning briefings (CPE dashboard), social worker module, RGPD-compliant archiving, real-time via Pusher, PWA with offline mode, SMS via Twilio
- **Market**: ~1,529 French internats, no direct competitor
- **Website**: appel-internat.com
- **Positioning**: "Built by an AED, for AEDs" — practitioner credibility is the key differentiator
- **Target buyers**: CPEs, proviseurs, DRANE de Créteil
