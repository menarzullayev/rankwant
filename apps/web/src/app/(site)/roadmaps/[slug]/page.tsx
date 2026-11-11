import type { Metadata, Route } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { Badge } from "@/components/ui/Badge";
import { inReaderAlphabet } from "@/i18n/alphabet";
import { fill, t } from "@/i18n/messages";
import { getLocale } from "@/i18n/server";
import { ApiError } from "@/lib/api";
import type { RoadmapDetail } from "@/lib/api/content";
import { getWithSession } from "@/lib/api.server";

import { Progress, stepHref } from "../_parts/Progress";

export const dynamic = "force-dynamic";

type Props = { params: Promise<{ slug: string }> };

async function load(slug: string, locale: string): Promise<RoadmapDetail> {
  try {
    return await getWithSession<RoadmapDetail>(`/roadmaps/${slug}/?lang=${locale}`);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const locale = await getLocale();
  const plan = await load((await params).slug, locale);
  return {
    title: inReaderAlphabet(plan.title, plan.locale),
    description: inReaderAlphabet(plan.description, plan.locale),
  };
}

/** A study plan's own page (ADR-0060 § 2.4): its sections and the reader's
 *  progress in each, and the next step to take. */
export default async function RoadmapPage({ params }: Props) {
  const locale = await getLocale();
  const { slug } = await params;
  const plan = await load(slug, locale);
  const title = inReaderAlphabet(plan.title, plan.locale);
  const next = plan.next_step ? stepHref(plan.next_step) : null;

  return (
    <div className="space-y-6">
      <Link href="/roadmaps" className="inline-flex min-h-11 items-center text-theme-sm rw-accent-ink hover:underline">
        {t(locale, "roadmaps.all")}
      </Link>
      <header className="space-y-3">
        <div className="flex flex-wrap items-center gap-2">
          <h1 className="text-title-sm font-bold rw-strong">{title}</h1>
          <Badge color="success">{t(locale, "roadmaps.free")}</Badge>
        </div>
        {plan.description && (
          <p className="max-w-3xl text-theme-sm rw-dim">
            {inReaderAlphabet(plan.description, plan.locale)}
          </p>
        )}
        <div className="max-w-md">
          <Progress solved={plan.solved_steps} total={plan.step_count} label={title} locale={locale} />
        </div>
        {plan.next_step && next && (
          <Link
            href={next as Route}
            className="inline-flex min-h-11 items-center rounded-full px-5 text-theme-sm font-semibold rw-accent-bg rw-focus-ring"
          >
            {fill(t(locale, plan.solved_steps > 0 ? "roadmaps.continue" : "roadmaps.start"), {
              step: inReaderAlphabet(plan.next_step.title, plan.locale),
            })}
          </Link>
        )}
        {!plan.next_step && plan.step_count > 0 && (
          <p className="text-theme-sm font-semibold rw-ok-ink">{t(locale, "roadmaps.done")}</p>
        )}
      </header>

      {plan.sections.length > 0 ? (
        <ol className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {plan.sections.map((section) => {
            const name = inReaderAlphabet(section.title, section.locale);
            return (
              <li key={section.order}>
                <Link
                  href={`/roadmaps/${slug}/${section.order}` as Route}
                  className="block h-full rw-radius border rw-line rw-surface p-5 rw-shadow rw-hover-line rw-focus-ring"
                >
                  <span className="block text-theme-xs rw-faint tabular-nums">
                    {fill(t(locale, "roadmaps.sectionNumber"), { number: section.order })}
                  </span>
                  <span className="mt-1 block font-semibold rw-strong">{name}</span>
                  {section.description && (
                    <span className="mt-1 block text-theme-sm rw-dim">
                      {inReaderAlphabet(section.description, section.locale)}
                    </span>
                  )}
                  <span className="mt-3 block">
                    <Progress
                      solved={section.solved_steps}
                      total={section.step_count}
                      label={name}
                      locale={locale}
                    />
                  </span>
                </Link>
              </li>
            );
          })}
        </ol>
      ) : (
        <ol className="space-y-2">
          {plan.steps.map((step) => {
            const href = stepHref(step);
            return (
              <li key={step.order} className="text-theme-sm">
                {href ? (
                  <Link href={href as Route} className="inline-flex min-h-11 items-center rw-accent-ink hover:underline">
                    {step.title || step.problem || step.article}
                  </Link>
                ) : (
                  step.title
                )}
              </li>
            );
          })}
        </ol>
      )}
    </div>
  );
}
