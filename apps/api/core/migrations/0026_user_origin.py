# WP3: User.origin — foydalanuvchi kelib chiqishi (North Star metrikalar)

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0025_alter_user_rating_default"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="origin",
            field=models.CharField(
                max_length=16,
                choices=[
                    ("real", "Real"),
                    ("demo", "Demo"),
                    ("imported", "Imported"),
                    ("staff", "Staff"),
                ],
                default="real",
            ),
        ),
    ]
