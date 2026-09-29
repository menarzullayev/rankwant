"""M10 heuristikasi — migratsiya va testlar uchun umumiy manba.

Migratsiya fayllari testlar tomonidan import qilinishi nozik (Django
migration modullari nom bo'yicha yuklanadi), shuning uchun heuristika
alohida kichik modulda yashaydi va ikkala tomondan ishlatiladi.
"""

from __future__ import annotations


def judge_meta_choice(meta: dict[str, object] | None) -> str:
    """Bitta eski `RE` qator uchun yangi verdikt (M10 heuristikasi).

    Telemetriya manbasi `Attempt.judge_meta` (JSONField). Heuristik:

    - `meta` lug'at bo'lmasa (NULL/boshqa tur) → RE_SIGNAL
    - `signal` kaliti bo'lsa → RE_SIGNAL
    - `exit_code` kaliti bo'lsa → RE_EXIT
    - Aks holda → RE_SIGNAL (default — eski davrda signal xatolar ko'proq
      uchragan; judge `ExitCode >= 128` ni RE_SIGNAL deb sanaydi)

    ⚠️ O'lchangan cheklov (2026-09-29, QA): judge-go signal/exit kodini
    faqat `classify` bosqichida verdiktga aylantiradi va natijaga
    YOZMAYDI (`judge_meta`da `signal`/`exit_code` kalitlari yo'q).
    Shuning uchun migratsiya amalda barcha qatorlarni default RE_SIGNAL
    ga o'tkazadi. Bu — hujjatlashtirilgan qaror: ajratish ma'lumoti
    tarixiy qatorlarda aslo saqlanmagan, uni o'ylab topib bo'lmaydi.
    WP7 (judge hardening) tavsiyasi: judge `judge_meta` ga
    `signal`/`exit_code` ni yozsin — kelajakdagi qayta yorliqlashlar
    ishonchli bo'lsin.
    """
    if not isinstance(meta, dict):
        return "RE_SIGNAL"
    if "signal" in meta:
        return "RE_SIGNAL"
    if "exit_code" in meta:
        return "RE_EXIT"
    return "RE_SIGNAL"
