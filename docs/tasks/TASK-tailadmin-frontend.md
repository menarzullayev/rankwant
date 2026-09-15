# TASK: TailAdmin UI — RankWant `apps/web` professional frontend

**Beruvchi:** product owner (2026-09-07)  
**Ijrochi:** Claude Code (yoki boshqa agent)  
**Manba shablon:** [TailAdmin/free-nextjs-admin-dashboard](https://github.com/TailAdmin/free-nextjs-admin-dashboard) (MIT, v2.3.x)  
**Demo:** https://nextjs-demo.tailadmin.com  
**Holat:** ready — boshlash mumkin

---

## Maqsad

RankWant web (`apps/web`) hozir minimal Tailwind shell. **TailAdmin** layout va UI komponentlarini integratsiya qilib, **professional ko‘rinish** berish — backend (`apps/api`) va mavjud API client o‘zgarmasdan.

Bu task **shell + mavjud sahifalarni qayta skin qilish**. Monaco editor / to‘liq submit oqimi **Phase 2** (alohida task).

---

## Qattiq cheklovlar

1. **`apps/api/` ga tegma** — faqat `apps/web/`.
2. **`src/lib/api.ts` mantiqini saqla** — `API_BASE`, SSR `API_BASE_INTERNAL`, barcha fetch metodlari ishlashi shart.
3. **Route yo‘llari o‘zgarmasin** (SEO, E2E, typedRoutes):
   - `/`, `/problems`, `/problems/[slug]`, `/contests`, `/contests/[slug]`
   - `/leaderboard`, `/rating`, `/qvant`, `/blog`, `/blog/[slug]`
   - `/learn`, `/learn/[slug]`, `/notifications`, `/users/[username]`
4. **i18n:** `src/i18n/messages.ts` saqlansin; matnlar hali u yerdan o‘qilsin (keyinroq next-intl emas).
5. **Markdown + KaTeX:** `src/components/Markdown.tsx` va masala/maqola render ishlashi shart.
6. **Brend:** KEP/RoboContest UI nusxasi **yo‘q**. RankWant ranglari (override):
   - `--accent: #5b8cff`
   - qorong‘u fon `#0b0d12` / surface `#141821` (hozirgi `globals.css` dan)
   - Logo: `Rank` + `Want` (accent)
7. **CI yashil:** `apps/web` da `npm run lint`, `npm run typecheck`, `npm run build` o‘tishi kerak.
8. **Keraksiz dependency qo‘shma** — TailAdmin dan faqat ishlatiladigan paketlar (jsvectormap ishlatilmasa o‘tkazib yuborish mumkin).
9. **Commit:** faqat user so‘rasa; bu taskda kod tayyor, commit ixtiyoriy.

---

## Texnik moslik (allaqachon mos)

|            | TailAdmin | RankWant web |
| ---------- | --------- | ------------ |
| Next.js    | 16.x      | 16.x         |
| React      | 19        | 19           |
| Tailwind   | v4        | v4           |
| TypeScript | ✅        | ✅           |

ADR-0003 da `shadcn/ui` yozilgan — bu task **TailAdmin komponentlari** bilan ketadi; ADR yangilash **opsional** (alohida qator: «UI kit: TailAdmin MIT»).

---

## Integratsiya strategiyasi (tavsiya)

**Variant A (tavsiya):** TailAdmin komponentlarini `apps/web` ichiga **nusxa + moslashtirish**, repo alohida qolmasin.

```
apps/web/src/
├── app/                    # mavjud route'lar — layout TailAdmin shell
├── components/
│   ├── ui/                 # TailAdmin: Button, Table, Badge, Modal…
│   ├── layout/             # Sidebar, Header, ThemeToggle
│   └── Markdown.tsx        # SAQLANADI
├── lib/api.ts              # SAQLANADI
├── i18n/messages.ts        # SAQLANADI
└── context/                # TailAdmin: SidebarContext, ThemeContext (kerak bo‘lsa)
```

**Qilmaslik:** butun TailAdmin repo'sini `apps/web` ustiga yozib qo‘yish (demo sahifalar, mock auth backend).

---

## Fazalar

### Phase 1 — Poydevor (bloker)

- [ ] TailAdmin `package.json` dan kerakli dependencylarni qo‘sh (apexcharts, flatpickr, tailwind-merge, @tailwindcss/forms, …).
- [ ] PostCSS / Tailwind v4 config TailAdmin bilan kelishsin.
- [ ] Global layout: **collapsible sidebar** + **top header** + **dark mode** (default dark).
- [ ] Nav items → mavjud route'lar (`layout.tsx` dagi NAV ro‘yxati).
- [ ] RankWant theme tokenlari (accent, level-* ranglari saqlansin).
- [ ] `npm run build` yashil.

### Phase 2 — Mavjud sahifalarni qayta UI

Har sahifa TailAdmin **Table / Card / Badge** patternida, ma’lumot `api.ts` dan:

- [ ] `/` — hero + stat kartalar (API stats bo‘lmasa placeholder yoki `/users/` count)
- [ ] `/problems` — filter + jadval (difficulty badge, level rang)
- [ ] `/problems/[slug]` — Card layout; **Markdown statement** o‘ngda yoki markazda (editor hali yo‘q)
- [ ] `/contests` — ro‘yxat + status badge (running/finished)
- [ ] `/contests/[slug]` — `StandingsTable` TailAdmin table uslubida
- [ ] `/leaderboard` — sortable table
- [ ] `/rating` — formula matni + ApexCharts (ixtiyoriy demo chart)
- [ ] `/qvant` — wallet card + quest list
- [ ] `/blog`, `/learn`, `/notifications`, `/users/[username]` — Card/list layout

### Phase 3 — Auth UI (shell)

- [ ] `/login`, `/register` sahifalari — TailAdmin auth form dizayni
- [ ] Django API: `POST /api/v1/auth/login/`, `register/` — cookie session (ADR-0008)
- [ ] Header: login/logout holati

### Phase 4 — Tozalash

- [ ] Ishlatilmagan TailAdmin demo route/file larni **ko‘chirmaslik**
- [ ] Bundle: jsvectormap / swiper ishlatilmasa dependency olib tashlash
- [ ] E2E (`tests/e2e/`) buzilsa minimal fix
- [ ] Qisqa `apps/web/README.md` — TailAdmin attribution (MIT)

---

## Phase 2 (KEYINGI TASK — bu task emas)

- Monaco Editor (`@monaco-editor/react`) — masala submit
- Verdict badge komponentlari (AC/WA/TLE…)
- Contest submit + SSE standings live update

Reference (faqat UI nusxa): [code-compete](https://github.com/Pratham-Prog861/code-compete)

---

## Qabul qilish mezonlari (Definition of Done)

1. Barcha yuqoridagi route'lar brauzerda ochiladi, 404 yo‘q.
2. Kamida **3 ta** sahifa (`/problems`, `/leaderboard`, `/contests`) TailAdmin jadval/card ko‘rinishida.
3. Sidebar + dark mode ishlaydi.
4. `npm run lint && npm run typecheck && npm run build` — `apps/web` da xatosiz.
5. `docker compose up web api` — sahifalar API dan ma’lumot oladi (local).
6. RankWant brend ranglari saqlangan (ko‘k accent, KEP ko‘k-yashil emas).

---

## Fayllar — tegmaslik / ehtiyot

| Fayl                                   | Sabab           |
| -------------------------------------- | --------------- |
| `apps/web/src/lib/api.ts`              | API shartnomasi |
| `apps/web/src/components/Markdown.tsx` | Masala/maqola   |
| `apps/web/src/i18n/messages.ts`        | Tarjimalar      |
| `apps/api/**`                          | Backend         |
| `tests/e2e/**`                         | Faqat zarur fix |

---

## Foydali havolalar

- TailAdmin repo: https://github.com/TailAdmin/free-nextjs-admin-dashboard
- RankWant ADR stack: `docs/07-adr/0003-stack-django-next.md`
- RankWant auth: `docs/07-adr/0008-auth-session-plus-pat.md`
- Dev plan: `docs/09-development-plan/README.md`
- Hozirgi layout: `apps/web/src/app/layout.tsx`
- Level ranglar: `apps/web/src/app/globals.css` (`.level-*`)

---

## Claude Code uchun boshlash buyrug‘i (copy-paste)

```
RankWant monorepo: repo ildizi (`git rev-parse --show-toplevel`)

TASK faylini to‘liq o‘qi: docs/tasks/TASK-tailadmin-frontend.md

Qisqa: apps/web ga TailAdmin (MIT) UI shell integratsiya qil.
apps/api ga tegma. api.ts, Markdown, i18n, route yo‘llari saqlansin.
Phase 1 + Phase 2 ni bajar; Phase 3 auth ixtiyoriy agar vaqt yetmasa.
Oxirida lint, typecheck, build isbotla.
```
