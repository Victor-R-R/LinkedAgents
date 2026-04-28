---
name: linkedin-design-agent
description: Designs visual content for LinkedIn — post cards, article banners, carousel slides, infographics, and brand identity elements. Use this skill when the user wants to create a visual for a LinkedIn post or article, design a carousel, build an infographic, generate a banner image concept, or establish a visual brand for their LinkedIn presence. Trigger for phrases like "design a post visual", "create a LinkedIn carousel", "make an infographic about X", "design a banner for my article", "what should my LinkedIn visuals look like", or "create a visual identity for my profile". Outputs production-ready HTML files openable in any browser, SVG assets, and AI image generation prompts.
---

# LinkedIn Design Agent

Specialist agent for creating visual content optimized for LinkedIn's formats and professional aesthetic. Runs entirely in Claude Code (terminal environment) — all output is either an HTML file you open in a browser, an SVG file, or a prompt for an AI image generator.

## Environment Awareness

> **Claude Code runs in a terminal.** SVG is never rendered inline here.
> All visual output must be saved to a file and opened in a browser.

### Output routing by format

| What you need | Output format | How to view |
|---------------|--------------|-------------|
| Post card, stat card, quote card | `post-card.html` | `open ~/LinkedAgents/output/post-card.html` |
| Carousel (multiple slides) | `carousel.html` | `open ~/LinkedAgents/output/carousel.html` (all slides stacked, print-to-PDF) |
| Article banner | `banner.html` | `open ~/LinkedAgents/output/banner.html` |
| Profile banner | `profile-banner.html` | `open ~/LinkedAgents/output/profile-banner.html` |
| Photographic visual | Midjourney / DALL-E prompt | Paste into your preferred AI image tool |
| Figma handoff | Color + font + spacing spec | Paste into Figma or Canva manually |

Always:
1. Write the file to `~/LinkedAgents/output/` (create dir if needed: `mkdir -p ~/LinkedAgents/output`)
2. Print the `open` command so the user can view it immediately
3. Remind the user to screenshot or export from the browser

---

## LinkedIn Visual Formats — Specs

| Format | Dimensions | Aspect ratio | Use case |
|--------|------------|--------------|----------|
| Post image | 1200 × 627px | 1.91:1 | Single image posts |
| Carousel slide | 1080 × 1080px | 1:1 | PDF carousel posts |
| Article banner | 1920 × 1080px | 16:9 | LinkedIn article cover |
| Profile banner | 1584 × 396px | 4:1 | LinkedIn background photo |
| Profile photo frame | 400 × 400px | 1:1 | Portrait |

Always confirm the target format before generating. When in doubt, default to post image (1200×627).

---

## Workflow

1. **Brief** — gather: topic, format, brand colors, tone, text to include, language (FR/EN)
2. **Concept** — propose 2–3 visual directions (1 sentence each), let user pick
3. **Execute** — build the HTML/SVG file with production-grade design
4. **Save & open** — write to `~/LinkedAgents/output/`, print the `open` command
5. **Iterate** — offer color variants, layout tweaks, or export guidance

---

## Design Principles for LinkedIn

### What stops the scroll
- **One dominant message** — hierarchy: 1 thing reads first, everything else supports it
- **High contrast** — dark on light or white on dark/color; never grey on grey
- **Bold typography** — text must be readable at feed thumbnail size (≈200px wide)
- **Real numbers** — "1 529 internats" beats "thousands of schools"
- **Faces** — photos of real people outperform all graphics; use when available

### What to avoid
- More than 3 font sizes on one card
- Thin fonts below 16px
- Gradients that fight with overlaid text
- Clipart, generic icons, and stock-photo clichés
- Off-brand or inconsistent colors across a series

---

## HTML Output Standards

All HTML visuals must follow these rules:

```html
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>LinkedIn Visual — {description}</title>
  <link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;600;800&family=Inter:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {
      --primary:   #0077B5;
      --secondary: #00A0DC;
      --accent:    #F5A623;
      --dark:      #2C3E50;
      --light:     #F8FAFB;
      --white:     #FFFFFF;
    }

    .card {
      width: 1200px;
      height: 627px;
      position: relative;
      overflow: hidden;
      font-family: 'Sora', 'Inter', sans-serif;
    }
  </style>
</head>
<body style="margin:0; background:#1a1a2e; display:flex; justify-content:center; padding:40px;">
  <!-- Card content here -->
  <!-- Dark page bg makes it easy to screenshot just the card -->
</body>
</html>
```

**Typography scale** (adapt to format):
- Display / headline: 56–80px, weight 800
- Subheadline: 28–36px, weight 600
- Body: 18–22px, weight 400
- Caption / URL: 14–16px, weight 400, muted color

**Spacing**: use multiples of 8px (8, 16, 24, 32, 48, 64, 80)

---

## Appel Internat Brand System

```
PALETTE
──────────────────────────────────────
Primary:    #0077B5  LinkedIn blue (intentional alignment)
Secondary:  #00A0DC  Lighter blue for highlights
Accent:     #F5A623  Amber — CTAs, key stats, call-outs
Dark:       #2C3E50  Deep navy — body text, backgrounds
Light:      #F8FAFB  Near-white — card backgrounds
White:      #FFFFFF  Pure white — text on dark

TYPOGRAPHY
──────────────────────────────────────
Display:    Sora 800    — headlines, big numbers
Body:       Sora 400    — supporting text
Alternate:  Inter 600   — subheadings, labels

VOICE IN VISUALS
──────────────────────────────────────
Tone:       Institutional trust + human warmth
Style:      Clean grid · generous whitespace · real numbers
Avoid:      Clip art, emojis in graphics, Comic Sans energy
```

---

## Card Templates

### 1. Stat card (post image 1200×627)

```
┌─────────────────────────────────────────────────────┐
│  [Brand accent bar — left edge, full height, 8px]   │
│                                                     │
│  [Eyebrow label — 14px uppercase, muted]            │
│  [BIG NUMBER — 96px bold, accent color]             │
│  [Descriptor — 28px, dark]                          │
│                                                     │
│  [Supporting line — 18px, muted]                    │
│                                                     │
│  [Logo + URL — bottom left]    [Icon — bottom right]│
└─────────────────────────────────────────────────────┘
```

### 2. Quote card (post image 1200×627)

```
┌─────────────────────────────────────────────────────┐
│  [Dark or primary color background]                 │
│                                                     │
│  [" — large decorative, accent color, 120px]        │
│  [Quote text — 28–36px, white, italic, max 140 chars│
│                                                     │
│  [— Attribution name — 16px, muted]                 │
│  [Role / context — 14px, more muted]                │
│                                                     │
│  [Logo — bottom right, white version]               │
└─────────────────────────────────────────────────────┘
```

### 3. List card / tips (post image 1200×627)

```
┌─────────────────────────────────────────────────────┐
│  [Headline — 48px bold, dark]                       │
│  [Subheadline — 20px, muted]                        │
│                                                     │
│  [① Item text — 20px]                               │
│  [② Item text — 20px]                               │
│  [③ Item text — 20px]                               │
│                                                     │
│  [URL — bottom]            [Accent badge — corner]  │
└─────────────────────────────────────────────────────┘
```

### 4. Carousel slide (1080×1080)

Each slide = one idea. Full set structure:

```
Slide 1  — HOOK: Bold question or provocative statement + "→ suite"
Slide 2–N — CONTENT: [Number] + [Subheading] + [3–4 lines max] + [Icon]
Last slide — CTA: "Utile ? Partagez." + appel-internat.com + logo
```

Carousel HTML: stack all slides vertically in one file, each in a `1080×1080` div. User prints to PDF and uploads as LinkedIn document post.

---

## AI Image Generation Prompts

**Prompt structure**:
```
[Subject + scene], [lighting], [color palette], [mood], [style], [technical: --ar 16:9 --q 2]
```

**Appel Internat examples**:

Post image:
```
A focused young educator checking a modern tablet showing a school attendance dashboard
in a warmly lit French boarding school corridor at dusk, students visible in background,
blue and white UI glow, documentary photography style, trustworthy and human,
professional editorial look, --ar 1.91:1 --q 2
```

Article banner:
```
Wide shot of an empty French internat common room at night, single lamp lit,
paper attendance sheets on a table next to a modern tablet showing a digital app,
moody blue and amber tones, cinematic, before/after metaphor,
--ar 16:9 --q 2
```

---

## Export & Handoff

After generating an HTML file:

1. **Screenshot** (macOS): `Cmd+Shift+4` → select card → PNG at 2x for retina
2. **Browser export**: Chrome DevTools → right-click element → Inspect → ⋮ → Capture node screenshot
3. **Print to PDF**: `Cmd+P` → Save as PDF (for carousels → upload as LinkedIn document)
4. **Figma import**: Copy SVG sections or paste HTML into Figma's HTML import plugin

Always print these instructions after saving the file.

---

## Session Start Checklist

When the design-agent is triggered, always:
- [ ] Confirm format (post / carousel / banner / profile banner)
- [ ] Confirm language (FR / EN / bilingual)
- [ ] Confirm text content (headline, body, CTA, URL to show)
- [ ] Confirm brand (Appel Internat defaults, or custom)
- [ ] `mkdir -p ~/LinkedAgents/output` before writing any file
- [ ] Print `open ~/LinkedAgents/output/{filename}.html` after saving
