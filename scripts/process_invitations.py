#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["patchright"]
# ///
"""
Bulk-accept pending LinkedIn connection requests in a single browser session.

Navigates to /mynetwork/invitation-manager/, fetches all pending invitations,
optionally filters by keyword, then clicks "Accept" on each card directly —
no per-profile navigation, one session for everything.

Usage:
    uvx --from linkedin-scraper-mcp python3 scripts/process_invitations.py
    uvx --from linkedin-scraper-mcp python3 scripts/process_invitations.py --limit 20 --filter "EdTech,DRH,fondateur"
    uvx --from linkedin-scraper-mcp python3 scripts/process_invitations.py --dry-run

Options:
    --limit N          Max invitations to accept per run (default: 20, hard cap: 20)
    --filter KEYWORDS  Comma-separated keywords — only accept if headline/name matches
    --dry-run          List invitations found without accepting
    --delay SECONDS    Delay between accepts in seconds (default: 2.0)
    --output FILE      Save results JSON to FILE
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import tempfile
from pathlib import Path

COOKIE_FILE = Path.home() / ".linkedin-mcp" / "cookies.json"
INVITATION_MANAGER_URL = "https://www.linkedin.com/mynetwork/invitation-manager/received/"
AUTH_COOKIE_NAMES = {"li_at", "JSESSIONID", "bcookie", "bscookie", "lidc"}
DAILY_HARD_CAP = 20  # LinkedIn restriction — do not raise

_CHROMIUM_CANDIDATES = [
    Path.home() / "Library/Caches/ms-playwright/chromium_headless_shell-1217/chrome-headless-shell-mac-arm64/chrome-headless-shell",
    Path.home() / "Library/Caches/ms-playwright/chromium_headless_shell-1208/chrome-headless-shell-mac-arm64/chrome-headless-shell",
    Path.home() / "Library/Caches/ms-playwright/chromium_headless_shell-1200/chrome-headless-shell-mac-arm64/chrome-headless-shell",
]


def _find_chromium() -> str | None:
    return next((str(p) for p in _CHROMIUM_CANDIDATES if p.exists()), None)


def _matches_filter(invitation: dict, keywords: list[str]) -> bool:
    if not keywords:
        return True
    text = f"{invitation.get('name', '')} {invitation.get('headline', '')}".lower()
    return any(kw.lower() in text for kw in keywords)


async def process_invitations(
    limit: int = 20,
    filter_keywords: list[str] | None = None,
    dry_run: bool = False,
    delay: float = 2.0,
) -> dict:
    from patchright.async_api import async_playwright

    limit = min(limit, DAILY_HARD_CAP)
    keywords = filter_keywords or []

    if not COOKIE_FILE.exists():
        raise FileNotFoundError(
            f"LinkedIn cookie file not found: {COOKIE_FILE}\n"
            "Run: uvx linkedin-scraper-mcp --login"
        )

    raw_cookies = json.loads(COOKIE_FILE.read_text())
    auth_cookies = [
        c for c in raw_cookies
        if c.get("name") in AUTH_COOKIE_NAMES and "linkedin.com" in c.get("domain", "")
    ]

    if not any(c["name"] == "li_at" for c in auth_cookies):
        raise RuntimeError("li_at cookie missing — run: uvx linkedin-scraper-mcp --login")

    chromium_path = _find_chromium()

    with tempfile.TemporaryDirectory(prefix="linkedin-process-inv-") as tmp_dir:
        async with async_playwright() as pw:
            launch_kwargs: dict = {
                "headless": True,
                "locale": "en-US",
                "viewport": {"width": 1280, "height": 900},
            }
            if chromium_path:
                launch_kwargs["executable_path"] = chromium_path

            context = await pw.chromium.launch_persistent_context(tmp_dir, **launch_kwargs)
            page = context.pages[0] if context.pages else await context.new_page()

            await context.add_cookies(auth_cookies)  # type: ignore[arg-type]

            # ── Navigate to invitation manager ──────────────────────
            print(f"→ Navigating to invitation manager...", file=sys.stderr)
            await page.goto(INVITATION_MANAGER_URL, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(2)

            current_url = page.url
            if "login" in current_url or "authwall" in current_url:
                raise RuntimeError("LinkedIn redirected to login — cookies may be expired.")

            # ── Scroll to load all invitation cards ─────────────────
            print("→ Loading all invitation cards...", file=sys.stderr)
            for _ in range(30):
                prev = await page.evaluate("document.body.scrollHeight")
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(1.0)
                new = await page.evaluate("document.body.scrollHeight")
                if new == prev:
                    break

            # ── Extract invitation list ──────────────────────────────
            invitations: list[dict] = await page.evaluate("""() => {
                const extractUsername = href => {
                    if (!href) return null;
                    const idx = href.indexOf('/in/');
                    if (idx === -1) return null;
                    const rest = href.slice(idx + 4);
                    const end = rest.search(/[/?#]/);
                    return (end === -1 ? rest : rest.slice(0, end)) || null;
                };

                const cards = Array.from(document.querySelectorAll('li')).filter(li => {
                    const t = li.innerText || '';
                    return t.includes('Accept') && t.includes('Ignore');
                });

                return cards.map((li, idx) => {
                    const link = li.querySelector('a[href*="/in/"]');
                    const href = link ? (link.href || link.getAttribute('href') || '') : '';
                    const username = extractUsername(href);
                    const name = (link?.innerText || '').trim();
                    const headline = Array.from(li.querySelectorAll('span'))
                        .map(s => (s.innerText || '').trim())
                        .find(t => t && t !== name && !['Accept','Ignore','Connect'].some(w => t.includes(w)) && t.length > 3 && t.length < 200) || '';
                    return { idx, username, name, headline };
                }).filter(i => i.username);
            }""")

            total_found = len(invitations)
            print(f"→ Found {total_found} pending invitation(s)", file=sys.stderr)

            # ── Apply keyword filter ─────────────────────────────────
            if keywords:
                invitations = [i for i in invitations if _matches_filter(i, keywords)]
                print(f"→ {len(invitations)} match filter: {', '.join(keywords)}", file=sys.stderr)

            # ── Cap to daily limit ───────────────────────────────────
            to_process = invitations[:limit]

            if dry_run:
                print(f"\n[DRY RUN] Would accept {len(to_process)} invitation(s):\n", file=sys.stderr)
                for inv in to_process:
                    print(f"  • {inv['name']} — {inv['headline']} (@{inv['username']})", file=sys.stderr)
                await context.close()
                return {
                    "mode": "dry_run",
                    "found": total_found,
                    "would_accept": len(to_process),
                    "invitations": to_process,
                }

            # ── Accept each invitation ───────────────────────────────
            accepted = []
            failed = []

            for inv in to_process:
                username = inv["username"]
                name = inv["name"]

                try:
                    # Re-query the Accept button for this specific card
                    # (DOM may shift after previous accepts)
                    clicked = await page.evaluate(
                        """(username) => {
                            const cards = Array.from(document.querySelectorAll('li')).filter(li => {
                                const t = li.innerText || '';
                                return t.includes('Accept') && t.includes('Ignore');
                            });
                            for (const li of cards) {
                                const link = li.querySelector('a[href*="/in/' + username + '/"]') ||
                                             li.querySelector('a[href*="/in/' + username + '"]');
                                if (!link) continue;
                                // Find Accept button within this card
                                const btns = Array.from(li.querySelectorAll('button, [role="button"]'));
                                const acceptBtn = btns.find(b => {
                                    const t = (b.innerText || b.textContent || '').trim();
                                    return t === 'Accept' || t.startsWith('Accept');
                                });
                                if (acceptBtn) {
                                    acceptBtn.click();
                                    return true;
                                }
                            }
                            return false;
                        }""",
                        username,
                    )

                    if clicked:
                        accepted.append(inv)
                        print(f"  ✅  Accepted: {name} (@{username})", file=sys.stderr)
                        await asyncio.sleep(delay)
                    else:
                        failed.append({**inv, "reason": "Accept button not found"})
                        print(f"  ⚠️  Could not find Accept button for {name}", file=sys.stderr)

                except Exception as e:
                    failed.append({**inv, "reason": str(e)})
                    print(f"  ❌  Error for {name}: {e}", file=sys.stderr)
                    await asyncio.sleep(1.0)

            await context.close()

            print(
                f"\n→ Done: {len(accepted)} accepted, {len(failed)} failed "
                f"(out of {total_found} total)",
                file=sys.stderr,
            )

            return {
                "mode": "live",
                "found": total_found,
                "accepted": len(accepted),
                "failed": len(failed),
                "accepted_list": accepted,
                "failed_list": failed,
                "skipped": total_found - len(to_process),
            }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bulk-accept LinkedIn connection requests in one browser session"
    )
    parser.add_argument("--limit", type=int, default=20, metavar="N",
                        help=f"Max invitations to accept (default: 20, hard cap: {DAILY_HARD_CAP})")
    parser.add_argument("--filter", type=str, default="", metavar="KEYWORDS",
                        help='Comma-separated keywords to filter by name/headline (e.g. "EdTech,DRH,fondateur")')
    parser.add_argument("--dry-run", action="store_true",
                        help="List invitations without accepting")
    parser.add_argument("--delay", type=float, default=2.0, metavar="SECONDS",
                        help="Delay between accepts in seconds (default: 2.0)")
    parser.add_argument("--output", type=str, default=None, metavar="FILE",
                        help="Save results JSON to FILE")
    args = parser.parse_args()

    keywords = [k.strip() for k in args.filter.split(",") if k.strip()] if args.filter else []

    try:
        result = asyncio.run(process_invitations(
            limit=args.limit,
            filter_keywords=keywords,
            dry_run=args.dry_run,
            delay=args.delay,
        ))
    except (FileNotFoundError, RuntimeError) as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)

    output = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Results saved to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
