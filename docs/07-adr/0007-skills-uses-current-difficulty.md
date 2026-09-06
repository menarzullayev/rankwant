# ADR-0007: Skills reyting joriy qiyinlikdan hisoblanadi

**STATUS:** accepted (2026-09-06)
**Ta'siri:** qulflangan [04-prd](../04-prd/README.md) dagi monotonlik kafolati **tuzatildi**

## Muammo

[04-prd § Reyting formulalari](../04-prd/README.md#reyting-formulalari) Skills reyting uchun **«Monoton — hech qachon tushmaydi»** deb kafolat bergan edi. Bu kafolat formulaning o'zi uchun to'g'ri (isbotlangan: yangi masala qo'shish yig'indini kamaytirmaydi).

Lekin u bitta narsani hisobga olmagan: **`Problem.difficulty` o'zgarishi mumkin.** Masala qiyinligi dastlab taxminan beriladi, statistika yig'ilgach qayta baholanadi. Agar masala 2000 dan 1500 ga tushirilsa, uni allaqachon yechganlarning Skills reytingi **o'zlari hech narsa qilmasdan** tushadi.

## Variantlar

| # | Variant | Monotonlik | Izchillik |
| - | ------- | ---------- | --------- |
| 1 | `difficulty_at_solve` muzlatiladi | ✅ saqlanadi | ❌ bir masala turli userlarga turlicha ball |
| 2 | `max(yechilgandagi, joriy)` | ✅ saqlanadi | ⚠️ qisman |
| 3 | **Har doim joriy qiymat** | ❌ buziladi | ✅ to'liq |
| 4 | Qiyinlik hech qachon o'zgarmaydi | ✅ | ❌ arxiv sifati pasayadi |

## Tanlov

**Variant 3 — har doim joriy qiyinlik.**

## Sabab

- **Leaderboard adolatliligi ustun.** Reyting foydalanuvchilarni bir-biri bilan solishtiradi. Muzlatilgan qiymatda 2027 da yechgan va 2030 da yechgan ikki foydalanuvchi bir xil masala uchun turli ball olardi — reyting taqqoslash vositasi sifatida buziladi.
- **Arxiv sifati vaqt bilan yaxshilanadi.** Dastlabki qiyinlik taxmin; yuzlab submit'dan keyin haqiqiy qiyinlik ma'lum bo'ladi. Eski, noto'g'ri bahoni abadiy saqlash — xatoni abadiylashtirish.
- Muzlatilgan qiymat auditni ham murakkablashtiradi: «nega bu ikki odamda bir xil masala uchun har xil ball?» degan savol tez-tez chiqadi.

## Kafolatning tuzatilgan shakli

> **Skills reyting foydalanuvchining o'z harakatidan hech qachon kamaymaydi.**
> Yangi masala yechish reytingni hech qachon tushirmaydi (bu formulaning isbotlangan xossasi).
> Reyting faqat **masala qayta baholanganda** o'zgarishi mumkin — bu foydalanuvchi harakati emas, platforma qarori.

## Mitigatsiya (majburiy — principle #2 uchun)

Kafolat zaiflashgani uchun **shaffoflik kuchaytiriladi**:

1. **`RatingHistory` audit yozuvi** — har bir o'zgarish sababi bilan saqlanadi:
   `«Masala #123 qayta baholandi: 2000 → 1500 · Skills: 4 820 → 4 735 (−85)»`
2. **Foydalanuvchiga bildirishnoma** — reyting qayta baholash tufayli o'zgarsa xabar beriladi
3. **Qayta baholash siyosati** — yakka-yakka emas, **partiyada va oldindan e'lon bilan**; kamida N ta submit statistikasi to'planganidan keyin
4. **Profil sahifasida** «Skills reyting qanday hisoblanadi» havolasi — formula va qayta baholash siyosati ochiq

## Texnik oqibatlar

- `UserSolvedProblem` — `difficulty_at_solve` **audit uchun** saqlanadi, lekin formulada ishlatilmaydi
- `Problem.difficulty` o'zgarganda **Celery task** ishga tushadi: `UserSolvedProblem(problem_id=…)` bo'yicha barcha foydalanuvchilar Skills reytingi qayta hisoblanadi
- Shu sabab `UserSolvedProblem.problem_id` ga **indeks majburiy**
- Skills odatda inkremental (har AC da), qayta baholashda esa batch

## Oqibatlar

- `04-prd` dagi «Monoton» qatori tuzatildi va bu ADR ga havola qo'yildi (lock jurnaliga yozildi)
- `05-domain-model` ga `RatingHistory` entity qo'shildi
- Qayta baholash **arzon operatsiya emas** — mashhur masalada minglab foydalanuvchi qayta hisoblanadi; partiyada bajarish shart

## Bog'liq hujjatlar

- [0006-rating-model.md](0006-rating-model.md)
- [../04-prd/README.md](../04-prd/README.md)
