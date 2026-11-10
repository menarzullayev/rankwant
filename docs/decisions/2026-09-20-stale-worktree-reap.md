| Sana | Qaror | Kodda qayerda |
|---|---|---|
| 2026-09-20 | **Eski worktree stale-reap** (HITL). Agent o'z `wt/<tool>/` dagi toza, ochiq PR yo'q, yangi manifestsiz daraxtni o'chiradi. `wt/deploy` / `cp/rankwant` / boshqa tool taqiqlanadi | `tools/reap_stale_worktrees.py`; `tools/check_decisions.py` → `aop_stale_worktree_reap`; salbiy testlar 2 ta |
