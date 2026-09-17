import django.core.validators
from django.db import migrations, models

#: The names the judge used to derive from the code prefix. Writing them down
#: keeps existing rows working once the judge prefers the row's own file name.
LEGACY_SOURCE_FILES = (("cpp", "main.cpp"), ("py", "main.py"), ("java", "Main.java"))


def name_legacy_sources(apps, schema_editor):
    Language = apps.get_model("problems", "Language")
    for prefix, file_name in LEGACY_SOURCE_FILES:
        Language.objects.filter(code__startswith=prefix, source_file="").update(source_file=file_name)


class Migration(migrations.Migration):
    dependencies = [
        ("problems", "0015_reference_solution_and_test_origin"),
    ]

    operations = [
        migrations.AddField(
            model_name="language",
            name="source_file",
            field=models.CharField(
                blank=True,
                default="",
                max_length=64,
                validators=[
                    django.core.validators.RegexValidator(
                        "^[A-Za-z0-9_]+(\\.[A-Za-z0-9_]+)+\\Z", "Faqat fayl nomi: main.cpp, Main.java"
                    )
                ],
            ),
        ),
        migrations.AddField(
            model_name="language",
            name="compile_time_ms",
            field=models.PositiveIntegerField(default=10000),
        ),
        migrations.AddField(
            model_name="language",
            name="proc_self",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="language",
            name="open_files",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.RunPython(name_legacy_sources, migrations.RunPython.noop),
    ]
