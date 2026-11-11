import type { Metadata, Route } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { CATEGORY_LABEL, LibraryCard, isCategory } from "@/features/algorithms";
import { inReaderAlphabet } from "@/i18n/alphabet";
import { getLocale } from "@/i18n/server";
import { fill, t } from "@/i18n/messages";
import { api } from "@/lib/api";

export const dynamic = "force-dynamic";

type Props = { params: Promise<{ category: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { category } = await params;
  const locale = await getLocale();
  if (!isCategory(category)) return { title: t(locale, "algorithms.notFound") };
  return {
    title: `${t(locale, CATEGORY_LABEL[category])} · ${t(locale, "nav.algorithms")}`,
    alternates: { canonical: `/algorithms/${category}` },
  };
}

/** One section of the algorithms library, by its subsections. */
export default async function AlgorithmCategoryPage({ params }: Props) {
  const { category } = await params;
  if (!isCategory(category)) notFound();
  const locale = await getLocale();
  const rows = (await api.algorithmLibrary(locale)).filter((entry) => entry.category === category);
  if (rows.length === 0) notFound();

  // Subsections in the library's own order; their names are Uzbek only.
  const subsections: { name: string; rows: typeof rows }[] = [];
  for (const entry of rows) {
    const last = subsections[subsections.length - 1];
    if (last && last.name === entry.subcategory) last.rows.push(entry);
    else subsections.push({ name: entry.subcategory, rows: [entry] });
  }

  return (
    <div className="space-y-6">
      <nav aria-label={t(locale, "algorithms.breadcrumbs")} className="text-theme-sm rw-dim">
        <Link href={"/algorithms" as Route} className="rw-focus-ring hover:underline">
          {t(locale, "nav.algorithms")}
        </Link>
      </nav>
      <header>
        <h1 className="text-title-sm font-bold rw-strong">{t(locale, CATEGORY_LABEL[category])}</h1>
        <p className="mt-1 text-theme-xs rw-faint">{fill(t(locale, "algorithms.count"), { count: rows.length })}</p>
      </header>
      {subsections.map((section) => (
        <section key={section.name || "-"} className="space-y-3">
          {section.name && (
            <h2 className="text-theme-lg font-semibold rw-strong">{inReaderAlphabet(section.name, "uz")}</h2>
          )}
          <ul className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {section.rows.map((entry) => (
              <li key={entry.slug}>
                <LibraryCard entry={entry} locale={locale} />
              </li>
            ))}
          </ul>
        </section>
      ))}
    </div>
  );
}
