"""Mavjud ommaviy masalalarga raqam beradi.

Tartib — qo'shilgan vaqti bo'yicha, ya'ni eng eski masala `#0001`.
Qoralamalar (`is_public=False`) raqamsiz qoladi va e'lon qilinganda oladi.
"""

from __future__ import annotations

from django.db import migrations


def assign(apps, schema_editor) -> None:  # type: ignore[no-untyped-def]
    Problem = apps.get_model("problems", "Problem")
    number = 0
    for problem in Problem.objects.filter(is_public=True, code__isnull=True).order_by(
        "created_at", "pk"
    ):
        number += 1
        problem.code = number
        problem.save(update_fields=["code"])

    # Hisoblagich 0006 da yaratiladi; uni o'sha migratsiya to'ldiradi.


def clear(apps, schema_editor) -> None:  # type: ignore[no-untyped-def]
    apps.get_model("problems", "Problem").objects.update(code=None)


class Migration(migrations.Migration):
    dependencies = [("problems", "0004_problem_code")]

    operations = [migrations.RunPython(assign, clear)]
