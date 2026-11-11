# RankWant — agent uchun kirish nuqtasi

Loyiha hujjatlangan: `docs/` da 10 bo'lim, `docs/07-adr/` da har qaror alohida ADR.
**Bu fayl ularni takrorlamaydi** — bu yerda faqat kod yozayotganda darhol
kerak bo'ladigan buyruqlar va ilgari vaqt yegan tuzoqlar.

## Qayerga qarash kerak

| Savol | Hujjat |
| ----- | ------ |
| Entity, maydon, o'chirish qoidalari | `docs/05-domain-model/` (locked) |
| Nega shunday qilingan | `docs/07-adr/` — har qaror alohida ADR |
| Deploy, incident, backup, monitoring | `docs/10-operations/` |
| Verdikt kodlari, sahifalash, xato formati | `docs/08-technical-spec/` |
| Judge shartnomasi va bake-off | `services/bakeoff/protocol.md` |
| Saidakbar aka qarorlari — to'liq matn va o'lchovlar | `docs/decisions/` (indeks pastda) |

Pul mantiqi bo'yicha bitta qoida hammasidan muhim (ADR-0002):
**balans hech qachon to'g'ridan-to'g'ri yozilmaydi, faqat ledger orqali.**
`qvant_audit` buni butun baza bo'yicha tekshiradi.

## Saidakbar aka qarorlari

Bu qarorlarni **agent o'zi bekor qilmaydi** — «yaxshilash» deb ham.
O'zgartirish kerak bo'lsa, avval Saidakbar akadan aniq tasdiq olinadi va
qaror fayli shu PR'da yangilanadi. `tools/check_decisions.py` har PR'da
qarorlarni kodda tekshiradi. Sabab (2026-09-17): «faqat lokal zaxira» qarori
qabul qilingan kuniyoq boshqa agent R2 ga shifrsiz offsite qo'shdi (#31) va
foydalanuvchi ma'lumoti bor dump'lar tashqariga chiqdi.

Har qarorning to'liq matni — o'lchovlar, sabab, fayllar — `docs/decisions/`
da alohida faylda; bu yerda faqat bir qatorli indeks. Biror sohaga
tegishdan oldin indeksdan o'sha sohaning qatorlarini toping va fayllarini
o'qing: qisqa nom qarorning hammasini aytmaydi.

**Yangi qaror shunday yoziladi** (2026-11-10, audit Q-10) — bu yerga jadval
qatori emas:

1. `docs/decisions/YYYY-MM-DD-<slug>.md` — yangi fayl:
   `| Sana | Qaror | Kodda qayerda |` sarlavhasi va **bitta** qator (istalgan
   qo'shni fayl namuna). Qatordagi sana fayl nomidagi sana bilan boshlanadi.
2. Pastdagi indeksga, sana tartibida, qo'shni qatorlar shaklida bitta qator:
   faylga havola bo'lgan sana · qaror bir necha so'zda · `qoida`. Oxirgi
   maydon — `tools/check_decisions.py` dagi qoida funksiyasi yoki qaror
   yashaydigan fayl.
3. Mavjud qarorni o'zgartirish — faqat Saidakbar akaning tasdig'i bilan:
   o'sha fayl tahrirlanadi yoki yangi fayl eskisini «almashtiradi» deb yozadi.

`check_decisions.py` → `decisions_index_matches_files` indeksni fayllar bilan
solishtiradi: faqat bir joyda turgan qaror, yo'q qoida nomi, buzilgan sana
tartibi yoki bu faylga qaytgan jadval qatori CI'ni qizartiradi.

**Customization contract invariantlari** (2026-09-24 qarori: agentlar ularni
shu yerdan o'qiydi; manba — `docs/08-technical-spec/customization-contract.md` §7):

- «An agent MUST NOT introduce a new customization setting without updating this contract AND the gate that checks it»
- «MUST NOT add a key to the client that the server's `APPEARANCE_KEYS` does not accept — the whole `appearance` write fails, not just that key»
- «MUST NOT change the precedence of an existing setting without a decision record»
- «MUST NOT introduce a second persistence mechanism, a second apply path, or a second PATCH for preferences»
- «MUST NOT bypass customization validation»
- «Unknown values MUST have an explicit fallback, and an unknown schema version MUST be preserved rather than dropped»

### Indeks

- [2026-09-16](docs/decisions/2026-09-16-manual-deploy-builds-everything.md) · Deploy `tools/deploy.sh` bilan; bitta deploy hamma servisni quradi · `deploy_manual_only`
- [2026-09-17](docs/decisions/2026-09-17-local-only-backups.md) · Zaxira 30 kunda bir marta, faqat lokal; offsite yo'q · `backup_local_only`
- [2026-09-17](docs/decisions/2026-09-17-main-only-via-pr.md) · `main` ga faqat PR orqali; soxta muallif push qilinmaydi · `main_only_via_pr`
- [2026-09-17](docs/decisions/2026-09-17-ci-runner-in-container.md) · CI runner — Docker Desktop'dagi `rankwant-ci-runner` konteyneri · `container_runner_takes_ci`
- [2026-09-17](docs/decisions/2026-09-17-agents-deploy-on-green-main.md) · Agentlar `main` CI yashil bo'lsa so'ramasdan deploy qiladi; bir vaqtda bitta · `deploy_gated_on_green_main`
- [2026-09-17](docs/decisions/2026-09-17-mixed-language-repo.md) · Repo aralash tilda, migratsiya yo'q · `language_rule_written`
- [2026-09-17](docs/decisions/2026-09-17-cp-only-for-rankwant.md) · `cp/` faqat RankWant uchun; tadqiqot `docs/research/` da · `docs/research/README.md`
- [2026-09-18](docs/decisions/2026-09-18-ci-on-hosted-runners.md) · CI, Security, Nightly — `ubuntu-latest`; deploy self-hosted · `ci_test_on_hosted`
- [2026-09-18](docs/decisions/2026-09-18-second-ci-runner.md) · Ikkinchi runner, alohida volume; PR'da Security yo'q · `pr_skips_heavy_ci`
- [2026-09-18](docs/decisions/2026-09-18-indexing-open-ai-crawlers-closed.md) · Qidiruv tizimlariga ochiq, AI kraulerlarga yopiq (ADR-0023) · `search_open_ai_crawlers_blocked`
- [2026-09-18](docs/decisions/2026-09-18-nav-prefetch-on-intent.md) · Navigatsiya havolalari faqat niyatda prefetch qiladi · `nav_prefetch_on_intent`
- [2026-09-18](docs/decisions/2026-09-18-home-main-prefetch-on-intent.md) · Bosh sahifa `<main>` havolalari ham faqat niyatda prefetch qiladi · `home_main_prefetch_on_intent`
- [2026-09-18](docs/decisions/2026-09-18-dictionary-as-cached-file.md) · Lug'at alohida `immutable` faylda (`/i18n/<til>.js`) · `dictionary_as_cached_file`
- [2026-09-18](docs/decisions/2026-09-18-user-parity-fields.md) · `User` ga 21 tenglik maydoni; «ishlatilmaydi» deb olib tashlanmaydi (ADR-0024) · `user_parity_fields_kept`
- [2026-09-18](docs/decisions/2026-09-18-header-fits-320px.md) · Header 320 px ga sig'adi; til tanlagich endonimi `max-w-[3rem]` bilan · `mobile_header_fits_narrow_screen`
- [2026-09-18](docs/decisions/2026-09-18-mobile-drawer-accessible.md) · Mobil panel e'lon qilinadi, fokuslanadi, `Esc` bilan yopiladi · `mobile_drawer_is_accessible`
- [2026-09-18](docs/decisions/2026-09-18-home-kpi-four-up-at-lg.md) · Bosh sahifa KPI to'ri `lg` da 4 ustun, raqam 24 px · `kpi_grid_steps_at_lg`
- [2026-09-18](docs/decisions/2026-09-18-profile-kpi-four-up-at-xl.md) · Profil KPI to'ri `xl` da 4 ustun (2026-09-19 da almashtirildi) · `profile_sidebar_stacks_below_xl`
- [2026-09-18](docs/decisions/2026-09-18-difficulty-range-one-filter.md) · Qiyinlik diapazoni filtr rozetkasida bitta filtr · `difficulty_range_counts_as_one_filter`
- [2026-09-19](docs/decisions/2026-09-19-profile-stacks-below-xl.md) · Profil sahifasi `xl` gacha bir ustun; KPI `lg` dan 4 ustun · `profile_sidebar_stacks_below_xl`
- [2026-09-19](docs/decisions/2026-09-19-brand-in-header-footer-columns.md) · Brend header'da, footer uch ustun (footer 2026-10-06 da almashtirildi) · `brand_in_header_and_footer_columns`
- [2026-09-19](docs/decisions/2026-09-19-content-name-coverage-visible.md) · Kontent nomlarining `uz` zaxirasi belgisi bitta joyda (`ContentName`) · `content_coverage_visible`
- [2026-09-19](docs/decisions/2026-09-19-dictionary-survives-return.md) · Tilga qaytilganda lug'at yo'qolmaydi (`keepOnly`) · `dictionary_survives_return`
- [2026-09-19](docs/decisions/2026-09-19-homepage-guest-cdn-cache.md) · Bosh sahifa mehmon uchun CDN keshda; kirgan — `no-store` · `homepage_guest_cdn_cache`
- [2026-09-19](docs/decisions/2026-09-19-scale-50k.md) · 50k masshtab: modular monolit, replica, Redis, CDN, Celery · `scale_50k_locked`
- [2026-09-19](docs/decisions/2026-09-19-staff-groups-and-authors.md) · Rollar — staff Groups + obyekt mualliflari (ADR-0025) · `roles_groups_and_object_authors`
- [2026-09-19](docs/decisions/2026-09-19-locale-in-the-url.md) · Til havolada (`?lang=`): havola → cookie → `Accept-Language` → `uz` · `locale_travels_in_the_url`
- [2026-09-19](docs/decisions/2026-09-19-fully-automatic-deploy.md) · Deploy to'liq avtomatik — host watcher, GitHub Actions emas · `deploy_automation_is_safe`
- [2026-09-19](docs/decisions/2026-09-19-auto-deploy-first-run-fixes.md) · Avtomatik deploy: qulf topshiriladi, stdin `/dev/null` dan · `deploy_automation_is_safe`
- [2026-09-20](docs/decisions/2026-09-20-heavy-ci-only-in-nightly.md) · Og'ir stack faqat Nightly; PR'da tez CI · `pr_skips_heavy_ci`
- [2026-09-20](docs/decisions/2026-09-20-deploy-inventory-c-sort.md) · `check_deploy.sh` inventory `LC_ALL=C sort` bilan · `deploy_automation_is_safe`
- [2026-09-20](docs/decisions/2026-09-20-typescript-seven-side-by-side.md) · TypeScript 7 yonma-yon; yagona paket qilinmaydi · `typescript_side_by_side`
- [2026-09-20](docs/decisions/2026-09-20-types-node-tracks-runtime.md) · `@types/node` major = Node major (22) · `types_node_tracks_runtime`
- [2026-09-20](docs/decisions/2026-09-20-selected-kit-frozen.md) · Tanlangan kit muzlatilgan (nusxalash qismi 2026-10-27 da almashtirildi) · `selected_kit_frozen`
- [2026-09-20](docs/decisions/2026-09-20-eslint-ten.md) · ESLint 10, parser `typescript-eslint` · `eslint_ten_uses_ts_parser`
- [2026-09-20](docs/decisions/2026-09-20-pytest-nine.md) · pytest 9 + pytest-django 4.14 birga · `pytest_nine_and_django_plugin`
- [2026-09-20](docs/decisions/2026-09-20-react-and-dom-paired.md) · react = react-dom = 19.3 · `react_and_dom_stay_paired`
- [2026-09-20](docs/decisions/2026-09-20-lang-query-self-canonical.md) · `?lang=` self-canonical + hreflang · `lang_query_self_canonical`
- [2026-09-20](docs/decisions/2026-09-20-sitemap-hreflang.md) · Sitemap'da `xhtml:link` til muqobillari · `sitemap_locale_xhtml_alternates`
- [2026-09-20](docs/decisions/2026-09-20-vary-accept-language-at-edge.md) · `Vary: Accept-Language` Cloudflare chekkasida · `vary_accept_language_at_edge`
- [2026-09-20](docs/decisions/2026-09-20-problems-guest-cdn.md) · `/problems` mehmon CDN keshida, tilga bog'liq · `problems_list_guest_cdn`
- [2026-09-20](docs/decisions/2026-09-20-users-noindex.md) · `/users/` noindex qoladi · `users_profiles_stay_noindex`
- [2026-09-20](docs/decisions/2026-09-20-rank-colour-groups.md) · Rank ranglari 7 guruh tokeni, 16 emas · `rank_colour_groups_not_sixteen_tokens`
- [2026-09-20](docs/decisions/2026-09-20-homepage-css-inline.md) · Bosh sahifa CSS inline (`inlineCss`) · `homepage_css_is_inlined`
- [2026-09-20](docs/decisions/2026-09-20-dictionary-use-unconditional.md) · Lug'at `use()` shartsiz (React #467) · `locale_use_is_unconditional`
- [2026-09-20](docs/decisions/2026-09-20-no-cf-email-decode.md) · Cloudflare `email-decode` skripti yo'q · `homepage_skips_cf_email_decode`
- [2026-09-20](docs/decisions/2026-09-20-owned-paths-no-star-star.md) · `owned_paths` da `**` va bir segmentli katalog globi yo'q · `aop_owned_paths_no_star_star`
- [2026-09-20](docs/decisions/2026-09-20-stale-worktree-reap.md) · Agent o'z eski toza worktree'sini o'chiradi · `aop_stale_worktree_reap`
- [2026-09-20](docs/decisions/2026-09-20-canonical-restore-when-idle.md) · `cp/rankwant` bo'sh paytda `origin/main` ga ff-only · `aop_restore_when_idle`
- [2026-09-20](docs/decisions/2026-09-20-docker-disk-bounded.md) · Docker disk o'smasin: SHA teglar saqlanmaydi, log va GC chegarasi · `docker_disk_stays_bounded`
- [2026-09-20](docs/decisions/2026-09-20-timestamps-from-bases.md) · Vaqt tamg'alari abstrakt bazalardan · `timestamps_come_from_bases`
- [2026-09-21](docs/decisions/2026-09-21-security-run-disabled.md) · `security.yml` o'chiq; deploy darvozasi faqat CI · `security_run_is_disabled`
- [2026-09-21](docs/decisions/2026-09-21-login-narrow-auth-css.md) · `/login` yupqa `auth.css` bilan · `login_uses_narrow_auth_css`
- [2026-09-21](docs/decisions/2026-09-21-judge-latency-nightly-gate.md) · Judge latency darvozasi — doimiy Nightly job · `judge_latency_gate_is_nightly`
- [2026-09-21](docs/decisions/2026-09-21-deploy-poll-one-minute.md) · Deploy poll'i 1 daqiqa (30 s texnik jihatdan mumkin emas) · `deploy_automation_is_safe`
- [2026-09-21](docs/decisions/2026-09-21-threat-model.md) · Threat model — butun platforma · `threat_model_covers_the_platform`
- [2026-09-21](docs/decisions/2026-09-21-licence-inventory.md) · Litsenziya inventari — launch gate · `licence_inventory_is_current`
- [2026-09-21](docs/decisions/2026-09-21-security-boundary-statement.md) · Chegara bayonoti: faqat loopback portlar · `security_boundary_is_loopback_only`
- [2026-09-21](docs/decisions/2026-09-21-judge-latency-recorded.md) · Judge latency raqami run summary'ga yoziladi · `judge_latency_gate_is_recorded`
- [2026-09-21](docs/decisions/2026-09-21-security-suite-static-nightly.md) · Xavfsizlik to'plamining statik yarmi Nightly'da · `security_suite_runs_automatically`
- [2026-09-21](docs/decisions/2026-09-21-adminer-declared.md) · `adminer` e'lon qilingan, deploy zanjiridan tashqarida · `adminer_is_declared_outside_the_deploy_chain`
- [2026-09-24](docs/decisions/2026-09-24-root-lockfile-only.md) · `apps/web/package-lock.json` o'chirildi; root lockfile yagona · `package-lock.json`
- [2026-09-24](docs/decisions/2026-09-24-live-contest-deploy-override.md) · Faol contest paytida deploy — override faqat odam qo'lida · `deploy_automation_is_safe`
- [2026-09-24](docs/decisions/2026-09-24-auth-css-source-allowlist.md) · Auth CSS skani — musbat ro'yxat + yo'l yechilishi darvozasi · `login_uses_narrow_auth_css`
- [2026-09-24](docs/decisions/2026-09-24-design-tokens-one-source.md) · Dizayn tokenlari yagona manba — `theme.css` · `rank_colour_groups_not_sixteen_tokens`
- [2026-09-24](docs/decisions/2026-09-24-csp-nonce-coverage.md) · Har bajariladigan skriptda CSP nonce; render darvozasi · `tools/check_csp_nonce.py`
- [2026-09-24](docs/decisions/2026-09-24-customization-contract.md) · Customization contract + qat'iy darvoza (invariantlar yuqorida) · `customization_invariants_are_written`
- [2026-09-24](docs/decisions/2026-09-24-no-rollback-yet.md) · Rollback va server-majburlash ataylab YO'Q — real foydalanuvchilar kelganda qayta ko'riladi · `tools/rollback.sh`
- [2026-09-25](docs/decisions/2026-09-25-attempts-tab.md) · Masala «Urinishlar» tabi — 20 qaror; `?ordering=` endi ishlaydi · `apps/api/core/pagination.py`
- [2026-09-27](docs/decisions/2026-09-27-realtime-sse.md) · Real vaqt — alohida `realtime` xizmati, SSE (ADR-0029) · `apps/api/realtime/asgi.py`
- [2026-09-28](docs/decisions/2026-09-28-dependabot-config-fixed.md) · Dependabot npm `directory: /`; pip PR lock'ni yangilamasdi · `.github/dependabot.yml`
- [2026-09-28](docs/decisions/2026-09-28-dependabot-majors-refused.md) · Django 6 va `typescript` 7 major bump'lari rad etildi · `.github/dependabot.yml`
- [2026-09-28](docs/decisions/2026-09-28-minio-image-and-codeql.md) · MinIO obrazi `bitnamilegacy`; CodeQL qayta yoqildi · `docker-compose.yml`
- [2026-10-04](docs/decisions/2026-10-04-schema-change-wakes-web.md) · Sxema o'zgarsa Web job'i ham yuradi · `schema_change_wakes_web_job`
- [2026-10-04](docs/decisions/2026-10-04-sign-in-two-columns.md) · Kirish sahifasi — ikki ustun, sayt chrome'isiz · `sign_in_page_is_self_contained`
- [2026-10-05](docs/decisions/2026-10-05-clay-dark-palette.md) · `clay` uslubiga qorong'i palitra · `clay_follows_dark_mode`
- [2026-10-05](docs/decisions/2026-10-05-signed-in-dashboard.md) · Kirgan foydalanuvchi bosh sahifasi — shaxsiy panel · `signed_in_home_is_the_dashboard`
- [2026-10-05](docs/decisions/2026-10-05-dashboard-remaining-blocks.md) · Shaxsiy panelning qolgan bloklari; faollik `ActivityEvent` jadvalida · `home_presence_reads_sessions`
- [2026-10-05](docs/decisions/2026-10-05-settings-six-sections.md) · Sozlamalar — olti bo'lim, saqlash paneli, 14 kunlik o'chirish · `settings_six_sections_and_grace`
- [2026-10-05](docs/decisions/2026-10-05-signed-in-header-fits.md) · Kirgan foydalanuvchi header'i 320 px dan sig'adi · `signed_in_header_fits`
- [2026-10-05](docs/decisions/2026-10-05-api-tests-green.md) · API testlari yashil; `DJANGO_SECRET_KEY` zaxira qiymatsiz · `secret_key_has_no_fallback`
- [2026-10-05](docs/decisions/2026-10-05-dependabot-locks-recompiled.md) · Dependabot PR'ida API lock'lari avtomatik qayta yasaladi · `dependabot_locks_are_recompiled`
- [2026-10-05](docs/decisions/2026-10-05-profile-feed-from-events.md) · Profil lentasi ham `ActivityEvent` dan o'qiydi · `apps/api/profiles/public.py`
- [2026-10-05](docs/decisions/2026-10-05-settings-controls-44px.md) · Sozlamalar tablaridagi tugmalar 44 px · `settings_controls_are_44px`
- [2026-10-05](docs/decisions/2026-10-05-customizer-on-a-phone.md) · Sozlagich telefonda — hisob menyusida ikki qator · `customizer_reachable_on_a_phone`
- [2026-10-05](docs/decisions/2026-10-05-customizer-quick-row.md) · Sozlagich — tez qator, shablonlar, «Kengaytirilgan» · `customizer_quick_row_first`
- [2026-10-05](docs/decisions/2026-10-05-failed-sign-ins-limited.md) · Noto'g'ri kirish urinishlari IP va hisob bo'yicha cheklangan · `failed_sign_ins_are_limited`
- [2026-10-05](docs/decisions/2026-10-05-closed-gate-is-not-a-block.md) · Yopiq darvoza (exit 75) — to'siq emas; watcher logi aylanadi · `deploy_automation_is_safe`
- [2026-10-05](docs/decisions/2026-10-05-nightly-red-jobs.md) · Nightly qizillari: A+B hamma tilga ochiq, mehmon header'i har tilda sig'adi · `guest_header_fits_every_locale`
- [2026-10-05](docs/decisions/2026-10-05-customizer-small-fixes.md) · Sozlagich — «shablonga qaytish», gidratsiya, rang kodi · `customizer_quick_row_first`
- [2026-10-05](docs/decisions/2026-10-05-public-stack-secrets-from-env.md) · Ommaviy stack sirlari env'dan, majburiy (ADR-0044) · `public_stack_requires_its_secrets`
- [2026-10-05](docs/decisions/2026-10-05-team-page-one-person.md) · «Jamoa» sahifasi — 24 lavozim, bitta odam · `apps/web/src/content/team.ts`
- [2026-10-05](docs/decisions/2026-10-05-team-page-managed.md) · «Jamoa» bazadan o'qiladi, admin paneldan boshqariladi · `team_page_is_managed_data`
- [2026-10-05](docs/decisions/2026-10-05-site-search-one-engine.md) · Qidiruv — bitta dvigatel, bitta panel · `site_search_is_one_engine`
- [2026-10-06](docs/decisions/2026-10-06-notifications-inbox.md) · Bildirishnomalar — qo'ng'iroq paneli, sahifa, jonli kanal · `notifications_inbox_contract`
- [2026-10-06](docs/decisions/2026-10-06-site-search-parity.md) · Qidiruv — tezlik chegarasi, masala raqami, «eng mos natija» · `site_search_is_bounded_and_exact`
- [2026-10-06](docs/decisions/2026-10-06-attempts-feed-shared-table.md) · Urinishlar lentasi umumiy jadvalda; «faqat meniki» ishlaydi · `attempts_feed_is_the_shared_table`
- [2026-10-06](docs/decisions/2026-10-06-build-cache-pruned.md) · Build cache har deploy'dan keyin to'liq tozalanadi; GC 10 GB · `docker_disk_stays_bounded`
- [2026-10-06](docs/decisions/2026-10-06-scroll-one-vocabulary.md) · Scroll — bitta lug'at (`rw-scroll-*`), bitta modul · `scroll_is_one_vocabulary`
- [2026-10-06](docs/decisions/2026-10-06-less-inner-scroll-1.md) · Ichki scroll'ni kamaytirish, 1-bosqich: menyu, `@container` jadval · `apps/web/src/components/ui/Table.tsx`
- [2026-10-06](docs/decisions/2026-10-06-less-inner-scroll-2.md) · Ichki scroll, 2-bosqich: telefonda jadvallar va faollik xaritasi · `apps/web/src/features/profile/components/ActivityHeatmap.tsx`
- [2026-10-06](docs/decisions/2026-10-06-submit-panel-fits.md) · Yuborish paneli ekranga sig'adi · `apps/web/src/features/problems/components/SubmitPanel.tsx`
- [2026-10-06](docs/decisions/2026-10-06-dates-in-site-zone.md) · Sanalar sayt zonasida (Asia/Tashkent) yoziladi · `dates_are_written_in_the_site_zone`
- [2026-10-06](docs/decisions/2026-10-06-problems-table-header-cells.md) · Masalalar jadvalida sarlavha va katak bitta qoidada · `tools/check_scroll.py`
- [2026-10-06](docs/decisions/2026-10-06-footer-four-groups.md) · Footer — o'z tasmasi, to'rt guruh · `brand_in_header_and_footer_columns`
- [2026-10-06](docs/decisions/2026-10-06-attempt-dates-numeric.md) · Urinishlar jadvalidagi sana faqat raqamlar bilan · `dates_are_written_in_the_site_zone`
- [2026-10-06](docs/decisions/2026-10-06-side-menu-adaptive-density.md) · Yon menyu — moslashuvchan zichlik · `side_menu_keeps_its_sections`
- [2026-10-06](docs/decisions/2026-10-06-side-menu-badges.md) · Yon menyu belgilari — bitta so'rov, to'rt tur · `side_menu_badges_are_one_request`
- [2026-10-06](docs/decisions/2026-10-06-team-page-compact.md) · «Jamoa» sahifasi — ixcham ro'yxat · `team_page_is_compact`
- [2026-10-07](docs/decisions/2026-10-07-about-one-page.md) · «Qanday ishlaydi» — bitta sahifa, mundarija bilan · `about_page_is_one_searchable_page`
- [2026-10-07](docs/decisions/2026-10-07-about-translated.md) · «Qanday ishlaydi» matni sakkiz tilda tarjima qilindi · `apps/web/src/i18n/locales/`
- [2026-10-07](docs/decisions/2026-10-07-english-copies-translated.md) · Lug'atdagi inglizcha nusxalar yetti tilda tarjima qilindi · `apps/web/src/i18n/locales/`
- [2026-10-07](docs/decisions/2026-10-07-evaluation-paths-proven.md) · Special checker, interaktiv, scorer — haqiqiy judge'da isbotlangan · `evaluation_paths_are_proven`
- [2026-10-07](docs/decisions/2026-10-07-task-kinds-scope.md) · To'rt yangi masala turi — qamrov va tartib (ADR-0053) · `docs/07-adr/0053-task-kinds.md`
- [2026-10-07](docs/decisions/2026-10-07-function-task-kind.md) · Funksiya masalasi (`task_kind = function`) · `function_problems_are_composed`
- [2026-10-07](docs/decisions/2026-10-07-answer-task-kind.md) · «Faqat javob» masalasi (`task_kind = answer`) · `answer_problems_run_no_code`
- [2026-10-07](docs/decisions/2026-10-07-two-pass-task-kind.md) · Ikki bosqichli masala (`task_kind = two_pass`) · `two_pass_runs_share_nothing`
- [2026-10-07](docs/decisions/2026-10-07-sql-task-kind.md) · SQL masalasi — SQLite, faqat o'qish · `sql_queries_only_read`
- [2026-10-07](docs/decisions/2026-10-07-nightly-images-built-once.md) · Nightly har obrazni bir marta quradi; API testlari uch shardda · `nightly_builds_each_image_once`
- [2026-10-07](docs/decisions/2026-10-07-editor-sheet-clears-menu.md) · Muharrir varag'i yon menyu ostiga kirmaydi · `editor_sheet_clears_the_side_menu`
- [2026-10-08](docs/decisions/2026-10-08-npm-overrides-at-root.md) · npm `overrides` ildiz `package.json` da · `package.json`
- [2026-10-08](docs/decisions/2026-10-08-guest-zones.md) · Mehmon zonalari — to'rt daraja, bitta ro'yxat (ADR-0054) · `guest_zones_are_gated`
- [2026-10-08](docs/decisions/2026-10-08-contest-problems-and-archive.md) · Musobaqa masalalari: oldin yopiq, tugagach arxivda (ADR-0055) · `contest_problems_stay_out_of_the_archive`
- [2026-10-23](docs/decisions/2026-10-23-thousand-attempts-burst.md) · 1000 urinish o'lchovi; tozalagich natija yozilishini kutadi · `reaper_waits_for_unapplied_results`
- [2026-10-25](docs/decisions/2026-10-25-sign-up-cp-club.md) · Ro'yxatdan o'tish: taxallus 1-qadamda, namunalar, telefonda chiplar · `sign_up_asks_the_handle_and_names`
- [2026-10-25](docs/decisions/2026-10-25-api-version-endpoint.md) · Ochiq `/api/v1/version/` — jonli commit ko'rinadi · `apps/api/core/views.py`
- [2026-10-25](docs/decisions/2026-10-25-watcher-frees-dead-lock.md) · Watcher o'lik egali qulfni o'zi bo'shatadi · `tools/auto_deploy.sh`
- [2026-10-25](docs/decisions/2026-10-25-claude-mods-deploy-panel.md) · Claude Mods: faqat «Deploy paneli», `tools/mods/` da · `tools/mods/deploy-panel/`
- [2026-10-25](docs/decisions/2026-10-25-handle-live-check.md) · 1-qadamda taxallus jonli «band / bo'sh» ko'rsatadi · `sign_up_asks_the_handle_and_names`
- [2026-10-25](docs/decisions/2026-10-25-auth-panel-carousel.md) · Kirish paneli — 10 slaydli statik karusel · `auth_panel_is_a_static_carousel`
- [2026-10-26](docs/decisions/2026-10-26-auth-form.md) · Kirish va ro'yxatdan o'tish, 1-qism: forma (ism 1-qadamda, rozilik matni) · `sign_up_asks_the_handle_and_names`
- [2026-10-26](docs/decisions/2026-10-26-email-six-digit-code.md) · Email 6 xonali kod bilan tasdiqlanadi · `email_is_confirmed_by_six_digit_code`
- [2026-10-26](docs/decisions/2026-10-26-onboarding-three-steps.md) · Onboarding uch ixtiyoriy qadam, ta'lim bosqichi · `onboarding_is_three_optional_steps`
- [2026-10-27](docs/decisions/2026-10-27-row-dividers.md) · `rw-divide` har qatorga rang beradi · `row_dividers_colour_every_row`
- [2026-10-27](docs/decisions/2026-10-27-copy-one-control.md) · Nusxalash — bitta tugma, bitta yozish yo'li · `copy_is_one_control`
- [2026-10-27](docs/decisions/2026-10-27-web-version-route.md) · Web ham `/version` da o'z commitini aytadi · `web_reports_its_own_commit`
- [2026-10-27](docs/decisions/2026-10-27-versioning-points.md) · Versiya nuqtalari: judge shartnomasi, SSE, revision, kesh, `/api/v1/` · `versioning_points_are_wired`
- [2026-10-27](docs/decisions/2026-10-27-accent-cache-follows-mode.md) · Urg'u rang keshi rejimga bog'liq; ikonka `<rect>` tuzatildi · `accent_cache_follows_the_mode`
- [2026-10-29](docs/decisions/2026-10-29-title-ladder-readable.md) · Unvon zinapoyasi o'qiladi: nomlar saqlanadi, tartib ko'rsatiladi · `title_ladder_is_readable`
- [2026-11-08](docs/decisions/2026-11-08-no-judge-resource-limits-yet.md) · Judge resurs chegarasi ataylab YO'Q — birinchi haqiqiy musobaqadan oldin qayta ko'riladi · `docker-compose.yml`
- [2026-11-08](docs/decisions/2026-11-08-api-pytest-in-pr.md) · API pytest PR'da — faqat `apps/api` o'zgarganda · `pr_skips_heavy_ci`
- [2026-11-10](docs/decisions/2026-11-10-secrets-rotated.md) · Ommaviy stack sirlari aylantirildi; standart sir bilan deploy to'xtaydi · `deploy_refuses_default_secrets`
- [2026-11-10](docs/decisions/2026-11-10-nightly-bakeoff-gate.md) · Nightly bake-off haqiqiy darvoza; `login.png` CI'da qayta olindi · `nightly_bakeoff_is_a_gate`
- [2026-11-10](docs/decisions/2026-11-10-samples-only-earn-nothing.md) · Namunasiz masala Skills va Qvant bermaydi · `samples_only_problems_earn_nothing`
- [2026-11-10](docs/decisions/2026-11-10-dependabot-npm-go-inventory.md) · Dependabot npm/Go PR'larida litsenziya inventari; Web job 6 daqiqa · `dependabot_locks_are_recompiled`
- [2026-11-10](docs/decisions/2026-11-10-contest-insiders-unrated.md) · Musobaqa ichkaridagilari: sinovchi roli va reytingsiz qatnashish (ADR-0055, 2-qism) · `contest_insiders_play_unrated`
- [2026-11-10](docs/decisions/2026-11-10-required-checks.md) · `main` «Required checks» ni talab qiladi · `required_checks_cover_every_gate`
- [2026-11-10](docs/decisions/2026-11-10-privacy-text.md) · Maxfiylik matni haqiqiy yig'iladigan ma'lumotni aytadi · `privacy_text_matches_the_data`
- [2026-11-10](docs/decisions/2026-11-10-scanners-in-nightly.md) · gitleaks, pip-audit, npm audit — Nightly'da, faqat hisobot · `scanners_report_in_nightly`
- [2026-11-10](docs/decisions/2026-11-10-operations-docs-measured.md) · Eskirgan operatsion hujjatlar moslandi; katakchalar o'lchov bilan · `docs/10-operations/README.md`
- [2026-11-10](docs/decisions/2026-11-10-names-not-translated.md) · Tarjima qilinmaydigan nomlar — glossariy va ratchet · `names_are_not_translated`
- [2026-11-10](docs/decisions/2026-11-10-harness-in-staff-panel.md) · Hakam dasturi va til qatorlari xodim panelida · `function_harness_is_editable_by_staff`
- [2026-11-10](docs/decisions/2026-11-10-judge-not-privileged.md) · Judge konteyneri privileged emas (ADR-0046) · `judge_is_not_privileged`
- [2026-11-10](docs/decisions/2026-11-10-external-ratings-daily.md) · Bog'langan tashqi reytinglar kunlik yangilanadi · `external_ratings_refresh_daily`
- [2026-11-10](docs/decisions/2026-11-10-nightly-live-gates.md) · Nightly jonli darvozalari CI stack'ini o'lchaydi · `nightly_live_gates_measure`
- [2026-11-10](docs/decisions/2026-11-10-audit-small-items.md) · Auditning mayda bandlari (Q-16): klient sanalari, tunnel, watcher · `client_dates_are_numeric`
- [2026-11-10](docs/decisions/2026-11-10-qvant-history.md) · Qvant tranzaksiyalar tarixi `/qvant` da · `apps/web/src/app/(site)/qvant/page.tsx`
- [2026-11-10](docs/decisions/2026-11-10-optimistic-save.md) · `optimisticSave` sozlamalar saqlashini boshqaradi, standart o'chiq · `optimistic_save_reports_refusals`
- [2026-11-10](docs/decisions/2026-11-10-decisions-out-of-claude-md.md) · Qarorlar `docs/decisions/` da, CLAUDE.md da faqat bir qatorli indeks · `decisions_index_matches_files`
- [2026-11-10](docs/decisions/2026-11-10-contest-questions-and-announcements.md) · Musobaqa savol-javobi va e'lonlari; savollar yopiq (ADR-0055, 3-qism) · `contest_questions_stay_private`
- [2026-11-10](docs/decisions/2026-11-10-contest-fair-play.md) · Halol o'yin: muharrir signallari, hakam hisoboti, chetlatish (ADR-0055, 4-qism) · `contest_fair_play_is_judged`
- [2026-11-10](docs/decisions/2026-11-10-notification-email.md) · Email bildirishnomalari: opt-in, faqat shaxsiy, 5 daqiqa, zaxira 200, bir bosishda obuna · `notification_email_is_opt_in_and_bounded`
- [2026-11-10](docs/decisions/2026-11-10-region-ab.md) · Viloyat A/B o'z kaliti bilan, standart o'chiq; mehmon voronkasi tab id bilan · `region_ab_is_switched_and_measured`
- [2026-11-10](docs/decisions/2026-11-10-flags-reach-build.md) · `NEXT_PUBLIC_FLAG_*` web obrazi build'iga uzatiladi; bo'sh = o'chiq · `flags_reach_the_web_build`
- [2026-11-10](docs/decisions/2026-11-10-studio-problems.md) · Muallif qoralamasi `/studio/problems` da: 20 ta chegara, ko'rik so'rovi, xodim navbati · `studio_problems_panel`
- [2026-11-10](docs/decisions/2026-11-10-studio-contests.md) · Organizator musobaqasi `/studio/contests` da: 5 ta chegara, faqat o'z qoralama masalalari · `studio_contests_panel`
- [2026-11-10](docs/decisions/2026-11-10-graphite-palette.md) · `newPalette`: clay qorong'isi uchun «Grafit», standart o'chiq · `graphite_palette_is_flagged`
- [2026-11-10](docs/decisions/2026-11-10-dump-only-for-migrations.md) · Deploy oldidagi `pg_dump` faqat qo'llanmagan migratsiya bo'lsa, build bilan parallel; ro'yxat ko'rmaganini `migrate --check` ushlaydi · `dump_only_for_pending_migrations`
- [2026-11-10](docs/decisions/2026-11-10-gate-trusts-pr-ci.md) · Darvoza `main` CI tugamasdan merge qilingan PR'ning yashil CI'siga ishonadi — faqat daraxt bir xil va oxirgi main CI yashil bo'lsa · `gate_trusts_green_pr_on_same_tree`
- [2026-11-10](docs/decisions/2026-11-10-build-cache-budget.md) · Build cache 10 GB gacha saqlanadi (2026-10-06 ni almashtiradi); judge base obrazi qayta ishlatiladi; disk qo'riqchisi 5 GB · `build_cache_kept_within_budget`
- [2026-11-10](docs/decisions/2026-11-10-ci-fast-installs.md) · CI: Python paketlari `uv` bilan, `node_modules` lockfile va Node versiyasi bo'yicha keshlanadi · `ci_installs_are_fast`
- [2026-11-10](docs/decisions/2026-11-10-pr-update-queue.md) · Orqada qolgan auto-merge PR'larni watcher navbat bilan, bittadan yangilaydi; agentlar o'zi `update-branch` qilmaydi · `behind_prs_update_one_at_a_time`
- [2026-11-10](docs/decisions/2026-11-10-pr-negative-scope.md) · PR CI qaror salbiy testlarini faqat o'zgargan fayllar uchun yuritadi; main va Nightly — to'liq · `pr_runs_decision_cases_for_changed_files`
- [2026-11-10](docs/decisions/2026-11-10-host-memory-and-disk.md) · C: va xotira bosimi: pagefile D: ga (24 GB), faol bo'lmagan sessiyalar arxivda, og'ir MCP'lar mux, monitor C: < 15 GB va commit >= 90% ni yozadi · `monitor_watches_disk_and_commit`
- [2026-11-10](docs/decisions/2026-11-10-billing.md) · To'lov: 1/6/12 oy bir martalik, Click+Payme, Pro/Judge pullik kursni ochadi, Qvant pulga bog'lanmaydi, `billing` bayrog'i o'chiq, qaytarishda huquq bekor · `billing_is_checked_and_reversible`
- [2026-11-10](docs/decisions/2026-11-10-courses-classroom.md) · Sinfga kurs: faqat bepul kurs o'quvchilarga avtomatik ochiladi, hisobot (foiz, darslar, test, sertifikat) faqat egasiga, ixtiyoriy muddat · `course_given_to_a_class`
- [2026-11-10](docs/decisions/2026-11-10-courses-certificate.md) · Kurs sertifikati (musobaqa kabi), yakuniy test >= chegara, bir martalik mukofot, Qvant narxi tasdiqlanadi va qaytarilmaydi · `course_rewards_and_certificate`
- [2026-11-10](docs/decisions/2026-11-10-courses-video-worker.md) · Video kodlash: alohida video-worker (1 vazifa, 2 CPU), musobaqa paytida ham · `course_video_is_encrypted_and_own`
- [2026-11-10](docs/decisions/2026-11-10-courses-video.md) · Kurs videosi: ffmpeg va tayyor HLS, manba sifatigacha, AES-128 kalit API'dan, R2 keyin, brauzerdan to'g'ridan yuklash · `course_video_is_encrypted_and_own`
- [2026-11-10](docs/decisions/2026-11-10-courses-studio.md) · Kurs studio'si: har kim yozadi (3 qoralama), matn darhol, tuzilma va narx xodimda · `course_studio_rules`
- [2026-11-10](docs/decisions/2026-11-10-courses.md) · Kurslar: Kurs → Modul → Bo'lim → Dars, ko'p tilli darslar, to'rt kirish turi, pullik video R2 + HLS, `courses` bayrog'i ortida (ADR-0056) · `courses_structure_and_access`
- [2026-11-10](docs/decisions/2026-11-10-revive-failed-containers.md) · Docker ko'tara olmagan konteynerni watcher ko'taradi (qo'lda to'xtatilgani emas); Docker o'chiqda deploy to'sig'i yo'q · `failed_containers_are_revived`
- [2026-11-10](docs/decisions/2026-11-10-rail-shell.md) · `newNav`: kompyuterda rail + guruh paneli, telefonda drawer, standart o'chiq · `rail_shell_is_flagged`
- [2026-11-10](docs/decisions/2026-11-10-public-env-reaches-build.md) · Web o'qiydigan har `NEXT_PUBLIC_*` build'ga uzatiladi; bo'sh `SITE_URL` = API origin'i · `flags_reach_the_web_build`
- [2026-11-11](docs/decisions/2026-11-11-ai-tutor.md) · AI ustoz: maslahat, yechim yo'q; 5/100/250/500; musobaqada o'chiq; adapter (API + `claude -p` zaxira), 90 kun, byudjet · `hali kod yo'q`
- [2026-11-11](docs/decisions/2026-11-11-plan-contents.md) · Judge: mualliflik kvotasi, yopiq va GYM musobaqa; Plus: tahlillar tekin, yechim kodlari, profil nishoni · `hali kod yo'q`
- [2026-11-11](docs/decisions/2026-11-11-teacher-tools.md) · Sinfga tasdiq bilan kirish, murabbiy, savollar banki va sinfga test (kodda), serverdagi test generatori (hali yo'q) · `teacher_quizzes_stay_in_class`
- [2026-11-11](docs/decisions/2026-11-11-content-and-archive.md) · Traektoriya o'quv rejasi, olimpiada arxivi, cp.uz CC BY-SA, Abramyan (ruxsat bor), norasmiy masalalar reytingsiz · `study_plans_have_sections`
- [2026-11-11](docs/decisions/2026-11-11-new-alphabet.md) · Yangi alifbo (O'RQ-1184): avtomatik o'giruvchi, hozirdan standart, butun platforma, qidiruvda ikkalasi bir · `alphabets_fold_as_one`
- [2026-11-11](docs/decisions/2026-11-11-community-and-contests.md) · Muhokama, fayl yuklash, taymer, fokus; hudud filtri, PDF, hamkor/mirror; bloglar va karma; seriya, xarita · `hali kod yo'q`
- [2026-11-11](docs/decisions/2026-11-11-problem-translations.md) · Masala tarjimalari: asosiy matn + `ProblemTranslation`, maydonma-maydon zaxira, yopiq tahlil yopiq, nashrni xodim tahrirlaydi, qidiruvda tarjima nomlari · `problem_translations_fall_back`
- [2026-11-11](docs/decisions/2026-11-11-deploy-disk-writes.md) · Deploy diskka kamroq yozadi: compose tahriri faqat `build:` bo'limi o'zgargan obrazni quradi, `up` hamma servisga; web'da `node_modules` `.next` dan oldin · `tools/deploy_scope.py`
- [2026-11-11](docs/decisions/2026-11-11-abramyan-import.md) · Abramyan importi: judge'da haqiqiy son solishtiruvi, 64 MB + til ustamasi, norasmiy (raqamsiz, faollik hisoblanadi), «Begin1. Nom», agent bahosi bilan nashr, production'da tungi tekshiruv · `real_numbers_compared_in_the_judge`
- [2026-11-11](docs/decisions/2026-11-11-abramyan-verification.md) · Abramyan: tekshiruv hozir production judge'da, izi qoladi (o'chirish keyin); 150 × 4 matnni agent tekshiradi, muammolar Report'dan; 19 bo'lim → mavjud mavzular · `abramyan_publishes_only_verified`
- [2026-11-11](docs/decisions/2026-11-11-next-directions.md) · Abramyan hammasi tuzalguncha kutadi, e'lonsiz; keyingi tartib: o'qituvchi vositalari → jamoa funksiyalari → cp.uz importi → AI agent (prototiplar bilan) · `abramyan_publishes_only_verified`
- [2026-11-11](docs/decisions/2026-11-11-teacher-tools-details.md) · O'qituvchi vositalari batafsil: eski sinflar darhol, 3×40 / 50×50, murabbiy ≤3 alohida ruxsat bilan, test turlari, Qvant'siz, generator stdin, kvota hammasini sanaydi (1–3-bosqich kodda) · `classroom_joins_and_quotas`

## Tekshiruvlar

Pre-push hook **tor**: `push_guard`, API `ruff`/`format`, web `check_i18n`
va `check_hardcoded`. mypy, pytest, tsc, eslint, salbiy testlar — faqat
CI. 2026-09-18 o'lchov: to'liq hook Windows'da 5.8 daqiqa edi.

Qo'lda to'liq to'plam:

```bash
cd apps/api && export DJANGO_SECRET_KEY=dev && uv run ruff check . && uv run ruff format --check . && uv run mypy . && env CELERY_EAGER=1 uv run pytest -q -n 4
```

```bash
cd apps/web && npm run lint && npm run typecheck && npm run build
```

```bash
python3 tools/check_i18n.py && python3 tools/check_contrast.py && python3 tools/check_docs.py && python3 tools/check_contract.py
```

Endpoint qo'shilsa yoki serializer o'zgarsa, sxemani yangilash **shart** —
aks holda CI yiqiladi:

```bash
cd apps/api && DJANGO_SECRET_KEY=dev uv run python manage.py spectacular --file openapi/schema.yml
```

Kod yoki compose yangi muhit o'zgaruvchisini o'qisa, u `.env.example` ga
yoziladi (sir bo'lsa qiymatsiz) — aks holda `tools/check_env_example.py`
CI da yiqiladi.

`pytest -n 4` — `auto` EMAS: runner shu mashinada, jonli preview bilan
yonma-yon ishlaydi.

`CELERY_EAGER=1` CI pytest uchun **shart**. Busiz task navbatga yoziladi
va test javobni kutib qotadi; `settings.py` uni `CELERY_TASK_ALWAYS_EAGER`
ga o'giradi. O'lchangan farq: 14m54s → 1m57s.

## Preview

Kundalik ish uchun **web rebuildsiz** rejim: [local-dev.md](docs/10-operations/local-dev.md) — `powershell -File tools/dev-local.ps1` → UI `http://127.0.0.1:8310/`.

```bash
docker compose -p rankwant --env-file .env.public -f docker-compose.yml -f docker-compose.public.yml up -d --build --wait
```

**`-p rankwant` tushib qolmasin.** `docker-compose.yml` da `name:` kaliti
yo'q, ya'ni loyiha nomi joriy KATALOG nomidan olinadi. Worktree ichidan
bayroqsiz chaqirilsa, compose jimgina alohida stack va **alohida baza**
ko'taradi — xato bermaydi, shunchaki boshqa ma'lumot ko'rsatadi. Faqat
`docker-compose.ci.yml` o'z nomini (`rankwant-ci`) o'zi belgilaydi.

Mashina dual-boot (Linux + Windows), har tizimda preview'ning o'z bazasi bor.
Tizim almashtirishdan **oldin** `tools/handoff.sh out` (Linux) yoki
`tools\handoff.ps1 out` (Windows), yuklangandan keyin `in` — aks holda ikki
baza jimgina ajralib ketadi. Protokol: [10-operations](docs/10-operations/README.md)
§ «Ikki tizimli preview».
Linux'da `in` ni yuklanishda `rankwant-handoff.service` o'zi chaqiradi va
`tools/handoff.sh switch` bitta buyruqda `out` + Windows'ga qayta yuklashni
bajaradi. Windows'da bunday `switch` yo'q: `out`, keyin qayta yuklash —
EFI tartibi Ubuntu'ni birinchi qo'yadi. U yerda avtomatik `in` uchun logon
vazifasi bir marta ro'yxatga olinadi (hujjatda).

**Servis nomini ro'yxatlab qisqartirmang.** Django kodi API'da ham,
`worker` da ham, `beat` da ham ishlaydi; faqat `api` ni qayta qursangiz
worker eski kodda qoladi. O'lchangan oqibat: judge yangi verdikt
yubordi, eski worker uni tanimay `IE` ga aylantirdi va sabab faqat
worker logida ko'rindi.

Portlar: web `127.0.0.1:8300`, API `127.0.0.1:8301`. `ALLOWED_HOSTS`
tufayli curl'ga host sarlavhasi kerak, aks holda bo'sh 400 keladi:

```bash
curl -H 'Host: rankwant.uz' http://127.0.0.1:8301/api/v1/health/
```

## Bake-off (judge izolyatsiyasi)

Ishga tushirishdan oldin `worker` va `beat` **to'xtatilishi shart** —
`drain_results` natijalarni harness'dan oldin olib ketadi va hisobot
«XAVFSIZLIKDAN O'TMADI» deb yozadi, aslida sandbox soz:

```bash
docker compose -p rankwant --env-file .env.public -f docker-compose.yml -f docker-compose.public.yml stop worker beat
IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' rankwant-redis-1)
apps/api/.venv/bin/python services/bakeoff/harness/runner.py --worker judge-go --redis redis://$IP:6379/0
docker compose -p rankwant --env-file .env.public -f docker-compose.yml -f docker-compose.public.yml start worker beat
```

Redis host portiga chiqarilmagan — shuning uchun konteyner IP'si olinadi.
`rankwant-redis-1` nomi ham aynan `-p rankwant` bo'lgandagina topiladi:
konteyner nomini compose loyiha nomidan yasaydi. Bayroq tushsa
`docker inspect` bo'sh qaytaradi va `IP` o'zgaruvchisi jimgina bo'sh
qoladi.

## Ish uslubi

**Ish tartibi** (Saidakbar aka bilan kelishilgan, 2026-10-25):
IDEA → PLAN → IMPLEMENT → TEST & VERIFY → COMMIT → PUSH → PR → REVIEW + CI →
MERGE → DEPLOY → POST-DEPLOY VERIFY → REPORT. Uch band qat'iy:

1. **TEST**: PR ochishdan oldin tegilgan qismning testi mahalliy YASHIL bo'lishi
   shart. CI nimani yurgizmasa (API pytest PR'da yurmaydi — `pr_skips_heavy_ci`),
   uni o'zim yurgizaman. 2026-10-23: #438 mahalliy qizil bilan merge bo'ldi,
   #439 tuzatdi.
2. **REVIEW**: murakkab o'zgarishda (mantiq, xavfsizlik, migratsiya, judge)
   merge'dan oldin o'z diff'imni mustaqil ko'rib chiqaman (`/code-review`).
   Kichik matn va hujjat o'zgarishida shart emas.
3. **POST-DEPLOY VERIFY**: deploy'dan keyin qaysi commit chiqqanini
   (`deploy tugadi: <sha>`) va o'zgargan sahifani jonli saytda o'lchayman;
   `deploy tugadi` yo'q bo'lsa, watcher'ni (qulf, log) tekshiraman. 2026-10-25:
   ikki kun deploy to'xtab qolgan edi (o'lik egali qulf), monitor esa «OK»
   deb turardi.

Issue ishlatilmaydi — **PR asosida**. Vazifa qo'shish
kerak bo'lsa branch va PR ochiladi, tracker'ga ticket yozilmaydi.

**Orqada qolgan PR'ni o'zingiz yangilamang** (2026-11-10): PR'ga auto-merge
yoqing va `BEHIND` bo'lsa `gh pr update-branch` qilmang — watcher
(`tools/pr_update_queue.py`) auto-merge PR'larini navbat bilan, bittadan
yangilaydi. Faqat `DIRTY` (konflikt) PR'ni o'zingiz hal qilasiz: `main` ni
branch'ga merge qiling, force push'siz.

Til: izoh va docstring inglizcha, mavjud hujjat o'z tilida — to'liq qoida
[CONTRIBUTING § Til](CONTRIBUTING.md#til). Mavjud izohlarni tarjima qilmang.

CI, Security va Nightly `ubuntu-latest` da (public repo — standard
runner daqiqasi $0). Deploy `tools/deploy.sh` / `deploy.yml` shu
mashinada qoladi. PR'da Security yo'q. Smoke, E2E, bake-off, language
matrix va API pytest — Nightly.

**`main` ga to'g'ridan-to'g'ri push'ni hook rad etadi** (`tools/push_guard.py`).
GitHub bu tarifda branch protection bermaydi (403), ya'ni server hech narsani
to'xtatmaydi — qoidani faqat shu hook ushlab turadi. Tartib: branch → PR →
CI yashil → GitHub'da merge. `RANKWANT_ALLOW_MAIN_PUSH=1` va `--no-verify` —
agent uchun faqat Saidakbar akaning aniq ruxsati bilan.

**Commit qilishdan oldin identity'ni tekshiring:**
`git config --show-origin user.email`. 2026-09-16 da salbiy test haqiqiy
repoda ishlab `.git/config` ga `test@example.com` yozib qo'ygan va 42 commit
shu nom bilan ketgan (tarix `.mailmap` da to'g'rilangan). Hook endi soxta
muallifli commit'ni ham, ifloslangan config'ni ham rad etadi; salbiy
to'plam esa haqiqiy repo config'i o'zgarsa o'zi yiqiladi.
