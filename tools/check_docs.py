#!/usr/bin/env python3
"""Hujjat yaxlitligi tekshiruvi — CI da har PR da ishlaydi.

Tekshiradi:
  1. Buzilgan nisbiy markdown havolalari
  2. Markdown jadval ustunlari mosligi
  3. Kirill/lotin yozuv aralashuvi (ruscha bloklar bundan mustasno)
  4. Locked hujjatlarda STATUS qatori borligi
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

CYRILLIC = re.compile(r"[Ѐ-ӿ]")
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
RU_MARKERS = ("| ru ", "Зарабатывай", "для тех", "Поднимайся")

ROOT = Path(__file__).resolve().parent.parent


def markdown_files() -> list[Path]:
    return sorted(
        p for p in ROOT.rglob("*.md")
        # `test-results` — Playwright yiqilganda yozadigan nusxa. U hujjat
        # emas, lekin ichida sahifa matni bo'lgani uchun yozuv aralashuvi
        # tekshiruvini yiqitardi: darvoza sinovdan KEYIN ishlamay qolardi.
        if not any(
            part in {".git", "node_modules", ".venv", "test-results", "playwright-report"}
            for part in p.parts
        )
    )


def check_links(path: Path, text: str) -> list[str]:
    out = []
    for match in LINK.finditer(text):
        target = match.group(1)
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        target = target.split("#")[0]
        if target and not (path.parent / target).exists():
            out.append(f"{path.relative_to(ROOT)}: buzilgan havola -> {target}")
    return out


def check_tables(path: Path, text: str) -> list[str]:
    out, rows, start, in_fence = [], [], 0, False
    for lineno, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if line.lstrip().startswith("|"):
            if not rows:
                start = lineno
            rows.append(line.count("|"))
        else:
            if len(rows) >= 2 and len(set(rows)) > 1:
                out.append(f"{path.relative_to(ROOT)}:{start}: jadval ustunlari mos emas {sorted(set(rows))}")
            rows = []
    if len(rows) >= 2 and len(set(rows)) > 1:
        out.append(f"{path.relative_to(ROOT)}:{start}: jadval ustunlari mos emas {sorted(set(rows))}")
    return out


def check_script_mixing(path: Path, text: str) -> list[str]:
    out = []
    for lineno, line in enumerate(text.splitlines(), 1):
        if CYRILLIC.search(line) and not any(m in line for m in RU_MARKERS):
            out.append(f"{path.relative_to(ROOT)}:{lineno}: kirill/lotin aralashuvi")
    return out


def check_status(path: Path, text: str) -> list[str]:
    if path.parent.name[:2].isdigit() and path.name == "README.md":
        if "**STATUS:**" not in text:
            return [f"{path.relative_to(ROOT)}: STATUS qatori yo'q"]
    return []


def main() -> int:
    problems: list[str] = []
    files = markdown_files()
    for path in files:
        text = path.read_text(encoding="utf-8")
        problems += check_links(path, text)
        problems += check_tables(path, text)
        problems += check_script_mixing(path, text)
        problems += check_status(path, text)

    print(f"Tekshirildi: {len(files)} ta markdown fayl")
    if problems:
        print(f"\n{len(problems)} ta muammo:\n")
        for p in problems:
            print(f"  {p}")
        return 1
    print("Muammo topilmadi ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
