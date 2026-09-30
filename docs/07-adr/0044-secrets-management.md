# ADR 0044 — Secrets management

**STATUS:** accepted
**Sana:** 2026-09-29
**Tasdiqlagan:** Saidakbar (owner)
**Manba:** D5 (ADR 0044 secrets) · `owner-decision-closure-matrix-2026-09-29.md`
**Ta'sir doirasi:** Phase 0
**Dalil:** `docker-compose.yml` (`POSTGRES_PASSWORD: dev`) · `docker-compose.yml` (`MINIO_ROOT_PASSWORD: devdevdev` · `S3_SECRET: devdevdev`) · `apps/api/config/settings.py` (`SECRET_KEY` fallback `dev-only-not-for-production`) · `.github/workflows/security.yml` (`if: false`)

## 1. Muammo

Dev-default sirlar compose'da **hardcode**: DB paroli `dev`, MinIO/S3 siri `devdevdev`. `docker-compose.public.yml` bu qiymatlarni **override qilmaydi**, ya'ni production'da ham hardcode amal qiladi. `config/settings.py` da `SECRET_KEY` fallback `dev-only-not-for-production` — ommaviy repo'da ma'lum kalit; sessiya/CSRF/PAT forge → superuser egallash. `.github/workflows/security.yml` da `if: false` — gitleaks/pip-audit/npm audit CI'da **umuman ishlamaydi**.

## 2. Variantlar

1. Env fayl.
2. Docker secret.
3. Vault.
4. Env + majburiy env + fail-fast.

## 3. Tanlov

**Variant 4** (D5) — **env + majburiy env (`${VAR:?}`) + fail-fast**. Docker secret va Vault **rad etildi**. Sir **aylantirish (rotation) wiring va fail-fast dan KEYIN** bajariladi — tartib qulflangan.

## 4. Sabab

Docker secret va Vault ops murakkabligi qo'shadi; Phase 0 uchun env + majburiy env yetarli. Fail-fast dev-default bilan prod build'ni **yiqitadi** — shunda default sir production'ga chiqmaydi. Rotation faqat wiring va fail-fast o'rnatilgandan keyin ma'noga ega (aks holda eski sir hali ham ishlatiladi).

## 5. Oqibatlar

- `docker-compose.yml` va `docker-compose.public.yml` sirlari env'ga o'tadi (`${VAR:?}`).
- `config/settings.py` da `SECRET_KEY` fallback olib tashlanadi → `ImproperlyConfigured`.
- `.github/workflows/security.yml` `if: false` olib tashlanadi (gitleaks/pip-audit/npm audit yashil).
- Sir aylantirish wiring va fail-fast dan **keyin**.

## 6. Qaytarilishi

`docker-compose.public.yml` ni o'zgartirish prod stack'ni buzishi mumkin. Rollback = env qiymatini `.env.public` ga qo'yish. Rotation tartibi qulflangan.

## 7. Tasdiq

- `grep "PASSWORD: dev"` va `grep "devdevdev"` → **0 natija**.
- `security.yml` `if: false` olib tashlangan va CI **yashil**.
- Default sir bilan prod build **yiqiladi** (exit ≠ 0).
- `SECRET_KEY` fallback → **`ImproperlyConfigured`**.
- Rotation **keyin** bajariladi (tartib qulflangan).

## 8. Bog'liq hujjatlar

- D5 — `owner-decision-closure-matrix-2026-09-29.md`
- `acceptance-criteria-lock-2026-09-29.md` — WP4 bloki
- Blueprint §21 (ADR 0044) · §24 (Phase 0 done-condition ④)
- `docs/10-operations/runbooks/secrets-rotation.md`
- ADR 0043 (backup / PITR / DR)

**STATUS:** ADR 0044 — accepted. Phase 0. **implementatsiya holati: WP4 (davom etmoqda).**
