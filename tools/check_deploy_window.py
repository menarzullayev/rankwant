#!/usr/bin/env python3
"""Live contest oynasi — deploy qoidasi №1 ning darvozasi.

NEGA KERAK: `docs/10-operations` 1-qoidasi «live contest paytida deploy
YO'Q» deydi, sabab — deploy paytida verdict yoki standings o'zgarishi
davom etayotgan musobaqa natijasini buzadi. CI bu oynani BILMAYDI:
`deploy.yml` da hamon `::warning::` bilan «qo'lda tekshirilsin» deb
yozilgan TODO turadi.

Ya'ni tekshiruv ilgari **odamning yodida** edi. 2026-09-16 da u
bajariladigan ko'rinishga keltirildi (`tools/deploy.sh` shu faylni
chaqiradi) — yodda saqlanadigan qadam bir kun o'tkazib yuboriladi.

CHIQISH KODLARI (uchinchi holat ataylab ajratilgan):
  0 — oyna bo'sh: faol contest ham, arena ham yo'q
  1 — faol contest/arena BOR: deploy taqiqlanadi
  2 — ANIQLANMADI: API javob bermadi

⚠️ Nega 2 alohida: «javob bermadi» ni «0 ta» deb o'qish yolg'on yashil
berardi va aynan sayt yiqilganda — ya'ni tuzatish deploy'i eng kerak
bo'lgan paytda — darvoza eng ishonchsiz bo'lardi. Qarorni chaqiruvchi
qabul qiladi (`deploy.sh` ogohlantiradi va davom etadi).

⚠️ User-Agent SHART: sayt Cloudflare ortida va u `Python-urllib/3.x` ni
bot deb bloklaydi — o'lchandi: 403 (`browser_signature_banned`). Ayni
shu tuzoq `core/mail_providers.py` da ham uchragan.

⚠️ LOKAL ORIGIN ZAXIRASI (2026-09-19). Tekshiruv `https://rankwant.uz` ga
uradi, ya'ni Cloudflare tunnel'idan o'tadi. Sayt yiqilganda javob yo'q →
`exit 2` → va aynan o'sha paytda tuzatish deploy'i eng kerak bo'ladi.
Qo'lda rejimda odam buni hal qiladi, AVTOMATIK rejimda esa odam yo'q:
`exit 2` jimgina «davom et» ga aylanadi va contest paytida ham deploy
o'tib ketishi mumkin.

Shuning uchun tashqi manzil javob bermasa, LOKAL origin so'raladi
(`127.0.0.1:8301`, `Host: rankwant.uz` bilan). Uch holat:
  1. tashqi javob berdi        → javob haqiqiy;
  2. tashqi yo'q, lokal bor    → javob haqiqiy (muammo tunnelda, deploy'da emas);
  3. ikkisi ham yo'q           → stack yiqilgan → `exit 2` (deploy — bu tuzatish).
Ya'ni `exit 2` endi faqat «stack butunlay yiqilgan» holatida qoladi.

⚠️ `RANKWANT_API_BASE` berilgan bo'lsa zaxira ISHLATILMAYDI: aniq manzil
«aynan shuni o'lcha» degani (salbiy testlar ham shunga tayanadi).
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

# Chiqish quvurga yo'naltirilganda Windows uni cp1252 deb yozadi va
# birinchi `✓` da qulaydi — sabab `tools/_console.py` da.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _console  # noqa: E402

_console.force_utf8()

DEFAULT_BASE = "https://rankwant.uz/api/v1"
#: Lokal origin — tashqi manzil javob bermaganda so'raladi. Sayt Cloudflare
#: ortida, ya'ni tashqi manzil o'lgan bo'lsa ham origin sog'lom bo'lishi mumkin.
LOCAL_BASE = "http://127.0.0.1:8301/api/v1"
#: ⚠️ `Host` sarlavhasi SHART: API `ALLOWED_HOSTS` ni tekshiradi va
#: `127.0.0.1` ni rad etadi — Hostsiz javob 400 (o'lchandi, topics/01).
LOCAL_HOST = "rankwant.uz"
USER_AGENT = "RankWant/1.0 (+https://rankwant.uz)"
TIMEOUT = 15

#: Tekshiriladigan resurslar: yo'l → odam o'qiydigan nomi.
RESOURCES = {
    "contests": "contest",
    "arena": "arena raundi",
}

#: Sahifalash chegarasi. Bitta sahifada 20-50 yozuv keladi; oyna
#: yorlig'i faqat joriy holatga qarab qo'yiladi, ya'ni birinchi sahifa
#: yetadi. Chegara cheksiz siklga tushib qolmaslik uchun.
MAX_PAGES = 5


class Unknown(Exception):
    """API javob bermadi yoki javob o'qilmadi — «0 ta» EMAS."""


def _get(url: str, host: str | None = None) -> dict[str, object]:
    headers = {"User-Agent": USER_AGENT}
    if host:
        headers["Host"] = host
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return json.loads(response.read().decode("utf-8", "replace"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError, ValueError) as exc:
        raise Unknown(f"{url}: {exc}") from exc


def running_rows(base: str, resource: str, host: str | None = None) -> list[dict[str, object]]:
    """`is_running` bayrog'i yoqilgan yozuvlar (sahifalab)."""
    url: str | None = f"{base}/{resource}/"
    found: list[dict[str, object]] = []
    for _ in range(MAX_PAGES):
        if not url:
            break
        payload = _get(url, host)
        rows = payload.get("results")
        if rows is None:  # sahifalanmagan javob
            rows = payload if isinstance(payload, list) else []
        for row in rows:  # type: ignore[union-attr]
            if isinstance(row, dict) and row.get("is_running"):
                found.append(row)
        nxt = payload.get("next")
        url = str(nxt) if isinstance(nxt, str) and nxt else None
    return found


def sources() -> list[tuple[str, str, str | None]]:
    """Tekshiriladigan manbalar: (nom, base, Host sarlavhasi).

    ⚠️ `RANKWANT_API_BASE` berilgan bo'lsa FAQAT o'sha qaytadi: aniq manzil
    «aynan shuni o'lcha» degani, zaxira esa o'lchovni chalg'itardi (salbiy
    testlar ham shunga tayanadi).
    """
    explicit = os.environ.get("RANKWANT_API_BASE")
    if explicit:
        return [("API", explicit.rstrip("/"), None)]
    return [("tashqi", DEFAULT_BASE, None), ("lokal origin", LOCAL_BASE, LOCAL_HOST)]


def collect(base: str, host: str | None) -> tuple[list[str], list[str]]:
    """Bitta manbadan: (faol yozuvlar, xatolar).

    Xato bo'lsa javob ISHONCHSIZ — «0 ta» deb o'qilmaydi va keyingi manba
    sinaladi.
    """
    live: list[str] = []
    errors: list[str] = []
    for resource, label in RESOURCES.items():
        try:
            rows = running_rows(base, resource, host)
        except Unknown as exc:
            errors.append(f"{label}: {exc}")
            continue
        for row in rows:
            slug = row.get("slug") or row.get("title") or row.get("id") or "?"
            end = row.get("end_at") or "?"
            live.append(f"{label} «{slug}» — {end} gacha")
    return live, errors


def main() -> int:
    live: list[str] = []
    unknown: list[str] = []
    answered: str | None = None

    for name, base, host in sources():
        rows, errors = collect(base, host)
        if errors:
            unknown.append(f"{name} ({base}) — {errors[0]}")
            continue
        live, answered = rows, name
        break

    if answered is None:
        print("⚠ Oyna aniqlanmadi — na tashqi manzil, na lokal origin javob berdi:")
        for line in unknown:
            print(f"    • {line}")
        print("  «0 ta» deb hisoblanmadi: buni o'zingiz tasdiqlang.")
        return 2

    # Zaxira ishlatilgani JIM QOLMAYDI: aks holda «tashqi manzil sog'lom»
    # degan yolg'on taassurot qoladi va tunnel o'lganini hech kim sezmaydi.
    if unknown:
        print("⚠ Tashqi manzil javob bermadi — lokal origin ishlatildi:")
        for line in unknown:
            print(f"    • {line}")

    if live:
        print(f"✗ Faol oyna topildi ({answered}) — deploy TAQIQLANADI (10-operations, qoida №1):")
        for line in live:
            print(f"    • {line}")
        print("  Musobaqa tugagach qayta urinib ko'ring.")
        return 1

    print(f"✓ Faol contest ham, arena ham yo'q — oyna bo'sh ({answered})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
