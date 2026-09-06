import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";
import { StandingsTable } from "@/components/StandingsTable";

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
    <div>
      <h1 className="text-2xl font-bold">{contest.title}</h1>
      <p className="mt-1 text-sm" style={{ color: "var(--muted)" }}>
        {new Date(contest.start_at).toLocaleString(locale)} —{" "}
        {new Date(contest.end_at).toLocaleString(locale)}
        {contest.is_rated && ` · ${t(locale, "contests.rated")}`}
      </p>

      {contest.is_finished && (
        <p className="mt-3 text-sm" style={{ color: "var(--muted)" }}>
          Musobaqa tugagan — uni <strong>virtual</strong> tarzda o&apos;z
          vaqtingizda yechishingiz mumkin. Virtual natija reytingga
          ta&apos;sir qilmaydi va rasmiy jadvalga kirmaydi.
        </p>
      )}

      <h2 className="mt-8 mb-3 text-lg font-medium">{t(locale, "standings.title")}</h2>
      {/* Contest ketayotgan bo'lsa SSE bilan jonli, aks holda statik */}
      <StandingsTable
        slug={slug}
        initial={standings}
        live={contest.is_running}
        locale={locale}
      />
    </div>
  );
}
