import type { Metadata, Route } from "next";
import Link from "next/link";

import { EmptyState } from "@/components/ui/EmptyState";
import { inReaderAlphabet } from "@/i18n/alphabet";
import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";
import { api, type GlossaryEntry } from "@/lib/api";

export const dynamic = "force-dynamic";

export async function generateMetadata(): Promise<Metadata> {
  const locale = await getLocale();
  return {
    title: `${t(locale, "algorithms.glossary.title")} · ${t(locale, "nav.algorithms")}`,
    description: t(locale, "algorithms.glossary.intro"),
    alternates: { canonical: "/algorithms/glossary" },
  };
}

/** The library's glossary (ADR-0062 § 3): every term with its English name,
 *  other names and a short note. Article texts link their first use of a term
 *  here (`#<slug>`). The terms are Uzbek, from the library. */
export default async function GlossaryPage() {
  const locale = await getLocale();
  const entries = await api.algorithmGlossary().catch((): GlossaryEntry[] => []);
  const groups: { letter: string; rows: GlossaryEntry[] }[] = [];
  for (const entry of entries) {
    const letter = entry.term.charAt(0).toUpperCase();
    const last = groups[groups.length - 1];
    if (last && last.letter === letter) last.rows.push(entry);
    else groups.push({ letter, rows: [entry] });
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <nav aria-label={t(locale, "algorithms.breadcrumbs")} className="text-theme-sm rw-dim">
        <Link href={"/algorithms" as Route} className="rw-focus-ring hover:underline">
          {t(locale, "nav.algorithms")}
        </Link>
      </nav>
      <header>
        <h1 className="text-title-sm font-bold rw-strong">{t(locale, "algorithms.glossary.title")}</h1>
        <p className="mt-2 max-w-2xl text-theme-sm rw-dim">{t(locale, "algorithms.glossary.intro")}</p>
      </header>

      {groups.length > 1 && (
        <nav aria-label={t(locale, "algorithms.glossary.letters")} className="flex flex-wrap gap-1.5">
          {groups.map((group) => (
            <a
              key={group.letter}
              href={`#letter-${group.letter}`}
              className="inline-flex min-h-9 min-w-9 items-center justify-center rw-radius-sm border rw-line text-theme-sm font-medium rw-dim transition rw-hover-line rw-focus-ring"
            >
              {inReaderAlphabet(group.letter, "uz")}
            </a>
          ))}
        </nav>
      )}

      {groups.map((group) => (
        <section key={group.letter} id={`letter-${group.letter}`} className="space-y-3">
          <h2 className="text-theme-lg font-semibold rw-strong">{inReaderAlphabet(group.letter, "uz")}</h2>
          <dl className="space-y-3">
            {group.rows.map((entry) => (
              <div key={entry.slug} id={entry.slug} className="rw-radius border rw-line rw-surface p-4">
                <dt className="font-semibold rw-strong">
                  {inReaderAlphabet(entry.term, "uz")}{" "}
                  <span className="text-theme-sm font-normal rw-faint" lang="en">
                    ({entry.english})
                  </span>
                </dt>
                <dd className="mt-1 text-theme-sm rw-dim">{inReaderAlphabet(entry.note, "uz")}</dd>
                {entry.aliases.length > 0 && (
                  <dd className="mt-1 text-theme-xs rw-faint">
                    {t(locale, "algorithms.glossary.aliases")} {entry.aliases.join(", ")}
                  </dd>
                )}
              </div>
            ))}
          </dl>
        </section>
      ))}

      {groups.length === 0 && (
        <EmptyState variant="card" title={t(locale, "common.empty")} hint={t(locale, "common.emptyHint")} />
      )}
    </div>
  );
}
