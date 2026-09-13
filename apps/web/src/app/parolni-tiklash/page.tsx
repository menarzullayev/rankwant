import type { Metadata } from "next";
import type { Route } from "next";
import { redirect } from "next/navigation";

import { getLocale } from "@/i18n/server";

/** ESKI kanonik manzil — SAQLANADI, o'chirilmaydi.
 *
 *  `TABS` va `AuthTabs` izohi `parolni-tiklash` ni "BUZILADIGAN
 *  havolalar (`/login`, `/register`, `/parolni-tiklash`) saqlanib
 *  qoldi" deb sanaydi. `/login` va `/register` uchun yo'naltirish
 *  fayllari bor edi, bu uchtasi esa 2026-09-13 da o'chirilib
 *  yuborilgan edi — ya'ni shartnoma bir joyda yozilgan, amalda
 *  bajarilmagan.
 *
 *  Nega bu muhim: `TABS` dagi `parolni-tiklash` qiymati FAQAT manzil
 *  qatoridagi `?tab=` uchun emas. U `?token=` bilan keladigan
 *  havolaning bir qismi (`/parolni-tiklash?token=…`) va eski
 *  xatlar/xatcho'plar/tashqi saytlar ham shunday yozadi. Fayl
 *  bo'lmasa Next 404 beradi — havola sindiriladi.
 *
 *  `redirect()` 307 (metod va tanani saqlaydi), ya'ni `?token=` ham
 *  `?next=` ham o'tadi. `permanentRedirect` ATAYLAB emas: 301
 *  keshlanadi va keyin uni qaytarib bo'lmaydi. */
export default async function LegacyResetPasswordPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const params = await searchParams;
  const query = new URLSearchParams({ tab: "reset-password" });
  for (const key of ["token", "next"] as const) {
    const value = params[key];
    if (typeof value === "string" && value) query.set(key, value);
  }
  redirect(`/kirish?${query}` as Route);
}

/** Ishlatilmaydi — `redirect` oldin bajariladi. `Metadata` uchun til
 *  o'qiladi va shu bilan `getLocale` importi ishlaydi. */
export async function generateMetadata(): Promise<Metadata> {
  await getLocale();
  return {};
}

export const dynamic = "force-dynamic";
