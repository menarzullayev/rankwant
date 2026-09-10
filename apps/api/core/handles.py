"""Taxallus qoidalari va skeleti — ADR-0016.

Taxallus standings'da, profil manzilida va musobaqa jadvalida ko'rinadi,
ya'ni u KIMLIK. Shu sababli ikkita alohida masala hal qilinadi: qaysi
belgilar ruxsat etiladi va ikki taxallus bir-biriga o'xshab qolmasligi.
"""

from __future__ import annotations

import re

from django.core.exceptions import ValidationError

MIN_LENGTH = 3
MAX_LENGTH = 20

#: Kirill, lotin, raqam, pastki chiziq va nuqta. Bo'sh joy yo'q.
#:
#: O'zbekcha maxsus harflar ataylab TASHQARIDA: lotinda `U+02BB` (`o'`,
#: `g'` dagi belgi), kirillda `U+045E`, `U+049B`, `U+0493`, `U+04B3`.
#: Ular URL'da, terminalda va boshqa platformalarga ko'chirishda
#: muammo tug'diradi, taxallus esa hamma joyda bir xil ko'chirilishi kerak.
ALLOWED = re.compile(r"^[A-Za-z0-9._а-яА-ЯёЁ]+$")

#: Kirill harflari, lotinda ko'zga AYNAN bir xil ko'rinadigani bilan.
#:
#: Ro'yxat `casefold()` dan KEYIN qo'llanadi, shuning uchun katta
#: harflardagi juftliklar ham shu yerda: `U+0412` (kirill Ve) va lotin `B`
#: bosh harfda farqsiz, kichik harfda esa farq qiladi — fold qilinmasa
#: taqlid katta harf bilan yozilib o'tib ketardi.
FOLD = str.maketrans(
    {
        "а": "a",  # а
        "в": "b",  # в  (В ≡ B)
        "е": "e",  # е
        "к": "k",  # к  (К ≡ K)
        "м": "m",  # м  (М ≡ M)
        "н": "h",  # н  (Н ≡ H)
        "о": "o",  # о
        "р": "p",  # р
        "с": "c",  # с
        "т": "t",  # т  (Т ≡ T)
        "у": "y",  # у
        "х": "x",  # х
        "ё": "e",  # ё → е → e
    }
)


def skeleton(username: str) -> str:
    """Taqlidni aniqlash uchun soddalashtirilgan shakl.

    Registr olib tashlanadi va ko'zga bir xil ko'rinadigan kirill harflari
    lotin juftiga keltiriladi. Shu bilan `admin` ning birinchi harfini
    kirillga almashtirib olingan nom mavjud `admin` bilan bir skeletga
    tushadi va rad etiladi.

    Nuqta va pastki chiziq TEGILMAYDI: `ali.2007` va `ali_2007` ko'zga
    yetarlicha farq qiladi va ularni birlashtirish haqiqiy taxalluslarni
    keraksiz to'sardi.
    """
    return username.casefold().translate(FOLD)


def validate(username: str) -> None:
    """Qoidaga mos kelmasa `ValidationError`. Xabar — foydalanuvchi tilida emas,
    chaqiruvchi uni tarjima qiladi."""
    if not MIN_LENGTH <= len(username) <= MAX_LENGTH:
        raise ValidationError(f"Taxallus {MIN_LENGTH}–{MAX_LENGTH} belgi bo'lishi kerak")
    if not ALLOWED.match(username):
        raise ValidationError(
            "Taxallusda faqat lotin yoki kirill harflari, raqam, nuqta va "
            "pastki chiziq bo'lishi mumkin"
        )
