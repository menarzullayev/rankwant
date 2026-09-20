# ADR-0027: New accounts start at 1200 (droplet, green / 0).

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0024_alter_siteappearance_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="rating_contest",
            field=models.IntegerField(db_index=True, default=1200),
        ),
    ]
