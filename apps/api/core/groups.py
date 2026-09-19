"""Staff guruhlari — ADR-0025 (qaror 23).

`sync_staff_groups()` — idempotent: guruhlarni yaratadi (yo'q bo'lsa),
model permission'larini biriktiradi. `core/apps.py` post_migrate'da
chaqiradi — chunki migration ICHIDA `Permission` qatorlarini so'rash
ishlamaydi: `auth_permission` qatorlari post_migrate to'laganidan KEYIN
paydo bo'ladi (o'lchandi: test bazasi yaratilishida DoesNotExist).

Foydalanuvchilarni guruhlarga QO'SHISH bu yerda Yo'Q: superuser Django
admin'da biriktiradi (aks holda superuser olib tashlagan guruh har
migrate'da qaytib kelardi). Bir martalik qo'shish — seed migration'da.
"""

from __future__ import annotations

from django.contrib.auth.models import Group, Permission

GROUPS: tuple[str, ...] = ("staff-support", "staff-content", "staff-ops")

#: Guruh model permission'lari — Django admin uchun. Staff API'dagi amal
#: darajasidagi tekshiruvlar guruh NOMI bo'yicha (`core.permissions`).
PERMISSIONS: dict[str, tuple[tuple[str, str], ...]] = {
    "staff-support": (("core", "view_user"),),
    "staff-content": (
        ("core", "view_school"),
        ("core", "add_school"),
        ("core", "change_school"),
        ("core", "delete_school"),
        ("blog", "view_post"),
        ("blog", "add_post"),
        ("blog", "change_post"),
        ("blog", "delete_post"),
        ("content", "view_article"),
        ("content", "add_article"),
        ("content", "change_article"),
        ("content", "delete_article"),
        ("content", "view_roadmap"),
        ("content", "add_roadmap"),
        ("content", "change_roadmap"),
        ("content", "delete_roadmap"),
    ),
    "staff-ops": (
        ("core", "view_user"),
        ("core", "change_user"),
    ),
}


def sync_staff_groups() -> None:
    """Guruhlar + permission'lar — istalgancha chaqirilsa ham xavfsiz.

    Tolerant: post_migrate har app uchun fires bo'ladi va `core` boshida
    turadi — birinchi chaqiruvlarda `blog`/`content` permission'lari hali
    yaratilmagan bo'lishi mumkin. Yetishmaganlar O'TKAZIB YUBORILADI;
    oxirgi appning signalida barcha perm'lar mavjud va sync to'liq
    yakunlanadi (idempotent, shuning uchun yakuniy holat to'g'ri).
    """
    for name in GROUPS:
        group, _ = Group.objects.get_or_create(name=name)
        wanted = []
        for app_label, codename in PERMISSIONS[name]:
            try:
                wanted.append(
                    Permission.objects.get(content_type__app_label=app_label, codename=codename)
                )
            except Permission.DoesNotExist:
                continue  # keyingi post_migrate chaqiruvida qo'shiladi
        group.permissions.set(wanted)
