import type { Metadata } from "next";
import Link from "next/link";
import { Markdown } from "@/components/Markdown";
import { Badge, DifficultyBadge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { SampleTests } from "@/components/SampleTests";
import SubmitPanel from "@/components/SubmitPanel";
import { notFound } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";

type Props = {
  params: Promise<{ slug: string }>;
  searchParams: Promise<{ contest?: string }>;
};

/** SSR + metadata — masala sahifalari qidiruvda topilishi kerak (ADR-0003). */
// Jonli ma'lumot: har so'rovda serverda render qilinadi.
// Build vaqtida prerender qilinmaydi — CI da API ishlamaydi, va reyting
// jadvali baribir keshlanmasligi kerak. SSR SEO uchun yetarli (ADR-0003);
// ISR keyinroq optimizatsiya sifatida qo'shilishi mumkin.
export const dynamic = "force-dynamic";

export async function generateMetadata({
  params,
}: Pick<Props, "params">): Promise<Metadata> {
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

export default async function ProblemPage({ params, searchParams }: Props) {
  const { slug } = await params;
  // Musobaqa sahifasidan kelgan bo'lsa urinish o'sha musobaqaga yoziladi —
  // aks holda jadval yangilanmasdi (`AttemptCreateSerializer.contest`).
  const { contest } = await searchParams;
  const locale = DEFAULT_LOCALE;

  let problem;
  try {
    problem = await api.problem(slug);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }

  // Tillar ro'yxati serverda keshlanadi — muharrir uchun brauzerdan
  // qo'shimcha so'rov kerak emas, mehmonga ham ko'rinadi.
  const languages = await api.languages().then((page) => page.results);

  return (
    <div className="grid items-start gap-6 xl:grid-cols-[minmax(0,1fr)_minmax(0,560px)]">
      <article className="space-y-6">
        <header>
          <h1 className="text-title-sm font-bold rw-strong">{problem.title}</h1>
          <div className="mt-3 flex flex-wrap items-center gap-2">
            <DifficultyBadge value={problem.difficulty} />
            <span
              className={`level-${problem.level} text-theme-sm font-medium`}
            >
              {problem.level_label}
            </span>
            <Badge>
              {t(locale, "problems.limits")}: {problem.time_limit_ms} ms,{" "}
              {Math.round(problem.memory_limit_kb / 1024)} MB
            </Badge>
            {problem.topics.map((topic) => (
              <Badge key={topic} color="info">
                {topic}
              </Badge>
            ))}
          </div>
        </header>

        {contest && (
          <p className="rw-radius-sm rw-accent-soft px-4 py-2.5 text-theme-sm rw-accent-ink">
            Yechim <strong>{contest}</strong> musobaqasi hisobiga yoziladi.{" "}
            <Link href={`/contests/${contest}`} className="underline">
              Musobaqaga qaytish
            </Link>
          </p>
        )}

        <Card>
          <Markdown>{problem.statement}</Markdown>
        </Card>

        <SampleTests samples={problem.samples} />
      </article>

      <SubmitPanel
        problem={slug}
        languages={languages}
        samples={problem.samples}
        contest={contest}
      />
    </div>
  );
}
