import Link from "next/link";
import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { api, ApiError, type RatingKind, type UserPublic } from "@/lib/api";
import { DifficultyBadge } from "@/components/ui/Badge";
import { Card, StatCard } from "@/components/ui/Card";
import {
  EmptyRow,
  TBody,
  TD,
  TH,
  THead,
  TR,
  Table,
} from "@/components/ui/Table";
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

  const solvedLevels = user.solved_by_level.filter((level) => level.solved > 0);
  const peakLevel = Math.max(...solvedLevels.map((l) => l.solved), 1);

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-center gap-4 rw-radius border rw-line rw-surface p-6 rw-shadow">
        <span className="flex size-14 items-center justify-center rounded-full rw-accent-soft text-theme-xl font-bold rw-accent-ink">
          {(user.display_name || user.username).charAt(0).toUpperCase()}
        </span>
        <div>
          <h1 className="text-title-sm font-bold rw-strong">
            {user.display_name || user.username}
          </h1>
          {user.bio && <p className="mt-1 text-theme-sm rw-dim">{user.bio}</p>}
        </div>
      </header>

      {/* Reyting yonida O'RIN: raqamning o'zi «ko'p yoki oz» ekanini
          aytmaydi, u faqat boshqalar bilan solishtirganda ma'lum bo'ladi
          (KEP profilida ham shunday). Eng yuqori qiymat esa hozirgisi
          tushib ketgan bo'lsa ham mehnat yo'qolmaganini ko'rsatadi. */}
      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Skills"
          value={user.rating_skills}
          hint={ratingHint(user, "skills")}
        />
        <StatCard
          label="Contests"
          value={user.rating_contest}
          hint={ratingHint(user, "contest")}
        />
        <StatCard
          label={t(locale, "leaderboard.activity")}
          value={user.rating_activity}
          hint={ratingHint(user, "activity")}
        />
        <StatCard
          label={t(locale, "leaderboard.streak")}
          value={user.streak_count}
        />
      </section>

      {solvedLevels.length > 0 && (
        <Card title="Daraja bo'yicha yechilganlar" bodyClassName="space-y-2.5">
          {solvedLevels.map((level) => (
            <div key={level.code}>
              <div className="flex items-baseline justify-between gap-2 text-theme-sm">
                <span className={`level-${level.code} font-medium`}>
                  {level.label}
                </span>
                <span className="rw-faint tabular-nums">{level.solved}</span>
              </div>
              <div className="mt-1 h-1.5 overflow-hidden rounded-full rw-chip">
                <div
                  className={`level-${level.code} h-full rounded-full`}
                  style={{
                    width: `${Math.round((level.solved / peakLevel) * 100)}%`,
                    backgroundColor: "currentColor",
                  }}
                />
              </div>
            </div>
          ))}
        </Card>
      )}

      {/* Principle #2 ning ko'rinadigan qismi: har o'zgarish sababi bilan */}
      <Card
        title={t(locale, "profile.history")}
        action={
          <Link
            href="/rating"
            className="text-theme-sm rw-accent-ink hover:underline"
          >
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
                <TD className="font-medium rw-strong">{row.rating_type}</TD>
                <TD align="right">
                  <span
                    className={
                      row.delta >= 0
                        ? "font-semibold rw-ok-ink"
                        : "font-semibold rw-bad-ink"
                    }
                  >
                    {row.delta > 0 ? "+" : ""}
                    {row.delta}
                  </span>
                </TD>
                <TD className="rw-dim">
                  {REASON_LABEL[row.reason] ?? row.reason}
                  {row.rank !== null && ` · ${row.rank}-o'rin`}
                  {row.ref_id && ` · ${row.ref_id}`}
                </TD>
                <TD align="right" className="rw-faint">
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
              className="flex items-center gap-2 rw-radius-sm border rw-line px-3 py-1.5 text-theme-sm transition rw-hover-line"
              // Joriy va yechilgandagi qiyinlik farq qilsa — qayta baholangan
              title={
                p.difficulty !== p.difficulty_at_solve
                  ? `${p.difficulty_at_solve} → ${p.difficulty} (${t(locale, "profile.rerated")})`
                  : undefined
              }
            >
              <span className="rw-strong">{p.title}</span>
              <DifficultyBadge value={p.difficulty} />
              {p.difficulty !== p.difficulty_at_solve && (
                <span className="rw-warn-ink" aria-hidden="true">
                  *
                </span>
              )}
            </Link>
          ))}
          {solved.results.length === 0 && (
            <p className="text-theme-sm rw-faint">{t(locale, "empty")}</p>
          )}
        </div>
      </Card>
    </div>
  );
}

/** «#7 · eng yuqori 1500» — o'rin va erishilgan cho'qqi. */
function ratingHint(user: UserPublic, kind: RatingKind): string | undefined {
  const parts: string[] = [];
  const rank = user.ranks[kind];
  const max = user.max_ratings[kind];
  if (rank) parts.push(`#${rank}`);
  if (max !== undefined && max > 0) parts.push(`eng yuqori ${max}`);
  return parts.length ? parts.join(" · ") : undefined;
}
