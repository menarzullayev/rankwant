import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { getLocale } from "@/i18n/server";
import { dateTime, t } from "@/i18n/messages";
import { StandingsTable } from "@/components/StandingsTable";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";

type Props = { params: Promise<{ slug: string }> };

// Jonli ma'lumot: har so'rovda serverda render qilinadi.
// Build vaqtida prerender qilinmaydi — CI da API ishlamaydi, va reyting
// jadvali baribir keshlanmasligi kerak. SSR SEO uchun yetarli (ADR-0003);
// ISR keyinroq optimizatsiya sifatida qo'shilishi mumkin.
export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  try {
    const contest = await api.contest(slug);
    return { title: contest.title };
  } catch {
    return { title: "Musobaqa topilmadi" };
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

  return (
    <div className="space-y-6">
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
          <span className="text-theme-xs rw-dim">
            {dateTime(contest.start_at, locale)} —{" "}
            {dateTime(contest.end_at, locale)}
          </span>
        </div>
      </div>

      {contest.is_finished && (
        <div className="rw-radius border rw-line rw-surface p-5 text-theme-sm rw-dim">
          Musobaqa tugagan — uni <strong>virtual</strong> tarzda o&apos;z
          vaqtingizda yechishingiz mumkin. Virtual natija reytingga ta&apos;sir
          qilmaydi va rasmiy jadvalga kirmaydi.
        </div>
      )}

      {contest.problems.length > 0 && (
        <Card title="Masalalar" bodyClassName="p-0">
          <ul className="rw-divide divide-y">
            {contest.problems.map((entry) => (
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
                    {entry.points} ball
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </Card>
      )}

      <Card title={t(locale, "standings.title")} bodyClassName="p-0">
        {/* Contest ketayotgan bo'lsa SSE bilan jonli, aks holda statik */}
        <StandingsTable
          slug={slug}
          initial={standings}
          live={contest.is_running}
          locale={locale}
        />
      </Card>
    </div>
  );
}
