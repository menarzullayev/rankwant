"""Test guruhlari siyosati (PROMPT_0 §3 · ADR 0051).

Modelda faqat TASNIF turadi (`TestCase.Group`). Qarorlar — ko'rinish, nashr
talabi, judge siyosati — shu yerda, ya'ni bitta joyda. Sabab: guruh bo'yicha
siyosat serializer, view, nashr darvozasi va judge payload'ining hammasiga
kerak; uni har biriga ko'chirib yozish ertami-kechmi ajralib ketadi.

Guruh — FAQAT metadata emas. Uchta haqiqiy oqim shunga tayanadi:

1. **Ko'rinish** — `PUBLIC_GROUPS` dan tashqari hamma test yashirin. Ommaviy
   API hech qachon yashirin testni ko'rsatmaydi.
2. **Nashr talabi** — `REQUIRED_GROUPS` bo'sh bo'lsa masala nashr bo'lmaydi
   (release checklist §9, `TEST_GROUP_MISSING`).
3. **Judge siyosati** — `STRESS` testlari yechimni baholashga KIRMAYDI:
   ular kalibrlash dalili, ya'ni sekin yechimni ataylab TLE qiladi. Ular
   baholansa har bir oddiy yechim yiqilardi.
"""

from __future__ import annotations

from collections.abc import Iterable

from problems.models import TestCase

Group = TestCase.Group

#: Ommaviy API da ko'rinadigan guruhlar. Qolgani — yashirin.
PUBLIC_GROUPS: frozenset[str] = frozenset({Group.SAMPLE})

#: Tartib va izoh — UI va serializerlar uchun yagona manba.
#: Tartib muhim: namuna birinchi, stress oxirgi.
GROUP_META: dict[str, tuple[int, str]] = {
    Group.SAMPLE: (10, "Shartdagi namuna — ommaviy ko'rinadi"),
    Group.MINIMAL: (20, "Eng kichik ruxsat etilgan kiritma"),
    Group.BOUNDARY: (30, "Chegara qiymatlari"),
    Group.SPECIAL: (40, "Alohida holatlar (hammasi teng, bitta element...)"),
    Group.RANDOM: (50, "Tasodifiy holatlar"),
    Group.ADVERSARIAL: (60, "Noto'g'ri algoritmlarni ushlash uchun"),
    Group.MAXIMUM: (70, "Limitga yaqin hajm"),
    Group.STRESS: (80, "Kalibrlash dalili — baholashga kirmaydi"),
    Group.UNCLASSIFIED: (90, "Tasniflanmagan (faqat ko'chirish holati)"),
}

#: Nashr uchun MAJBURIY: har biri kamida bitta testga ega bo'lishi kerak.
#: Release checklist §9: «Edge case, boundary va maksimal testlar mavjud».
REQUIRED_GROUPS: frozenset[str] = frozenset({Group.BOUNDARY, Group.MAXIMUM})

#: Yechimni baholashga KIRMAYDIGAN guruhlar. Sabab — modul docstringi.
NON_JUDGED_GROUPS: frozenset[str] = frozenset({Group.STRESS})

#: Yangi test uchun standart guruh: muallif yozgan test tasniflanmagan
#: bo'lsa, u qasddan emas — balki hali belgilanmagan. `RANDOM` deb yozish
#: yolg'on bo'lardi (test tasodifiy bo'lmasligi mumkin).
DEFAULT_GROUP = Group.UNCLASSIFIED


def is_public_group(group: str) -> bool:
    """Shu guruh ommaviy API da ko'rinadimi."""
    return group in PUBLIC_GROUPS


def group_order(group: str) -> int:
    """UI tartibi; noma'lum guruh oxirida turadi."""
    return GROUP_META.get(group, (1000, ""))[0]


def group_label(group: str) -> str:
    return GROUP_META.get(group, (1000, group))[1]


def missing_required_groups(groups: Iterable[str]) -> list[str]:
    """Nashr uchun yetishmayotgan majburiy guruhlar (barqaror tartibda).

    `UNCLASSIFIED` majburiy guruhni QOPLAMAYDI: tasniflanmagan test chegara
    testi emas. Aks holda ko'chirish holati darvozani jimgina ochib qo'yardi.
    """
    present = {g for g in groups if g != Group.UNCLASSIFIED}
    return sorted(REQUIRED_GROUPS - present, key=group_order)


def judged_groups() -> frozenset[str]:
    """Yechimni baholashda ishlatiladigan guruhlar."""
    return frozenset(Group.values) - NON_JUDGED_GROUPS


def is_judged(group: str) -> bool:
    return group not in NON_JUDGED_GROUPS
