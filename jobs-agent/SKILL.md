---
name: linkedin-jobs-agent
description: Searches, filters, and analyzes LinkedIn job listings relevant to the user's profile and goals. Use this skill when the user wants to find jobs, explore career opportunities, search for roles on LinkedIn, check what positions are available, or get a tailored cover letter for a specific listing. Also trigger for phrases like "find me jobs", "what roles are available for X", "LinkedIn job search", or "help me apply to this position". Scores each opportunity against the user's profile and can draft tailored cover letters per listing.
---

# LinkedIn Jobs Agent

Specialist agent for discovering, filtering, and acting on LinkedIn job opportunities. Uses web search as the primary discovery mechanism (LinkedIn Jobs API requires partner access), then applies AI analysis to rank and match against the user's profile.

## Workflow

1. **Profile intake** — gather or recall user's skills, location, seniority, salary range, and preferences
2. **Search** — run targeted web searches for job listings (see search strategy below)
3. **Score and rank** — evaluate each listing against the user's profile (0–10 match score)
4. **Present** — output a ranked summary with key details per role
5. **Act** — offer to draft a cover letter or tailor a CV summary for the selected role

## Job Search Strategy

> The LinkedIn Jobs API requires partner access and is not available for personal use.
> LinkedIn also blocks most `site:linkedin.com/jobs` queries on Google.
> Use the multi-source strategy below for reliable results.

### Search query patterns (in order of reliability)

```
# 1. Welcome to the Jungle (France's best job board, indexes LinkedIn reposts)
"{role}" "{location}" site:welcometothejungle.com

# 2. Indeed — broad coverage
"{role}" "{location}" CDI site:indeed.fr

# 3. LinkedIn direct URL (paste in browser, not web search)
https://www.linkedin.com/jobs/search/?keywords={role}&location={location}&f_TPR=r604800

# 4. French job boards
"{role}" "{location}" site:apec.fr OR site:regionsjob.com

# 5. Google general (least reliable for LinkedIn specifically)
"{role}" "{location}" EdTech CDI 2025
```

**Always run at least 3 different searches before presenting results.**
**Always include the direct LinkedIn search URL so the user can check it themselves.**

### LinkedIn direct search URL builder

```bash
# Encode the role and location for a URL
ROLE="développeur full-stack"
LOCATION="Île-de-France"
ENCODED_ROLE=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$ROLE'))")
ENCODED_LOC=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$LOCATION'))")

echo "Direct LinkedIn URL (paste in browser):"
echo "https://www.linkedin.com/jobs/search/?keywords=${ENCODED_ROLE}&location=${ENCODED_LOC}&f_TPR=r604800&f_JT=F"
# f_TPR=r604800 = posted in last 7 days
# f_JT=F = full-time only
```

### Search parameters to gather from user
| Parameter | Options |
|-----------|---------|
| Role / title | e.g. "développeur full-stack", "CTO", "lead dev EdTech" |
| Location | City, region, remote, hybrid |
| Contract type | CDI, CDD, freelance, alternance |
| Seniority | Junior, mid, senior, lead |
| Sector | EdTech, SaaS, public sector, startup |
| Salary range | Optional, used for filtering |
| Languages | French, English, both |

## Scoring Rubric

Score each listing on a 0–10 scale across these dimensions:

| Dimension | Weight | What to assess |
|-----------|--------|----------------|
| Skills match | 30% | % of required skills the user has |
| Sector fit | 20% | Alignment with user's domain experience |
| Role level | 20% | Seniority match (not over/under-qualified) |
| Location | 15% | Commute, remote policy vs user preference |
| Growth potential | 15% | Career trajectory, company stage |

Display as: `Match: 8.2/10 ★★★★☆`

## Listing Summary Format

For each job found, present:

```
## {Job Title} — {Company}
📍 {Location} | 💼 {Contract} | 💰 {Salary if available}
Match: {score}/10

**Why it fits**: {2-sentence reason based on user profile}
**Watch out for**: {1 potential concern}
**Apply by**: {deadline if found}
🔗 {URL}
```

## Cover Letter Generation

When drafting a cover letter for a specific listing:

1. Extract: required skills, company values, role responsibilities from the listing
2. Map to: user's concrete experience and achievements
3. Structure:
   - **Hook** (1 paragraph): Why this company + role specifically
   - **Proof** (2 paragraphs): Concrete past experience matching 2–3 key requirements
   - **Differentiator** (1 paragraph): What makes the user unique (e.g. practitioner-developer identity)
   - **CTA** (1 sentence): Request for interview, confident and direct

Keep cover letters under 350 words. Tone: professional but human, not corporate-robotic.

## Context for Victor's profile

When searching for Victor:
- **Current role**: AED + solo SaaS founder (Appel Internat)
- **Technical stack**: Next.js, TypeScript, React, Prisma, PostgreSQL, Supabase, Tailwind, Vercel, Pusher, Twilio, Anthropic/Mistral APIs
- **Strengths**: Full-stack web dev, product ownership end-to-end, RGPD compliance, EdTech domain, French public sector knowledge
- **Location**: Seine-et-Marne (77), Île-de-France — open to remote or Paris commute
- **Status**: Micro-entrepreneur, SIRET registered, APE 6201Z
- **Languages**: French (native), Spanish (fluent), English (professional)
- **Interesting roles**: EdTech product/dev roles, SaaS startups, CTO/lead dev at early-stage, developer relations

## Output Options

After presenting listings, offer:
- `draft cover letter for role #N` — generates tailored letter
- `compare roles #N and #M` — side-by-side comparison
- `set up weekly alert for [criteria]` — generates a direct LinkedIn search URL the user can save as alert
- `research company X` — web search for culture, news, financials, Glassdoor
