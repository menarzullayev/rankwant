import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";
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
  const locale = DEFAULT_LOCALE;

  let contest;
  let standings;
  try {
    [contest, standings] = await Promise.all([api.contest(slug), api.standings(slug)]);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-title-sm font-bold text-gray-800 dark:text-white/90">
          {contest.title}
        </h1>
        <div className="mt-2 flex flex-wrap items-center gap-2">
          <Badge color={contest.is_running ? "success" : contest.is_finished ? "neutral" : "info"}>
            {t(
              locale,
              contest.is_running
                ? "contests.running"
                : contest.is_finished
                  ? "contests.finished"
                  : "contests.upcoming",
            )}
          </Badge>
          {contest.is_rated && <Badge color="brand">{t(locale, "contests.rated")}</Badge>}
          <span className="text-theme-xs text-gray-500 dark:text-gray-400">
            {new Date(contest.start_at).toLocaleString(locale)} —{" "}
            {new Date(contest.end_at).toLocaleString(locale)}
          </span>
        </div>
      </div>

      {contest.is_finished && (
        <div
          className="rounded-2xl border border-gray-200 bg-white p-5 text-theme-sm text-gray-500
            dark:border-[#232936] dark:bg-[#141821] dark:text-gray-400"
        >
          Musobaqa tugagan — uni <strong>virtual</strong> tarzda o&apos;z vaqtingizda
          yechishingiz mumkin. Virtual natija reytingga ta&apos;sir qilmaydi va rasmiy
          jadvalga kirmaydi.
        </div>
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
