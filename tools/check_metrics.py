#!/usr/bin/env python3
"""North Star metrikalar tekshiruvi — WP3.

Foydalanuvchi kelib chiqishi (origin) bo'yicha asosiy ko'rsatkichlarni
o'lchaydi va sanity checklar bilan birga chiqaradi.

Ishlatish:
    python tools/check_metrics.py
    DATABASE_URL=postgres://... python tools/check_metrics.py
"""

from __future__ import annotations

import argparse
import os
import sys
from urllib.parse import urlparse

#: North Star query — haqiqiy foydalanuvchilar soni
NORTH_STAR_SQL = "SELECT COUNT(*) FROM core_user WHERE origin = 'real'"
#: Umumiy foydalanuvchilar
TOTAL_SQL = "SELECT COUNT(*) FROM core_user"
#: Demo foydalanuvchilar
DEMO_SQL = "SELECT COUNT(*) FROM core_user WHERE origin = 'demo'"
#: Import qilingan foydalanuvchilar
IMPORTED_SQL = "SELECT COUNT(*) FROM core_user WHERE origin = 'imported'"
#: Staff foydalanuvchilar
STAFF_SQL = "SELECT COUNT(*) FROM core_user WHERE origin = 'staff'"
#: NULL origin tekshiruvi
NULL_SQL = "SELECT COUNT(*) FROM core_user WHERE origin IS NULL"


def get_database_url() -> str:
    """DATABASE_URL ni muhitdan oladi."""
    url = os.environ.get("DATABASE_URL")
    if not url:
        print("error: DATABASE_URL muhit o'zgaruvchisi kerak")
        sys.exit(1)
    return url


def run_query(conn, sql: str) -> int:
    """Bitta COUNT query ni bajaradi."""
    with conn.cursor() as cur:
        cur.execute(sql)
        result = cur.fetchone()
        return result[0] if result else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="North Star metrikalar tekshiruvi")
    parser.add_argument(
        "--self-test", action="store_true", help="Sintaksis va chiqishni sinaydi (DB kerak emas)"
    )
    parser.add_argument(
        "--allow-empty",
        action="store_true",
        help="Bo'sh bazani xato sanama (migrate qilingan, seed'siz baza — CI test bazasi)",
    )
    args = parser.parse_args()

    if args.self_test:
        print("check_metrics.py self-test: ok")
        return 0

    url = get_database_url()
    parsed = urlparse(url)

    conn_kwargs: dict[str, str | int] = {
        "host": parsed.hostname or "localhost",
        "dbname": parsed.path.lstrip("/"),
    }
    if parsed.port:
        conn_kwargs["port"] = parsed.port
    if parsed.username:
        conn_kwargs["user"] = parsed.username
    if parsed.password:
        conn_kwargs["password"] = parsed.password

    try:
        # `psycopg` (v3) — requirements'dagi yagona Postgres drayveri.
        # Ilgari `psycopg2` import qilingandi — u o'rnatilmagan va
        # CI'da bu qadam ImportError bilan yiqilar edi (QA 2026-09-29).
        import psycopg
    except ImportError:
        print("error: psycopg o'rnatilmagan")
        return 1

    try:
        conn = psycopg.connect(**conn_kwargs)
    except Exception as exc:
        print(f"error: bazaga ulanib bo'lmadi — {exc}")
        return 1

    try:
        north_star = run_query(conn, NORTH_STAR_SQL)
        total = run_query(conn, TOTAL_SQL)
        demo = run_query(conn, DEMO_SQL)
        imported = run_query(conn, IMPORTED_SQL)
        staff = run_query(conn, STAFF_SQL)
        null_count = run_query(conn, NULL_SQL)

        print(f"North Star (real users): {north_star}")
        print(f"  total:   {total}")
        print(f"  demo:    {demo}")
        print(f"  imported:{imported}")
        print(f"  staff:   {staff}")
        print(f"  null:    {null_count}")

        errors: list[str] = []

        # North Star o'zi nol bo'lsa — darvoza ma'nosiz (mutatsiya:
        # `WHERE origin = 'not_real'` ham exit 0 berardi). Bo'sh bazada
        # (--allow-empty) bu mezon kechiriladi.
        if north_star == 0 and not args.allow_empty:
            errors.append("North Star (origin='real') = 0 — real foydalanuvchi yo'q")

        if null_count > 0:
            errors.append(f"NULL origin lar topildi: {null_count}")

        if total == 0 and not args.allow_empty:
            # CI'da `rankwant_test` migrate qilinadi, lekin seed qilinmaydi —
            # bo'sh baza u yerda NORMA. Bo'sh baza faqat shu bayroq bilan
            # kechiriladi (CTO qarori 2026-09-29): joriy muhit o'chirib
            # yuborilgan bo'lsa, "--allow-empty" siz ham exit 1 beradi.
            errors.append("Bazada umuman foydalanuvchi yo'q (--allow-empty bilan kechiriladi)")

        # Seed foydalanuvchilar mavjud bo'lsa demo > 0 bo'lishi kerak
        # Bu faqat ogohlantirish — biznes qoidasi emas
        if demo == 0 and total > 100:
            print("  warning: demo=0, lekin seed foydalanuvchilar mavjud bo'lishi mumkin")

        if errors:
            print()
            print("Xatolar:")
            for err in errors:
                print(f"  - {err}")
            return 1

        print()
        print("Barcha tekshiruvlar o'tdi")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
