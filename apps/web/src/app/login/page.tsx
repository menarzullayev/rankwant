import type { Metadata } from "next";
import type { Route } from "next";
import { redirect } from "next/navigation";

import { getLocale } from "@/i18n/server";
import { parseTab } from "@/lib/auth-tabs";

/** Kirish va ro'yxatdan o'tish endi bitta sahifada (1-qaror):
 *  `/kirish?tab=kirish` va `/kirish?tab=royxat`.
 *
 *  Havolalar SAQLANADI: `/login` email xatlarida, xatcho'plarda va
 *  boshqa saytlarda uchraydi. Ularni shunchaki o'chirish o'sha
 *  havolalarni sindirardi.
 *
 *  `redirect()` = 307, ya'ni `?next=...` saqlanib o'tadi. `next.config.ts`
 *  dagi 301 qoidasi parametrlarni tashlab yuborardi va himoyalangan
 *  sahifadan uchirilgan odam login'dan keyin bosh sahifaga tushib
 *  qolardi — shuning uchun bu yerda `permanentRedirect` ATAYLAB
 *  ishlatilmaydi. */
async function go(tab: "kirish" | "royxat", params: RouteQuery) {
  const query = new URLSearchParams({ tab });
  for (const key of ["next", "link", "social"] as const) {
    const value = params[key];
    if (typeof value === "string" && value) query.set(key, value);
  }
  return redirect(`/kirish?${query}` as Route);
}

type RouteQuery = Record<string, string | string[] | undefined>;

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<RouteQuery>;
}) {
  return go("kirish", await searchParams);
}

/** Ishlatilmaydi — `redirect` oldin bajariladi. Sarlavha baribir
 *  o'qiladi: brauzer yangi manzilga o'tayotganda eski sahifaning
 *  `<title>` i ko'rinib turadi. */
export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getLocale()) && "RankWant" };
}
