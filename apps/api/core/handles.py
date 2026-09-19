"""Taxallus qoidalari va skeleti — ADR-0016.

Taxallus standings'da, profil manzilida va musobaqa jadvalida ko'rinadi,
ya'ni u KIMLIK. Shu sababli ikkita alohida masala hal qilinadi: qaysi
belgilar ruxsat etiladi va ikki taxallus bir-biriga o'xshab qolmasligi.
"""

from __future__ import annotations

import re

from django.core.exceptions import ValidationError

MIN_LENGTH = 3
MAX_LENGTH = 30

#: Faqat ASCII: lotin harfi, raqam, nuqta, pastki chiziq, chiziqcha.
#:
#: KIRILL OLIB TASHLANDI. Sabab taxmin emas, o'lchov: O'zbekistondagi
#: ikkala yirik platformaning 379 ta taxallusi ko'rildi (RoboContest 129,
#: KEP.uz 250) va ularning BIRORTASIDA ham ASCII bo'lmagan belgi yo'q.
#: Ikkalasi ham bir xil naqshni ishlatadi: taxallus ASCII, ko'rsatiladigan
#: ism esa cheklovsiz Unicode — bizda `display_name` shu vazifani bajaradi.
#: Taxallus URL yo'lida, `@` eslatmada va terminal chiqishida turadi,
#: kirill esa u yerda `%D0%B0%D0%BB%D0%B8` bo'lib ko'rinadi.
#:
#: O'zbekcha maxsus harflar ham shu sababdan tashqarida: lotinda `U+02BB`
#: (`o'`, `g'` dagi belgi), kirillda `U+045E`, `U+049B`, `U+0493`, `U+04B3`.
ALLOWED = re.compile(r"^[A-Za-z0-9._-]+$")

#: Kirill harflari, lotinda ko'zga AYNAN bir xil ko'rinadigani bilan.
#:
#: Kirill endi `ALLOWED` darvozasidan o'tmaydi, ya'ni bu jadval YANGI
#: nomlarga ta'sir qilmaydi. U saqlanadi, chunki `username_skeleton`
#: ustuni va uning yagonalik cheklovi bazada turibdi: qoida
#: toraytirilishidan oldin ochilgan hisoblar hamon shu skelet bilan
#: solishtiriladi.
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
        raise ValidationError(f"Handle must be {MIN_LENGTH}–{MAX_LENGTH} characters")
    if not ALLOWED.match(username):
        raise ValidationError(
            "A handle may only contain Latin letters, digits, dots, underscores, "
            "and hyphens"
        )
