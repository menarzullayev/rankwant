import type { Metadata } from "next";
import type { Route } from "next";
import { redirect } from "next/navigation";

import { getLocale } from "@/i18n/server";

/** Kanonik manzil endi `/login?tab=reset-password` (1-qaror): uch
 *  bo'lim bitta sahifada, ya'ni odam bo'limlar orasida erkin
 *  yurishi kerak.
 *
 *  `redirect()` Next'da 307 beradi (metod va tanani saqlaydi), shuning
 *  uchun `?token=...` ham `?next=...` ham yo'qolmaydi — `next.config.ts`
 *  dagi 301 qoidasi esa parametrlarni TASHLAB yuborardi va xatdagi
 *  havola ishlamay qolardi. */
export default async function ResetPasswordPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const query = new URLSearchParams({ tab: "reset-password" });
  const params = await searchParams;

  //: `token` — xatdagi havola. U bo'lmasa bu shunchaki bo'lim almashuvi
  //: bo'lardi va bo'sh token bilan «yangi parol» formasi ochilardi.
  for (const key of ["token", "next"] as const) {
    const value = params[key];
    if (typeof value === "string" && value) query.set(key, value);
  }

  //: `generateMetadata` SHART EMAS: bu sahifa hech qachon chizilmaydi.
  //: Xato bo'lsa (masalan `?token=` juda uzun) foydalanuvchi
  //: `/reset-password` da qoladi va `reset.invalid` ni ko'radi — bu
  //: havoladan ko'ra tushunarliroq.
  redirect(`/login?${query}` as Route);
}

/** Ishlatilmaydi — `redirect` oldin bajariladi. `Metadata` uchun til
 *  o'qiladi va shu bilan `getLocale` importi ishlaydi. */
export async function generateMetadata(): Promise<Metadata> {
  await getLocale();
  return {};
}

export const dynamic = "force-dynamic";
