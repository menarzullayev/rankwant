import type { Metadata } from "next";
import { notFound } from "next/navigation";

import {
  ProblemEditorialPanel,
  ProblemSolversPanel,
  ProblemStatsPanel,
  ProblemTabs,
  SubmitPanel,
} from "@/features/problems";
import { ProblemAttemptsPanel } from "./_panels/ProblemAttemptsPanel";
import { ProblemDescription } from "./_panels/ProblemDescription";
import { ApiError, type ProblemDetail } from "@/lib/api";
import { getWithSession } from "@/lib/api.server";
import { SITE_URL, jsonLd } from "@/lib/site";
import { getLocale } from "@/i18n/server";
import { localeAlternatesFor } from "@/i18n/locale-alternates.server";
import { fill, t } from "@/i18n/messages";
import { resolveProblemTab } from "@/lib/problem-tabs";

type Props = {
  params: Promise<{ slug: string }>;
  searchParams: Promise<{
    tab?: string | string[];
    contest?: string;
    cursor?: string;
    verdict?: string;
    language?: string;
    mine?: string;
    username?: string;
    ordering?: string;
    size?: string;
  }>;
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
  const locale = await getLocale();
  try {
    const problem = await getWithSession<ProblemDetail>(
      `/problems/${slug}/`,
    );
    const title = problem.code
      ? `#${String(problem.code).padStart(4, "0")} · ${problem.title}`
      : problem.title;
    const description = fill(t(locale, "problem.difficultyDescription"), {
      title: problem.title,
      difficulty: problem.difficulty,
    });
    // Havolalar asosan Telegramda ulashiladi: OG'siz ular yalang'och
    // manzil bo'lib chiqadi. Filtr (`contest`) canonical'da yo'q;
    // `?lang=` self-canonical (HITL 2026-09-20).
    const path = `/problems/${slug}`;
    const alternates = await localeAlternatesFor(path);
    return {
      title,
      description,
      alternates,
      openGraph: {
        type: "article",
        title,
        description,
        url: alternates.canonical,
      },
      twitter: { card: "summary", title, description },
    };
  } catch {
    return { title: t(locale, "problem.notFound") };
  }
}

/** Masala bo'limlari — bitta manzil, beshta tab (`?tab=`).
 *
 *  Nega SERVERDA va `?tab=` bilan (auth sahifasi naqshi):
 *  - har tab HAQIQIY manzil — ulashsa, yangilasa, Back/Forward da holat
 *    saqlanadi; noto'g'ri qiymat `description` ga tushadi;
 *  - almashish `<Link scroll={false}>` — to'liq qayta yuklash yo'q;
 *  - faqat faol tabning ma'lumoti so'raladi (urinish/statistika/yechganlar
 *    keraksiz yuklanmaydi), kesh `api.*` dagi kabi (`stats` 30 s);
 *  - qo'shimcha klient holati yo'q — URL allaqachon holat.
 *
 *  `description` + `editorial` — ikki ustun (matn + muharrir, avvalgidek);
 *  `attempts`/`statistics`/`solvers` — bir ustun (eski alohida sahifalar
 *  kabi, muharrirsiz — Monaco keraksiz yuklanmaydi).
 */
export default async function ProblemPage({ params, searchParams }: Props) {
  const { slug } = await params;
  // Musobaqa sahifasidan kelgan bo'lsa urinish o'sha musobaqaga yoziladi —
  // aks holda jadval yangilanmasdi (`AttemptCreateSerializer.contest`).
  const query = await searchParams;
  const { contest } = query;
  const tab = resolveProblemTab(query.tab);
  const locale = await getLocale();

  let problem: ProblemDetail;
  try {
    problem = await getWithSession<ProblemDetail>(`/problems/${slug}/`);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }

  const jsonLdDescription = fill(t(locale, "problem.difficultyDescription"), {
    title: problem.title,
    difficulty: problem.difficulty,
  });

  // Muharrirli ko'rinish — faqat yechish kontekstidagi tablarda.
  if (tab === "description" || tab === "editorial") {
    return (
      <div className="grid grid-cols-[minmax(0,1fr)] items-start gap-6 xl:grid-cols-[minmax(0,1fr)_minmax(0,560px)]">
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: jsonLd({
              "@context": "https://schema.org",
              "@type": "LearningResource",
              name: problem.title,
              description: jsonLdDescription,
              url: `${SITE_URL}/problems/${slug}`,
              educationalLevel: problem.level_label,
              learningResourceType: "Problem",
              inLanguage: locale,
              isAccessibleForFree: true,
              creator: { "@id": `${SITE_URL}/#organization` },
            }),
          }}
        />
        <div className="min-w-0 space-y-6">
          <ProblemTabs slug={slug} current={tab} contest={contest} />
          {tab === "description" ? (
            <ProblemDescription
              problem={problem}
              slug={slug}
              contest={contest}
              locale={locale}
            />
          ) : (
            <ProblemEditorialPanel
              problem={problem}
              slug={slug}
              locale={locale}
            />
          )}
        </div>

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

  return (
    <div className="space-y-6">
      <ProblemTabs slug={slug} current={tab} contest={contest} />
      {tab === "attempts" && (
        <ProblemAttemptsPanel
          problem={problem}
          slug={slug}
          query={{
            cursor: one(query.cursor),
            verdict: one(query.verdict),
            language: one(query.language),
            mine: one(query.mine),
            username: one(query.username),
            ordering: one(query.ordering),
            size: one(query.size),
          }}
          locale={locale}
        />
      )}
      {tab === "statistics" && (
        <ProblemStatsPanel problem={problem} slug={slug} locale={locale} />
      )}
      {tab === "solvers" && (
        <ProblemSolversPanel
          problem={problem}
          slug={slug}
          ordering={one(query.ordering) ?? "first"}
          locale={locale}
        />
      )}
    </div>
  );
}

/** Query qiymati bitta satr bo'lsa shuni, massiv bo'lsa BIRINCHISINI
 *  qaytaradi (`login` sahifasidagi `one()` bilan bir xil sabab). */
function one(value: string | string[] | undefined): string | undefined {
  return Array.isArray(value) ? value[0] : value;
}
