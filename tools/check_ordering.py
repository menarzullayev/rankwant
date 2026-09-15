"""DRF `ordering` da tiebreaker borligini tekshiradi.

⚠️ Nega kerak: `ordering = ["-created_at"]` YAKKA o'zi yetarli emas.
Ikkita yozuv bir mikrosekundda yaratilsa (testda ketma-ket `create()`,
`auto_now_add` esa soat aniqligida yozadi) tartib SQL ixtiyoriga qoladi —
ya'ni bir so'rovda `[A, B]`, boshqasida `[B, A]`. Bu ikki oqibatga olib
keladi:

  1. **Sahifalash beqaror** — bir odam ikki sahifada chiqadi yoki umuman
     ko'rinmaydi.
  2. **Test tasodifiy yiqiladi** — o'lchandi: `test_qidiruv_va_tartib`
     5 ishga tushirishning 1 tasida yiqilardi.

`pk` (yoki UUID maydon) — yakuniy, deterministik tiebreaker. U asosiy
kalitdan keyin turishi kerak va yo'nalishi mos bo'lishi shart emas: `pk`
o'zi yagona, ya'ni teng holat qolmaydi.

Qoida faqat O'QISH yo'lidagi (`views.py`, `staff_views.py`) `ordering`
e'lonlarini tekshiradi. Model `Meta.ordering` ham xuddi shunday muammoga
ega, lekin u `annotate()` chaqirilganda baribir tashlab yuboriladi (memory
§7), ya'ni viewset darajasidagi e'lon — haqiqiy manba.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Chiqish quvurga yo'naltirilganda Windows uni `cp1252` deb yozadi va
# birinchi `✓` belgisida qulaydi — sabab va o'lchov `tools/_console.py` da.
import _console

_console.force_utf8()

ROOT = Path(__file__).resolve().parent.parent

#: `ordering = [...]` — `ordering_fields` EMAS.
ORDERING_RE = re.compile(r"^\s*ordering\s*(?::\s*[^=]+)?=\s*\[(?P<body>[^\]]*)\]")

#: Tiebreaker deb qabul qilinadigan maydonlar. `pk` — asosiy kalit;
#: `slug`/`id` ham yagona bo'lsa bo'ladi, lekin ular `unique=True`
#: ekanini bu skript bilmaydi, ya'ni faqat `pk` ishonchli.
TIEBREAKERS = {"pk", "-pk", "id", "-id"}


def _view_files() -> list[Path]:
    """Faqat API qatlami — model emas (sababi modul docstring'ida)."""
    out: list[Path] = []
    for path in ROOT.rglob("*.py"):
        if any(
            part in {".git", "node_modules", ".next", ".venv", ".tmp", "__pycache__"}
            for part in path.parts
        ):
            continue
        rel = path.relative_to(ROOT)
        # `tools/` — bu skript va salbiy testlar; ular buzuq namuna yozadi.
        if rel.parts[0] in {"tools", ".workbuddy-ai"}:
            continue
        if rel.name not in {"views.py", "staff_views.py"}:
            continue
        out.append(path)
    return sorted(out)


def check_ordering_tiebreakers() -> list[str]:
    out: list[str] = []
    for path in _view_files():
        text = path.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), 1):
            m = ORDERING_RE.match(line)
            if not m:
                continue
            body = m.group("body")
            fields = [f.strip().strip("\"'") for f in body.split(",") if f.strip()]
            if not fields:
                # `ordering = []` — DRF uchun "tartib yo'q" degani, ya'ni
                # tiebreaker talab qilinmaydi.
                continue
            if TIEBREAKERS & set(fields):
                continue
            out.append(
                f"{path.relative_to(ROOT)}:{lineno}: `ordering = {fields}` — "
                f"tiebreaker yo'q (`pk` qo'shilsin)"
            )
    return out


def main() -> int:
    problems = check_ordering_tiebreakers()
    files = _view_files()
    print(f"Tekshirildi: {len(files)} ta view fayli")
    if problems:
        print(f"\n{len(problems)} ta muammo:\n")
        for p in problems:
            print(f"  {p}")
        return 1
    print("Muammo topilmadi ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
