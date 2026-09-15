"""Chiqishni UTF-8 ga majburlaydi — Windows uchun.

Nega kerak: tekshiruvlar `✓`, `✗`, `⚠` va `→` belgilarini chiqaradi.
Windows'da `sys.stdout` kodlashi konsol yoki lokal sozlamadan olinadi va
chiqish QUVURGA yo'naltirilganda `cp1252` bo'lib qoladi. O'shanda birinchi
`✓` da jarayon qulaydi:

    UnicodeEncodeError: 'charmap' codec can't encode character '\\u2713'

⚠️ 2026-09-15 da o'lchandi: 10 ta `check_*.py` dan 8 tasi aynan shu sabab
quvur ostida yiqildi. Bu ikki xil zarar keltiradi:

  * odam `python tools/check_i18n.py | less` desa — tekshiruv kod haqida
    emas, o'z chiqishi haqida yiqiladi;
  * `check_negative.py` bolalarni `capture_output=True` bilan, ya'ni
    QUVUR orqali chaqiradi. Bola qulasa chiqish kodi nolga teng bo'lmaydi,
    salbiy test esa buni «buzuq holatni tutdi» deb o'qiydi — YOLG'ON
    YASHIL. Ya'ni darvoza jim o'lardi.

`PYTHONUTF8=1` ham shu muammoni yechadi, lekin u CHAQIRUVCHIdan talab
qilinadi: uni unutgan har bir yurish yana qulaydi. Shuning uchun tuzatish
skriptning o'zida — qanday chaqirilishidan qat'i nazar ishlaydi.
"""

from __future__ import annotations

import sys


def force_utf8() -> None:
    """`stdout`/`stderr` ni UTF-8 ga o'tkazadi. Bir necha marta chaqirsa bo'ladi.

    Allaqachon UTF-8 bo'lsa hech narsa qilinmaydi (Linux va CI shu yo'lda).
    Oqim `reconfigure` ni qo'llamasa — masalan almashtirilgan soxta oqim —
    jim o'tiladi: bu bezak, tekshiruvni to'xtatishga arzimaydi.
    """
    for stream in (sys.stdout, sys.stderr):
        encoding = getattr(stream, "encoding", None) or ""
        if encoding.lower().replace("-", "") == "utf8":
            continue
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (ValueError, OSError):
            pass
