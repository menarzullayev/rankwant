import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { DuelDetail } from "@/components/DuelDetail";
import { api, ApiError } from "@/lib/api";

type Props = { params: Promise<{ slug: string }> };
export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  try {
    return { title: (await api.duel(slug)).title };
  } catch {
    return { title: "404" };
  }
}

export default async function DuelPage({ params }: Props) {
  const { slug } = await params;
  let duel;
  try {
    duel = await api.duel(slug);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <h1 className="text-title-sm font-bold text-gray-800 dark:text-white/90">{duel.title}</h1>
      <DuelDetail initial={duel} />
    </div>
  );
}
