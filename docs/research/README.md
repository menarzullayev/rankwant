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
