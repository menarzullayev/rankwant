import Link from "next/link";
import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { api, ApiError } from "@/lib/api";
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

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div
      className="rounded-lg border p-4"
      style={{ borderColor: "var(--border)", background: "var(--surface)" }}
    >
      <p className="text-xs" style={{ color: "var(--muted)" }}>
        {label}
      </p>
      <p className="mt-1 text-2xl font-bold">{value}</p>
    </div>
  );
}

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
    <div className="space-y-8">
      <header>
        <h1 className="text-2xl font-bold">{user.display_name || user.username}</h1>
        {user.bio && (
          <p className="mt-1 text-sm" style={{ color: "var(--muted)" }}>
            {user.bio}
          </p>
        )}
      </header>

      <section className="grid gap-4 sm:grid-cols-4">
        <Stat label="Skills" value={user.rating_skills} />
        <Stat label="Contests" value={user.rating_contest} />
        <Stat label={t(locale, "leaderboard.activity")} value={user.rating_activity} />
        <Stat label={t(locale, "leaderboard.streak")} value={user.streak_count} />
      </section>

      <section>
        <h2 className="mb-1 text-lg font-medium">{t(locale, "profile.history")}</h2>
        {/* Principle #2 ning ko'rinadigan qismi: har o'zgarish sababi bilan */}
        <p className="mb-3 text-xs" style={{ color: "var(--muted)" }}>
          <Link href="/rating" className="underline">
            {t(locale, "nav.ratingInfo")}
          </Link>
        </p>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left" style={{ color: "var(--muted)" }}>
              <th className="pb-2">Reyting</th>
              <th className="pb-2 pr-4 text-right">{t(locale, "profile.change")}</th>
              <th className="pb-2">{t(locale, "profile.reason")}</th>
              <th className="pb-2 text-right">Sana</th>
            </tr>
          </thead>
          <tbody>
            {history.results.map((row, i) => (
              <tr
                key={`${row.created_at}-${i}`}
                className="border-t"
                style={{ borderColor: "var(--border)" }}
              >
                <td className="py-2">{row.rating_type}</td>
                <td
                  className="py-2 pr-4 text-right"
                  style={{ color: row.delta >= 0 ? "#4ade80" : "#f87171" }}
                >
                  {row.delta > 0 ? "+" : ""}
                  {row.delta}
                </td>
                <td className="py-2" style={{ color: "var(--muted)" }}>
                  {REASON_LABEL[row.reason] ?? row.reason}
                  {row.rank !== null && ` · ${row.rank}-o'rin`}
                  {row.ref_id && ` · ${row.ref_id}`}
                </td>
                <td className="py-2 text-right" style={{ color: "var(--muted)" }}>
                  {new Date(row.created_at).toLocaleDateString(locale)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {history.results.length === 0 && (
          <p style={{ color: "var(--muted)" }}>{t(locale, "empty")}</p>
        )}
      </section>

      <section>
        <h2 className="mb-3 text-lg font-medium">{t(locale, "profile.solved")}</h2>
        <div className="flex flex-wrap gap-2">
          {solved.results.map((p) => (
            <Link
              key={p.slug}
              href={`/problems/${p.slug}`}
              className="rounded border px-3 py-1 text-sm"
              style={{ borderColor: "var(--border)", background: "var(--surface)" }}
              // Joriy va yechilgandagi qiyinlik farq qilsa — qayta baholangan
              title={
                p.difficulty !== p.difficulty_at_solve
                  ? `${p.difficulty_at_solve} → ${p.difficulty} (${t(locale, "profile.rerated")})`
                  : undefined
              }
            >
              {p.title}
              <span className="ml-2" style={{ color: "var(--muted)" }}>
                {p.difficulty}
                {p.difficulty !== p.difficulty_at_solve && " *"}
              </span>
            </Link>
          ))}
        </div>
        {solved.results.length === 0 && (
          <p style={{ color: "var(--muted)" }}>{t(locale, "empty")}</p>
        )}
      </section>
    </div>
  );
}
