import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";

type Props = { params: Promise<{ slug: string }> };

/** SSR + metadata — masala sahifalari qidiruvda topilishi kerak (ADR-0003). */
// Jonli ma'lumot: har so'rovda serverda render qilinadi.
// Build vaqtida prerender qilinmaydi — CI da API ishlamaydi, va reyting
// jadvali baribir keshlanmasligi kerak. SSR SEO uchun yetarli (ADR-0003);
// ISR keyinroq optimizatsiya sifatida qo'shilishi mumkin.
export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  try {
    const problem = await api.problem(slug);
    return {
      title: problem.title,
      description: `${problem.title} — qiyinlik ${problem.difficulty}. RankWant masala arxivi.`,
    };
  } catch {
    return { title: "Masala topilmadi" };
  }
}

export default async function ProblemPage({ params }: Props) {
  const { slug } = await params;
  const locale = DEFAULT_LOCALE;

  let problem;
  try {
    problem = await api.problem(slug);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }

  return (
    <article>
      <header className="mb-6">
        <h1 className="text-2xl font-bold">{problem.title}</h1>
        <p className="mt-1 text-sm" style={{ color: "var(--muted)" }}>
          <span className={`level-${problem.level}`}>{problem.level_label}</span>
          {" · "}
          {t(locale, "problems.limits")}: {problem.time_limit_ms} ms,{" "}
          {Math.round(problem.memory_limit_kb / 1024)} MB
          {problem.topics.length > 0 && ` · ${problem.topics.join(", ")}`}
        </p>
      </header>
      <div className="whitespace-pre-wrap leading-relaxed">{problem.statement}</div>
    </article>
  );
}
