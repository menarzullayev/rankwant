#!/usr/bin/env python3
"""UI tarjimalari TO'LIQ ekanini tekshiradi.

`uz` — manba: kalitlar shundan olinadi. Har bir til o'sha kalitlarning
HAMMASINI, bo'sh bo'lmagan qiymat bilan berishi shart.

TypeScript ham buni ushlaydi (`Record<MessageKey, string>`), lekin u
bo'sh satrni yoki tarjimasiz qoldirilgan o'zbekcha nusxani ko'rmaydi —
shuning uchun bu tekshiruv alohida turadi va CI da ishlaydi.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCALES_DIR = ROOT / "apps/web/src/i18n/locales"
INDEX = ROOT / "apps/web/src/i18n/messages.ts"
SOURCE = "uz"
#: Manba bilan bir xil qolishi ATAYIN bo'lgan kalitlar.
#:
#: Bir xillikni xato deb hisoblash muhim — u odatda tarjima qilishni
#: unutganni bildiradi. Lekin haqiqiy tasodiflar ham bor, shuning uchun
#: har biri shu yerda YOZMA ravishda tasdiqlanadi.
#:
#: `*` — brend va reyting nomlari: ular hech qaysi tilda tarjima
#: qilinmaydi (Codeforces «Div. 2» ni ham tarjima qilmaydi).
UNTRANSLATED_OK: dict[str, set[str]] = {
    "*": {
        "nav.qvant", "qvant.title", "leaderboard.skills", "leaderboard.contest",
        "leaderboard.activity", "leaderboard.streak", "leaderboard.challenges",
        "nav.arena", "auth.email", "hackathon.demo", "settings.channelTelegram",
    },
    # Qoraqalpoq tili o'zbek tiliga eng yaqini — xalqaro o'zlashmalar
    # ikkalasida ham aynan bir xil yoziladi.
    "kaa": {
        "nav.leaderboard", "contests.rated", "leaderboard.title", "qvant.balance",
        "nav.menu", "auth.password", "navGroup.lab", "navGroup.campus",
        "navGroup.platform", "nav.classroom", "nav.duels", "nav.tournaments",
        "nav.formulas", "attempts.verdict", "attempts.language",
        "tournament.points", "hackathon.score", "hackathon.repo",
        "settings.nav.profile", "profile.ratingColumn", "profile.tab.rating",
        "settings.company", "settings.effect.none", "settings.language",
        "settings.password", "settings.technologies", "settings.website",
        # Unvon zinapoyasi va daraja nomlari — xalqaro fizika atamalari.
        "level.expert", "level.master", "title.kvark", "title.foton", "title.elektron",
        "title.proton", "title.atom", "title.molekula", "title.kristal", "title.galaktika",
        "profile.reason.duel", "profile.virtual",
        # Qoraqalpoqchada ham shunday: o'zlashma so'zlar.
        "role.champion", "profile.online", "tier.bronze",
    },
    # «Duel» — inglizchadan o'zlashgan, ingliz tilida o'sha so'zning o'zi.
    "en": {"nav.duels", "level.master", "title.proton", "title.atom",
           "profile.reason.duel", "profile.virtual"},
    # Turk tilida ham «Profil» — o'zbekcha bilan harfma-harf bir xil.
    "tr": {"settings.nav.profile", "title.foton", "title.elektron", "title.proton",
           "title.atom", "title.kristal"},
    # Ispan tilida ham «Virtual».
    "es": {"profile.virtual"},
}
#: Kalit tirnoqli ham, tirnoqsiz ham bo'lishi mumkin: prettier `quoteProps`
#: sozlamasi bilan oddiy identifikatorlardan tirnoqni olib tashlaydi va
#: faqat tirnoqlisini qidirgan tekshiruv o'sha kalitni JIMGINA o'tkazib
#: yuborardi — o'lchandi, 161 o'rniga 160 ta kalit ko'rindi.
PAIR = re.compile(r'^\s*(?:"([^"]+)"|([A-Za-z_$][\w$]*)):\s*"((?:[^"\\]|\\.)*)",\s*$', re.M)


def load(path: Path) -> dict[str, str]:
    return {
        quoted or bare: value
        for quoted, bare, value in PAIR.findall(path.read_text(encoding="utf-8"))
    }


def declared_locales() -> list[str]:
    block = re.search(r"export const LOCALES = \[(.*?)\] as const;", INDEX.read_text(), re.S)
    if block is None:
        sys.exit("messages.ts da LOCALES topilmadi")
    return re.findall(r'"([a-z-]+)"', block.group(1))


def main() -> int:
    codes = declared_locales()
    if SOURCE not in codes:
        sys.exit(f"manba til {SOURCE!r} LOCALES da yo'q")

    source = load(LOCALES_DIR / f"{SOURCE}.ts")
    if not source:
        sys.exit(f"{SOURCE}.ts bo'sh yoki o'qib bo'lmadi")

    problems: list[str] = []
    for code in codes:
        path = LOCALES_DIR / f"{code}.ts"
        if not path.exists():
            problems.append(f"{code}: fayl yo'q ({path.name})")
            continue
        values = load(path)
        missing = [k for k in source if k not in values]
        extra = [k for k in values if k not in source]
        blank = [k for k, v in values.items() if not v.strip()]
        allowed = UNTRANSLATED_OK["*"] | UNTRANSLATED_OK.get(code, set())
        same = [
            k
            for k, v in values.items()
            if code != SOURCE and k not in allowed and v == source.get(k)
        ]
        for nom, rows in (("yetishmaydi", missing), ("ortiqcha", extra), ("bo'sh", blank)):
            if rows:
                problems.append(f"{code}: {len(rows)} kalit {nom} — {rows[:5]}")
        if same:
            problems.append(f"{code}: {len(same)} kalit tarjimasiz (uz bilan bir xil) — {same[:5]}")

    if problems:
        print("i18n to'liq emas:")
        for row in problems:
            print(f"  {row}")
        return 1

    print(f"Tekshirildi: {len(codes)} til × {len(source)} kalit — to'liq ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
