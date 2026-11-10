| Sana | Qaror | Kodda qayerda |
|---|---|---|
| 2026-09-19 | **Rollar (ADR-0025)**: Django staff Groups (`staff-support` / `staff-content` / `staff-ops`) + obyekt M2M (`Contest.organizers`, `Problem.authors`). `User.role` CharField yo'q. Mavjud `is_staff` seed'da uchala guruhga qo'shiladi; permission qatorlari `sync_staff_groups()` post_migrate'da. `/contests/mine/` va `/problems/mine/` | `core/groups.py`; `contests/models.py`; `problems/models.py`; `tools/check_decisions.py` → `roles_groups_and_object_authors`; salbiy testlar 4 ta |
