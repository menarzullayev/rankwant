import { inReaderAlphabet } from "@/i18n/alphabet";
import { t, type Locale } from "@/i18n/messages";

/** The idea, the complexity and the uses — the library's short card above the
 *  text (Uzbek; not shown over the English original). */
export function ArticleFacts({
  idea,
  complexity,
  uses,
  locale,
}: {
  idea: string;
  complexity: string;
  uses: string;
  locale: Locale;
}) {
  const rows = [
    { key: "algorithms.idea" as const, value: idea },
    { key: "algorithms.complexity" as const, value: complexity },
    { key: "algorithms.uses" as const, value: uses },
  ].filter((row) => row.value);
  if (rows.length === 0) return null;
  return (
    <dl className="grid gap-4 rw-radius border rw-line rw-surface p-5 md:grid-cols-3">
      {rows.map((row) => (
        <div key={row.key}>
          <dt className="text-theme-xs font-semibold uppercase tracking-wide rw-faint">{t(locale, row.key)}</dt>
          <dd className="mt-1 text-theme-sm rw-strong">{inReaderAlphabet(row.value, "uz")}</dd>
        </div>
      ))}
    </dl>
  );
}
