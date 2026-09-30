from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("judging", "0008_relabel_re_legacy"),
    ]

    operations = [
        migrations.AddField(
            model_name="attempt",
            name="running_test_index",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
