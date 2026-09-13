#!/usr/bin/env python3
"""Yangi commit'lardan changelog qoralamasi uchun material tayyorlaydi.

Qaror 13–16 (DECISION-SESSION.md): manba — GitHub (PR / release / commit /
issue), matn — **AI qoralama → jamoa tahriri → AI tarjima ×10 → nashr**.

`rankwant-updates-design/backfill/backfill.py` — BIR MARTALIK ish edi:
butun tarixni qamrab oldi va yozuvlar qo'lda tuzilgan ro'yxatdan
(`ENTRIES`) olindi. Bu skript esa DOIMIY: oxirgi sinxronizatsiya
nuqtasidan keyingi commit'larni ko'rsatadi va nuqtani suradi.

Ishlatish (repo ildizidan):

    python tools/sync_updates.py                 # yangi commit'lar ro'yxati
    python tools/sync_updates.py --status        # hozirgi nuqta qayerda
    python tools/sync_updates.py --advance       # nuqtani HEAD ga surish
    python tools/sync_updates.py --since <sha>   # nuqtani chetlab o'tish

⚠️ Skript YOZUV YOZMAYDI va hech narsani bazaga yubormaydi. U faqat
MATERIAL tayyorlaydi. Sabab: commit sarlavhasi foydalanuvchi tilida emas —
`fix(api): allow blank username in register` ni avtomatik ko'chirish
o'qib bo'lmaydigan changelog berardi. Yozuvni AI yoki jamoa qoralama
qiladi, keyin:

    docker exec rankwant-api-1 python manage.py load_updates <fayl.json>
    python tools/sync_updates.py --advance

`load_updates` standart holatda **qoralama** yuklaydi (qaror 15: har yozuv
qo'lda tasdiqlanadi), ya'ni bu qadam hech narsani ommaga chiqarmaydi.

Nuqta `tools/.update-sync.json` da saqlanadi. Fayl repoga commit
QILINMAYDI (`.gitignore`) — u har ish joyining o'z holatini ko'rsatadi.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = Path(__file__).resolve().parent / ".update-sync.json"

#: Foydalanuvchiga ko'rinmaydigan commit turlari.
#:
#: ⚠️ Bu ro'yxat `backfill.py` dagi bilan bir xil — u yerda ham shunday.
#: Backfill endi ISHLATILMAYDI (bir martalik), ya'ni haqiqat manbai shu
#: fayl. Ikkalasi ajralib ketsa, yangi commit'lar jimgina tushib qolardi.
SKIP_TYPES = {"chore", "test", "ci", "docs", "style", "refactor", "merge", "build"}

#: Ichki scope'lar: `fix(ci)` turi `fix` bo'lsa ham foydalanuvchiga
#: ko'rinmaydi — tur bo'yicha filtr buni ushlamaydi.
SKIP_SCOPES = {"ci", "smoke", "e2e", "test", "deps", "build", "lint", "types"}

SUBJECT = re.compile(r"^([a-z]+)(?:\(([^)]*)\))?!?:")


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout


def commits_since(since: str | None) -> list[dict[str, str]]:
    """`since` dan keyingi commit'lar, eskidan yangiga.

    `since` bo'sh bo'lsa — butun tarix (birinchi ishga tushirish uchun).
    """
    rng = f"{since}..HEAD" if since else "HEAD"
    out = git("log", "--reverse", "--format=%ad|%h|%H|%s", "--date=short", rng)
    rows: list[dict[str, str]] = []
    for line in out.splitlines():
        date, short, sha, subject = line.split("|", 3)
        match = SUBJECT.match(subject)
        rows.append(
            {
                "date": date,
                "short": short,
                "sha": sha,
                "subject": subject,
                "type": match.group(1) if match else "other",
                "scope": (match.group(2) or "") if match else "",
            }
        )
    return rows


def user_facing(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        row
        for row in rows
        if row["type"] not in SKIP_TYPES and row["scope"] not in SKIP_SCOPES
    ]


def read_state() -> dict[str, str]:
    if not STATE.exists():
        return {}
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        # Buzuq fayl jimgina "nuqta yo'q" ga aylanmasin — aks holda butun
        # tarix qaytadan ko'rsatilardi va sabab ko'rinmasdi.
        print(f"⚠️ {STATE.name} o'qilmadi (JSON buzuq) — nuqta yo'q deb qabul qilindi", file=sys.stderr)
        return {}


def write_state(sha: str, date: str) -> None:
    STATE.write_text(
        json.dumps({"last_commit": sha, "last_date": date}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--since", default=None, help="Bu commit'dan keyingisini ko'rsat")
    parser.add_argument("--advance", action="store_true", help="Nuqtani HEAD ga surish")
    parser.add_argument(
        "--set", dest="set_to", default=None, help="Nuqtani shu commit'ga qo'yish"
    )
    parser.add_argument("--status", action="store_true", help="Nuqta va qamrovni ko'rsatish")
    options = parser.parse_args()

    state = read_state()
    since = options.since or state.get("last_commit") or None

    target = options.set_to or ("HEAD" if options.advance else None)
    if target is not None:
        sha = git("rev-parse", target).strip()
        date = git("log", "-1", "--format=%ad", "--date=short", target).strip()
        # ⚠️ Nuqta surilganda ORQADA QOLGAN ko'rinadigan commit'lar
        # ko'rsatiladi: aks holda ular jimgina yo'qolardi va keyingi
        # chaqiruvda hech qachon chiqmasdi.
        if since and since != sha:
            skipped = user_facing(commits_since(since))
            passed = [row for row in skipped if row["sha"] != sha]
            if passed:
                print(f"⚠️ nuqta orqasida {len(passed)} ta ko'rinadigan commit qoldi:")
                for row in passed[:10]:
                    print(f"   {row['short']}  {row['subject'][:70]}")
                if len(passed) > 10:
                    print(f"   … yana {len(passed) - 10} ta")
        write_state(sha, date)
        print(f"nuqta: {sha[:7]} ({date})")
        return 0

    rows = commits_since(since)
    usable = user_facing(rows)

    if options.status:
        if since:
            print(f"oxirgi nuqta: {since[:7]} ({state.get('last_date', '?')})")
        else:
            print("oxirgi nuqta: YO'Q — keyingi chaqiruv butun tarixni ko'rsatadi")
        print(f"o'shandan beri: {len(rows)} commit, shundan ko'rinadigani {len(usable)}")
        return 0

    if not usable:
        print("Yangi foydalanuvchiga ko'rinadigan commit yo'q.")
        if since:
            print(f"(nuqta: {since[:7]})")
        return 0

    print(f"Yangi commit'lar: {len(usable)} ta ko'rinadigan ({len(rows)} dan)\n")
    day = ""
    for row in usable:
        if row["date"] != day:
            day = row["date"]
            print(f"{day}")
        print(f"  {row['short']}  {row['subject']}")

    print(
        "\nKeyingi qadam:\n"
        "  1. Yuqoridagilardan foydalanuvchi sezadigan mavzularni guruhlang\n"
        "     (muhim o'zgarish alohida, kichik tuzatishlar guruhda — qaror 10).\n"
        "  2. Har guruh uchun `kind` va `module` tanlab, JSON tayyorlang\n"
        "     (namuna: rankwant-updates-design/backfill/updates.json).\n"
        "  3. Yuklang — standart holatda QORALAMA bo'lib tushadi:\n"
        "     docker exec rankwant-api-1 python manage.py load_updates <fayl.json>\n"
        "  4. Nuqtani suring:  python tools/sync_updates.py --advance"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
