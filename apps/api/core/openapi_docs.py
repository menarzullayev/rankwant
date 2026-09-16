"""OpenAPI uchun qisqa tavsiflar — 138 ta «tavsifsiz» operatsiyani yopish.

Muammo: DRF ViewSet'lar `list`/`retrieve`/`create`/`update`/`destroy`
amallarini o'zi yasaydi, ya'ni kodda ularga mos metod yo'q — docstring
yozib bo'lmaydi. Sxemada esa 138 ta operatsiya tavsifsiz qolgan edi.

Yechim: `drf_spectacular` ning `extend_schema_view` dekoratori amal
**nomi** bo'yicha ishlaydi, metod bo'lishini talab qilmaydi.

`many`/`one` alohida so'raladi: o'zbekcha ko'plik qo'shimchasi doimiy
(`-lar`) bo'lsa ham, qo'shma so'zlarda («platforma yo'l xaritasi»)
avtomatik ko'plik g'alati chiqardi.
"""

from __future__ import annotations

from typing import Any

from drf_spectacular.utils import extend_schema, extend_schema_view

#: Standart ModelViewSet amallari. Boshqacha nomlangan amal (`publish`,
#: `finalize`) `extra` orqali qo'shiladi.
DEFAULT_ACTIONS = (
    "list",
    "retrieve",
    "create",
    "update",
    "partial_update",
    "destroy",
)


def crud_summaries(
    *, one: str, many: str, extra: dict[str, str] | None = None, only: tuple[str, ...] | None = None
) -> Any:
    """Amallarga bir qatorda tavsif beradi.

    `only` — faqat shu amallarga (masalan faqat o'qish uchun
    `only=("list", "retrieve")`). Ko'rsatilmasa `DEFAULT_ACTIONS`.
    """
    texts = {
        "list": f"{many} ro'yxati",
        "retrieve": f"Bitta {one}",
        "create": f"Yangi {one} yaratish",
        "update": f"{one}ni yangilash",
        "partial_update": f"{one}ni qisman yangilash",
        "destroy": f"{one}ni o'chirish",
    }
    names = only or DEFAULT_ACTIONS
    actions = {name: texts[name] for name in names if name in texts}
    actions.update(extra or {})
    return extend_schema_view(
        **{name: extend_schema(summary=text) for name, text in actions.items()}
    )


def action_summaries(**actions: str) -> Any:
    """CRUD bo'lmagan ViewSet'lar uchun: faqat o'ziga xos amallar.

    `action_summaries(login="Tizimga kirish", logout="Chiqish")`
    """
    return extend_schema_view(
        **{name: extend_schema(summary=text) for name, text in actions.items()}
    )
