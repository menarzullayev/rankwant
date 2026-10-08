# ADR 0054 — Web'da kirish darajalari: mehmon nimani ko'radi

**STATUS:** accepted
**Sana:** 2026-10-08
**Tasdiqlagan:** Saidakbar (owner) — 2026-10-08, 12 savol va prototip (8 holat)
**Ta'sir doirasi:** `apps/web/src/lib/access.ts`, `lib/access.server.ts`, `proxy.ts`, `components/auth/`, masala sahifasi, shaxsiy panellar, `tools/check_access.py`
**Dalil:** o'lchov 2026-10-08 — jonli saytda mehmon sifatida 15 yo'l va 9 API manzili so'raldi

## 1. Muammo

Ma'lumotni himoya qiladigan chegara — API (`IsAuthenticatedOrReadOnly`,
xodim guruhlari). U to'g'ri ishlaydi va bu ADR uni o'zgartirmaydi. Muammo
web qatlamida edi:

- 80 sahifadan faqat uchtasi (`/settings`, `/settings/<bo'lim>`,
  `/onboarding`) mehmonni serverda qaytarardi;
- `/notifications` va `/admin` ning 24 sahifasi mehmonga **200** qaytarib,
  brauzerda «ruxsat yo'q» matnini chizardi — admin qobig'i hammaga yuborilardi;
- masala sahifasida yechim paneli (muharrir, til tanlash, namunada sinash)
  mehmonga to'liq chizilardi, faqat «Yuborish» o'rnida havola turardi;
- «kim nimani ochadi» qoidasi uch joyda yozilgan, hech qayerda ro'yxat yo'q;
- sessiya sahifa ochiq turganda tugasa, odam buni faqat amali jim
  bajarilmagani bilan bilardi.

## 2. Qaror

### 2.1. To'rt daraja, bitta ro'yxat

`apps/web/src/lib/access.ts` — yo'lning **birinchi bo'lagi** → daraja:

| Daraja | Kim | Mehmon nima oladi |
|---|---|---|
| `public` | hamma | sahifa ochiq; ichidagi shaxsiy blok o'rnida kirish kartasi |
| `guest` | kirmaganlar (`/login`) | — (kirgan odam davom ettiriladi) |
| `user` | kirganlar | `307 → /login?tab=login&next=<manzil>` |
| `staff` | xodimlar | mehmon — login'ga; kirgan, lekin xodim emas — **404** |

«Emaili tasdiqlangan» darajasi yo'q: tasdiqlanmagan hisob hozirgidek to'liq
ishlaydi (eslatma tasmasi qoladi). Kerak bo'lsa alohida qaror.

### 2.2. Uch qatlam

1. **`proxy.ts`** — `user`/`staff` yo'lida sessiya cookie'si umuman bo'lmasa,
   sahifa kodi yurmasdan va API so'ralmasdan login'ga yo'naltiradi.
2. **Server qo'riqchisi** (`requireUser`, `requireStaff`) — cookie bor, lekin
   yaroqsiz yoki xodim emas holatini `/me/` orqali hal qiladi. Sahifaning
   hech narsasi yuborilmaydi.
3. **API** — haqiqiy chegara, o'zgarmaydi.

### 2.3. Mehmonga ko'rinish

- **Sof shaxsiy sahifa** — yo'naltirish, kirgach o'sha manzilga qaytish.
- **Aralash sahifa** — ommaviy qism ko'rinadi; shaxsiy blok **chizilmaydi**,
  o'rnida bitta umumiy `SignInGate` kartasi: sarlavha, bir qator sabab,
  «Kirish» va «Ro'yxatdan o'tish» (ikkalasi shu sahifaga qaytaradi).
- **Masala sahifasi** — shart, namunalar, limitlar ochiq. Yechim paneli
  serverda hal qilinadi: mehmon sahifasida muharrirning belgilari ham,
  ma'lumoti ham, Monaco fayli ham yo'q. Telefonda pastki varaq va uni
  ochadigan tugma ham yo'q — karta shart ostida turadi.
- Xuddi shu qoida: tahlil (editorial), urinishning manba kodi, test
  savollari, arena, xakaton topshirig'i, duel, auditoriya, Qvant balansi.
- **Kichik amallar** (kuzatish, ovoz, sevimli, shikoyat, izoh) — tugma
  ko'rinadi; mehmon bossa sahifadan chiqmasdan kichik oyna (`GuestPrompt`).

Ochiq qoladi (ataylab): urinishlar lentasi va urinish natijasi, masalaning
Statistika / Yechganlar / Urinishlar tablari, profil va xaridlar sahifasi.

### 2.4. Tugagan sessiya

API mijozi har 401 ni e'lon qiladi. Sahifa o'zini kirgan deb bilsa, `/me/`
yana bir marta so'raladi — bitta manzilning 401 i ham, tarmoq xatosi ham
sessiya tugaganini bildirmaydi. Faqat `/me/` «hech kim» desa xabar chiqadi
va 5 soniyadan keyin sahifa `/login?next=<joriy manzil>` ga o'tadi.
Muharrirdagi kod — brauzerdagi qoralama, qaytganda joyida.

### 2.5. Qo'riqchi

`tools/check_access.py` (CI): har sahifaning bo'limi ro'yxatda bo'lishi
shart; ro'yxatda sahifasiz yozuv bo'lmasligi shart; `user`/`staff`
bo'limining har sahifasi tegishli server qo'riqchisi ortida bo'lishi shart
(izohdagi chaqiruv hisobga olinmaydi); `proxy.ts` ro'yxatdan foydalanishi
shart.

## 3. Rad etilgan variantlar

- **Faqat klient tekshiruvi** (`<Can>`) — avvalgi holat: sahifa baribir
  yuboriladi va 200 qaytadi.
- **Faqat `proxy.ts`** — cookie borligini ko'radi, yaroqliligini emas;
  xodimni ajrata olmaydi.
- **Masala sahifasini butunlay yopish** — masalalar qidiruv tizimidan
  yo'qolardi (ADR-0023).
- **Muharrirni chizib, ustidan qoplama qo'yish** — belgilar va Monaco
  baribir yuklanadi; «ko'rmasligi kerak» talabiga javob bermaydi.
- **Karta ichida kirish formasi** — ijtimoiy kirish, Turnstile va xatolar
  uchun forma ikki joyda yashardi.

## 4. Oqibatlar

- Mehmon masala sahifasida kod yoza olmaydi va namunada sinay olmaydi —
  bu ataylab. Narxi: «avval sinab ko'rib, keyin ro'yxatdan o'tish» yo'li
  yopildi.
- `/admin` begonaga 404 beradi; xodim huquqi olib tashlangan odam ham
  sababini ko'rmaydi.
- Yangi yuqori darajali bo'lim qo'shilganda `access.ts` ga yozilmasa CI
  yiqiladi.
- Mehmon keshi (`/`, `/login`, huquqiy sahifalar, `/problems`) o'zgarmadi;
  yo'naltirish javoblari `private, no-store`.
