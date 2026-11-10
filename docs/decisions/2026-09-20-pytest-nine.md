| Sana | Qaror | Kodda qayerda |
|---|---|---|
| 2026-09-20 | **pytest 9 + pytest-django 4.14** (HITL: ikkalasi birga). Lock allaqachon `pytest==9.1.1` / `pytest-django==4.14.0` (Nightly shu pinni o'rnatadi); floor `>=8` / `>=4.9` qolgani compile'ni 8.x ga qaytarishi mumkin. Floor va lock birga 9.x da. PR CI pytest yugurtirmaydi — `pr_skips_heavy_ci` | `apps/api/requirements-dev.txt`; `apps/api/requirements-dev.lock`; `tools/check_decisions.py` → `pytest_nine_and_django_plugin`; salbiy testlar 2 ta |
