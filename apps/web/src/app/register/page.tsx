import type { Metadata } from "next";
import type { Route } from "next";
import { redirect } from "next/navigation";

import { getLocale } from "@/i18n/server";

/** Ro'yxatdan o'tish endi bitta sahifaning bo'limi (1-qaror):
 *  `/kirish?tab=royxat`. Sabab `/login` bilan bir xil — havola
 *  saqlanadi, `?next=` esa yo'qolmaydi (307, 301 emas). */
export default async function RegisterPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const query = new URLSearchParams({ tab: "royxat" });
  const params = await searchParams;
  const next = params.next;
  if (typeof next === "string" && next) query.set("next", next);
  redirect(`/kirish?${query}` as Route);
}

/** Ishlatilmaydi — `redirect` oldin bajariladi. */
export async function generateMetadata(): Promise<Metadata> {
  await getLocale();
  return { title: "RankWant" };
}
