import Link from "next/link";
import type { Metadata } from "next";

import { Card } from "@/components/ui/Card";
import { CountryFlag } from "@/components/ui/CountryFlag";
import { UserName } from "@/components/ui/Identity";
import {
  EmptyRow,
  TBody,
  TD,
  TH,
  THead,
  TR,
  Table,
} from "@/components/ui/Table";
import { getLocale } from "@/i18n/server";
import { fill, t } from "@/i18n/messages";
import { api } from "@/lib/api";

// Jonli ma'lumot: har so'rovda serverda render qilinadi.
// Build vaqtida prerender qilinmaydi — CI da API ishlamaydi, va reyting
// jadvali baribir keshlanmasligi kerak. SSR SEO uchun yetarli (ADR-0003);
// ISR keyinroq optimizatsiya sifatida qo'shilishi mumkin.
export const dynamic = "force-dynamic";

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "leaderboard.title") };
}

/** Birinchi uchtalik — TailAdmin jadvalida ham ko'zga tashlansin. */
const MEDAL = ["rw-warn-ink", "rw-faint", "text-orange-400"];

type Props = { searchParams: Promise<{ school?: string }> };

export default async function LeaderboardPage({ searchParams }: Props) {
  const locale = await getLocale();
  const { school } = await searchParams;
  // Maktab reytingi (ADR-0017) — katalogdagi maktab bo'yicha.
  // Topilmagan maktab filtri e'tiborsiz qoldiriladi — bo'sh jadval o'rniga umumiy reyting.
  const schoolRow =
    school && /^\d+$/.test(school) ? await api.school(school).catch(() => null) : null;
  const data = await api.leaderboard(schoolRow ? String(schoolRow.id) : undefined);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-title-sm font-bold rw-strong">
          {schoolRow
            ? fill(t(locale, "leaderboard.school"), { school: schoolRow.name })
            : t(locale, "leaderboard.title")}
        </h1>
        {schoolRow && (
          <Link
            href="/leaderboard"
            className="mt-1 mr-4 inline-block text-theme-sm rw-accent-ink hover:underline"
          >
            {t(locale, "leaderboard.schoolAll")}
          </Link>
        )}
        {/* ADR-0006 fazali ochilish: Phase 0 da faqat Skills va Contests */}
        <Link
          href="/rating"
          className="mt-1 inline-block text-theme-sm rw-accent-ink hover:underline"
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
            <TH align="right" className="hidden @xl:table-cell">{t(locale, "leaderboard.contest")}</TH>
            {/* Activity — ADR-0006 fazali ochilish, Phase 1 da yoqildi */}
            <TH align="right" className="hidden @xl:table-cell">{t(locale, "leaderboard.activity")}</TH>
            {/* Challenges — Phase 3, duel qurilgach ochildi */}
            <TH align="right" className="hidden @xl:table-cell">{t(locale, "leaderboard.challenges")}</TH>
            <TH align="right" className="hidden @xl:table-cell">{t(locale, "leaderboard.streak")}</TH>
          </THead>
          <TBody>
            {data.results.map((u, i) => (
              <TR key={u.username}>
                <TD className={`font-semibold ${MEDAL[i] ?? "rw-faint"}`}>
                  {i + 1}
                </TD>
                <TD>
                  {/* Bayroq — ismning yonida. Global reytingda davlat
                      taqsimoti ko'zga tashlanadi (qaror: hamma joyda).
                      Yashirilgan mamlakatda `country` bo'sh keladi va
                      `CountryFlag` hech narsa chizmaydi. */}
                  <span className="flex items-center gap-2 max-[359px]:break-all">
                    <CountryFlag code={u.country} />
                    <UserName username={u.username} name={u.display_name} title={u.title} locale={locale} />
                  </span>
                  {/* The four columns a narrow table hides, as one line. */}
                  <span className="mt-1 block text-theme-xs rw-faint tabular-nums @xl:hidden">
                    {[
                      `${t(locale, "leaderboard.contest")} ${u.rating_contest}`,
                      `${t(locale, "leaderboard.activity")} ${u.rating_activity}`,
                      `${t(locale, "leaderboard.challenges")} ${u.rating_challenges}`,
                      `${t(locale, "leaderboard.streak")} ${u.streak_count}`,
                    ].join(" · ")}
                  </span>
                </TD>
                <TD align="right" className="font-semibold rw-strong">
                  {u.rating_skills}
                </TD>
                <TD align="right" className="hidden @xl:table-cell">{u.rating_contest}</TD>
                <TD align="right" className="hidden @xl:table-cell">{u.rating_activity}</TD>
                <TD align="right" className="hidden @xl:table-cell">{u.rating_challenges}</TD>
                <TD align="right" className="hidden rw-faint @xl:table-cell">
                  {u.streak_count}
                </TD>
              </TR>
            ))}
            {data.count === 0 && (
              <EmptyRow colSpan={7}>{t(locale, "common.empty")}</EmptyRow>
            )}
          </TBody>
        </Table>
      </Card>
    </div>
  );
}
