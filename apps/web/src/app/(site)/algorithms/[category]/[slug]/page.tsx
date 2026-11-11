import type { Metadata, Route } from "next";
import Link from "next/link";
import { notFound, permanentRedirect } from "next/navigation";

import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { Markdown } from "@/components/ui/Markdown";
import {
  ArticleFacts,
  CATEGORY_LABEL,
  LEVEL_COLOR,
  LEVEL_LABEL,
  PracticeLists,
  SourceNote,
  algorithmPath,
  isCategory,
  isLevel,
  linkTerms,
  withoutPracticeSection,
  withoutTitle,
} from "@/features/algorithms";
import { inReaderAlphabet } from "@/i18n/alphabet";
import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";
import { api, ApiError, type ArticleDetail } from "@/lib/api";

export const dynamic = "force-dynamic";

type Props = { params: Promise<{ category: string; slug: string }> };

async function load(slug: string, locale: string): Promise<ArticleDetail | null> {
  try {
    return await api.algorithm(slug, locale);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) return null;
    throw error;
  }
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const locale = await getLocale();
  const article = await load(slug, locale);
  if (article === null || !article.category) return { title: t(locale, "algorithms.notFound") };
  return {
    title: inReaderAlphabet(article.title, article.locale),
    description: inReaderAlphabet(article.summary, "uz"),
    alternates: { canonical: algorithmPath(article.category, article.slug) },
  };
}

/** An article of the algorithms library (ADR-0062). The English reader gets
 *  the cp-algorithms original; every article carries its attribution. */
export default async function AlgorithmPage({ params }: Props) {
  const { category, slug } = await params;
  const locale = await getLocale();
  const article = await load(slug, locale);
  if (article === null || !article.category) notFound();
  // One address per article: a wrong section in the link leads to the right one.
  if (article.category !== category) permanentRedirect(algorithmPath(article.category, slug) as Route);

  const section = isCategory(article.category) ? t(locale, CATEGORY_LABEL[article.category]) : article.category;
  // `?? null`: a response cached before a deploy may lack the field.
  const attribution = article.attribution ?? null;
  const translated = attribution !== null && !article.original;
  // The title is above, and the practice links get their own list below.
  const title = withoutTitle(article.body);
  const text = article.external_links.length > 0 ? withoutPracticeSection(title) : title;
  // The first use of a glossary term links to it, its note as the tooltip;
  // the glossary is Uzbek, so the English original goes without.
  const glossary = article.original ? [] : await api.algorithmGlossary().catch(() => []);
  const body = linkTerms(text, glossary, { note: (note) => inReaderAlphabet(note, "uz") });

  return (
    <article className="mx-auto max-w-4xl space-y-6">
      <nav aria-label={t(locale, "algorithms.breadcrumbs")} className="flex flex-wrap gap-1.5 text-theme-sm rw-dim">
        <Link href={"/algorithms" as Route} className="rw-focus-ring hover:underline">
          {t(locale, "nav.algorithms")}
        </Link>
        <span aria-hidden>/</span>
        <Link href={`/algorithms/${article.category}` as Route} className="rw-focus-ring hover:underline">
          {section}
        </Link>
      </nav>

      <header>
        <h1 className="text-title-sm font-bold rw-strong">{inReaderAlphabet(article.title, article.locale)}</h1>
        <div className="mt-3 flex flex-wrap items-center gap-2">
          {isLevel(article.level) && (
            <Badge color={LEVEL_COLOR[article.level]}>{t(locale, LEVEL_LABEL[article.level])}</Badge>
          )}
          <Badge>
            {article.reading_minutes} {t(locale, "learn.minutes")}
          </Badge>
          {translated && <Badge color="info">{t(locale, "algorithms.aiMark")}</Badge>}
        </div>
      </header>

      {!article.original && (
        <ArticleFacts idea={article.idea} complexity={article.complexity} uses={article.uses} locale={locale} />
      )}

      <Card>
        <Markdown lang={article.locale} anchors>
          {body}
        </Markdown>
      </Card>

      <PracticeLists here={article.practice_here} elsewhere={article.external_links} locale={locale} />

      {attribution !== null && (
        <SourceNote
          source={attribution}
          changes={article.review?.changes ?? 0}
          original={article.original}
          locale={locale}
        />
      )}
    </article>
  );
}
