import type { Metadata, Route } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { Markdown } from "@/components/ui/Markdown";
import { eventPath } from "@/features/olympiads";
import { inReaderAlphabet } from "@/i18n/alphabet";
import { getLocale } from "@/i18n/server";
import { fill, t } from "@/i18n/messages";
import { api, ApiError, type OlympiadTask } from "@/lib/api";

export const dynamic = "force-dynamic";

type Props = { params: Promise<{ event: string; task: string }> };

async function load(event: string, task: string): Promise<OlympiadTask | null> {
  try {
    return await api.olympiadTask(event, task);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) return null;
    throw error;
  }
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { event, task } = await params;
  const locale = await getLocale();
  const row = await load(event, task);
  if (row === null) return { title: t(locale, "olympiads.notFound") };
  return {
    title: `${inReaderAlphabet(row.title, "uz")} · ${inReaderAlphabet(row.event_title, "uz")}`,
    alternates: { canonical: `/olympiads/${row.event}/${row.slug}` },
  };
}

const LINK = "font-medium underline underline-offset-2 rw-accent-ink rw-focus-ring";

/** A statement of a past round (not judged here): the text, its limits, the
 *  original and where to solve it — ours first when we have the problem. */
export default async function OlympiadTaskPage({ params }: Props) {
  const { event, task: slug } = await params;
  const locale = await getLocale();
  const task = await load(event, slug);
  if (task === null) notFound();
  const kepSource = task.links.find((row) => row.kind === "original");

  return (
    <article className="mx-auto max-w-4xl space-y-6">
      <nav aria-label={t(locale, "olympiads.breadcrumbs")} className="flex flex-wrap gap-1.5 text-theme-sm rw-dim">
        <Link href={"/olympiads" as Route} className="rw-focus-ring hover:underline">
          {t(locale, "olympiads.title")}
        </Link>
        <span aria-hidden>/</span>
        <Link href={eventPath(task.event) as Route} className="rw-focus-ring hover:underline">
          {inReaderAlphabet(task.event_title, "uz")}
        </Link>
      </nav>
      <header>
        <h1 className="text-title-sm font-bold rw-strong">
          {task.code && <span className="rw-faint">{task.code}. </span>}
          {inReaderAlphabet(task.title, "uz")}
        </h1>
        {task.original_title && (
          <p className="mt-1 text-theme-sm rw-faint" lang="en">
            {task.original_title}
          </p>
        )}
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <Badge>{inReaderAlphabet(task.set_title, "uz")}</Badge>
          {task.time_limit_ms !== null && task.memory_limit_mb !== null && (
            <Badge>{fill(t(locale, "olympiads.limits"), { ms: task.time_limit_ms, mb: task.memory_limit_mb })}</Badge>
          )}
          {task.max_score !== null && <Badge>{fill(t(locale, "olympiads.maxScore"), { score: task.max_score })}</Badge>}
        </div>
      </header>

      {task.from_kep && (
        <p className="rw-radius-sm rw-warn-soft px-4 py-3 text-theme-sm rw-warn-ink" data-kep-note="">
          {t(locale, "olympiads.kepNote")}{" "}
          {kepSource && (
            <a href={kepSource.url} target="_blank" rel="noopener noreferrer" className={LINK}>
              {kepSource.url}
              <span className="sr-only"> {t(locale, "footer.opensNewTab")}</span>
            </a>
          )}
        </p>
      )}

      {task.statement && (
        <Card>
          <Markdown lang="uz">{task.statement}</Markdown>
        </Card>
      )}

      {(task.practice_here.length > 0 || task.links.length > 0) && (
        <Card title={t(locale, "olympiads.solve")}>
          <ul className="space-y-2 text-theme-sm">
            {task.practice_here.map((problem) => (
              <li key={problem.slug}>
                <Link href={`/problems/${problem.slug}` as Route} className={LINK}>
                  {fill(t(locale, "olympiads.solveHere"), { title: problem.title })}
                </Link>
              </li>
            ))}
            {task.links.map((row) => (
              <li key={`${row.kind}-${row.url}`}>
                <a href={row.url} target="_blank" rel="noopener noreferrer nofollow" className={LINK}>
                  {inReaderAlphabet(row.title, "uz")}
                  <span className="sr-only"> {t(locale, "footer.opensNewTab")}</span>
                </a>
                {row.platform && <span className="ml-2 text-theme-xs rw-faint">{row.platform}</span>}
              </li>
            ))}
            {task.statement_pdf && (
              <li>
                <a href={task.statement_pdf} target="_blank" rel="noopener noreferrer" className={LINK}>
                  {t(locale, "olympiads.pdf")}
                  <span className="sr-only"> {t(locale, "footer.opensNewTab")}</span>
                </a>
              </li>
            )}
          </ul>
        </Card>
      )}

      <p className="text-theme-xs rw-faint">{t(locale, "olympiads.source")}</p>
    </article>
  );
}
