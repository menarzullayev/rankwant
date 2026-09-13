import type { Metadata } from "next";
import type { Route } from "next";
import { redirect } from "next/navigation";

import { getLocale } from "@/i18n/server";

/** `/register` — yo'naltiruvchi manzil, sahifa emas. Ro'yxatdan o'tish
 *  bitta sahifaning bo'limi (1-qaror): `/login?tab=register`.
 *  Sabab `/reset-password` bilan bir xil — `redirect()` 307 beradi,
 *  ya'ni `?next=` yo'qolmaydi (`next.config.ts` dagi 301 qoidasi uni
 *  tashlab yuborardi). */
export default async function RegisterPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const query = new URLSearchParams({ tab: "register" });
  const params = await searchParams;
  const next = params.next;
  if (typeof next === "string" && next) query.set("next", next);
  redirect(`/login?${query}` as Route);
}

/** Ishlatilmaydi — `redirect` oldin bajariladi. */
export async function generateMetadata(): Promise<Metadata> {
  await getLocale();
  return { title: "RankWant" };
}
