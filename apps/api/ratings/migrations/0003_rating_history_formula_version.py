from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ratings", "0002_alter_ratinghistory_reason"),
    ]

    operations = [
        # Added WITHOUT a default so existing rows stay `null`: their rules
        # were not recorded, and a backfilled "1" would invent history.
        migrations.AddField(
            model_name="ratinghistory",
            name="formula_version",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        # New rows get the current version (the default is applied in Python).
        migrations.AlterField(
            model_name="ratinghistory",
            name="formula_version",
            field=models.PositiveSmallIntegerField(blank=True, default=1, null=True),
        ),
    ]
