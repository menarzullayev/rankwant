import Link from "next/link";
import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { DifficultyBadge } from "@/components/ui/Badge";
import { Card, StatCard } from "@/components/ui/Card";
import { EmptyRow, TBody, TD, TH, THead, TR, Table } from "@/components/ui/Table";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";

type Props = { params: Promise<{ username: string }> };

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { username } = await params;
  // Mavjud bo'lmagan foydalanuvchi nomini sarlavhaga qo'ymaymiz —
  // 404 sahifasi begona satrni ko'rsatib turmasin. `api.user` fetch'i
  // sahifa render'i bilan bir xil, ya'ni ikkinchi so'rov ketmaydi.
  try {
    const user = await api.user(username);
    return { title: user.display_name || user.username };
  } catch {
    return { title: "404" };
  }
}

const REASON_LABEL: Record<string, string> = {
  problem_solved: "masala yechildi",
  problem_rerated: "masala qayta baholandi",
  contest: "musobaqa",
  recalculation: "qayta hisoblash",
};

export default async function ProfilePage({ params }: Props) {
  const { username } = await params;
  const locale = DEFAULT_LOCALE;

  let user;
  try {
    user = await api.user(username);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }
  const [history, solved] = await Promise.all([
    api.ratingHistory(username),
    api.solved(username),
  ]);

  return (
    <div className="space-y-6">
      <header
        className="flex flex-wrap items-center gap-4 rounded-2xl border border-gray-200
          bg-white p-6 shadow-theme-xs dark:border-[#232936] dark:bg-[#141821]"
      >
        <span
          className="flex size-14 items-center justify-center rounded-full bg-brand-50
            text-theme-xl font-bold text-brand-600 dark:bg-brand-500/12 dark:text-brand-400"
        >
          {(user.display_name || user.username).charAt(0).toUpperCase()}
        </span>
        <div>
          <h1 className="text-title-sm font-bold text-gray-800 dark:text-white/90">
            {user.display_name || user.username}
          </h1>
          {user.bio && (
            <p className="mt-1 text-theme-sm text-gray-500 dark:text-gray-400">{user.bio}</p>
          )}
        </div>
      </header>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Skills" value={user.rating_skills} />
        <StatCard label="Contests" value={user.rating_contest} />
        <StatCard label={t(locale, "leaderboard.activity")} value={user.rating_activity} />
        <StatCard label={t(locale, "leaderboard.streak")} value={user.streak_count} />
      </section>

      {/* Principle #2 ning ko'rinadigan qismi: har o'zgarish sababi bilan */}
      <Card
        title={t(locale, "profile.history")}
        action={
          <Link href="/rating" className="text-theme-sm text-brand-500 hover:underline">
            {t(locale, "nav.ratingInfo")}
          </Link>
        }
        bodyClassName="p-0"
      >
        <Table>
          <THead>
            <TH>Reyting</TH>
            <TH align="right">{t(locale, "profile.change")}</TH>
            <TH>{t(locale, "profile.reason")}</TH>
            <TH align="right">Sana</TH>
          </THead>
          <TBody>
            {history.results.map((row, i) => (
              <TR key={`${row.created_at}-${i}`}>
                <TD className="font-medium text-gray-800 dark:text-white/90">
                  {row.rating_type}
                </TD>
                <TD align="right">
                  <span
                    className={
                      row.delta >= 0
                        ? "font-semibold text-success-500"
                        : "font-semibold text-error-500"
                    }
                  >
                    {row.delta > 0 ? "+" : ""}
                    {row.delta}
                  </span>
                </TD>
                <TD className="text-gray-500 dark:text-gray-400">
                  {REASON_LABEL[row.reason] ?? row.reason}
                  {row.rank !== null && ` · ${row.rank}-o'rin`}
                  {row.ref_id && ` · ${row.ref_id}`}
                </TD>
                <TD align="right" className="text-gray-400">
                  {new Date(row.created_at).toLocaleDateString(locale)}
                </TD>
              </TR>
            ))}
            {history.results.length === 0 && (
              <EmptyRow colSpan={4}>{t(locale, "empty")}</EmptyRow>
            )}
          </TBody>
        </Table>
      </Card>

      <Card title={t(locale, "profile.solved")}>
        <div className="flex flex-wrap gap-2">
          {solved.results.map((p) => (
            <Link
              key={p.slug}
              href={`/problems/${p.slug}`}
              className="flex items-center gap-2 rounded-lg border border-gray-200 px-3 py-1.5
                text-theme-sm transition hover:border-brand-400 dark:border-[#232936]"
              // Joriy va yechilgandagi qiyinlik farq qilsa — qayta baholangan
              title={
                p.difficulty !== p.difficulty_at_solve
                  ? `${p.difficulty_at_solve} → ${p.difficulty} (${t(locale, "profile.rerated")})`
                  : undefined
              }
            >
              <span className="text-gray-700 dark:text-gray-200">{p.title}</span>
              <DifficultyBadge value={p.difficulty} />
              {p.difficulty !== p.difficulty_at_solve && (
                <span className="text-warning-500" aria-hidden="true">
                  *
                </span>
              )}
            </Link>
          ))}
          {solved.results.length === 0 && (
            <p className="text-theme-sm text-gray-400">{t(locale, "empty")}</p>
          )}
        </div>
      </Card>
    </div>
  );
}
