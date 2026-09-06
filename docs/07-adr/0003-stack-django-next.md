# ADR-0003: Stack — Django 5.2 LTS + DRF backend, Next.js frontend

**STATUS:** accepted (2026-09-06)

## Muammo

`06-architecture` 4 ta stack variantini ochiq qoldirgan edi (A: Django REST + React, B: Laravel + Inertia, C: Next.js fullstack, D: Django + Next + DMOJ). Shu bilan birga savol kengroq edi: **tayyor OJ platformasini fork qilamizmi, yoki o'zimiz quramizmi?**

## Qaror 1 — kod litsenziya pozitsiyasi

**RankWant kodi yopiq (tijorat).** PRD [P2-3](../04-prd/README.md) obuna modelini (Free/Plus/Pro) nazarda tutadi.

Bu bitta qaror mavjud OJ platformalarining yarmini chiqarib tashlaydi:

| Platforma   | Litsenziya           | Stack                     | Holat (2026-09)        | Yopiq tijorat uchun                 |
| ----------- | -------------------- | ------------------------- | ---------------------- | ----------------------------------- |
| **QDUOJ**   | MIT                  | Django 3.2 + Vue 2, Py3.8 | ⚠️ oxirgi yangilanish 2024-04 | Litsenziya toza, **stack EOL**      |
| **Hydro**   | AGPL-3.0 (dual)      | TypeScript + MongoDB      | ✅ faol (v5.0.5)       | Tijorat litsenziyasi sotib olinadi  |
| **DMOJ**    | AGPL-3.0             | Django + Python           | ✅ faol                | ❌ modifikatsiyalar ochilishi shart |
| **Judge0**  | GPL-3.0              | alohida HTTP servis       | ✅ faol, 90+ til       | ✅ (pastga qarang)                  |

**Hal qiluvchi huquqiy nuqta — GPL ≠ AGPL:**

- **AGPL** (DMOJ, Hydro): tarmoq orqali xizmat + kodni o'zgartirish → o'zgarishlarni ochish shart
- **GPLv3** (Judge0): «tarmoq orqali muloqot *conveying* emas» → tarqatish bo'lmasa majburiyat ham yo'q. Alohida servis sifatida chaqirilsa, RankWant kodi yopiq qolaveradi

> ⚠️ Bu litsenziyalarning umumiy talqini, yuridik xulosa emas. Launch oldidan yurist tasdiqlashi shart.

## Qaror 2 — fork emas, o'zimiz quramiz

QDUOJ fork qilish rad etildi: Python 3.8 / Django 3.2 / Vue 2 — hammasi EOL, oxirgi yangilanish 2024-04, xavfsizlik patchlari yo'q. Birinchi 2–4 oy mahsulot qiymatisiz upgrade'ga ketardi, keyin differensiatorlar (4 reyting, Qvant, o'z kontent) begona kod bazasiga o'rnatilardi.

Bu vision principle #1 («clone emas, **o'z engine va UX**») bilan ham mos.

## Tanlov — stack

| Qatlam       | Tanlov                                                      |
| ------------ | ----------------------------------------------------------- |
| **Backend**  | Django 5.2 **LTS** + DRF, Python 3.12+                      |
| **Frontend** | Next.js + React 19 + TypeScript + Tailwind 4 + shadcn/ui    |
| **DB**       | PostgreSQL                                                  |
| **Queue**    | Redis + Celery                                              |
| **Storage**  | S3 / Cloudflare R2 — statement assets, test data            |
| **Judge**    | alohida servis — [ADR-0004](0004-judge-engine.md)           |
| **Realtime** | SSE + qisqa polling (WebSocket **emas**)                    |

## Sabab

**Django + DRF** — sabab domenga xos, umumiy «Python yaxshi» emas:

1. **Django admin → P0-2 deyarli bepul.** Masala CRUD, test-case yuklash, contest sozlash, user boshqaruvi — OJ da bu kundalik og'ir operatsion ish. Boshqa framework'da 2–4 hafta qo'l mehnati.
2. **drf-spectacular → OpenAPI avtomatik** — vision goal #5 («ochiq API») tekinga keladi. KEP ~102 ochiq endpoint bilan raqobat qiladi.
3. **Python — CP tooling'ning ona tili** — Polygon paketlari, `testlib` checker/generator, masala import konvertorlari.
4. **Celery** — rejudge, standings, 4 reyting ([ADR-0006](0006-rating-model.md)) qayta hisoblash.
5. **Mahalliy kadr** — KEP ham, cp.uz ham Django REST tanlagan.

**5.2 LTS, 6.0 emas** — LTS 2028 gacha qo'llab-quvvatlanadi; platforma yillab ishlashi kerak.

**Next.js** — `rankglass` tajribasi (Next 15, React 19, TS, Tailwind 4) to'g'ridan-to'g'ri ishlaydi. Muhimi: **SSR → SEO** — «o'z o'zbek kontenti» ([ADR-0005](0005-content-strategy-own-content.md)) faqat qidiruvda topilsa qiymat beradi.

**SSE, WebSocket emas** — contest standings 10–30 soniyada yangilansa yetarli (oxirida muzlatiladi). Django Channels/ASGI murakkabligi MVP'da asossiz. O'lchangan ehtiyoj bo'lsa keyin qo'shiladi.

## Rad etilgan variantlar

| Variant                     | Rad sababi                                                                       |
| --------------------------- | -------------------------------------------------------------------------------- |
| **B: Laravel + Inertia**    | Inertia'da API yopiq default → vision goal #5 («ochiq API») ga zid                |
| **D: … + DMOJ**             | DMOJ AGPL-3.0 → yopiq tijorat bilan sig'ishmaydi                                 |
| **C: Next.js fullstack**    | Admin (P0-2) va OpenAPI (goal #5) qo'lda quriladi; batch reyting hisoblash noqulay |
| **Spring Boot / ASP.NET**   | «Professional» lekin admin yo'q, CRUD 2–3× sekin, mahalliy kadr tor              |
| **QDUOJ fork**              | MIT toza, lekin Python 3.8 / Django 3.2 / Vue 2 — EOL                            |
| **Hydro tijorat litsenziyasi** | Nazorat plugin doirasi bilan cheklanadi; narx muzokaraga bog'liq              |

## Professionallik — qanday ta'minlanadi

«Professionallik» framework tanlovida emas. Majburiy shartlar:

- `mypy` strict rejimi + DRF serializer tiplari
- Service layer — biznes logika view'da emas
- Test qamrovi: judge pipeline va reyting hisoblash uchun **majburiy**
- CI: lint + type + test har PR da
- Observability: structured log, Sentry, judge latency metrikasi

## Oqibatlar

- `06-architecture` — stack ochiq emas; diagramma va servis ro'yxati aniqlashtirildi
- `08-technical-spec` — placeholder holatidan chiqadi, to'ldirilishi mumkin
- `09-development-plan` — Sprint 0 ga judge bake-off spike'i qo'shiladi
- Ikki til (Python backend + TS frontend), ikki deploy — **qabul qilingan narx**
- ~~Repo tuzilishi: uch alohida repo~~ → **monorepo**, [ADR-0009](0009-monorepo.md) bilan almashtirildi

## Bog'liq hujjatlar

- [0004-judge-engine.md](0004-judge-engine.md)
- [../06-architecture/README.md](../06-architecture/README.md)
