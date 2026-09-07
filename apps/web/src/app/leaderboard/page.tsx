import Link from "next/link";
import type { Metadata } from "next";

import { Card } from "@/components/ui/Card";
import { EmptyRow, TBody, TD, TH, THead, TR, Table } from "@/components/ui/Table";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";
import { api } from "@/lib/api";

// Jonli ma'lumot: har so'rovda serverda render qilinadi.
// Build vaqtida prerender qilinmaydi — CI da API ishlamaydi, va reyting
// jadvali baribir keshlanmasligi kerak. SSR SEO uchun yetarli (ADR-0003);
// ISR keyinroq optimizatsiya sifatida qo'shilishi mumkin.
export const dynamic = "force-dynamic";

export const metadata: Metadata = { title: "Reyting" };

/** Birinchi uchtalik — TailAdmin jadvalida ham ko'zga tashlansin. */
const MEDAL = ["text-warning-500", "text-gray-400", "text-orange-400"];

export default async function LeaderboardPage() {
  const locale = DEFAULT_LOCALE;
  const data = await api.leaderboard();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-title-sm font-bold text-gray-800 dark:text-white/90">
          {t(locale, "leaderboard.title")}
        </h1>
        {/* ADR-0006 fazali ochilish: Phase 0 da faqat Skills va Contests */}
        <Link
          href="/rating"
          className="mt-1 inline-block text-theme-sm text-brand-500 hover:underline"
        >
          {t(locale, "nav.ratingInfo")}
        </Link>
      </div>

      <Card bodyClassName="p-0">
        <Table>
          <THead>
            <TH>#</TH>
            <TH>{t(locale, "standings.user")}</TH>
            <TH align="right">{t(locale, "leaderboard.skills")}</TH>
            <TH align="right">{t(locale, "leaderboard.contest")}</TH>
            {/* Activity — ADR-0006 fazali ochilish, Phase 1 da yoqildi */}
            <TH align="right">{t(locale, "leaderboard.activity")}</TH>
            {/* Challenges — Phase 3, duel qurilgach ochildi */}
            <TH align="right">{t(locale, "leaderboard.challenges")}</TH>
            <TH align="right">{t(locale, "leaderboard.streak")}</TH>
          </THead>
          <TBody>
            {data.results.map((u, i) => (
              <TR key={u.username}>
                <TD className={`font-semibold ${MEDAL[i] ?? "text-gray-400"}`}>{i + 1}</TD>
                <TD>
                  <Link
                    href={`/users/${u.username}`}
                    className="font-medium text-gray-800 hover:text-brand-500 dark:text-white/90"
                  >
                    {u.display_name || u.username}
                  </Link>
                </TD>
                <TD align="right" className="font-semibold text-gray-800 dark:text-white/90">
                  {u.rating_skills}
                </TD>
                <TD align="right">{u.rating_contest}</TD>
                <TD align="right">{u.rating_activity}</TD>
                <TD align="right">{u.rating_challenges}</TD>
                <TD align="right" className="text-gray-400">
                  {u.streak_count}
                </TD>
              </TR>
            ))}
            {data.count === 0 && <EmptyRow colSpan={7}>{t(locale, "empty")}</EmptyRow>}
          </TBody>
        </Table>
      </Card>
    </div>
  );
}
