"""Verdikt kodlari API bilan mos kelishini tekshiradi.

⚠️ Nega kerak: kodlar ro'yxati **ikki joyda** yashaydi va ular jimgina
ajralib ketadi.

  * `apps/api/judging/verdicts.py` — haqiqiy manba (Django `TextChoices`).
  * `apps/web/src/lib/theme/verdict.ts` — rang, ikonka va guruh.
  * `apps/web/src/icons/phosphor.tsx` — kod → ikonka xaritasi.
  * `apps/web/src/i18n/locales/*.ts` — `verdict.<KOD>` yorlig'i, 10 til.

Bu **bir marta sodir bo'ldi**: API'da 23 ta kod bor edi, web'da 10 ta.
`verdictOf()` noma'lum kodni `PD` ga tushirardi, ya'ni **14 ta kod
«Navbatda» bo'lib ko'rinardi** (`RE_SIGNAL`, `WRONG_TEST`, `CHECKER_ERROR`,
`PARTIAL`, `SECURITY_VIOLATION`, …). Hech qanday tekshiruv buni tutmasdi:
`tsc` o'tadi (kalit `string`), sahifa ochiladi, konsol toza.

Endi `Verdict` komponenti noma'lum kodni **xom holda** ko'rsatadi, ya'ni
xato ko'rinadi — lekin baribir kech bo'ladi. Shuning uchun bu skript
push'dan oldin ishlaydi.

Xato chiqsa nima qilinadi:
  1. `tools/gen-verdict-icons.mjs` ga yangi kodni qo'shing (ikonka bilan),
  2. `lib/theme/verdict.ts` ga kodni, guruhni va yorliqni qo'shing,
  3. `node tools/gen-verdict-icons.mjs` ni ishga tushiring,
  4. `verdict.<KOD>` yorlig'ini 10 tilga qo'shing.
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

API_FILE = ROOT / "apps/api/judging/verdicts.py"
WEB_FILE = ROOT / "apps/web/src/lib/theme/verdict.ts"
ICON_FILE = ROOT / "apps/web/src/icons/phosphor.tsx"
LOCALE_DIR = ROOT / "apps/web/src/i18n/locales"

#: `AC = "AC", "Accepted"` — Django `TextChoices` qatori.
CHOICE_RE = re.compile(r"^\s{4}(?P<name>[A-Z][A-Z0-9_]*)\s*=\s*\"(?P<value>[A-Z0-9_]+)\"", re.M)
#: `  | "AC"` — `VerdictKey` birlashmasi a'zosi.
UNION_RE = re.compile(r"^\s*\|\s*\"(?P<key>[A-Z][A-Z0-9_]*)\"", re.M)
#: `  AC: VerdictIconCheckCircle,` — ikonka xaritasi qatori.
ICONMAP_RE = re.compile(r"^\s*(?P<key>[A-Z][A-Z0-9_]*):\s*Ph", re.M)
#: `  "verdict.AC": "Accepted",` — i18n yorlig'i (`.hint`/`.style` emas).
LABEL_RE = re.compile(r'^\s{2}"verdict\.(?P<key>[A-Z][A-Z0-9_]*)"\s*:', re.M)

LOCALES = ["en", "uz", "ru", "tr", "es", "zh", "kk", "ky", "tg", "kaa"]


def api_codes() -> set[str]:
    text = API_FILE.read_text(encoding="utf-8")
    return {m.group("value") for m in CHOICE_RE.finditer(text)}


def web_codes() -> set[str]:
    text = WEB_FILE.read_text(encoding="utf-8")
    return {m.group("key") for m in UNION_RE.finditer(text)}


def icon_codes() -> set[str]:
    text = ICON_FILE.read_text(encoding="utf-8")
    # Faqat `VERDICT_ICONS` bloki — faylda boshqa `Key: VerdictIcon…` yo'q,
    # lekin komponent e'lonlari ham shu naqshga tushmasligi uchun kesamiz.
    i = text.find("export const VERDICT_ICONS")
    return {m.group("key") for m in ICONMAP_RE.finditer(text[i:])} if i >= 0 else set()


def locale_labels(code: str) -> set[str]:
    """Qaysi tillarda `verdict.<KOD>` yorlig'i bor."""
    have: set[str] = set()
    for loc in LOCALES:
        path = LOCALE_DIR / f"{loc}.ts"
        if not path.exists():
            continue
        if re.search(rf'^\s{{2}}"verdict\.{re.escape(code)}"\s*:', path.read_text(encoding="utf-8"), re.M):
            have.add(loc)
    return have


def main() -> int:
    for path in (API_FILE, WEB_FILE, ICON_FILE):
        if not path.exists():
            print(f"✗ Fayl topilmadi: {path.relative_to(ROOT)}")
            return 1

    api = api_codes()
    web = web_codes()
    icons = icon_codes()
    if not api:
        print("✗ API'da birorta verdikt kodi topilmadi — naqsh o'zgargan bo'lishi mumkin")
        return 1

    problems: list[str] = []

    missing_web = sorted(api - web)
    if missing_web:
        problems.append(
            "`lib/theme/verdict.ts` da yo'q (xom kod bo'lib ko'rinadi): "
            + ", ".join(missing_web)
        )

    missing_icons = sorted(api - icons)
    if missing_icons:
        problems.append(
            "`icons/phosphor.tsx` da yo'q (savol ikonkasi chiqadi): "
            + ", ".join(missing_icons)
        )

    extra_web = sorted(web - api)
    if extra_web:
        problems.append(
            "API'da yo'q, lekin web'da bor (o'lik kod): " + ", ".join(extra_web)
        )

    # Har bir kod 10 tilda yorliqqa ega bo'lishi shart.
    for code in sorted(api):
        have = locale_labels(code)
        if len(have) != len(LOCALES):
            absent = [l for l in LOCALES if l not in have]
            problems.append(f"`verdict.{code}` yorlig'i yetishmaydi: {', '.join(absent)}")

    print(
        f"Tekshirildi: API {len(api)} kod · web {len(web)} · ikonka {len(icons)} · "
        f"{len(LOCALES)} til"
    )
    if problems:
        print(f"\n{len(problems)} ta muammo:\n")
        for p in problems:
            print(f"  {p}")
        print("\nTuzatish tartibi modul docstring'ida.")
        return 1
    print("Kodlar mos ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
