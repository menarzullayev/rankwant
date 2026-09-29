import type { Route } from "next";
import { redirect } from "next/navigation";

/** Eski `/stats` manzili — kanonik tabga yo'naltiradi. */
export const dynamic = "force-dynamic";

type Props = { params: Promise<{ slug: string }> };

export default async function ProblemStatsRedirect({ params }: Props) {
  const { slug } = await params;
  redirect(`/problems/${slug}?tab=statistics` as Route);
}
