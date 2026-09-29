# QA Verification — Batch 2 (WP4 · D1 · F1) — adversarial

**Sana:** 2026-09-29 · **Tekshiruvchi:** Edward (QA Engineer, software-qa-engineer-2)
**Repo:** rankwant · **HEAD:** `462e327` (yangi commit yo'q) · **Usul:** mustaqil, adversarial — Engineer o'z ishini o'zi tasdiqlagan, bu yerda har bir da'vo alohida o'lchandi. Rubber-stamp qilinmadi.

> ⚠️ Muhit cheklovi: repo `.venv` buzuq (WSL'da yaratilgan; `.venv/bin/python` **0 bayt**). Shuning uchun Engineer qo'shgan pytest fayllarini yurgizib bo'lmadi. `config.settings` guard'i **stub-django** harness'da haqiqiy fayl ustida o'lchandi (pastda). Bu — mustaqil dalil, lekin "pytest orqali tasdiqlandi" **emas**.

---

## 1. Da'volar jadvali

| # | Da'vo | Buyruq | Kutilgan | Haqiqiy | Hukm |
|---|---|---|---|---|---|
| WP4① | compose'da dev sir yo'q | `grep -rn "PASSWORD: dev"` + `grep -rn "devdevdev"` (`docker-compose*.yml`, `.env.example`) | 0 natija | 0 natija (exit 1) | **PASS** |
| WP4②a | security.yml qayta yoqilgan | `git diff .github/workflows/security.yml` | `if: false` yo'q; `push`+`schedule`; `pull_request` yo'q | aynan shunday | **PASS** |
| WP4②b | gitleaks yashil | `docker run ... gitleaks detect` (895 commit) | exit 0, sir yo'q | `895 commits scanned`, `no leaks found`, exit 0 | **PASS** (mustaqil) |
| WP4②c | pip-audit yashil | `pip-audit -r apps/api/requirements.lock` | zaiflik yo'q | `No known vulnerabilities found`, exit 0 | **PASS** (mustaqil) |
| WP4②d | npm audit yashil | `npx npm@11 audit --audit-level=high` | 0 high | `found 0 vulnerabilities`, exit 0 | **PASS** (mustaqil) |
| WP4③ | compose majburiy env | `docker compose -p rankwant-qa-probe -f docker-compose.yml config` | env'siz exit 1; env bilan exit 0 | env'siz exit 1 (`required variable ... D5-majburiy`); dummy env bilan exit 0 | **PASS** |
| WP4④ | SECRET_KEY fail-fast | real `settings.py` ni stub-django bilan yuklash | yo'q/bo'sh → `ImproperlyConfigured` | yo'q → RAISED; bo'sh → RAISED; berilgan → LOADED_OK | **PASS** (stub harness) |
| WP4⑤ | rotation hali yo'q | `git diff` sir qiymatlari | yangi sir qiymati yo'q | faqat `dev`/`devdevdev` **olib tashlangan** → `${VAR:?}`; yangi qiymat yo'q | **PASS** |
| DEC | ag'darilgan qoida tirik | `if: false` qaytarib `check_decisions.py` | exit 1 | exit 1 (to'g'ri xabar); asl holatga qaytarilgach exit 0 | **PASS** |
| DEC-neg | qoidaning salbiy testi bor | `grep neg_decisions_security` | mavjud + ro'yxatga ulangan | 4 ta (`run_disabled` 6613-qatorda ulangan) | **PASS** |
| DEC | qarorlar gate | `python tools/check_decisions.py` | exit 0 | `59 ta qaror kodda amalda`, exit 0 | **PASS** |
| D1 | 18 ADR | `ls docs/07-adr/00{28..45}-*.md` | 18 | 18 | **PASS** |
| D1 | H1 inglizcha, bo'limlar o'zbekcha | `head -1` + `grep "^## "` | H1 EN; 8 bo'lim UZ | 18×EN H1; 18×8 UZ bo'lim | **PASS** |
| D1 | kirill yo'q | `grep -P "[0400-04FF]"` | 0 | 0 (0028–0045) | **PASS** |
| D1 | indeks to'liq | README `0001..0045` | 45 qator + 0027 | 0001–0045 hammasi, 0027 bor | **PASS** |
| D1 | mazmun sodiqligi | 0037 / 0044 / 0028 o'qish | D8-F · D5 · D3+D10 | mos | **PASS** |
| D1 | docs gate | `python tools/check_docs.py` | exit 0 | `Muammo topilmadi`, exit 0 | **PASS** |
| F1 | AI chegara teshigi yopilgan | mutatsiya: `from problems import models` / `from . import models` | exit 1 | exit 1 (ikkisi ham tutildi) | **PASS** |
| F1 | salbiy testlar | `python tools/check_negative.py neg_ai_boundary` | 5/5 | `5/5`, exit 0 | **PASS** |
| REG | to'liq salbiy to'plam | `python tools/check_negative.py` | faqat litsenziya red | `1/338 YIQILDI` = litsenziya/nazorat | **PASS** |
| REG | chegara gate | `python tools/check_security_boundary.py` | exit 0 | exit 0 | **PASS** |
| REG | env namunasi | `python tools/check_env_example.py` | exit 0 | `74 o'zgaruvchi`, exit 0 | **PASS** |

---

## 2. To'liq o'zgarishlar auditi (fayl → WP/qaror)

**Tracked (19 fayl, +741 / −54):**

| Fayl | Tegishli WP/qaror |
|---|---|
| `.env.example` | WP4 · D5 (majburiy sirlar hujjatlashtirildi) |
| `.github/workflows/security.yml` | WP4 · D5 (qayta yoqildi) |
| `.github/workflows/ci.yml` | WP4 · D5 (`DJANGO_SECRET_KEY`) **+ WP5/WP6** (ai/arch gate qadamlari) |
| `.github/workflows/deploy.yml` | WP4 · D5 (sirlar + preflight) |
| `.github/workflows/nightly.yml` | WP4 · D5 (sirlar) **+ #18** (21→25 izoh) |
| `CLAUDE.md` | WP4 · D5 (qaror jurnali qatori + `pytest` buyrug'i) |
| `apps/api/Makefile` | WP4 · D5 (`?=` fallback) |
| `apps/api/config/settings.py` | WP4 · D5 (fail-fast) |
| `docker-compose.yml` | WP4 · D5 |
| `docker-compose.public.yml` | WP4 · D5 |
| `tools/check_decisions.py` | WP4 · D5 (qoida ag'darildi) |
| `tools/ci_stack.sh` | WP4 · D5 (CI sirlar) |
| `docs/07-adr/README.md` | D1 (indeks 0028–0045) |
| `services/bakeoff/README.md` | #18 (21→25 case) |
| `docs/research/README.md` | research deliverable (ai-agent-enterprise) |
| `apps/web/package.json` | recharts (boshqa WP — drift) |
| `apps/web/package-lock.json` | recharts (boshqa WP — drift) |
| `apps/web/next-env.d.ts` | **IZOHSIZ** — Next.js dev auto-regen artefakti (F2-1) |

**Untracked:**

| Fayl | Tegishli WP/qaror |
|---|---|
| `docs/07-adr/0028..0045-*.md` (18) | D1 |
| `docs/10-operations/runbooks/secrets-rotation.md` | WP4 · D5 (ADR 0044 havolasi) |
| `tools/check_ai_boundary.py`, `tools/_boundary_apps.py` | WP5 |
| `apps/api/ai/` (README + `__init__`) | WP5 |
| `apps/api/tests/test_ai_boundary.py` | WP5 |
| `tools/check_architecture.py`, `tools/architecture-allowlist.txt` | WP6 |
| `apps/api/tests/test_architecture_boundary.py` | WP6 |
| `apps/api/tests/test_settings_secrets.py` | WP4 |
| `docs/research/2026-09-29-ai-agent-enterprise/` | research deliverable |
| `prototypes/` (recharts contest-analytics) | boshqa WP (recharts) |
| `deliverables/` | jamoa deliverable'lari |
| `.freebuff/` (`project-id`) | **IZOHSIZ** — tool artefakti (F2-2) |

**Scope creep tekshiruvi:**
- `docker-compose.yml` da `privileged: true` (**201-qator**) va `cgroup: host` (**202-qator**) — **hali ham bor** ✓ (WP7 ishi, ataylab tegilmagan).
- `apps/api/ai/` — faqat `README.md` + `__init__.py`; chegaraga taqiqlangan import yo'q. WP5 skeleton, batch2'da o'zgarmagan.
- **Yangi migration yo'q** ✓ (`git status` da `migrations/` da yangi fayl yo'q).
- **Yangi commit yo'q** ✓ (`git log --oneline -1` = `462e327`).
- `apps/api/Makefile`: `export DJANGO_SECRET_KEY ?= local-only-not-for-production` — `?=` (GNU Make documented semantikasi: muhitda berilgan qiymatni **ustidan yozmaydi**). ⚠️ `make` bu mashinada o'rnatilmagan — semantika bo'yicha tasdiq, bajarib emas.

---

## 3. Topilmalar

**🔴 Bloklovchi:** yo'q.

**🟠 O'rta:** yo'q.

**🟡 Past (bloklamaydi, tozalash tavsiya etiladi):**

- **F2-1** — `apps/web/next-env.d.ts` o'zgardi: `./.next/types/` → `./.next/dev/types/`. Bu Next.js dev-server yozadigan **generatsiya fayli** ("should not be edited"); hech bir WP natijasi emas. Commit qilinsa `next build` bilan flip-flop bo'lishi va typecheck drifti mumkin. **Tavsiya:** `git checkout -- apps/web/next-env.d.ts`.
- **F2-2** — `.freebuff/` (untracked, `project-id`) — tool artefakti; hech bir WP emas. **Tavsiya:** gitignore yoki o'chirish (tasodifan commit bo'lmasin).
- **F2-3** — ADR 0028 "Dalil" `docker-compose.yml:192`/`:193` ga havola qiladi, lekin `privileged`/`cgroup: host` aslida **201/202**-qatorda (9 qator siljigan). Hujjat aniqlik xatosi.
- **F2-4** — Hisobot bo'shlig'i: Engineer hisobotida **12+ o'zgargan fayl** aytilmagan (`CLAUDE.md`, `apps/api/Makefile`, `tools/check_decisions.py`, `tools/ci_stack.sh`, `deploy.yml`, `nightly.yml`, `ci.yml`, `.env.example`, `docs/research/README.md`, `services/bakeoff/README.md`, `next-env.d.ts`, `package*.json`). Kod nuqsoni emas — jarayon/shaffoflik nuqsoni.

> Eslatma: `git grep "devdevdev"` repo bo'ylab 3 ta **hujjat** yozuvini topadi (`CLAUDE.md`, `docs/10-operations/threat-model.md`, `docs/research/2026-09-21-security-boundary/`). Bular — tarixiy xavf **A-2** ning yozma qaydi, compose'da emas. WP4① sharti faqat compose + `.env.example` ni qamraydi → buzilish emas.

---

## 4. WP4 · D1 · F1 holati

- **WP4 — PASS.** ①–⑤ hammasi o'lchandi. ② uchun **uchala skaner mustaqil yurgizildi** (gitleaks docker-cached image, pip-audit temp venv, npm audit) — hammasi exit 0. ④ faqat stub-django harness bilan (pytest imkonsiz: `.venv` buzuq) — bu cheklov ochiq qayd etildi.
- **D1 — PASS.** 18 fayl, H1 inglizcha, bo'limlar o'zbekcha, kirill yo'q, indeks to'liq, mazmun sodiq (D8-F · D5 · D3+D10), `check_docs.py` exit 0.
- **F1 — PASS.** Mutatsiya bilan tasdiqlandi: `from problems import models` va `from . import models` ikkisi ham ushlanadi; `neg_ai_boundary` 5/5.
- **check_decisions ag'darilgan qoida — PASS.** `if: false` qaytarilganda gate yiqiladi (o'lik emas); salbiy testi mavjud va ulangan.

---

## 5. Routing qarori

**NoOne** — WP4 · D1 · F1 ning barcha da'volari mustaqil dalil bilan **PASS**; birorta gate manba kodi nuqsoni tufayli yiqilmadi. To'liq regressiyada yagona qizil — `litsenziya/nazorat` (recharts drifti), sessiya boshidan mavjud, **boshqa WP**.

**Ixtiyoriy (bloklamaydi):** F2-1, F2-2, F2-3 ni Engineer tozalashi mumkin (fayl + nima qilish yuqorida aniq).

---

## 6. Vaqtinchalik o'zgarish qolmadi

Vaqtinchalik mutatsiyalar (security.yml `if: false`; `apps/api/ai/_qa_probe.py`) **bayt-aniq** qaytarildi:
- `security.yml` md5 mutatsiyadan oldin = keyin = `e64897ffd7b66f089b39f3864c3c6bfe`.
- `_qa_probe.py` o'chirildi; `apps/api/ai/` da faqat `README.md` + `__init__.py`.
- `git diff --stat` mutatsiyadan keyin ham **19 fayl, +741 / −54** (boshidan aynan bir xil); `git status` ham bir xil.

---

**STATUS:** QA batch2 — **PASS** (WP4 · D1 · F1) · Routing: **NoOne** · 0 bloklovchi · 4 ta 🟡 (tozalash tavsiyasi) · vaqtinchalik o'zgarish qolmadi.
