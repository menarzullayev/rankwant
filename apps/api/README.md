# apps/api — Django 5.2 LTS + DRF

Sprint 1 da to'ldiriladi ([09-development-plan](../../docs/09-development-plan/README.md)).

Spec: [08-technical-spec](../../docs/08-technical-spec/README.md) · Model: [05-domain-model](../../docs/05-domain-model/README.md)

## Mas'uliyat

- REST API `/api/v1/` + OpenAPI (`drf-spectacular`)
- Django admin — masala/contest/test boshqaruvi (PRD P0-2)
- Celery task'lar: rejudge, standings, 4 reyting hisoblash
- Auth: session (web) + PAT (API) — [ADR-0008](../../docs/07-adr/0008-auth-session-plus-pat.md)

## Qoidalar

- `mypy` strict · biznes logika **service layer'da**, view'da emas
- Foydalanuvchi kodi **hech qachon** bu yerda ishlamaydi — faqat judge hostda
