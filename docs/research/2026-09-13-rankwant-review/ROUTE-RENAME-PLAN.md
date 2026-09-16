# RankWant — web yo'llarini 100% inglizchaga o'tkazish rejasi

Sana: 2026-09-13 · Repo: `rankwant/` (`main`, HEAD `6570380`)
**Holat: KOD TUGADI — deploy kutilmoqda.** O'zbekcha yo'l ham, stub ham qolmadi.

## Natija

4 ta commit (`ee1e0a4` dan keyin): `2b649c3` · `0276335` · `0c4c34f` · `6570380`.

| Tekshiruv | Natija |
|---|---|
| `ci-local.sh types` | ✓ |
| `ci-local.sh fast` | ✓ |
| `ci-local.sh api` | ✓ |
| `ci-local.sh web` (lint + types + build) | ✓ |
| Build route soni | **78**, o'zbekcha segment **0** |
| Deploy | ⏳ qilinmagan — `web api worker beat` TO'RTALASI qayta qurilishi kerak |


⚠️ Bu — ishlab turgan saytda breaking change. Auth yo'llari o'zgarsa,
foydalanuvchi kira olmay qolishi mumkin. Shuning uchun bosqichma-bosqich.

## 1. Yo'llar xaritasi (18 ta)

| # | Hozir | Yangi | Toifa |
|---|---|---|---|
| 1 | `kirish` | `login` | auth |
| 2 | `parolni-tiklash` | `reset-password` | auth |
| 3 | `qoshimcha-malumot` | `onboarding` | auth |
| 4 | `emailni-tasdiqlash` | `verify-email` | auth |
| 5 | `maxfiylik` | `privacy` | huquqiy |
| 6 | `shartlar` | `terms` | huquqiy |
| 7 | `sertifikat/[id]` | `certificates/[id]` | mahsulot |
| 8 | `admin/analitika` | `admin/analytics` | admin |
| 9 | `users/[u]/faoliyat` | `users/[u]/activity` | profil |
| 10 | `users/[u]/musobaqalar` | `users/[u]/contests` | profil |
| 11 | `users/[u]/obunachilar` | `users/[u]/followers` | profil |
| 12 | `users/[u]/obunalar` | `users/[u]/following` | profil |
| 13 | `users/[u]/sertifikatlar` | `users/[u]/certificates` | profil |
| 14 | `users/[u]/shaxsiy` | `users/[u]/profile` | profil |
| 15 | `users/[u]/urinishlar` | `users/[u]/attempts` | profil |
| 16 | `users/[u]/xaridlar` | `users/[u]/purchases` | profil |
| 17 | `users/[u]/yechilganlar` | `users/[u]/solved` | profil |
| 18 | `users/[u]/yutuqlar` | `users/[u]/achievements` | profil |

O'zbekcha yo'llar **butunlay o'chiriladi** — stub qoldirilmaydi.

## 2. Inglizcha stub'lar qoladi (bu boshqa narsa)

`/login`, `/register`, `/reset-password` — bugun ham mavjud va ular **inglizcha**.
Ular qoladi, faqat nishoni o'zgaradi:

```text
Hozir:  /login -> /kirish?tab=kirish
Keyin:  /register      -> /login?tab=register          (stub qoladi)
        /reset-password -> /login?tab=reset-password    (stub qoladi)
        /kirish         -> O'CHIRILADI
```

Sabab: auth — bitta sahifa, uchta bo'lim (1-qaror). Sahifa `/login` da turadi,
qolgan ikkitasi unga havola. Bu o'zbekcha stub emas, shuning uchun qarorga zid emas.

## 3. `?tab=` qiymatlari ham inglizchaga

`lib/auth-tabs.ts`: `TABS = ["kirish", "royxat", "parolni-tiklash"]`
→ `["login", "register", "reset-password"]`

Tegadigan joylar:
- `lib/auth-tabs.ts` — `TABS`, `TAB_BAR`, `DEFAULT_TAB`
- `components/auth/AuthTabs.tsx` — yozuv kalitlari, `grid-cols-N`
- `apps/api/core/emails.py` — `tab="parolni-tiklash"` → `tab="reset-password"`
- `qoshimcha-malumot/page.tsx` → `tab=kirish` → `tab=login`
- `tools/check_contract.py` — `check_tab_bar()` va `"parolni-tiklash"` tekshiruvi

## 4. ⚠️ Yagona haqiqiy oqibat — va uning narxi o'lchandi

Eski xatlardagi havolalar o'lik bo'ladi. Lekin bu **cheklangan oyna**, chunki
tokenlar tez eskiradi:

| Token | Umri | Manba |
|---|---|---|
| `PasswordResetToken` | **1 soat** | `apps/api/core/models.py:359` |
| `EmailVerifyToken` | **24 soat** | `apps/api/core/models.py:311` |

Ya'ni deploy paytida xavf ostida bo'lgan yagona havolalar:

- oxirgi **1 soat** ichida yuborilgan parol tiklash xatlari
- oxirgi **24 soat** ichida yuborilgan pochtani tasdiqlash xatlari

Bundan eski xatlardagi tokenlar **allaqachon o'lik** — havola ishlamaydi, stub
bo'lsa ham. Ya'ni stub qo'yish bu xatlarni qutqarmasdi.

**Yumshatish:** tasdiqlash uchun qayta yuborish yo'li bor
(`POST /api/v1/auth/email/resend/`), parol tiklashni esa odam qaytadan
so'rashi mumkin. Deploydan keyin 24 soat ichida "xat ishlamadi" shikoyati
bo'lsa — sabab shu.

**Doimiy oqibat:** xatcho'p va tashqi/qidiruv havolalari 404 bo'ladi.
Buni qaytarib bo'lmaydi, lekin yangi manzillar indekslanadi.

## 5. Ta'sir doirasi (o'lchandi)

| Narsa | Soni |
|---|---|
| O'zgaradigan route papkalari | 18 |
| `/kirish` ga havola qiluvchi fayllar | 30 |
| `/qoshimcha-malumot` | 11 |
| `/parolni-tiklash` | 9 |
| `/emailni-tasdiqlash` | 9 |
| `/maxfiylik`, `/shartlar` | 8 + 8 |
| Test fayllari | `test_auth.py`, `test_emails.py`, `test_oauth.py`, `test_oauth_consent.py`, `test_content.py`, `e2e/submit-ui.spec.ts` |
| CI | `check_contract.py` (`check_tab_bar`, `BARE`) |

## 6. Bosqichlar

| Bosqich | Ish | Xavf |
|---|---|---|
| **1** | `lib/auth-tabs.ts` + `AuthTabs.tsx` — tab qiymatlari | past |
| **2** | Auth sahifasi `kirish` → `login`; `kirish` va `parolni-tiklash` papkalari o'chiriladi | **yuqori** |
| **3** | Huquqiy + sertifikat + admin | past |
| **4** | 10 ta profil bo'limi | o'rta |
| **5** | `emails.py` — yangi havolalar | o'rta |
| **6** | Ichki havolalar (~75 fayl) | past |
| **7** | Testlar + `check_contract.py` | past |
| **8** | Deploy + jonli tekshiruv | — |

Har bosqichdan keyin `bash tools/ci-local.sh fast` va `bash tools/check_deploy.sh`.

## 7. Qaytarish

Har bosqich alohida commit → `git revert`. Diqqat: 2-bosqich qaytarilsa
o'zbekcha yo'llar qaytadi, ya'ni deploy ham qaytarilishi kerak.

## 8. Hal qilinishi kerak

1. **`onboarding` nomi to'g'rimi?** `qoshimcha-malumot` = "qo'shimcha ma'lumot"
   → `additional-info` ham bo'lardi.
2. **`?tab=` qiymatlari** — `login`/`register`/`reset-password` bo'lsinmi?
   Aks holda `/login?tab=kirish` kabi aralash holat qoladi.
