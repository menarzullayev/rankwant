| Sana | Qaror | Kodda qayerda |
|---|---|---|
| 2026-09-21 | **Security run o'chiq**. `security.yml` avtomatik push/cron yo'q, `audit` `if: false`. Deploy darvozasi faqat `CI`. Fayl qoladi — qayta yoqish qo'lda | `security.yml`; `check_deploy_gate.py` `REQUIRED`; `tools/check_decisions.py` → `security_run_is_disabled`; salbiy testlar 2 ta |
