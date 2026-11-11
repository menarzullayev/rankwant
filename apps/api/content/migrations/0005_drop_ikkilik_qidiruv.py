"""Delete the old `ikkilik-qidiruv` article (ADR-0062 § 3; owner decision ⑨).

The cp.uz library brings its own binary search article; the owner chose to
delete ours without a redirect. A roadmap step that pointed only at it would
be left with neither an article nor a problem (`RoadmapStep.clean` refuses
that), so such a step goes too. Our own article only: an imported one with
the same slug (`source_ref` set) is never touched.

Not reversible: the text is in the pre-migration dump the deploy takes.
"""

from django.db import migrations

SLUG = "ikkilik-qidiruv"


def drop(apps, schema_editor):  # type: ignore[no-untyped-def]
    Article = apps.get_model("content", "Article")
    RoadmapStep = apps.get_model("content", "RoadmapStep")
    for article in Article.objects.filter(slug=SLUG, source_ref=""):
        RoadmapStep.objects.filter(article=article, problem__isnull=True).delete()
        article.delete()


class Migration(migrations.Migration):
    dependencies = [("content", "0004_cpuz_library")]

    operations = [migrations.RunPython(drop, migrations.RunPython.noop)]
