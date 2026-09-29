import type { Route } from "next";
import { redirect } from "next/navigation";

/** Eski `/solvers` manzili — kanonik tabga yo'naltiradi.
 *  Saralash (`?ordering=`) saqlanadi.
 */
export const dynamic = "force-dynamic";

type Props = {
  params: Promise<{ slug: string }>;
  searchParams: Promise<{ ordering?: string | string[] }>;
};

export default async function ProblemSolversRedirect({
  params,
  searchParams,
}: Props) {
  const { slug } = await params;
  const { ordering } = await searchParams;
  const first = Array.isArray(ordering) ? ordering[0] : ordering;
  redirect(
    `/problems/${slug}?tab=solvers${first ? `&ordering=${encodeURIComponent(first)}` : ""}` as Route,
  );
}
