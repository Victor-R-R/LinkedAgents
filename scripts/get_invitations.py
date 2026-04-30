#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["patchright"]
# ///
"""
Fetch pending LinkedIn connection requests from the invitation manager.

Uses the LinkedIn MCP server's stored cookies (~/.linkedin-mcp/cookies.json)
to authenticate, then scrapes /mynetwork/invitation-manager/ with Patchright.

Usage:
    uvx run scripts/get_invitations.py [--max-results N] [--output FILE]
    # or if linkedin-scraper-mcp is installed:
    uvx --from linkedin-scraper-mcp python3 scripts/get_invitations.py

Output: JSON array to stdout (or file), one object per pending invitation:
    {"username": "...", "name": "...", "headline": "...", "profile_path": "..."}
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import tempfile
from pathlib import Path

COOKIE_FILE = Path.home() / ".linkedin-mcp" / "cookies.json"
INVITATION_MANAGER_URL = "https://www.linkedin.com/mynetwork/invitation-manager/"

# Cookies sufficient to authenticate (same subset the MCP server uses)
AUTH_COOKIE_NAMES = {"li_at", "JSESSIONID", "bcookie", "bscookie", "lidc"}

# Chromium binary candidates (descending preference)
_CHROMIUM_CANDIDATES = [
    Path.home() / "Library/Caches/ms-playwright/chromium_headless_shell-1217/chrome-headless-shell-mac-arm64/chrome-headless-shell",
    Path.home() / "Library/Caches/ms-playwright/chromium_headless_shell-1208/chrome-headless-shell-mac-arm64/chrome-headless-shell",
    Path.home() / "Library/Caches/ms-playwright/chromium_headless_shell-1200/chrome-headless-shell-mac-arm64/chrome-headless-shell",
]


def _find_chromium() -> str | None:
    for p in _CHROMIUM_CANDIDATES:
        if p.exists():
            return str(p)
    return None


async def fetch_invitations(max_results: int = 100) -> list[dict[str, str]]:
    from patchright.async_api import async_playwright

    if not COOKIE_FILE.exists():
        raise FileNotFoundError(
            f"LinkedIn cookie file not found: {COOKIE_FILE}\n"
            "Run the LinkedIn MCP server with --login first."
        )

    raw_cookies: list[dict] = json.loads(COOKIE_FILE.read_text())
    auth_cookies = [
        c for c in raw_cookies
        if c.get("name") in AUTH_COOKIE_NAMES and "linkedin.com" in c.get("domain", "")
    ]

    if not any(c["name"] == "li_at" for c in auth_cookies):
        raise RuntimeError("li_at cookie missing — run --login to refresh the session.")

    chromium_path = _find_chromium()

    # Use a temporary profile to avoid conflicting with the running MCP server
    with tempfile.TemporaryDirectory(prefix="linkedin-invitations-") as tmp_dir:
        async with async_playwright() as pw:
            launch_kwargs: dict = {
                "headless": True,
                "locale": "en-US",
                "viewport": {"width": 1280, "height": 720},
            }
            if chromium_path:
                launch_kwargs["executable_path"] = chromium_path

            context = await pw.chromium.launch_persistent_context(
                tmp_dir,
                **launch_kwargs,
            )
            page = context.pages[0] if context.pages else await context.new_page()

            # Seed the session with stored auth cookies
            await context.add_cookies(auth_cookies)  # type: ignore[arg-type]

            # Navigate to the invitation manager
            await page.goto(INVITATION_MANAGER_URL, wait_until="domcontentloaded", timeout=30000)

            # Wait for invitation list or redirect to login
            try:
                await page.wait_for_selector("main", timeout=10000)
            except Exception:
                pass

            current_url = page.url
            if "login" in current_url or "authwall" in current_url:
                raise RuntimeError(
                    "LinkedIn redirected to login — cookies may be expired. "
                    "Run the MCP server with --login to refresh."
                )

            # Scroll to lazy-load all invitation cards
            for _ in range(20):
                prev_height = await page.evaluate("document.body.scrollHeight")
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(1.0)
                new_height = await page.evaluate("document.body.scrollHeight")
                if new_height == prev_height:
                    break

            invitations: list[dict[str, str]] = await page.evaluate(
                """(maxResults) => {
                    const extractUsername = (href) => {
                        if (!href) return null;
                        const idx = href.indexOf('/in/');
                        if (idx === -1) return null;
                        const rest = href.slice(idx + 4);
                        const end = rest.search(/[/?#]/);
                        const u = end === -1 ? rest : rest.slice(0, end);
                        return u || null;
                    };

                    // Invitation cards contain both "Accept" and "Ignore" text
                    const cards = Array.from(document.querySelectorAll('li')).filter(li => {
                        const text = li.innerText || '';
                        return text.includes('Accept') && text.includes('Ignore');
                    });

                    const results = [];
                    const seen = new Set();

                    for (const li of cards.slice(0, maxResults)) {
                        const profileLink = li.querySelector('a[href*="/in/"]');
                        if (!profileLink) continue;

                        const href = profileLink.href || profileLink.getAttribute('href') || '';
                        const username = extractUsername(href);
                        if (!username || seen.has(username)) continue;
                        seen.add(username);

                        const name = (profileLink.innerText || '').trim();

                        const headline = Array.from(li.querySelectorAll('span'))
                            .map(s => (s.innerText || '').trim())
                            .find(t =>
                                t && t !== name &&
                                !t.includes('Accept') && !t.includes('Ignore') &&
                                !t.includes('Connect') && t.length > 3 && t.length < 200
                            ) || '';

                        results.push({
                            username,
                            name,
                            headline,
                            profile_path: '/in/' + username + '/',
                        });
                    }

                    return results;
                }""",
                max_results,
            )

            await context.close()
            return invitations


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch pending LinkedIn connection requests")
    parser.add_argument("--max-results", type=int, default=100, metavar="N",
                        help="Maximum number of invitations to fetch (default: 100)")
    parser.add_argument("--output", type=str, default=None, metavar="FILE",
                        help="Write JSON output to FILE instead of stdout")
    args = parser.parse_args()

    try:
        invitations = asyncio.run(fetch_invitations(max_results=args.max_results))
    except (FileNotFoundError, RuntimeError) as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)

    result = json.dumps(invitations, ensure_ascii=False, indent=2)

    if args.output:
        Path(args.output).write_text(result, encoding="utf-8")
        print(f"Saved {len(invitations)} invitations to {args.output}", file=sys.stderr)
    else:
        print(result)


if __name__ == "__main__":
    main()
