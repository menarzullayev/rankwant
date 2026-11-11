import type { Metadata, Route } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { DifficultyBadge } from "@/components/ui/Badge";
import { inReaderAlphabet } from "@/i18n/alphabet";
import { fill, t } from "@/i18n/messages";
import { getLocale } from "@/i18n/server";
import { ApiError } from "@/lib/api";
import type { RoadmapSectionPage } from "@/lib/api/content";
import { getWithSession } from "@/lib/api.server";

import { Progress, stepHref } from "../../_parts/Progress";

export const dynamic = "force-dynamic";

type Props = { params: Promise<{ slug: string; section: string }> };

async function load(slug: string, section: string, locale: string): Promise<RoadmapSectionPage> {
  if (!/^\d+$/.test(section)) notFound();
  try {
    return await getWithSession<RoadmapSectionPage>(
      `/roadmaps/${slug}/sections/${section}/?lang=${locale}`,
    );
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const locale = await getLocale();
  const { slug, section } = await params;
  const page = await load(slug, section, locale);
  return {
    title: `${inReaderAlphabet(page.section.title, page.section.locale)} — ${inReaderAlphabet(page.roadmap.title, page.roadmap.locale)}`,
  };
}

/** One chapter of a study plan (ADR-0060 § 2.4): its steps, which of them the
 *  reader has solved, and the chapters around it. */
export default async function RoadmapSectionRoute({ params }: Props) {
  const locale = await getLocale();
  const { slug, section } = await params;
  const page = await load(slug, section, locale);
  const name = inReaderAlphabet(page.section.title, page.section.locale);

  return (
    <div className="space-y-6">
      <Link href={`/roadmaps/${slug}` as Route} className="inline-flex min-h-11 items-center text-theme-sm rw-accent-ink hover:underline">
        {inReaderAlphabet(page.roadmap.title, page.roadmap.locale)}
      </Link>
      <header className="space-y-3">
        <p className="text-theme-xs rw-faint tabular-nums">
          {fill(t(locale, "roadmaps.sectionNumber"), { number: page.section.order })}
        </p>
        <h1 className="text-title-sm font-bold rw-strong">{name}</h1>
        {page.section.description && (
          <p className="max-w-3xl text-theme-sm rw-dim">
            {inReaderAlphabet(page.section.description, page.section.locale)}
          </p>
        )}
        <div className="max-w-md">
          <Progress
            solved={page.section.solved_steps}
            total={page.section.step_count}
            label={name}
            locale={locale}
          />
        </div>
      </header>

      <ol className="divide-y rw-divide rw-radius border rw-line rw-surface">
        {page.steps.map((step) => {
          const href = stepHref(step);
          return (
            <li key={step.order} className="flex items-center gap-3 px-4">
              <span
                className={`inline-flex size-5 shrink-0 items-center justify-center rounded-full text-theme-xs ${
                  step.solved ? "rw-ok-soft" : "border rw-line"
                }`}
                aria-hidden="true"
              >
                {step.solved && "✓"}
              </span>
              {step.solved && <span className="sr-only">{t(locale, "roadmaps.solved")}</span>}
              {href ? (
                <Link href={href as Route} className="flex min-h-11 grow items-center text-theme-sm rw-strong hover:underline rw-focus-ring">
                  {inReaderAlphabet(step.title, page.roadmap.locale)}
                </Link>
              ) : (
                <span className="grow text-theme-sm">{step.title}</span>
              )}
              {step.difficulty !== null && <DifficultyBadge value={step.difficulty} />}
            </li>
          );
        })}
      </ol>

      <nav className="flex flex-wrap justify-between gap-3 text-theme-sm">
        {page.previous !== null ? (
          <Link href={`/roadmaps/${slug}/${page.previous}` as Route} className="inline-flex min-h-11 items-center rw-accent-ink hover:underline">
            {t(locale, "roadmaps.previous")}
          </Link>
        ) : (
          <span />
        )}
        {page.next !== null && (
          <Link href={`/roadmaps/${slug}/${page.next}` as Route} className="inline-flex min-h-11 items-center rw-accent-ink hover:underline">
            {t(locale, "roadmaps.next")}
          </Link>
        )}
      </nav>
    </div>
  );
}
