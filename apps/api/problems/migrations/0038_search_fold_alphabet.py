"""Stored search columns refolded for the new alphabet (ADR-0059).

`title_search`, `Topic.name_search` and `translated_titles` hold
`normalize_search` output, which now maps `ö ğ ş ç` and drops `ʼ`. A row
folded the old way would miss a query folded the new way.
"""

from django.db import migrations

from core.search import normalize_search

BATCH = 500


def refold(apps, schema_editor):  # type: ignore[no-untyped-def]
    Problem = apps.get_model("problems", "Problem")
    Topic = apps.get_model("problems", "Topic")
    Translation = apps.get_model("problems", "ProblemTranslation")

    titles: dict[int, list[str]] = {}
    for problem_id, title in Translation.objects.values_list("problem_id", "title"):
        if title:
            titles.setdefault(problem_id, []).append(normalize_search(title))

    changed = []
    for problem in Problem.objects.only("id", "title", "title_search", "translated_titles").iterator(
        chunk_size=BATCH
    ):
        title_search = normalize_search(problem.title)
        translated = "\n".join(titles.get(problem.id, []))
        if (title_search, translated) != (problem.title_search, problem.translated_titles):
            problem.title_search = title_search
            problem.translated_titles = translated
            changed.append(problem)
    Problem.objects.bulk_update(changed, ["title_search", "translated_titles"], batch_size=BATCH)

    topics = []
    for topic in Topic.objects.only("id", "name_uz", "name_search"):
        name_search = normalize_search(topic.name_uz)
        if name_search != topic.name_search:
            topic.name_search = name_search
            topics.append(topic)
    Topic.objects.bulk_update(topics, ["name_search"], batch_size=BATCH)


class Migration(migrations.Migration):
    dependencies = [("problems", "0037_problem_translations")]

    operations = [migrations.RunPython(refold, migrations.RunPython.noop)]
