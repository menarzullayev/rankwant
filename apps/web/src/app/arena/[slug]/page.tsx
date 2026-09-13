import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { ArenaPlayer } from "@/components/ArenaPlayer";
import { Badge } from "@/components/ui/Badge";
import { getLocale } from "@/i18n/server";
import { dateTime, t } from "@/i18n/messages";
import { api, ApiError } from "@/lib/api";

type Props = { params: Promise<{ slug: string }> };
export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  try {
    return { title: (await api.arena(slug)).title };
  } catch {
    return { title: "404" };
  }
}

export default async function ArenaPage({ params }: Props) {
  const { slug } = await params;
  const locale = await getLocale();
  let arena;
  try {
    arena = await api.arena(slug);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }
  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-title-sm font-bold rw-strong">{arena.title}</h1>
        <div className="mt-2 flex flex-wrap items-center gap-2">
          <Badge>
            {arena.question_count} {t(locale, "quiz.questions")}
          </Badge>
          <Badge>
            {arena.seconds_per_question}
            {t(locale, "arena.perQuestion")}
          </Badge>
          <Badge color="brand">+{arena.reward_qvant} Qvant</Badge>
          <span className="text-theme-xs rw-faint">
            {dateTime(arena.start_at, locale)}
          </span>
        </div>
        {arena.description && (
          <p className="mt-2 text-theme-sm rw-dim">{arena.description}</p>
        )}
      </header>
      <ArenaPlayer initial={arena} />
    </div>
  );
}
