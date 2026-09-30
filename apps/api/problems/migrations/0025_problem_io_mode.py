from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("problems", "0024_backfill_readiness"),
    ]

    operations = [
        migrations.AddField(
            model_name="problem",
            name="io_mode",
            field=models.CharField(
                choices=[("stdio", "Stdin/stdout"), ("both", "Stdin/stdout yoki fayl")],
                default="stdio",
                help_text="both: input.txt/output.txt ham, stdin/stdout ham qabul qilinadi.",
                max_length=8,
            ),
        ),
    ]
