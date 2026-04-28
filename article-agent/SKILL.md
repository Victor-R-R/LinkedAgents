---
name: linkedin-article-agent
description: Writes complete, long-form LinkedIn articles (1,500–3,000 words) structured for professional audiences and optimized for LinkedIn's native publishing format. Use this skill when the user wants to write a LinkedIn article, newsletter, long-form post, thought leadership piece, or any content longer than a standard post. Trigger for phrases like "write an article about X", "help me publish a LinkedIn article", "write a long-form piece", "draft a newsletter", or "create thought leadership content". Handles research, structure, SEO, and formatting.
---

# LinkedIn Article Agent

Specialist agent for writing complete, publication-ready long-form articles for LinkedIn. Produces structured, engaging content that builds authority and drives profile visibility.

## Workflow

1. **Brief intake** — gather topic, target audience, angle, tone, desired length, and any source material
2. **Outline** — present a structured outline for user approval before writing
3. **Research** — web search for supporting data, stats, and current examples if needed
4. **Draft** — write the complete article with all sections
5. **Optimize** — add SEO title variants, meta description, and suggested cover image prompts
6. **Deliver** — output as clean Markdown ready to paste into LinkedIn

## Brief Intake Questions

Ask only what isn't already clear from context:
- **Topic**: What is the article about?
- **Angle**: What's the unique take or thesis? (e.g. "why paper roll calls are a liability", "what I learned building a SaaS as a non-developer")
- **Audience**: Who should read this? (CPEs, founders, EdTech professionals, general LinkedIn)
- **Tone**: See tone guide below
- **Length**: Short (800–1,200w), standard (1,500–2,000w), or long (2,500–3,000w)
- **Source material**: Any data, quotes, or personal stories to incorporate?

## Article Structure

### Standard structure (adapt as needed)
```
TITLE (compelling, specific, 8–12 words)
SUBTITLE (optional, adds context)

HOOK (150–250 words)
— Open with a personal story, surprising stat, or provocative question
— Make the reader feel the problem immediately

CONTEXT / PROBLEM (200–400 words)
— Define the problem or opportunity clearly
— Use concrete examples, not abstract claims

SOLUTION / INSIGHT (400–800 words)
— 3–5 key points, each with a concrete example
— Use subheadings (H2) for each point
— Include real numbers, named tools, or specific experiences

PERSONAL STORY / PROOF (200–400 words)
— Ground the article in lived experience
— This is what makes LinkedIn articles shareable

CONCLUSION + CTA (150–200 words)
— Summarize the core thesis in 1–2 sentences
— End with a question to drive comments
— Optional: link to product or resource
```

## Tone Guide

| Tone | Style | Best for |
|------|-------|----------|
| `expert` | Authoritative, data-driven, no fluff | Industry positioning, technical topics |
| `founder` | Vulnerable, personal, behind-the-scenes | Journey stories, lessons learned |
| `educator` | Clear, structured, step-by-step | How-to guides, frameworks, explainers |
| `provocateur` | Contrarian, challenges assumptions | Hot takes, industry critiques |
| `narrative` | Story-first, emotional, cinematic | Origin stories, transformation arcs |

## Writing Rules

- **No jargon without explanation** — if it needs a glossary, cut it
- **Short sentences** — avg 15–20 words. Vary rhythm deliberately
- **Active voice** — "I built X" not "X was built by me"
- **Concrete over abstract** — "37 students, 2 AEDs, 1 paper sheet" beats "operational challenges"
- **One idea per paragraph** — 2–4 sentences max per block
- **Subheadings every 300–400 words** — improves scannability dramatically
- **No bullet point overload** — max 1 list per 500 words, 5 items max per list
- **Quote-worthy sentences** — at least 2–3 lines strong enough to screenshot and share

## SEO & Discoverability

After drafting, provide:
- **3 title variants** ranked by click potential
- **Meta description** (155 chars): summarizes the article for search
- **Primary keyword** to place in title, first paragraph, and one subheading
- **3–5 related hashtags** for the post that accompanies the article
- **Cover image prompt** for DALL-E / Midjourney (describe the ideal banner image)

## LinkedIn Article Formatting

LinkedIn's editor supports:
- H1 (title only), H2, H3 subheadings
- Bold, italic, underline
- Bullet and numbered lists
- Block quotes
- Embedded links
- Images between sections

**Do not use**: markdown code blocks, tables (not supported natively), or complex nesting.

Output final article as clean text with `## Subheading` markers. Add a note at the top:
> *Paste into LinkedIn Article editor. Replace `##` with H2 heading style.*

Save draft to: `~/LinkedAgents/output/article-{slug}-$(date +%Y-%m-%d).md`

## Article Ideas for Appel Internat / Victor

Suggest these angles when the user needs inspiration:

| Title idea | Angle | Audience |
|------------|-------|----------|
| "I built a SaaS while working night shifts as an AED" | Founder journey, impossible odds | General LinkedIn, founders |
| "Why French internats are still using paper in 2026" | Industry critique, market opportunity | EdTech, proviseurs, DRANE |
| "What I learned deploying software in the Éducation Nationale" | Technical + institutional lessons | Developers, EdTech |
| "The AED who became a solo SaaS founder: a field guide" | How-to, inspiration | Career changers, AEDs |
| "RGPD in schools: what nobody tells you when you build EdTech" | Compliance, trust, legitimacy | EdTech founders, IT directors |
| "5 things CPEs tell me every time I demo Appel Internat" | Social proof, customer insight | CPEs, school leadership |
