/** Auth bo'limlari — manzil ↔ til biladigan qism (SOF modul).

 *  `AuthTabs` dan ALOHIDA turadi va bu shart: `AuthTabs` — klient
 *  komponenti, uning yuklanishini `"use client"` faylidan import
 *  qilish SERVER komponentini ham klient to'plamiga tortib ketardi,
 *  ya'ni SSR (SEO) afzalligi yo'qolardi. Bu faylda na `"use client"`,
 *  na React importi bor — faqat ro'yxat va tekshiruv.
 *
 *  SHU FAYL MANBA: `AuthTabs`, `/kirish` sahifasi va eski
 *  `/login`·`/register` yo'naltirishlari bo'lim nomlarini shu yerdan
 *  oladi. Ikki joyda yozilsa, biri o'zgarganda ikkinchisi jimgina
 *  eskirib qolardi.
 */

export const TABS = ["kirish", "royxat", "parolni-tiklash"] as const;
export type TabId = (typeof TABS)[number];

/** Tablar QATORIDA ko'rsatiladigan bo'limlar — `TABS` ning OST-TO'PLAMI.
 *
 *  Nega alohida ro'yxat: `parolni-tiklash` — haqiqiy bo'lim (manzili bor,
 *  xatdagi `?token=` shu yerga keladi, `/reset-password` ham shu yerga
 *  yo'naltiradi), ya'ni u `TABS` dan CHIQARILMAYDI. Lekin qatorda
 *  ko'rsatilmaydi.
 *
 *  SABAB (2026-09-13 da o'lchandi): `AuthTabs` `grid-cols-3` bilan uchta
 *  teng ustun yasaydi. 360px enli ekranda har ustunga ~68px tegadi,
 *  "Parolni tiklash" esa 89px o'lchamida bo'ladi — ya'ni matn o'rtasidan
 *  kesiladi (`truncate`). Bu FAQAT o'zbekchaga xos emas: o'lchov 10 tildan
 *  9 tasida kesilishini ko'rsatdi:
 *
 *      kk −115px · es −71px · ky −70px · tg −64px · uz −14px · en −23px …
 *
 *  `zh` (重置密码) yagona sig'adigani. "Ro'yxatdan o'tish" esa 414px gacha
 *  ham kesilardi. Uchta teng ustun bilan bu muammoni HAL QILIB BO'LMAYDI:
 *  qisqartirish yoki ikonka kerak bo'lardi, ikkalasi ham ma'no
 *  yo'qotadi. Shuning uchun qatorda ikkita QISQA va BARQAROR yozuv
 *  qoldi — ular hech qaysi tilda kesilmaydi.
 *
 *  Parolni tiklash shu sababli yo'qolmadi: uni kirish formasidagi
 *  "Parolni unutdingizmi?" havolasi ochadi (`AuthForm.tsx`) — bu odam
 *  uni qidiradigan joy, tab qatori emas. */
export const TAB_BAR: readonly TabId[] = ["kirish", "royxat"];

/** Manzil qatoridagi `?tab=` bo'lmasa yoki noto'g'ri bo'lsa shu. */
export const DEFAULT_TAB: TabId = "kirish";

/** Manzil qatoridagi `?tab=` ni bo'limga aylantiradi — SOF funksiya.
 *
 *  Noma'lum qiymat `null` qaytaradi, ya'ni chaqiruvchi standart holatga
 *  tushadi. Buzuq qiymatni jimgina qabul qilish bo'sh panel
 *  ko'rsatardi: bo'lim faqat ro'yxatdagi uchtadan biri bo'lishi mumkin.
 */
export function parseTab(raw: string | null | undefined): TabId | null {
  return (TABS as readonly string[]).includes(raw ?? "")
    ? (raw as TabId)
    : null;
}
