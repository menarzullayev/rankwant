import type { Route } from "next";
import { redirect } from "next/navigation";

/** Eski `/status` manzili — kanonik tabga yo'naltiradi.
 *
 *  Ulashilgan havolalar 404 emas, `/problems/[slug]?tab=attempts&...`
 *  ga tushadi. Filtrlar saqlanadi, `cursor` ham (yangi panel o'sha
 *  formatni o'qiydi). `redirect()` — shartsiz, shuning uchun bu route
 *  hech qanday ma'lumot so'ramaydi.
 */
export const dynamic = "force-dynamic";

type Props = {
  params: Promise<{ slug: string }>;
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

export default async function ProblemStatusRedirect({
  params,
  searchParams,
}: Props) {
  const { slug } = await params;
  const query = await searchParams;
  const paramsOut = new URLSearchParams({ tab: "attempts" });
  for (const key of [
    "cursor",
    "verdict",
    "language",
    "mine",
    "username",
    "ordering",
    "size",
  ] as const) {
    const value = query[key];
    const first = Array.isArray(value) ? value[0] : value;
    if (first) paramsOut.set(key, first);
  }
  redirect(`/problems/${slug}?${paramsOut}` as Route);
}
