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
#: `ADR-0016` — kod izohlarida ham, hujjatlarda ham uchraydi.
ADR_REF = re.compile(r"\bADR-(\d{4})\b")
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
        # `i18n-review/` — ikki tilli jadval: bir qatorda o'zbekcha (lotin)
        # manba va qozoqcha/qirg'izcha (kirill) qiymat turadi. Aralashuv
        # bu yerda XATO EMAS, balki varaqning ma'nosi. Yozuv aralashuvi
        # tekshiruvi nasr uchun yozilgan, jadval uchun emas.
        and "i18n-review" not in p.parts
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


def check_adr_refs() -> list[str]:
    """`ADR-NNNN` havolasi MAVJUD ADR fayliga ishora qilsin.

    ⚠️ Nega kerak: kod izohida `(ADR-0016)` yozilgan edi, u esa ro'yxatdan
    o'tish haqida — huquqiy matn tillari haqida emas. Havola mavjud faylga
    ishora qilardi, shuning uchun na til, na tip, na oddiy havola
    tekshiruvi uni ushlay olmasdi (o'lchandi: 441 havola, 0 buzuq — ya'ni
    qoida kerak edi, mavjudlari yetmadi).

    Bu tekshiruv faqat havolaning MAVJUDLIGINI tasdiqlaydi; raqam mazmunan
    to'g'ri ekanini odam o'qib hal qiladi. Eski raqam butunlay o'chirilsa
    (fayl olib tashlansa) yoki yangi raqam xato yozilsa — bu yerda
    ushlanadi.
    """
    adr_dir = ROOT / "docs/07-adr"
    if not adr_dir.exists():
        return ["docs/07-adr topilmadi"]
    # Fayl nomi `0015-account-email.md` — raqam BOSHIDA, `ADR-` prefiksi
    # yo'q. Prefiksni qidirish barcha 19 faylni "yo'q" deb ko'rsatgan edi.
    have = {
        m.group(1)
        for p in adr_dir.glob("*.md")
        if (m := re.match(r"^(\d{4})-", p.stem))
    }
    out: list[str] = []
    for path in [*markdown_files(), *_source_files()]:
        text = path.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), 1):
            for m in ADR_REF.finditer(line):
                if m.group(1) not in have:
                    out.append(
                        f"{path.relative_to(ROOT)}:{lineno}: ADR-{m.group(1)} — "
                        f"bunday ADR fayli yo'q"
                    )
    return out


def _source_files() -> list[Path]:
    """Kod izohlarida ham ADR havolasi uchraydi.

    ⚠️ `tools/` ataylab CHIQARILMAYDI: salbiy testlar buzuq holatni matn
    sifatida yozadi (`ADR-9999`, `empty2:`, …). Ular manba kodida turgani
    uchun qoidaga tushib qoladi va tekshiruv O'Z testini tutib, doim
    qizil bo'ladi. Testlar `Mutation` bilan vaqtinchalik fayl yaratib
    tekshiriladi — demak ularni skanerlash shart emas.
    """
    out: list[Path] = []
    for suffix in (".ts", ".tsx", ".py"):
        for path in ROOT.rglob(f"*{suffix}"):
            if any(
                part in {".git", "node_modules", ".next", ".venv", ".tmp", "__pycache__"}
                for part in path.parts
            ):
                continue
            if path.relative_to(ROOT).parts[0] == "tools":
                continue
            out.append(path)
    return sorted(out)


def main() -> int:
    problems: list[str] = []
    files = markdown_files()
    for path in files:
        text = path.read_text(encoding="utf-8")
        problems += check_links(path, text)
        problems += check_tables(path, text)
        problems += check_script_mixing(path, text)
        problems += check_status(path, text)
    problems += check_adr_refs()

    print(f"Tekshirildi: {len(files)} ta markdown fayl + ADR havolalari")
    if problems:
        print(f"\n{len(problems)} ta muammo:\n")
        for p in problems:
            print(f"  {p}")
        return 1
    print("Muammo topilmadi ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
