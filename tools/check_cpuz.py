#!/usr/bin/env python3
"""The cp.uz articles keep the original's code and formulas (ADR-0062 § 2.3).

The Uzbek text is a machine translation. Its prose is reviewed by the agent;
its code and formulas must be the cp-algorithms original's, and a machine
can check that. For every article in `apps/api/content/cpuz/articles.json`
this compares the Uzbek file with the English original:

- **code**: every fenced block, in order. Comments are dropped first — the
  translation turns them into Uzbek, and that is allowed; a changed statement
  is not.
- **formulas**: every `$…$` and `$$…$$`, in order. `\\text{…}` words are
  dropped first for the same reason.

A known difference is listed in `apps/api/content/cpuz/mechanical-allow.json`:
`pending` until the agent review (ADR-0062 § 5.2) looks at it, then
`accepted` with its reason — or the text is fixed and the row goes. The
import publishes no article that is still `pending`. Anything unlisted
fails, and so does a row whose article no longer differs. Also fails: a file missing, a hash that does not match `articles.json`
for a file nobody edited, or raw HTML left in prose (the renderer would print
it as text).

Exit codes: 0 — equal or accepted; 1 — a difference; 2 — unreadable input.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# A piped Windows stdout is `cp1252` and dies on the first `✓`; see `_console.py`.
import _console

_console.force_utf8()

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT = ROOT / "apps/api/content/cpuz"
FENCE = re.compile(r"^\s*(?:>\s*)*(```+|~~~+)")


def blocks(text: str) -> tuple[list[str], str]:
    """Fenced code blocks, and the prose left without them."""
    code: list[str] = []
    prose: list[str] = []
    buf: list[str] | None = None
    close = ""
    for line in text.split("\n"):
        m = FENCE.match(line)
        if buf is None:
            if m:
                buf, close = [], m.group(1)
                continue
            prose.append(line)
        else:
            if (
                m
                and m.group(1).startswith(close[0])
                and line.strip().lstrip(">").strip().strip(close[0]) == ""
            ):
                code.append("\n".join(buf))
                buf = None
                continue
            buf.append(re.sub(r"^\s*(?:>\s?)+", "", line))
    if buf is not None:
        code.append("\n".join(buf))
    return code, "\n".join(prose)


def strip_comments(src: str) -> str:
    src = re.sub(r"/\*.*?\*/", " ", src, flags=re.DOTALL)
    out = []
    for line in src.split("\n"):
        line = re.sub(r"(?<![:\"'])//.*$", "", line)
        line = re.sub(
            r"^\s*#(?!include|define|pragma|if|else|endif|undef)\s.*$", "", line
        )
        line = re.sub(r"\s+#\s.*$", "", line)
        out.append(re.sub(r"\s+", "", line))
    return "\n".join(x for x in out if x)


def norm_formula(f: str) -> str:
    """Only what changes the mathematics is kept."""
    f = f.replace("−", "-").replace("–", "-").replace("≤", r"\le").replace("≥", r"\ge")
    f = re.sub(r"\\(?:text|textrm|textit|textbf|mathrm|mbox)\s*\{[^{}]*\}", "", f)
    f = re.sub(r"\\(?:,|;|:|!| |quad|qquad)|~", "", f)
    f = re.sub(r"\\(?:leq|leqslant)\b", r"\\le", f)
    f = re.sub(r"\\(?:geq|geqslant)\b", r"\\ge", f)
    f = re.sub(r"[\s{}]", "", f)
    return f.rstrip(".,;:")


def formulas(prose: str) -> tuple[list[str], list[str]]:
    """Display formulas (`$$…$$`) and inline ones (`$…$`)."""
    prose = re.sub(r"`[^`\n]+`", " ", prose)
    display: list[str] = []
    inline: list[str] = []
    for block, one in re.findall(
        r"\$\$(.+?)\$\$|(?<![\\$])\$(?!\s)([^$\n]+?)(?<![\s\\])\$",
        prose,
        flags=re.DOTALL,
    ):
        f = norm_formula(block or one)
        if f:
            (display if block else inline).append(f)
    return display, inline


def compare(uz: str, en: str) -> list[str]:
    problems = []
    uz_code, uz_prose = blocks(uz)
    en_code, en_prose = blocks(en)
    uc = [strip_comments(c) for c in uz_code]
    ec = [strip_comments(c) for c in en_code]
    if len(uc) != len(ec):
        problems.append(f"code blocks: {len(uc)} vs original {len(ec)}")
    else:
        bad = [i + 1 for i, (a, b) in enumerate(zip(uc, ec, strict=True)) if a != b]
        if bad:
            problems.append(f"code blocks differ: {bad}")
    (ud, ui), (ed, ei) = formulas(uz_prose), formulas(en_prose)
    # A display formula stands alone: the translation has no reason to touch it.
    if sorted(ud) != sorted(ed):
        missing = [f[:60] for f in sorted(set(ed) - set(ud))][:2]
        extra = [f[:60] for f in sorted(set(ud) - set(ed))][:2]
        problems.append(
            f"display formulas: {len(ud)} vs original {len(ed)}; missing {missing}; extra {extra}"
        )
    # An inline formula may be said once more or once less in another
    # language, but never be one the original does not have.
    invented = sorted(set(ui) - set(ei) - set(ed))
    if invented:
        problems.append(
            f"inline formulas not in the original: {[f[:60] for f in invented][:3]}"
        )
    tags = re.findall(
        r"</?[a-zA-Z][a-zA-Z0-9]*\b[^>\n]*>",
        re.sub(r"\$[^$\n]*\$", "", re.sub(r"`[^`\n]+`", "", uz_prose)),
    )
    if tags:
        problems.append(f"raw HTML in prose: {sorted(set(tags))[:3]}")
    return problems


def main(argv: list[str]) -> int:
    root = Path(argv[argv.index("--root") + 1]) if "--root" in argv else SNAPSHOT
    try:
        data = json.loads((root / "articles.json").read_text(encoding="utf-8"))
        allowed = json.loads(
            (root / "mechanical-allow.json").read_text(encoding="utf-8")
        )
    except (OSError, ValueError) as exc:
        print(f"✗ cp.uz snapshot o'qilmadi: {exc}")
        return 2
    allow = {row["id"]: row for row in allowed["articles"]}
    failures = []
    for article in data["articles"]:
        files = {}
        for lang in ("uz", "en"):
            path = root / lang / article["category"] / f"{article['slug']}.md"
            if not path.exists():
                failures.append(
                    f"{article['id']}: {lang} fayli yo'q ({path.relative_to(root).as_posix()})"
                )
                continue
            files[lang] = path.read_text(encoding="utf-8")
        if len(files) < 2:
            continue
        problems = compare(files["uz"], files["en"])
        listed = allow.get(article["id"])
        if listed and listed.get("status") not in ("pending", "accepted"):
            failures.append(
                f"{article['id']}: ruxsat holati noma'lum: {listed.get('status')!r}"
            )
        elif listed and listed["status"] == "accepted" and not listed.get("reason"):
            failures.append(
                f"{article['id']}: qabul qilingan farqning sababi yozilmagan"
            )
        elif problems and not listed:
            failures.append(f"{article['id']}: " + "; ".join(problems))
        elif not problems and listed:
            failures.append(
                f"{article['id']}: ruxsat ro'yxatida, lekin farq yo'q — yozuvni olib tashlang"
            )
    unknown = sorted(set(allow) - {a["id"] for a in data["articles"]})
    if unknown:
        failures.append(f"ruxsat ro'yxatida noma'lum maqolalar: {unknown[:3]}")
    if failures:
        print(
            f"✗ cp.uz: {len(failures)} ta maqolada kod yoki formula asldan farq qiladi"
        )
        for line in failures:
            print(f"  - {line}")
        return 1
    pending = sum(1 for row in allow.values() if row["status"] == "pending")
    accepted = len(allow) - pending
    same = len(data["articles"]) - len(allow)
    print(
        f"✓ cp.uz: {len(data['articles'])} ta maqola — {same} tasi asl bilan bir xil, "
        f"{accepted} tasining farqi sabab bilan qabul qilingan, {pending} tasi agent ko'rigini kutadi"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
