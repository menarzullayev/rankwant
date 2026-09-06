# ADR-0008: Auth — session cookie (web) + Personal Access Token (API)

**STATUS:** accepted (2026-09-06)
**Ta'siri:** qulflangan [05-domain-model](../05-domain-model/README.md) ga `ApiToken` entity qo'shiladi

## Muammo

Vision goal #5 — **«ochiq API — mobile va uchinchi tomon integratsiyasi»**. Shu bilan birga frontend Next.js SSR ([ADR-0003](0003-stack-django-next.md)) va Telegram bot auth rejalashtirilgan. Bitta auth mexanizmi ikkala ehtiyojni ham yaxshi qoplay olmaydi.

## Variantlar

| # | Variant | Web (SSR) | Uchinchi tomon | Xavf |
| - | ------- | --------- | -------------- | ---- |
| 1 | **Session + PAT** | ✅ tabiiy | ✅ PAT | past |
| 2 | JWT access + refresh | ⚠️ saqlash muammosi | ✅ | **revocation qiyin** |
| 3 | Faqat session | ✅ | ❌ | past, lekin goal #5 bajarilmaydi |
| 4 | To'liq OAuth2 | ✅ | ✅ | MVP uchun og'ir |

## Tanlov

**Variant 1** — web uchun Django session (httpOnly cookie), API/bot uchun **Personal Access Token**.

## Sabab

- **XSS yuzasi nolga tushadi.** Token JavaScript'da saqlanmaydi; `httpOnly` cookie'ni skript o'qiy olmaydi. JWT'ni `localStorage` da saqlash eng keng tarqalgan real zaiflik.
- **Bekor qilish oson.** Session va PAT ikkalasi ham server tomonda — o'g'irlangan bo'lsa darhol o'chiriladi. JWT'da bu blacklist talab qiladi, ya'ni «statesizlik» afzalligi baribir yo'qoladi.
- **SSR bilan tabiiy** — Next.js server so'rovga cookie'ni uzatadi, qo'shimcha token boshqaruvi kerak emas.
- **GitHub modeli** — foydalanuvchi o'zi token yaratadi, nom beradi, scope beradi, bekor qiladi. Ochiq API uchun tushunarli va isbotlangan.

OAuth2 rad etilmadi — uchinchi tomon **ilovalari** paydo bo'lganda alohida ADR bilan qo'shiladi. Hozir 0 ta shunday ilova bor.

## Texnik qoidalar

**Session:**

- Backend: Redis
- Cookie: `httpOnly`, `Secure`, `SameSite=Lax`
- CSRF: Django CSRF token; Next.js SSR uzatadi
- Muddat: 30 kun, faollikda yangilanadi

**Personal Access Token:**

- Format: `rw_` prefiks + 32 bayt tasodifiy (base62)
- Saqlash: **faqat SHA-256 hash**; to'liq token bir marta, yaratilganda ko'rsatiladi
- `scopes`: `read`, `submit`, `contest:manage` — minimal ruxsat prinsipi
- `expires_at` majburiy (maksimal 1 yil), `last_used_at` kuzatiladi
- Bir foydalanuvchida maksimal 10 ta faol token

**Telegram auth:** Telegram login widget imzosi tekshiriladi → `User.telegram_id` bog'lanadi → **session ochiladi** (PAT emas).

## Yangi entity — `ApiToken`

| Maydon | Tavsif |
| ------ | ------ |
| `user_id`, `name` | foydalanuvchi bergan nom |
| `prefix` | ko'rsatish uchun (`rw_a1b2…`) |
| `token_hash` | SHA-256, uniq |
| `scopes` | massiv |
| `expires_at`, `last_used_at`, `revoked_at` | |
| `created_at` | |

Indeks: uniq `(token_hash)`, `(user_id, revoked_at)`.

## Rate limit

| Subyekt | Limit |
| ------- | ----- |
| Anonim | 60 so'rov/min |
| Session yoki PAT | 300 so'rov/min |
| Submit | 1 ta / 10 soniya / foydalanuvchi |
| Auth urinishi | 10 / 15 min / IP |

## Oqibatlar

- `05-domain-model` ga `ApiToken` qo'shildi (lock jurnaliga yozildi)
- `08-technical-spec` auth bo'limi shu ADR asosida to'ldiriladi
- Mobil ilova (out of scope v1) PAT bilan ishlay oladi — qayta arxitektura kerak emas
- OAuth2 — kelajakda alohida ADR

## Bog'liq hujjatlar

- [0003-stack-django-next.md](0003-stack-django-next.md)
- [../05-domain-model/README.md](../05-domain-model/README.md)
