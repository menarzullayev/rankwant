"""Ko'nikmalar katalogi — boshlang'ich ro'yxat.

Ma'lumot migratsiya ichiga KO'CHIRILGAN, katalog moduli import
qilinmaydi: keyinroq modul o'zgarsa, eski migratsiya boshqa natija
bermasligi kerak.
"""

from django.db import migrations

SKILLS = [
    ('algorithms', 'Algoritmlar', 'Алгоритмы', 'Algorithms'),
    ('data-structures', "Ma'lumotlar tuzilmalari", 'Структуры данных', 'Data structures'),
    ('dynamic-programming', 'Dinamik dasturlash', 'Динамическое программирование', 'Dynamic programming'),
    ('graphs', 'Graflar', 'Графы', 'Graphs'),
    ('math', 'Matematika', 'Математика', 'Mathematics'),
    ('number-theory', 'Sonlar nazariyasi', 'Теория чисел', 'Number theory'),
    ('geometry', 'Geometriya', 'Геометрия', 'Geometry'),
    ('strings', 'Satrlar', 'Строки', 'Strings'),
    ('greedy', "Ochko'z algoritmlar", 'Жадные алгоритмы', 'Greedy algorithms'),
    ('combinatorics', 'Kombinatorika', 'Комбинаторика', 'Combinatorics'),
    ('competitive-programming', 'Sport dasturlash', 'Спортивное программирование', 'Competitive programming'),
    ('web-development', 'Veb-dasturlash', 'Веб-разработка', 'Web development'),
    ('backend', 'Backend', 'Бэкенд', 'Backend'),
    ('frontend', 'Frontend', 'Фронтенд', 'Frontend'),
    ('mobile', 'Mobil dasturlash', 'Мобильная разработка', 'Mobile development'),
    ('data-science', 'Data Science', 'Data Science', 'Data science'),
    ('machine-learning', "Mashinaviy o'qitish", 'Машинное обучение', 'Machine learning'),
    ('devops', 'DevOps', 'DevOps', 'DevOps'),
    ('databases', "Ma'lumotlar bazalari", 'Базы данных', 'Databases'),
    ('cybersecurity', 'Kiberxavfsizlik', 'Кибербезопасность', 'Cybersecurity'),
    ('game-development', "O'yin yaratish", 'Разработка игр', 'Game development'),
    ('web-scraping', 'Veb-skreyping', 'Веб-скрейпинг', 'Web scraping'),
]


def seed(apps, schema_editor):  # type: ignore[no-untyped-def]
    Skill = apps.get_model("profiles", "Skill")
    for order, (slug, uz, ru, en) in enumerate(SKILLS):
        Skill.objects.update_or_create(
            slug=slug, defaults={"name_uz": uz, "name_ru": ru, "name_en": en, "order": order}
        )


def unseed(apps, schema_editor):  # type: ignore[no-untyped-def]
    apps.get_model("profiles", "Skill").objects.filter(slug__in=[s[0] for s in SKILLS]).delete()


class Migration(migrations.Migration):
    dependencies = [("profiles", "0001_initial")]
    operations = [migrations.RunPython(seed, unseed)]
