"""Test guruhini ko'chirish (PROMPT_0 §3 · ADR 0051).

2026-09-30 gacha testlarda semantik tasnif yo'q edi. Backfill **faqat statik**
shartlar bilan ishlaydi — judge chaqirilmaydi, hech narsa o'ylab topilmaydi:

    origin = hack        -> `adversarial`   (hack testi tabiatan qarshi)
    is_sample = True     -> `sample`
    qolgani              -> `unclassified`  (tasnif yo'q — yolg'on yozmaymiz)

⚠️ TARTIB MUHIM: `hack` tekshiruvi BIRINCHI turadi. Agar hack testi
`is_sample=True` bo'lib qolgan bo'lsa (bug yoki noto'g'ri import), uni
`sample` deb belgilash testni OMMAVIY qilib qo'yardi — ya'ni hack testining
butun ma'nosi yo'qolardi. Shubhali holatda yopiq tomon tanlanadi.

`unclassified` ataylab: muallif yozgan testning xarakterini migratsiya bila
olmaydi. Uni `random` deb yozish yolg'on bo'lardi va nashr darvozasini
jimgina ochib qo'yardi (`testgroups.missing_required_groups` UNCLASSIFIED ni
majburiy guruh sifatida qabul qilmaydi).
"""

from __future__ import annotations

from django.db import migrations

SAMPLE = "sample"
ADVERSARIAL = "adversarial"
UNCLASSIFIED = "unclassified"


def backfill(apps, schema_editor) -> None:  # type: ignore[no-untyped-def]
    """Tasnifni yozadi va audit raqamlarini chop etadi."""
    TestCase = apps.get_model("problems", "TestCase")

    hack = TestCase.objects.filter(origin="hack").update(group=ADVERSARIAL)
    sample = TestCase.objects.filter(origin="author", is_sample=True).update(group=SAMPLE)
    rest = TestCase.objects.filter(group=UNCLASSIFIED).count()

    print(f"test group backfill: adversarial={hack} sample={sample} unclassified={rest}")
    if TestCase.objects.filter(group="").exists():
        raise RuntimeError("test group backfill left an empty group")


class Migration(migrations.Migration):
    dependencies = [("problems", "0026_test_group")]

    operations = [
        migrations.RunPython(backfill, migrations.RunPython.noop, elidable=True),
    ]
