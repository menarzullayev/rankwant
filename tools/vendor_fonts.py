#!/usr/bin/env python3
"""Vendor the Google Fonts used by `apps/web` into the repository.

Why this exists
---------------
`apps/web/src/app/layout.tsx` used to pull seven families through
`next/font/google`. That makes every `next build` depend on a live HTTPS
call to `fonts.googleapis.com` / `fonts.gstatic.com`, and Google's answer
is not stable: roughly one response in sixty comes back with the font
`src` URL in an extensionless form (`https://fonts.gstatic.com/l/font?kit=...`).
Turbopack cannot parse that shape and fails the whole build with
`next/font/google queries have exactly one entry` — see vercel/next.js#99114.

Next's built-in `retry()` only covers transport errors and non-200
statuses. The bad response is a `200`, so it is never retried. The result
was a build that failed at random on CI and passed on rebuild.

`NEXT_FONT_GOOGLE_MOCKED_RESPONSES` is not a way out: it is wired only
into the webpack font loader, and setting it under Turbopack (the only
bundler left in Next 16) makes the resolver fail differently — measured
2026-09-24, `Module not found:
'@vercel/turbopack-next/internal/font/google/cssmodule.module.css'` for
every family.

So the fonts are fetched ONCE, here, and committed. The build then reads
them from disk: deterministic, offline, and no request to Google at
either build or run time.

Usage
-----
    python3 tools/vendor_fonts.py            # refresh the vendored files
    python3 tools/vendor_fonts.py --check    # verify the tree is complete

The `--check` mode is what the check suite runs: it does not touch the
network, it only asserts that every file the CSS refers to is present.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

import _console

_console.force_utf8()

ROOT = Path(__file__).resolve().parent.parent
FONT_ROOT = ROOT / "apps" / "web" / "src" / "fonts"
MANIFEST = FONT_ROOT / "manifest.json"

# The exact UA `next/font` sends. Google varies the CSS and the file
# format by User-Agent; anything else can hand back `.ttf` instead of
# `.woff2`, which would silently change what we ship.
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/104.0.0.0 Safari/537.36"
)

# One entry per `next/font/google` call that used to live in `layout.tsx`.
# `directory` is the folder under `src/fonts/`; `slug` is the CSS family
# name Google uses in the `@font-face` rule.
FAMILIES: list[dict] = [
    {"slug": "IBM Plex Mono", "directory": "ibm-plex-mono", "weights": ["400", "500", "600"]},
    {
        "slug": "IBM Plex Serif",
        "directory": "ibm-plex-serif",
        "weights": ["400", "600"],
        "styles": ["normal", "italic"],
    },
    {"slug": "Inter", "directory": "inter", "weights": ["400", "500", "600"]},
    {"slug": "Plus Jakarta Sans", "directory": "plus-jakarta-sans", "weights": ["400", "500", "600"]},
    {"slug": "Roboto", "directory": "roboto", "weights": ["400", "500", "700"]},
    {"slug": "DM Sans", "directory": "dm-sans", "weights": ["400", "500", "600"]},
    {"slug": "Lexend", "directory": "lexend", "weights": ["400", "500", "600"]},
]

DISPLAY = "swap"


def sort_variant_values(a: str, b: str) -> int:
    """Port of `sortFontsVariantValues` from next/font.

    Google requires the axes sorted, ital before wght, and the order of
    the pairs decides the URL. Getting this wrong means the cache key in
    `manifest.json` does not match the URL `next/font/local` is asked
    for, and the refresh would silently write a different set of files.
    """
    if "," in a and "," in b:
        a_prefix, a_suffix = a.split(",", 1)
        b_prefix, b_suffix = b.split(",", 1)
        if a_prefix == b_prefix:
            return int(a_suffix) - int(b_suffix)
        return int(a_prefix) - int(b_prefix)
    return int(a) - int(b)


def stylesheet_url(family: str, weights: list[str], styles: list[str] | None, display: str) -> str:
    """Rebuild the `css2` URL exactly as `getGoogleFontsUrl` would."""
    variants: list[list[tuple[str, str]]] = []
    for weight in weights:
        if not styles:
            variants.append([("wght", weight)])
        else:
            for style in styles:
                variants.append([("ital", "0" if style == "normal" else "1"), ("wght", weight)])

    url = f"https://fonts.googleapis.com/css2?family={family.replace(' ', '+')}"
    if variants:
        axes = ",".join(key for key, _ in variants[0])
        values = sorted(
            (",".join(value for _, value in variant) for variant in variants),
            key=_variant_sort_key,
        )
        url = f"{url}:{axes}@{';'.join(values)}"
    return f"{url}&display={display}"


def _variant_sort_key(value: str) -> tuple[int, int]:
    """Comparable key mirroring `sort_variant_values` without cmp_to_key."""
    if "," in value:
        prefix, suffix = value.split(",", 1)
        return (int(prefix), int(suffix))
    return (int(value), -1)


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310
        if response.status != 200:
            raise SystemExit(f"GET {url} -> {response.status}")
        return response.read()


def fetch_family(entry: dict) -> dict:
    """Download the CSS and every font file for one family."""
    url = stylesheet_url(entry["slug"], entry["weights"], entry.get("styles"), DISPLAY)
    css = fetch(url).decode("utf8")

    directory = FONT_ROOT / entry["directory"]
    directory.mkdir(parents=True, exist_ok=True)

    # ⚠️ One `@font-face` per (weight, style, subset), but NOT one file per
    # face. Google's `css2` endpoint serves *variable* fonts for most
    # families: every weight points at the SAME file per subset, and the
    # weight is applied by the renderer. Measured 2026-09-24 on the seven
    # families in `FAMILIES`: IBM Plex Mono/Serif are static (1 file per
    # face), while Inter, Plus Jakarta Sans, Roboto, DM Sans and Lexend
    # are variable (1 file per subset, reused across weights).
    #
    # So the file list is de-duplicated by URL, but the face list is kept
    # whole. `fonts.ts` needs the faces (to emit the right `weight`), and
    # `check_fonts.py` compares the two.
    faces: list[dict] = []
    seen: dict[str, str] = {}
    for subset, block in _face_blocks(css):
        source = re.search(r"url\((https://fonts\.gstatic\.com/[^)]+)\)", block).group(1)
        if source not in seen:
            name = f"{entry['directory']}-{len(seen)}.{_extension_for(source)}"
            (directory / name).write_bytes(fetch(source))
            seen[source] = name
        faces.append(
            {
                "subset": subset,
                "file": seen[source],
                "weight": _declared(block, "font-weight", "400"),
                "style": _declared(block, "font-style", "normal"),
                "range": _declared(block, "unicode-range", ""),
            }
        )

    # Point the CSS at the files we just wrote, relative to the CSS file,
    # so the stylesheet we keep is the one `next/font/local` would build.
    local_css = css
    for source, name in seen.items():
        local_css = local_css.replace(f"url({source})", f"url(./{name})")
    (directory / "fonts.css").write_text(local_css, encoding="utf8")

    return {
        "slug": entry["slug"],
        "directory": entry["directory"],
        "url": url,
        "weights": entry["weights"],
        "styles": entry.get("styles", ["normal"]),
        "variable": len(seen) < len(faces),
        "faces": faces,
    }


def _extension_for(url: str) -> str:
    match = re.search(r"\.(woff2|woff|ttf|otf|eot)$", url)
    if match:
        return match.group(1)
    # The extensionless `/l/font?kit=...` shape. Google serves woff2 to
    # the Chrome UA set above; the CSS `format()` hint says so too.
    return "woff2"


def _declared(block: str, prop: str, default: str) -> str:
    """Read one CSS declaration out of an `@font-face` block."""
    match = re.search(rf"{prop}:\s*([^;]+);", block)
    return match.group(1).strip() if match else default


def _face_blocks(css: str) -> list[tuple[str, str]]:
    """Return `(subset, block)` for every `@font-face` in the stylesheet.

    Google writes the subset as a leading `/* latin */` comment, which is
    the only place the subset name appears.
    """
    return [
        (subset, block)
        for subset, block in re.findall(r"/\* ([a-z-]+) \*/\s*(@font-face\s*\{[^}]*\})", css)
    ]


def write_manifest(families: list[dict]) -> None:
    MANIFEST.write_text(
        json.dumps({"generated_by": "tools/vendor_fonts.py", "display": DISPLAY, "families": families}, indent=2)
        + "\n",
        encoding="utf8",
    )


def check() -> int:
    """Assert the vendored tree is complete. No network access."""
    if not MANIFEST.is_file():
        print(f"✕ {MANIFEST.relative_to(ROOT)} topilmadi — `python3 tools/vendor_fonts.py` ishga tushiring")
        return 1

    manifest = json.loads(MANIFEST.read_text(encoding="utf8"))
    expected = {entry["directory"] for entry in FAMILIES}
    found = {entry["directory"] for entry in manifest["families"]}
    if missing := expected - found:
        print(f"✕ manifest'da yetishmayotgan oila: {', '.join(sorted(missing))}")
        return 1

    problems: list[str] = []
    total = 0
    for entry in manifest["families"]:
        directory = FONT_ROOT / entry["directory"]
        if not (directory / "fonts.css").is_file():
            problems.append(f"{entry['directory']}/fonts.css")
        for face in entry["faces"]:
            path = directory / face["file"]
            total += 1
            if not path.is_file():
                problems.append(f"{entry['directory']}/{face['file']}")
            elif path.stat().st_size == 0:
                problems.append(f"{entry['directory']}/{face['file']} (bo'sh)")

    if problems:
        print(f"✕ {len(problems)} ta shrift fayli yetishmayapti:")
        for item in problems[:20]:
            print(f"    {item}")
        if len(problems) > 20:
            print(f"    ... yana {len(problems) - 20} ta")
        return 1

    unique = len(
        {
            face["file"]
            for entry in manifest["families"]
            for face in entry["faces"]
        }
    )
    print(f"✓ Shriftlar joyida: {len(manifest['families'])} oila, {unique} fayl, {total} yozuv")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="faqat tekshirish (tarmoqqa chiqmaydi)")
    args = parser.parse_args(argv)

    if args.check:
        return check()

    families = []
    for entry in FAMILIES:
        result = fetch_family(entry)
        families.append(result)
        unique = len({face["file"] for face in result["faces"]})
        kind = "variable" if result["variable"] else "statik"
        print(f"  {result['slug']:20s} {kind:8s} yozuv={len(result['faces']):3d} fayl={unique:3d}")

    write_manifest(families)
    total = sum(len(entry["faces"]) for entry in families)
    unique = len({face["file"] for entry in families for face in entry["faces"]})
    print(f"✓ {len(families)} oila, {unique} fayl, {total} yozuv → {FONT_ROOT.relative_to(ROOT)}")
    return check()


if __name__ == "__main__":
    sys.exit(main())
