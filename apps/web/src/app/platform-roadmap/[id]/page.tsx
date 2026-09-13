import type { Metadata, Route } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { Card } from "@/components/ui/Card";
import { Markdown } from "@/components/Markdown";
import { RoadmapCommentForm } from "@/components/RoadmapCommentForm";
import { RoadmapStatusBadge } from "@/components/RoadmapStatusBadge";
import { RoadmapVote } from "@/components/RoadmapVote";
import { getLocale } from "@/i18n/server";
import { date, t } from "@/i18n/messages";
import { ApiError, api } from "@/lib/api";

export const dynamic = "force-dynamic";

type Props = { params: Promise<{ id: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  const locale = await getLocale();
  const item = await api.roadmapItem(Number(id)).catch(() => null);
  if (!item) return { title: t(locale, "roadmap.title") };
  return {
    title: item.title,
    description: item.body.slice(0, 160),
    alternates: { canonical: `/platform-roadmap/${item.id}` },
  };
}

export default async function RoadmapItemPage({ params }: Props) {
  const { id } = await params;
  const locale = await getLocale();

  const numeric = Number(id);
  if (!Number.isInteger(numeric) || numeric <= 0) notFound();

  const item = await api.roadmapItem(numeric).catch((error: unknown) => {
    if (error instanceof ApiError && error.status === 404) return null;
    throw error;
  });
  if (!item) notFound();

  const comments = await api.roadmapComments(item.id).catch(() => []);

  /** Holat tarixi — uchta o'tish vaqtidan. Bo'sh bosqichlar
   *  ko'rsatilmaydi: "hali bo'lmagan" narsani sanab chiqish shovqin. */
  const steps: { label: string; at: string | null }[] = [
    { label: t(locale, "roadmap.plannedAt"), at: item.planned_at },
    { label: t(locale, "roadmap.startedAt"), at: item.started_at },
    { label: t(locale, "roadmap.releasedAt"), at: item.released_at },
  ].filter((step) => step.at !== null);

  return (
    <article className="space-y-6">
      <Link
        href={"/platform-roadmap" as Route}
        className="inline-block text-theme-sm rw-accent-ink hover:underline"
      >
        ← {t(locale, "roadmap.back")}
      </Link>

      <header className="space-y-3">
        <div className="flex flex-wrap items-center gap-2">
          <RoadmapStatusBadge status={item.status} locale={locale} />
          {item.target_quarter && (
            <span className="text-theme-xs rw-faint">
              {t(locale, "roadmap.quarter")}: {item.target_quarter}
            </span>
          )}
        </div>
        <h1 className="text-title-sm font-bold rw-strong">{item.title}</h1>
        <p className="text-theme-sm rw-faint">
          {item.author ? (
            <>
              {t(locale, "roadmap.author")}:{" "}
              <Link
                href={`/users/${item.author}`}
                className="rw-accent-ink hover:underline"
              >
                {item.author_name || item.author}
              </Link>
              {" · "}
            </>
          ) : null}
          {date(item.created_at, locale)}
        </p>
      </header>

      <div className="flex flex-wrap items-center gap-3">
        <RoadmapVote
          id={item.id}
          initialVoted={item.has_voted}
          initialCount={item.vote_count}
        />
        {item.update_id !== null && (
          <Link
            href={`/updates/${item.update_id}`}
            className="text-theme-sm font-medium rw-accent-ink hover:underline"
          >
            {t(locale, "roadmap.changelog")} ↗
          </Link>
        )}
      </div>

      {/* Rad etilgan taklif yashirilmaydi — sababi aytiladi. */}
      {item.status === "declined" && (
        <p className="rw-radius border rw-line px-4 py-3 text-theme-sm rw-dim">
          {t(locale, "roadmap.declinedHint")}
        </p>
      )}

      {item.body && (
        <Card>
          <Markdown>{item.body}</Markdown>
        </Card>
      )}

      {steps.length > 0 && (
        <Card title={t(locale, "roadmap.timeline")}>
          <ol className="space-y-2">
            {steps.map((step) => (
              <li key={step.label} className="flex flex-wrap gap-2 text-theme-sm">
                <span className="font-medium rw-strong">{step.label}</span>
                <span className="rw-faint">{date(step.at ?? "", locale)}</span>
              </li>
            ))}
          </ol>
        </Card>
      )}

      <Card
        title={`${t(locale, "roadmap.comments")} · ${comments.length}`}
        bodyClassName="space-y-5"
      >
        {comments.length === 0 ? (
          <p className="text-theme-sm rw-faint">
            {t(locale, "roadmap.noComments")}
          </p>
        ) : (
          <ul className="divide-y rw-divide">
            {comments.map((comment) => (
              <li key={comment.id} className="py-3">
                <p className="flex flex-wrap items-center gap-2 text-theme-xs rw-faint">
                  {comment.author ? (
                    <Link
                      href={`/users/${comment.author}`}
                      className="font-medium rw-accent-ink hover:underline"
                    >
                      {comment.author_name || comment.author}
                    </Link>
                  ) : (
                    <span>{t(locale, "roadmap.deletedUser")}</span>
                  )}
                  <span>{date(comment.created_at, locale)}</span>
                </p>
                <p className="mt-1 whitespace-pre-wrap text-theme-sm rw-dim-2">
                  {comment.body}
                </p>
              </li>
            ))}
          </ul>
        )}

        <RoadmapCommentForm itemId={item.id} />
      </Card>
    </article>
  );
}
