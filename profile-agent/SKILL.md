---
name: linkedin-profile-agent
description: Audits, rewrites, and optimizes every section of a LinkedIn profile for maximum visibility, recruiter appeal, and professional authority. Use this skill when the user wants to improve their LinkedIn profile, rewrite their headline or About section, optimize their experience bullets, add skills, or audit their overall profile completeness. Trigger for phrases like "optimize my LinkedIn profile", "rewrite my LinkedIn headline", "improve my About section", "audit my profile", "what should my LinkedIn say", or "help me position myself on LinkedIn". Produces ready-to-paste copy for every section.
---

# LinkedIn Profile Agent

Specialist agent for auditing and rewriting LinkedIn profiles. Produces ready-to-paste optimized copy for every section, benchmarked against top profiles in the user's niche.

## Workflow

1. **Profile intake** — gather current profile content (or ask user to paste each section)
2. **Audit** — score each section and identify gaps
3. **Research** — web search for top profiles in the user's role/niche for benchmarking
4. **Rewrite** — produce optimized copy for each section, multiple variants where useful
5. **Checklist** — output a final action list of changes to apply manually

## Important Limitation

⚠️ LinkedIn's public API does not expose write access to profile sections for non-partner developers. All copy produced by this agent must be **applied manually** by the user in the LinkedIn interface. Remind the user of this at the start of the session.

Reading basic profile info (name, headline, email) is possible via:
```bash
curl -s -H "Authorization: Bearer $LINKEDIN_TOKEN" \
     -H "LinkedIn-Version: 202410" \
     https://api.linkedin.com/v2/userinfo | jq '{sub, name, given_name, family_name, email}'
```

---

## Profile Sections

### 1. Headline (220 chars max)

The headline is the most important SEO field on LinkedIn — it appears in search results, connection requests, and the feed.

**Formula**:
```
{Role} | {Value proposition} | {Credibility signal} | {Target keyword}
```

**Rules**:
- Never just use job title — it wastes the field
- Include 2–3 keywords recruiters / buyers search for
- Lead with what you DO, not what you ARE
- Avoid generic words: passionate, innovative, results-driven

**Good example**:
```
Fondateur Appel Internat | SaaS pour internats | AED & développeur Next.js | EdTech · Éducation Nationale
```

### 2. About / Summary (2,600 chars max)

Structure:
```
HOOK (2–3 lines): What's the one thing someone should know about you?
STORY (1 paragraph): Why you do what you do — specific and personal
PROOF (1 paragraph): What you've built/achieved — concrete numbers
OFFER (1 paragraph): What you offer now, who you help
CTA (1–2 lines): How to reach you, what to do next
```

**Rules**:
- Write in first person ("Je" / "I") — not third person
- Avoid walls of text — short paragraphs, whitespace
- No clichés: "passionné par", "forte expertise", "orienté résultats"
- Include 3–5 natural keywords woven into sentences
- End with a direct invitation: "N'hésitez pas à me contacter" is weak — "Envoyez-moi un message si..." is better

### 3. Experience Section

For each role:
```
{Company Name} | {Title}
{Start date – End date} | {Location}

{2–3 sentence summary of what the role was}

Key contributions:
• {Achievement with metric — "Deployed X to Y users, reducing Z by N%"}
• {Achievement with metric}
• {Achievement with metric}
```

**Rules**:
- Lead with impact, not duties
- Every bullet should have a number, scope, or result
- Use past tense for past roles, present for current
- Include relevant tech stack or tools used (for developer profiles)

**Weak → Strong examples**:
- ❌ "Responsible for evening roll calls"
- ✅ "Managed nightly attendance for 180+ boarding students across 3 dorms, reducing response time to incidents from 20 min to under 5 min"

- ❌ "Built a web application"
- ✅ "Sole developer and founder of Appel Internat — a SaaS deployed in production at IES Sourdun (77), serving CPEs and AEDs across a 180-student boarding school"

### 4. Skills Section

LinkedIn allows up to 50 skills. Top 3 appear prominently and can be endorsed.

**Strategy**:
- Pin your 3 most strategic skills (what you want to be known for)
- Mix: technical skills + domain skills + soft skills (1–2 max)
- Remove outdated or irrelevant skills
- Add skills that match the keywords your target audience searches for

**For Victor / Appel Internat profile**:
```
Top 3 (pinned):
1. Next.js / React — technical credibility
2. SaaS Development — product positioning
3. EdTech / Éducation Nationale — domain authority

Additional (add all that apply):
TypeScript, Prisma, PostgreSQL, Supabase, Tailwind CSS, Vercel,
API Design, RGPD / Data Privacy, Product Management,
Micro-entrepreneuriat, Full-Stack Development, Node.js,
Twilio, Push Notifications, PWA, Playwright, CI/CD
```

### 5. Featured Section

Curate 3–5 items maximum. Options:
- Link to product / website (appel-internat.com)
- Best-performing LinkedIn post
- A published article
- A PDF case study or one-pager
- GitHub repo (if relevant)

Always add a custom title and description to each featured item — the default is blank.

### 6. Education & Certifications

Keep concise. Add any relevant online certifications (Vercel, Supabase, Next.js, etc.). Even unofficial learning counts if it's specific.

### 7. Recommendations

Ask for recommendations from:
- Current/past colleagues or collaborators
- Early users or clients (CPE at Sourdun, etc.)
- Technical collaborators

Offer to draft recommendation request messages.

---

## Profile Audit Scorecard

Score the current profile across these dimensions:

| Section | Max | Criteria |
|---------|-----|----------|
| Headline | 20 | Keywords, value prop, no generic terms |
| Profile photo | 10 | Professional, face visible, good lighting |
| Banner image | 10 | Custom, on-brand, not default |
| About | 20 | Story, proof, CTA, keywords, readable |
| Experience | 20 | Achievement-led, metrics, complete dates |
| Skills | 10 | 10+ skills, top 3 pinned, relevant |
| Featured | 5 | At least 1 item, custom title |
| Recommendations | 5 | At least 1 received |
| **Total** | **100** | |

Present as: `Profile score: 67/100 — Here's how to get to 90+`

---

## Context for Victor's Profile

Current situation to reflect in rewrites:
- **Dual identity**: AED (practitioner) + solo SaaS founder (builder) — this is the differentiator
- **Product**: Appel Internat, live at IES Sourdun (77), appel-internat.com
- **Stack**: Next.js, TypeScript, Prisma, Supabase, Tailwind, Vercel, Pusher, Twilio, Anthropic API
- **Business**: Micro-entrepreneur, SIRET, APE 6201Z (Programmation informatique)
- **Market**: Targeting ~1,529 French internats, currently outreaching DRANE de Créteil
- **Location**: Seine-et-Marne (77), Île-de-France
- **Languages**: French (native), Spanish (fluent), English (professional)
- **Target audience for profile**: CPEs, proviseurs, DRANE staff, EdTech investors, technical recruiters

## Headline Variants for Victor

Produce these variants and let Victor choose:
1. French / institutional angle: `Fondateur Appel Internat · SaaS pour internats | AED & Dev Next.js | appel-internat.com`
2. French / founder angle: `Dev solo → SaaS EdTech en production | Appel Internat · digitalisation des internats | AED & micro-entrepreneur`
3. Bilingual / broad: `EdTech SaaS Founder | Built by an AED, for AEDs | Next.js · Supabase · Éducation Nationale`
