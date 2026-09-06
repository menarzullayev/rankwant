# RankWant web

Next.js 16 (App Router) + React 19 + Tailwind v4. Sahifalar **server
komponenti** — SSR SEO uchun majburiy ([ADR-0003](../../docs/07-adr/0003-stack-django-next.md)).

## Ishga tushirish

```bash
npm install
npm run dev                     # http://localhost:3000
```

To'liq stack (API, judge, Postgres bilan birga):

```bash
docker compose -f docker-compose.yml up -d --wait   # repo ildizida
```

## Muhit o'zgaruvchilari

| O'zgaruvchi | Kim o'qiydi | Izoh |
| ----------- | ----------- | ---- |
| `NEXT_PUBLIC_API_BASE` | brauzer | **Build vaqtida** bundle'ga yoziladi (`Dockerfile` da `ARG`). Runtime'da o'zgartirib bo'lmaydi. |
| `API_BASE_INTERNAL` | SSR | Konteyner ichidan API manzili (`http://api:8000/api/v1`). Brauzerdagi `localhost` SSR uchun ishlamaydi. |

API boshqa origin'da bo'lgani uchun backend'da `CORS_ALLOWED_ORIGINS` va
`CSRF_TRUSTED_ORIGINS` shu manzilni o'z ichiga olishi shart — aks holda
kirgan foydalanuvchining har bir POST'i CSRF Origin tekshiruvida yiqiladi.

## Tekshiruvlar

```bash
npm run lint && npm run typecheck && npm run build
```

## UI

Layout va komponentlar [TailAdmin](https://github.com/TailAdmin/free-nextjs-admin-dashboard)
(MIT) asosida: sidebar, header, karta va jadval patternlari `src/layout/`
va `src/components/ui/` ichiga **ko'chirilib moslashtirilgan** — paket
sifatida bog'lanmagan.

RankWant o'zgartirishlari:

- `brand-*` palitrasi TailAdmin ko'kidan RankWant accent (`#5b8cff`) ga almashtirilgan;
- qorong'u rejim standart, sirtlar mavjud `#0b0d12` / `#141821` palitrasida;
- ikonkalar inline SVG (`src/icons/`) — TailAdmin `@svgr/webpack` + 58 SVG
  fayl o'rniga, ortiqcha dependency qo'shmaslik uchun;
- demo sahifalar, mock auth va ishlatilmaydigan paketlar (apexcharts,
  flatpickr, fullcalendar, jsvectormap, swiper) **ko'chirilmagan**.

TailAdmin MIT litsenziyasi ostida tarqatiladi; mualliflik huquqi
TailAdmin mualliflariga tegishli.
