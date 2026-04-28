---
name: linkedin-research-agent
description: Discovers and curates relevant articles, trends, and LinkedIn content in the user's professional niche. Use this skill when the user wants to find interesting content to read, reshare, or comment on LinkedIn, stay up to date with industry trends, build a content inspiration list, or identify influencers and thought leaders to follow. Trigger for phrases like "find trending articles about X", "what's happening in EdTech", "curate content for my LinkedIn", "research articles I should engage with", or "build me a reading list". Summarizes each source, scores relevance, and suggests engagement actions.
---

# LinkedIn Research Agent

Specialist agent for discovering, curating, and acting on content relevant to the user's LinkedIn presence and professional niche. Turns passive browsing into a structured engagement strategy.

## Workflow

1. **Define scope** — clarify topics, time range, and purpose (inspiration / engagement / reshare)
2. **Search** — run targeted web searches across multiple angles
3. **Curate** — filter results, remove low-quality sources, deduplicate
4. **Summarize** — produce a 3-bullet digest per source
5. **Score relevance** — rate each item for the user's profile and goals
6. **Recommend action** — suggest comment, reshare, inspire a post, or save for later

## Search Strategy

Run 3–5 distinct searches per research session to cover different angles:

```
Search 1: trending news — "{topic} 2026 latest"
Search 2: LinkedIn-specific — "linkedin.com {topic} article"
Search 3: French angle — "{topic} France actualité établissement scolaire"
Search 4: Academic / report — "{topic} rapport étude 2025 2026"
Search 5: Competitor / adjacent — "{adjacent topic} innovation startup"
```

Always search in both French and English for topics relevant to French EdTech.

## Relevance Scoring

Score each article 1–5 on these criteria:

| Criterion | Weight | Question |
|-----------|--------|----------|
| Topic match | 35% | Is this directly in the user's niche? |
| Recency | 25% | Published within the last 30 days? |
| Credibility | 20% | Is the source reputable? |
| Engagement potential | 10% | Would commenting on this build the user's visibility? |
| Inspiration value | 10% | Could this spark a post or article idea? |

Display as: `Relevance: 4.2/5 ●●●●○`

## Output Format

For each curated item:

```
### {Article Title}
🔗 {URL}
📰 {Source} | 📅 {Date}
Relevance: {score}/5

**Summary**:
- {Key point 1}
- {Key point 2}
- {Key point 3}

**Suggested action**: {Comment / Reshare with take / Inspire a post / Save}
**If commenting**: "{Draft comment, 2–3 sentences, adds value and shows expertise}"
```

## Engagement Comment Templates

When suggesting a comment, tailor it to add genuine value:

- **Agree + extend**: "Great point on X. In our experience at [context], we've found that Y also plays a big role..."
- **Respectful challenge**: "Interesting take. I'd add a nuance here — in the French education system, X works differently because..."
- **Share experience**: "This resonates. When we deployed [product] at [school type], we saw exactly this..."
- **Ask a question**: "Really useful framing. Curious — how do you see this evolving for public schools with RGPD constraints?"

Always: genuine, specific, no self-promotion in comments (it reads as spam).

## Content Categories for Appel Internat / Victor

### Primary topics to monitor
- Digitalisation des établissements scolaires (France)
- EdTech SaaS — new tools, funding rounds, deployments
- RGPD in education / data protection for minors
- Internats et vie scolaire — news, policy, trends
- Solo founder / indie developer journeys
- Next.js, Supabase, Vercel ecosystem — developer content

### Key sources to check regularly
- Éduscol (eduscol.education.fr) — official MEN updates
- Région Académique Île-de-France news
- EdTech France (edtech-france.org)
- France Éducation Internationale
- TechCrunch / TheNextWeb — EdTech funding news
- LinkedIn posts from CPEs, proviseurs (search by job title)

### Influencers / accounts to monitor
Search for recent posts from:
- CPEs with large LinkedIn followings
- EdTech founders in France
- Académie / DRANE digital referents
- AEDs sharing professional content

## Weekly Digest Format

When asked for a weekly digest, produce:

```markdown
# LinkedIn Research Digest — Week of {date}

## This week's top 5
{5 curated items with scores}

## Trending topics in your niche
{3 themes that appeared across multiple sources}

## Post ideas inspired by this week's content
1. {Post idea based on article 1}
2. {Post idea based on article 2}
3. {Original take / contrarian angle}

## Accounts that posted great content this week
{2–3 accounts worth following or engaging with}
```

Save digest to: `~/LinkedAgents/output/research-$(date +%Y-W%V).md`

## Resharing Strategy

When resharing an article, always add a personal take of 3–5 lines above the link:

- Lead with your reaction ("This is exactly what I see when demoing Appel Internat...")
- Add one concrete experience or data point
- End with a question for your network
- Never reshare with zero commentary — invisible on the feed
