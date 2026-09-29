#!/usr/bin/env python3
"""Every executable `<script>` the app renders must carry the CSP nonce.

Why this exists. `proxy.ts` mints a nonce per request and puts it in the
`Content-Security-Policy` header, and it also sets `x-nonce` so the render can
read it. Next writes that nonce into its *own* inline tags — but not into the
tags the application writes by hand. Measured on the live `/login` (2026-09-24,
Chrome console, the negative control):

    [error] Loading the script 'https://rankwant.uz/i18n/uz.js?v=…' violates
            the following Content Security Policy directive: "script-src
            'self' 'nonce-…' 'strict-dynamic'"
    [error] Executing inline script violates … (x3)
    [issue] Content Security Policy blocks inline execution of scripts (count: 3)

Four scripts were blocked: the three pre-hydration bootstrap tags (`theme`,
`style`, `appearance`) and the dictionary's fast path. `'strict-dynamic'` is
listed, which makes `'self'` irrelevant — a script tag without the nonce is
blocked even though it is same-origin.

The consequences were invisible to every gate: a white flash on every dark-mode
load (the theme class was never applied before hydration), and `LocaleProvider`
falling back to `loadDictionary()` on every page load, which is the race the
`<head>` script exists to win.

This gate measures the rendered page, not the source: it reads the CSP header,
extracts the nonce, and requires that nonce on every script tag the browser
would execute. `application/ld+json` is skipped — the browser does not execute
it, so `script-src` does not apply (confirmed in the same console capture: it
is not among the blocked resources).

Exit codes: 0 clean · 1 a script without the nonce · 2 nothing to measure
(no stack, no nonce in the header, no scripts at all).
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

# Windows writes the pipe as `cp1252` and dies on the first `✓`; the reason and
# the measurement live in `tools/_console.py`.
import _console

_console.force_utf8()

#: The running stack. `tools/ci_csp_gate.sh` and the E2E job share the default.
DEFAULT_BASE = "http://localhost:3400"

#: Routes worth measuring: guest pages that carry the nonce-bearing layout and
#: are never served from a CDN cache (a cached header would carry a stale nonce
#: and make the comparison meaningless).
ROUTES = ("/login", "/verify-email")

CSP_NONCE_RE = re.compile(r"'nonce-([^']+)'")
SCRIPT_TAG_RE = re.compile(r"<script\b[^>]*>", re.IGNORECASE)
NONCE_ATTR_RE = re.compile(r'nonce="([^"]+)"')
TYPE_ATTR_RE = re.compile(r'type="([^"]+)"')

#: Types the browser never executes, so `script-src` does not apply to them.
NON_EXECUTABLE = frozenset({"application/ld+json", "application/json", "text/template"})


def is_executable(tag: str) -> bool:
    """A script tag the browser will run — i.e. one CSP actually governs."""
    match = TYPE_ATTR_RE.search(tag)
    if match is None:
        return True
    return match.group(1).lower() not in NON_EXECUTABLE


def fetch(base: str, route: str) -> tuple[str, str]:
    """Return `(csp_header, html)` for one route."""
    request = urllib.request.Request(base.rstrip("/") + route, headers={"Accept": "text/html"})
    with urllib.request.urlopen(request, timeout=20) as response:
        csp = response.headers.get("content-security-policy", "")
        body = response.read().decode("utf-8", errors="replace")
    return csp, body


def check(csp: str, html: str, drop_nonce: int = 0) -> tuple[list[str], int, int]:
    """Return `(problems, executable_count, nonced_count)`.

    `drop_nonce` removes the attribute from the n-th executable tag. It exists
    for one reason: `check_negative.py` has to prove this gate is not vacuous,
    and stripping the attribute from the real page is the cheapest honest
    mutation — a rebuild would cost minutes and prove no more.
    """
    problems: list[str] = []

    match = CSP_NONCE_RE.search(csp)
    if not csp:
        return ["CSP sarlavhasi yo'q — bu sahifa darvozani o'lchamaydi"], 0, 0
    if match is None:
        return [f"CSP da nonce yo'q — tekshiruv bo'sh bo'lardi: {csp[:90]}"], 0, 0

    header_nonce = match.group(1)
    tags = SCRIPT_TAG_RE.findall(html)
    executable = [t for t in tags if is_executable(t)]
    if not executable:
        return ["sahifada bajariladigan `<script>` umuman yo'q — tekshiruv bo'sh"], 0, 0

    nonced = 0
    for index, tag in enumerate(executable, start=1):
        if drop_nonce and index == drop_nonce:
            tag = NONCE_ATTR_RE.sub("", tag)
        found = NONCE_ATTR_RE.search(tag)
        if found is None:
            problems.append(f"{index}-skript noncesiz: {tag[:88]}")
            continue
        if found.group(1) != header_nonce:
            problems.append(f"{index}-skript nonce'i sarlavhanikidan boshqa: {tag[:88]}")
            continue
        nonced += 1

    return problems, len(executable), nonced


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default=os.environ.get("E2E_BASE_URL", DEFAULT_BASE))
    parser.add_argument("--route", action="append", dest="routes")
    parser.add_argument(
        "--drop-nonce",
        type=int,
        default=0,
        metavar="N",
        help="strip the nonce from the n-th executable script (negative test only)",
    )
    args = parser.parse_args()
    routes = args.routes or list(ROUTES)

    total_problems: list[str] = []
    measured = 0
    for route in routes:
        try:
            csp, html = fetch(args.base, route)
        except (urllib.error.URLError, OSError) as exc:
            print(f"✗ {route}: stack javob bermadi ({exc})")
            return 2
        problems, executable, nonced = check(csp, html, args.drop_nonce)
        measured += 1
        if problems:
            for problem in problems:
                total_problems.append(f"{route}: {problem}")
        else:
            print(f"✓ {route}: {nonced}/{executable} bajariladigan skript nonce bilan")

    if total_problems:
        print(f"\n✗ CSP nonce qamrovi: {len(total_problems)} ta muammo")
        for problem in total_problems:
            print(f"  - {problem}")
        print(
            "\nTuzatish: `proxy.ts` qo'yadigan `x-nonce` ni render'da o'qing va uni"
            " qo'lda yozilgan HAR BIR `<script>` tegiga bering."
        )
        return 1

    print(f"\n✓ CSP nonce qamrovi to'liq — {measured} marshrut o'lchandi")
    return 0


if __name__ == "__main__":
    sys.exit(main())
