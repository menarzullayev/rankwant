import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { api, ApiError, type ClarificationList, type ContestViewer } from "@/lib/api";
import { getSessionUser, getWithSession } from "@/lib/api.server";
import { getLocale } from "@/i18n/server";
import { Countdown, TimeStamp } from "@/components/kit/TimeStamp";
import { fill, t } from "@/i18n/messages";
import {
  ContestClarifications,
  ContestCrew,
  ContestEntry,
  ContestIntegrity,
  StandingsTable,
} from "@/features/contests";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { SITE_URL, jsonLd } from "@/lib/site";

type Props = { params: Promise<{ slug: string }> };

// Jonli ma'lumot: har so'rovda serverda render qilinadi.
// Build vaqtida prerender qilinmaydi — CI da API ishlamaydi, va reyting
// jadvali baribir keshlanmasligi kerak. SSR SEO uchun yetarli (ADR-0003);
// ISR keyinroq optimizatsiya sifatida qo'shilishi mumkin.
export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const locale = await getLocale();
  try {
    const contest = await api.contest(slug);
    return { title: contest.title };
  } catch {
    return { title: t(locale, "contest.notFound") };
  }
}

export default async function ContestPage({ params }: Props) {
  const { slug } = await params;
  const locale = await getLocale();

  let contest;
  let standings;
  try {
    [contest, standings] = await Promise.all([
      api.contest(slug),
      api.standings(slug),
    ]);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }

  // The visitor's own standing: registered, an insider, testing before the
  // start (ADR-0055, part 2). Asked separately so the contest stays one
  // answer for everybody.
  const signedIn = (await getSessionUser()) !== null;
  const viewer = signedIn
    ? await getWithSession<ContestViewer>(`/contests/${slug}/viewer/`).catch(() => null)
    : null;
  // Questions and announcements (ADR-0055, part 3): the visitor's own and
  // the public ones; the jury reads everything.
  const clarifications = await getWithSession<ClarificationList>(
    `/contests/${slug}/clarifications/`,
  ).catch(() => null);
  // Before the start the problems are shown to the people who test them.
  const problems =
    contest.problems.length > 0 ? contest.problems : viewer?.testing ? viewer.problems : [];

  return (
    <div className="space-y-6">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: jsonLd({
            "@context": "https://schema.org",
            "@type": "Event",
            name: contest.title,
            startDate: contest.start_at,
            endDate: contest.end_at,
            url: `${SITE_URL}/contests/${slug}`,
            eventStatus: contest.is_finished
              ? "https://schema.org/EventCompleted"
              : contest.is_running
                ? "https://schema.org/EventInProgress"
                : "https://schema.org/EventScheduled",
            eventAttendanceMode:
              "https://schema.org/OnlineEventAttendanceMode",
            location: {
              "@type": "VirtualLocation",
              url: `${SITE_URL}/contests/${slug}`,
            },
            organizer: { "@id": `${SITE_URL}/#organization` },
          }),
        }}
      />
      <div>
        <h1 className="text-title-sm font-bold rw-strong">{contest.title}</h1>
        <div className="mt-2 flex flex-wrap items-center gap-2">
          <Badge
            color={
              contest.is_running
                ? "success"
                : contest.is_finished
                  ? "neutral"
                  : "info"
            }
          >
            {t(
              locale,
              contest.is_running
                ? "contests.running"
                : contest.is_finished
                  ? "contests.finished"
                  : "contests.upcoming",
            )}
          </Badge>
          {contest.is_rated && (
            <Badge color="brand">{t(locale, "contests.rated")}</Badge>
          )}
          <TimeStamp value={contest.start_at} locale={locale} tone="dual" />
          <TimeStamp value={contest.end_at} locale={locale} tone="dual" />
          {!contest.is_finished && (
            <Countdown
              until={contest.is_running ? contest.end_at : contest.start_at}
              locale={locale}
            />
          )}
        </div>
      </div>

      {contest.is_finished && (
        <div className="rw-radius border rw-line rw-surface p-5 text-theme-sm rw-dim">
          {t(locale, "contest.finishedNote")}
        </div>
      )}

      {/* Fair play (ADR-0055, part 4): the rule is told before anyone
          writes a line, and so is what the editor records. */}
      {!contest.is_finished && (
        <p className="rw-radius-sm rw-warn-soft px-3 py-2 text-theme-sm rw-warn-ink" data-fair-rule="">
          {t(locale, "contest.fair.rule")}
        </p>
      )}
      {viewer?.disqualified_reason && (
        <div className="rw-radius border rw-line rw-bad-soft p-4 text-theme-sm rw-bad-ink" role="status">
          <strong className="block">{t(locale, "contest.fair.youAreOut")}</strong>
          {viewer.disqualified_reason}
        </div>
      )}

      <ContestEntry
        slug={slug}
        viewer={viewer}
        signedIn={signedIn}
        finished={contest.is_finished}
      />

      {problems.length === 0 && contest.problem_count > 0 && (
        <div className="rw-radius border rw-line rw-surface p-5 text-theme-sm rw-dim" data-problems-hidden="">
          {fill(t(locale, "contest.problemsAtStart"), { count: contest.problem_count })}
        </div>
      )}

      {problems.length > 0 && (
        <Card title={t(locale, "contest.problems")} bodyClassName="p-0">
          <ul className="rw-divide divide-y">
            {problems.map((entry) => (
              <li key={entry.slug}>
                <Link
                  href={{
                    pathname: `/problems/${entry.slug}`,
                    query: { contest: slug },
                  }}
                  className="flex items-center gap-3 px-5 py-3 transition rw-hover-bg"
                >
                  <span className="flex size-7 shrink-0 items-center justify-center rw-radius-sm rw-chip text-theme-xs font-semibold rw-dim-2">
                    {entry.index_letter}
                  </span>
                  <span className="min-w-0 flex-1 truncate text-theme-sm font-medium rw-strong">
                    {entry.title}
                  </span>
                  <span className="text-theme-xs rw-faint">
                    {entry.points} {t(locale, "col.points")}
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </Card>
      )}

      <ContestClarifications
        slug={slug}
        initial={clarifications}
        letters={problems.map((entry) => entry.index_letter)}
        started={contest.is_running || contest.is_finished}
        finished={contest.is_finished}
      />

      <Card title={t(locale, "standings.title")} bodyClassName="p-0">
        {/* Contest ketayotgan bo'lsa SSE bilan jonli, aks holda statik */}
        <StandingsTable
          slug={slug}
          initial={standings}
          live={contest.is_running}
          locale={locale}
          hacks={contest.hack_room || contest.hack_open_until !== null}
        />
      </Card>

      {viewer?.judge && contest.is_finished && <ContestIntegrity slug={slug} />}

      <ContestCrew crew={contest.crew} locale={locale} />
    </div>
  );
}
