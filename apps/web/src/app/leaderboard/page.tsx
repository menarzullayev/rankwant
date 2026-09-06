import Link from "next/link";
import type { Metadata } from "next";
import { api } from "@/lib/api";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";

// Jonli ma'lumot: har so'rovda serverda render qilinadi.
// Build vaqtida prerender qilinmaydi — CI da API ishlamaydi, va reyting
// jadvali baribir keshlanmasligi kerak. SSR SEO uchun yetarli (ADR-0003);
// ISR keyinroq optimizatsiya sifatida qo'shilishi mumkin.
export const dynamic = "force-dynamic";

export const metadata: Metadata = { title: "Reyting" };

export default async function LeaderboardPage() {
  const locale = DEFAULT_LOCALE;
  const data = await api.leaderboard();

  return (
    <div>
      <h1 className="mb-2 text-2xl font-bold">{t(locale, "leaderboard.title")}</h1>
      {/* ADR-0006 fazali ochilish: Phase 0 da faqat Skills va Contests */}
      <p className="mb-6 text-sm" style={{ color: "var(--muted)" }}>
        <Link href="/rating" className="underline">
          {t(locale, "nav.ratingInfo")}
        </Link>
      </p>
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left" style={{ color: "var(--muted)" }}>
            <th className="pb-2">#</th>
            <th className="pb-2">{t(locale, "standings.user")}</th>
            <th className="pb-2 text-right">{t(locale, "leaderboard.skills")}</th>
            <th className="pb-2 text-right">{t(locale, "leaderboard.contest")}</th>
            {/* Activity — ADR-0006 fazali ochilish, Phase 1 da yoqildi */}
            <th className="pb-2 text-right">{t(locale, "leaderboard.activity")}</th>
            <th className="pb-2 text-right">{t(locale, "leaderboard.streak")}</th>
          </tr>
        </thead>
        <tbody>
          {data.results.map((u, i) => (
            <tr key={u.username} className="border-t" style={{ borderColor: "var(--border)" }}>
              <td className="py-2" style={{ color: "var(--muted)" }}>{i + 1}</td>
              <td className="py-2">
                <Link href={`/users/${u.username}`} className="hover:underline">
                  {u.display_name || u.username}
                </Link>
              </td>
              <td className="py-2 text-right">{u.rating_skills}</td>
              <td className="py-2 text-right">{u.rating_contest}</td>
              <td className="py-2 text-right">{u.rating_activity}</td>
              <td className="py-2 text-right" style={{ color: "var(--muted)" }}>
                {u.streak_count}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {data.count === 0 && <p style={{ color: "var(--muted)" }}>{t(locale, "empty")}</p>}
    </div>
  );
}
