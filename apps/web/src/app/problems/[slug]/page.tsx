import type { Metadata } from "next";
import Link from "next/link";
import { Attachments } from "@/components/Attachments";
import { Markdown } from "@/components/Markdown";
import { ReportProblem } from "@/components/ReportProblem";
import { SimilarProblems } from "@/components/SimilarProblems";
import { Badge, DifficultyBadge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { Editorial } from "@/components/Editorial";
import { ProblemActions } from "@/components/ProblemActions";
import { ProblemTabs } from "@/components/ProblemTabs";
import { SampleTests } from "@/components/SampleTests";
import { StatementSize } from "@/components/StatementSize";
import SubmitPanel from "@/components/SubmitPanel";
import { notFound } from "next/navigation";
import { api, ApiError, type ProblemDetail } from "@/lib/api";
import { getWithSession } from "@/lib/api.server";
import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";

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
    const title = problem.code
      ? `#${String(problem.code).padStart(4, "0")} · ${problem.title}`
      : problem.title;
    const description = `${problem.title} — qiyinlik ${problem.difficulty}. RankWant masala arxivi.`;
    // Havolalar asosan Telegramda ulashiladi: OG'siz ular yalang'och
    // manzil bo'lib chiqadi. `canonical` esa filtrli va til cookie'li
    // variantlarni bitta manzilga yig'adi.
    return {
      title,
      description,
      alternates: { canonical: `/problems/${slug}` },
      openGraph: {
        type: "article",
        title,
        description,
        url: `/problems/${slug}`,
      },
      twitter: { card: "summary", title, description },
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
  const locale = await getLocale();

  let problem;
  try {
    problem = await getWithSession<ProblemDetail>(`/problems/${slug}/`);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }

  return (
    // `min-w-0` bezak emas: grid farzandining standart `min-width: auto`
    // uni MAZMUNIDAN kichik qilmaydi, ya'ni Monaco yoki keng jadval butun
    // sahifani cho'zib yuboradi. O'lchandi — 412 px li telefonda sahifa
    // 600 px bo'lib, yon tomonga siljirdi va tab tugmalarini bosib
    // bo'lmasdi.
    <div className="grid grid-cols-[minmax(0,1fr)] items-start gap-6 xl:grid-cols-[minmax(0,1fr)_minmax(0,560px)]">
      <article className="min-w-0 space-y-6">
        <ProblemTabs slug={slug} current="statement" />

        <header>
          <div className="flex flex-wrap items-baseline gap-3">
            {/* Ommaviy raqam — og'zaki muomala uchun ("431-masala"). */}
            {problem.code !== null && (
              <span className="font-mono text-theme-sm rw-faint tabular-nums">
                #{String(problem.code).padStart(4, "0")}
              </span>
            )}
            <h1 className="text-title-sm font-bold rw-strong">
              {problem.title}
            </h1>
          </div>
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
            {problem.partial_scoring && <Badge color="info">Qisman ball</Badge>}
            {!problem.has_tests && (
              <Badge color="warning">Testlar tayyorlanmoqda</Badge>
            )}
            {problem.topics.map((topic) => (
              <Badge key={topic} color="info">
                {topic}
              </Badge>
            ))}
          </div>

          {/* Yechilish foizi — masala qanchalik qiyinligini raqamdan
              ko'ra aniqroq ko'rsatadi (RoboContest «Murakkablik», CF da
              solve count). Urinish bo'lmasa foiz ma'nosiz. */}
          <p className="mt-3 text-theme-sm rw-dim">
            {problem.author && (
              <>
                Muallif:{" "}
                {problem.author.has_profile ? (
                  <Link
                    href={`/users/${problem.author.username}`}
                    className="rw-link-hover"
                  >
                    {problem.author.display_name}
                  </Link>
                ) : (
                  problem.author.display_name
                )}{" "}
                ·{" "}
              </>
            )}
            {problem.solved_count} kishi yechdi · {problem.attempt_count}{" "}
            urinish
            {problem.attempt_count > 0 &&
              ` · ${Math.round((problem.solved_count / problem.attempt_count) * 100)}% muvaffaqiyat`}
          </p>

          <div className="mt-2">
            <ProblemActions problem={problem} />
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
          <StatementSize>
            <div className="space-y-5">
              {problem.image && (
                /* eslint-disable-next-line @next/next/no-img-element --
                   rasm import qilingan arxivning tashqi domenida; uni
                   `next/image` ga berish har bir manba uchun alohida
                   `remotePatterns` yozishni talab qilardi. */
                <img
                  src={problem.image}
                  alt=""
                  className="w-full rw-radius-sm"
                />
              )}
              <Markdown>{problem.statement}</Markdown>

              {problem.input_format && (
                <section>
                  <h2 className="mb-1.5 text-theme-lg font-semibold rw-strong">
                    Kiruvchi ma&apos;lumot
                  </h2>
                  <Markdown>{problem.input_format}</Markdown>
                </section>
              )}

              {problem.output_format && (
                <section>
                  <h2 className="mb-1.5 text-theme-lg font-semibold rw-strong">
                    Chiquvchi ma&apos;lumot
                  </h2>
                  <Markdown>{problem.output_format}</Markdown>
                </section>
              )}
            </div>
          </StatementSize>
        </Card>

        <SampleTests samples={problem.samples} />

        {problem.note && (
          <Card title="Izoh">
            <Markdown>{problem.note}</Markdown>
          </Card>
        )}

        <Attachments items={problem.attachments} locale={locale} />

        {problem.editorial_state.available && (
          <Editorial
            slug={slug}
            text={problem.editorial}
            state={problem.editorial_state}
          />
        )}

        <SimilarProblems items={problem.similar} locale={locale} />

        <ReportProblem slug={slug} />

        {problem.source && (
          <p className="text-theme-sm rw-faint">
            Manba:{" "}
            {problem.source_url ? (
              <a
                href={problem.source_url}
                rel="noopener noreferrer"
                className="underline"
              >
                {problem.source}
              </a>
            ) : (
              problem.source
            )}
            {problem.source_rating !== null &&
              ` · asl reyting ${problem.source_rating}`}
          </p>
        )}
      </article>

      <SubmitPanel
        problem={slug}
        languages={problem.languages}
        samples={problem.samples}
        contest={contest}
        hasTests={problem.has_tests}
      />
    </div>
  );
}
