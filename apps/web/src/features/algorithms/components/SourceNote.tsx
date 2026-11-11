import { fill, t, type Locale } from "@/i18n/messages";
import type { ArticleSource } from "@/lib/api";

import { LICENCE_NAME, LICENCE_URL } from "../catalog";

const LINK = "font-medium underline underline-offset-2 rw-accent-ink rw-focus-ring";

/** The attribution CC BY-SA 4.0 asks for (ADR-0062 § 2.2): the original and
 *  its authors, who translated it and how it was reviewed, that we changed
 *  it, and the licence — under every imported article. */
export function SourceNote({
  source,
  changes,
  original,
  locale,
}: {
  source: ArticleSource;
  changes: number;
  original: boolean;
  locale: Locale;
}) {
  return (
    <section
      aria-labelledby="algorithm-source"
      className="space-y-2 rw-radius border rw-line rw-surface p-5 text-theme-sm rw-dim"
    >
      <h2 id="algorithm-source" className="text-theme-base font-semibold rw-strong">
        {t(locale, "algorithms.source.title")}
      </h2>
      <p>
        {t(locale, "algorithms.source.original")}{" "}
        <a href={source.url} target="_blank" rel="noopener noreferrer" className={LINK}>
          {source.title}
          <span className="sr-only"> {t(locale, "footer.opensNewTab")}</span>
        </a>
      </p>
      <p>{t(locale, "algorithms.source.authors")}</p>
      {original ? (
        <p>{t(locale, "algorithms.source.englishOriginal")}</p>
      ) : (
        <p>{t(locale, "algorithms.source.ai")}</p>
      )}
      <p>
        {original
          ? t(locale, "algorithms.source.changedMarkup")
          : fill(t(locale, "algorithms.source.changed"), { count: changes })}
      </p>
      <p>
        {t(locale, "algorithms.source.license")}{" "}
        <a href={LICENCE_URL} target="_blank" rel="noopener noreferrer license" className={LINK}>
          {LICENCE_NAME}
          <span className="sr-only"> {t(locale, "footer.opensNewTab")}</span>
        </a>
      </p>
    </section>
  );
}
