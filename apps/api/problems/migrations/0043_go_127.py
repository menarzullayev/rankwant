"""Go moves from 1.24 to 1.27 (decision 2026-11-14).

Go 1.24 left its support window in February 2026; the judge image now unpacks
Go 1.27 at /usr/lib/go-1.27 (services/judge-go/Dockerfile). The row is changed in
place — same primary key — so everything that points at Go stays: the languages
a problem allows, attempts, reference solutions.

Only the toolchain path inside the commands is rewritten, so a command an admin
has edited keeps its edit and still finds the compiler. The memory overhead stays
at 3 MB: measured again on the new image (decision file).
"""

from django.db import migrations

OLD = {"code": "go124", "version": "1.24", "root": "/usr/lib/go-1.24"}
NEW = {"code": "go127", "version": "1.27", "root": "/usr/lib/go-1.27"}


def repath(command, old_root, new_root):
    return [part.replace(old_root, new_root) if isinstance(part, str) else part for part in command]


def move(apps, old, new):
    Language = apps.get_model("problems", "Language")
    # A database seeded from the catalog after this change already has the new
    # row; renaming the old one onto it would break the unique code.
    if Language.objects.filter(code=new["code"]).exists():
        return
    for language in Language.objects.filter(code=old["code"]):
        language.code = new["code"]
        language.version = new["version"]
        language.compile_cmd = repath(language.compile_cmd, old["root"], new["root"])
        language.run_cmd = repath(language.run_cmd, old["root"], new["root"])
        language.save(update_fields=["code", "version", "compile_cmd", "run_cmd"])


def forwards(apps, schema_editor):
    move(apps, OLD, NEW)


def backwards(apps, schema_editor):
    move(apps, NEW, OLD)


class Migration(migrations.Migration):
    dependencies = [
        ("problems", "0042_test_generator"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
