# tests/security

Sandbox escape harness + ilova darajasi (IDOR, PAT scope, rate-limit)

To'liq strategiya: [docs/10-operations/test-strategy.md](../../docs/10-operations/test-strategy.md)

## Qayerda yuriydi

| Bo'lim | Nima tekshiradi | Qayerda yuriydi |
| --- | --- | --- |
| 1–2 (statik) | judge host qoidalari, IDOR, PAT hash, rate limit | **Nightly** `security` job'i — `SECURITY_STATIC_ONLY=1` bilan |
| 3 (dinamik) | izolyatsiya case'lari, haqiqiy nsjail | **Nightly** `e2e` job'i — bake-off qadami, ayni `runner.py` |

⚠️ `.github/workflows/security.yml` bu to'plamni chaqiradi, lekin u
**o'chirilgan** (`workflow_dispatch` + `if: false`, egasi qarori 2026-09-21).
Ya'ni skript PR darajasida ishlamaydi — faylning o'zida ilgari shunday deb
yozilgan edi va bu endi to'g'ri emas.

3-bo'limni lokal yuritish uchun `REDIS_URL` va ishlaydigan judge worker kerak
— `SECURITY_STATIC_ONLY` ni o'rnatmang.

1-bo'lim `yaml` talab qiladi (`check_compose.py`). Nightly job'i `pyyaml`
o'rnatadi; lokal mashinada u allaqachon bor.

Nega statik rejim: [docs/research/2026-09-21-security-suite/](../../docs/research/2026-09-21-security-suite/README.md)
