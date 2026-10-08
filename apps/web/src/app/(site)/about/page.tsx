import Link from "next/link";
import type { Metadata } from "next";

import { ABOUT_VERDICT_ORDER } from "@/content/about/verdict-guide-order";
import {
  AboutJourney,
  AboutToc,
  GuideSection,
  LanguageGuide,
  VerdictGuide,
} from "@/features/about/server";
import { localeAlternatesFor } from "@/i18n/locale-alternates.server";
import { getLocale } from "@/i18n/server";
import { fill, t, type MessageKey } from "@/i18n/messages";
import { api } from "@/lib/api";

const SUBMIT_STEPS: MessageKey[] = [
  "about.submit.pickProblem",
  "about.submit.pickLanguage",
  "about.submit.useStdio",
  "about.submit.sendForm",
  "about.submit.waitJudge",
  "about.submit.analyzeResult",
];

const PRACTICES: MessageKey[] = [
  "about.practices.samples",
  "about.practices.limits",
  "about.practices.algorithms",
  "about.practices.edges",
  "about.practices.format",
  "about.practices.fastIo",
  "about.practices.debug",
  "about.practices.readAll",
];

const NOTES: MessageKey[] = ["about.notes.io", "about.notes.cpp", "about.notes.java"];

/** The four ways an answer is graded - one line each. A problem uses
 *  exactly one of them, and which one decides what a solver has to do
 *  (flush after every write, or expect a score instead of a yes/no). */
const EVALUATION: MessageKey[] = [
  "about.eval.standard",
  "about.eval.special",
  "about.eval.interactive",
  "about.eval.scorer",
  "about.eval.function",
  "about.eval.answer",
  "about.eval.twoPass",
  "about.eval.sql",
];

/** The page is shared under its own title, sentence and address. It used
 *  to go out with the site's description and `og:url` of the home page
 *  (measured 2026-10-06). */
export async function generateMetadata(): Promise<Metadata> {
  const locale = await getLocale();
  const title = t(locale, "about.title");
  const description = t(locale, "about.lead");
  const alternates = await localeAlternatesFor("/about");
  return {
    title: t(locale, "nav.about"),
    description,
    alternates,
    openGraph: {
      title,
      description,
      url: alternates.canonical,
      type: "article",
      // A page's `openGraph` replaces the layout's, it is not merged.
      siteName: "RankWant",
    },
  };
}

/** How the platform works: a short way in, then the reference.
 *
 *  One page with a contents list, not tabs: this is a page people search —
 *  with the browser's "find in page", from a search engine, from a link
 *  to one section — and a tab would hide what they look for. Only the two
 *  parts that hold a choice are client components (`LanguageGuide`,
 *  `VerdictGuide`); the rest is rendered once on the server. */
export default async function AboutPage() {
  const locale = await getLocale();
  const languages = await api
    .languages()
    .catch(() => ({ results: [] as { code: string; name: string; version: string }[] }));
  const anchorLabel = t(locale, "about.anchor");
  const verdictCount = ABOUT_VERDICT_ORDER.length;

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <header className="space-y-2">
        <h1 className="text-title-sm font-bold rw-strong">{t(locale, "about.title")}</h1>
        <p className="max-w-prose text-theme-sm rw-dim">{t(locale, "about.lead")}</p>
      </header>

      <div className="xl:grid xl:grid-cols-[11rem_minmax(0,1fr)] xl:items-start xl:gap-6">
        <AboutToc />

        <div className="mt-4 min-w-0 space-y-6 xl:mt-0">
          <AboutJourney />

          <GuideSection id="submit" title={t(locale, "about.submit.title")} anchorLabel={anchorLabel}>
            <ol className="list-decimal space-y-2 pl-5 text-theme-sm rw-dim">
              {SUBMIT_STEPS.map((key) => (
                <li key={key}>{t(locale, key)}</li>
              ))}
            </ol>
          </GuideSection>

          <GuideSection
            id="languages"
            title={t(locale, "about.compilers.title")}
            note={
              languages.results.length > 0
                ? fill(t(locale, "about.lang.count"), { count: languages.results.length })
                : undefined
            }
            anchorLabel={anchorLabel}
          >
            <LanguageGuide languages={languages.results} />
            <ul className="mt-4 list-disc space-y-2 border-t rw-divider pt-4 pl-5 text-theme-sm rw-dim">
              {NOTES.map((key) => (
                <li key={key}>{t(locale, key)}</li>
              ))}
            </ul>
          </GuideSection>

          <GuideSection
            id="verdicts"
            title={fill(t(locale, "about.verdicts.title"), { count: verdictCount })}
            anchorLabel={anchorLabel}
          >
            <p className="mb-3 text-theme-sm rw-dim">
              {fill(t(locale, "about.verdicts.intro"), { count: verdictCount })}
            </p>
            <VerdictGuide />
          </GuideSection>

          <GuideSection id="practices" title={t(locale, "about.practices.title")} anchorLabel={anchorLabel}>
            <ul className="list-disc space-y-2 pl-5 text-theme-sm rw-dim">
              {PRACTICES.map((key) => (
                <li key={key}>{t(locale, key)}</li>
              ))}
            </ul>
          </GuideSection>

          <GuideSection id="judge" title={t(locale, "about.judge.title")} anchorLabel={anchorLabel}>
            <p className="text-theme-sm rw-dim whitespace-pre-line">{t(locale, "about.judge.body")}</p>
            <h3 className="mt-4 text-theme-sm font-semibold rw-strong">{t(locale, "about.eval.title")}</h3>
            <ul className="mt-2 list-disc space-y-2 pl-5 text-theme-sm rw-dim">
              {EVALUATION.map((key) => (
                <li key={key}>{t(locale, key)}</li>
              ))}
            </ul>
            <p className="mt-3 border-t rw-divider pt-3 text-theme-sm rw-dim">
              {t(locale, "about.ratingTeaser")}{" "}
              <Link href="/rating" className="font-medium rw-accent-ink hover:underline">
                {t(locale, "nav.formulas")}
              </Link>
              .
            </p>
          </GuideSection>
        </div>
      </div>
    </div>
  );
}
