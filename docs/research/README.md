# Tadqiqot yozuvlari

Sanali sessiya yozuvlari: qaror sessiyalari, dizayn variantlari, raqobatchi va
platforma auditlari. Bular **tirik hujjat emas** — yozilgan kunidagi holat.
Amaldagi qoidalar `docs/01`–`docs/10` bo'limlarida va [ADR](../07-adr/) larda;
bu yerdagi matn ular bilan zid kelsa, o'sha bo'limlar ustun.

2026-09-17 gacha bu hujjatlar repo'dan tashqarida, `C:\Users\nsn\project\cp\<papka>`
da turardi, kod va `docs/08-technical-spec` esa ularga havola qilardi — ya'ni
qarorlarning manbai versiyalanmagan edi. Endi `.md` hujjatlar shu yerda.
Skrinshotlar, HTML hisobotlar, xom JSON/CSV va bir martalik skriptlar repo'dan
tashqarida, `cp/research/<sana>-<nom>/` da qoladi.

Istisno — kod havola qiladigan ikki fayl:
`2026-09-13-rankwant-updates-design/backfill/` dagi `backfill.py` va
`updates.json` (`load_updates`, `tools/sync_updates.py`).

Yozuvlar ichidagi `rankwant-review/…` kabi yo'llar **eski** joyni bildiradi:
o'sha `.md` endi shu papkada `<sana>-<nom>/` ostida, boshqa turdagi fayl esa
`cp/research/<sana>-<nom>/` da. Matn ataylab qayta yozilmagan.

`tools/check_docs.py` bu papkada faqat **havolalarni** tekshiradi. Yozuvlarda
ataylab qoldirilgan narsalar bor — salbiy test misollari, i18n namunalaridagi
kirill matn, yozilganicha qolgan jadvallar.

| Sana | Yozuv | Mavzu | Kim havola qiladi |
|---|---|---|---|
| 2026-09-13 | [auth-analysis](2026-09-13-auth-analysis/HITL_QARORLAR.md) | Login/Register qaror sessiyasi (HITL) | — |
| 2026-09-13 | clist-analysis — faqat `cp/research/` | CLIST.by `/resources/` sahifa tahlili (HTML hisobot) | — |
| 2026-09-13 | [kep-channel-audit](2026-09-13-kep-channel-audit/KEP-HISTORY.md) | KEP.uz Telegram kanali auditi | — |
| 2026-09-13 | kep-updates-analysis — faqat `cp/research/` | kep.uz/updates tahlili (HTML hisobot) | — |
| 2026-09-13 | [rankwant-review](2026-09-13-rankwant-review/STAGE-REVIEW.md) | Bosqichma-bosqich ko'rik, 09-15 qarorlari, CI Windows tahlili, yo'llarni inglizchaga o'tkazish rejasi | `tools/setup_runner.sh` |
| 2026-09-13 | [rankwant-updates-design](2026-09-13-rankwant-updates-design/DECISION-SESSION.md) | Updates moduli: 20 qaror, 5 dizayn varianti, backfill | `apps/api/updates`, `apps/api/roadmap`, `tools/sync_updates.py` |
| 2026-09-13 | [robocontest-audit](2026-09-13-robocontest-audit/ROBOCONTEST-HISTORY.md) | RoboContest.UZ Telegram kanali auditi | — |
| 2026-09-14 | [rankwant-theme-customizer-design](2026-09-14-rankwant-theme-customizer-design/DECISION-SESSION.md) | Tema sozlagichi qarorlari (D1–D47), i18n steki tahlili | `docs/08-technical-spec/theme-customizer.md` |
| 2026-09-15 | [appearance-comparison](2026-09-15-appearance-comparison/REPORT.md) | Appearance: RankWant va kep.uz, ikonka inventarizatsiyasi | `tools/icon-keys.mjs`, `tools/gen-catalogue.mjs` |
| 2026-09-15 | [icon-comparison](2026-09-15-icon-comparison/DECISIONS-20.md) | Ikonka tizimi: 20 qaror, kutubxonalar, katalog (V3, generatsiya qilinadi) | `tools/gen-catalogue.mjs` |
| 2026-09-15 | [kep-customize-audit](2026-09-15-kep-customize-audit/REPORT.md) | kep.uz CUSTOMIZE paneli auditi | — |
| 2026-09-15 | [nav-typography-implementation](2026-09-15-nav-typography-implementation/REPORT.md) | Navigatsiya va erkin tipografiya — bajarilgan ish | — |
| 2026-09-15 | [self-hosted-runner-guide](2026-09-15-self-hosted-runner-guide/self-hosted-runner-guide.md) | GitHub Actions self-hosted runner qo'llanmasi | — |
| 2026-09-17 | [cloudflare-free](2026-09-17-cloudflare-free/REPORT.md) | Cloudflare Free rejasi: RankWant uchun foydali imkoniyatlar va cheklovlar, faktlar tekshirilgan | ADR-0023 (WAF qoidasi) |
| 2026-09-17 | [github-free](2026-09-17-github-free/REPORT.md) | GitHub Free + private repo: imkoniyatlar, cheklovlar, Actions daqiqalari | `docs/10-operations` |
| 2026-09-17 | [homepage-load](2026-09-17-homepage-load/REPORT.md) | Bosh sahifa SSR: 20/50/100 VU local k6, prefetch, 1000 tashrif hukmi | `tests/load/README.md` |
| 2026-09-18 | [appearance-audit](2026-09-18-appearance-audit/BOARD.md) | Appearance (customizer + `/settings/korinish`) auditi: 9 chipta, ikkita ildiz — `parseColor` va `prefs` sxemasi | `apps/api/core/prefs.py`, `apps/web/src/lib/theme/color.ts` |
| 2026-09-18 | [homepage-profile](2026-09-18-homepage-profile/REPORT.md) | Bosh sahifa profili: render CPU 12–17 ms, lug'at HTML'ning yarmi (A/B: CPU −32%), chrome prefetch'i tashrifga ~130–150 ms | `apps/web/src/components/ui/IntentLink.tsx`, CLAUDE.md qarorlar jadvali |
| 2026-09-18 | [user-model-benchmark](2026-09-18-user-model-benchmark/REPORT.md) | User modeli Codeforces, Robocontest va KEP bilan: 77 atribut, raqobatchilardagi 74 tadan 57 tasi bizda bor; taklif — 8 ta yangi ustun (46 → 54), 3 ta o'zgarish, 7 ta funksiyaga bog'liq band | — |
| 2026-09-18 | [problems-archive-adopt](2026-09-18-problems-archive-adopt/REPORT.md) | `/problems` arxivi: CF range+exclude, KEP ikki qatlam/like/muallif, sidebar mashhur+teg buluti | `apps/web/src/app/problems/page.tsx` |
| 2026-09-18 | [ci-hosted-public](2026-09-18-ci-hosted-public/REPORT.md) | Public repo standard Actions ni $0 qiladi, 4 vCPU; larger runner pullik; keyin HITL — CI `ubuntu-latest` | `ci.yml` → `ubuntu-latest` |
| 2026-09-19 | [login-load](2026-09-19-login-load/REPORT.md) | `/login?tab=login` origin: 20/50/100 VU + 100/200/300 spike, 100k ekstrapolatsiya | — |
| 2026-09-19 | [register-load](2026-09-19-register-load/REPORT.md) | `/login?tab=register` tab HTML: login bilan bir xil shift (~190/s), POST o‘lchanmadi | — |
| 2026-09-19 | [scale-50k](2026-09-19-scale-50k/RECOMMENDATIONS.md) · [implementatsiya](2026-09-19-scale-50k/IMPLEMENTATION.md) | 50k: 7 qaror + modul kod + o‘lchov (baseline 09-17/19) | `home-cache.ts`, `SloView`, `docker-compose.replicas.yml` |
| 2026-09-20 | [as-built-architecture](2026-09-20-as-built-architecture/README.md) · [modullar](2026-09-20-as-built-architecture/MODULES.md) · [oqimlar](2026-09-20-as-built-architecture/FLOWS.md) · [diagrammalar](2026-09-20-as-built-architecture/DIAGRAMS.md) | Joriy kod arxitekturasi: 5 qatlam, 19 Django app, submit/reyting/contest oqimlari. `docs/06` locked — bu yozuv data-flow boʻshligʻini toʻldiradi | `apps/api`, `apps/web`, `services/judge-go`, `docker-compose.yml` |
| 2026-09-20 | [architecture-diagrams](2026-09-20-architecture-diagrams/README.md) | As-built arxitektura diagrammalari — 5 ta mustaqil SVG (qatlamlar, modul xaritasi, submit→reyting, judge pull protokoli, deploy topologiya). Matn `as-built-architecture` yozuvida, bu yerda takrorlanmaydi | — |
| 2026-09-20 | [deploy-timing](2026-09-20-deploy-timing/README.md) · [metrikalar](2026-09-20-deploy-timing/METRICS.md) | Deploy E2E o'lchovi: TIMER wall-clock, issiq/sovuq `--no-cache`, taqiqlangan `rmi -f` / volume prune | `tools/deploy.sh`, `tools/measure_deploy.sh` |
| 2026-09-20 | [ship-timing](2026-09-20-ship-timing/README.md) · [topilmalar](2026-09-20-ship-timing/FINDINGS.md) | Commit/PR/push/merge/CI/deploy wall-clock: lokal ~14 s, CI 18–140 s, avto-deploy kutish ~5 min, bake 2.6–16 min | `ci.yml`, `auto_deploy.sh`, `deploy.sh` |
| 2026-09-21 | [security-boundary](2026-09-21-security-boundary/README.md) | Chegara o'lchandi: nashr etilgan 2 port, ikkisi ham loopback; judge port ham, DB credential ham e'lon qilmaydi. Divergensiyalar: `adminer` compose zanjiridan tashqarida, `tests/security` statik yarmi avtomatik yurmaydi (threat model o'sha kuni yozildi — `docs/10-operations/threat-model.md`) | `CLAUDE.md` |
| 2026-09-21 | [licence-inventory](2026-09-21-licence-inventory/README.md) · [paketlar](2026-09-21-licence-inventory/packages.tsv) | Litsenziya inventari (`09:81` launch gate): **848 paket** 6 manbadan, oflayn aniqlangan. **50 weak copyleft** (`@img/sharp-libvips-*` — LGPL-3.0, Next.js rasm optimizatori), **0 strong**, 3 ko'rib chiqish kerak (`python-dateutil` «Dual License», `caniuse-lite` `CC-BY-4.0`), **21 UNKNOWN** (hammasi Go — bu mashinada modul keshi ham, `go` ham yo'q). Huquqiy xulosa emas — advokatning kirishi | `tools/licence_inventory.py`, `CLAUDE.md` |
| 2026-09-21 | [judge-latency](2026-09-21-judge-latency/README.md) | Judge latency launch gate (`09` § Launch gate — agent yopa oladigan **yagona** band): job bor edi, lekin **hech qachon ishlamagan** va raqamni faqat logga yozardi ⇒ gate yashil job'da ham ochiq qolardi. Endi harness `LATENCY_JSON:` satri chiqaradi, `tools/latency_summary.py` uni run sahifasiga yozadi. Passiv o'lchov **yo'q** (o'lchandi: `judging_attempt` = 1 qator). CI raqami — regressiya bazasi, gate raqami emas | `tools/latency_summary.py`, `nightly.yml`, `CLAUDE.md` |
