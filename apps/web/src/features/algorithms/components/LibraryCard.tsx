import type { Route } from "next";
import Link from "next/link";

import { Badge } from "@/components/ui/Badge";
import { inReaderAlphabet } from "@/i18n/alphabet";
import { t, type Locale } from "@/i18n/messages";
import type { LibraryEntry } from "@/lib/api";

import { LEVEL_COLOR, LEVEL_LABEL, algorithmPath, isLevel } from "../catalog";

/** One article in the algorithms catalogue. The idea and the subsection are
 *  in Uzbek only, so an English reader (who gets the original's title) sees
 *  the title and the level alone. */
export function LibraryCard({ entry, locale }: { entry: LibraryEntry; locale: Locale }) {
  const uzbek = entry.locale === "uz";
  return (
    <Link
      href={algorithmPath(entry.category, entry.slug) as Route}
      className="flex h-full flex-col gap-2 rw-radius border rw-line rw-surface p-4 transition rw-hover-line rw-focus-ring"
    >
      <span className="font-semibold rw-strong">{inReaderAlphabet(entry.title, entry.locale)}</span>
      {uzbek && entry.summary && (
        <span className="line-clamp-2 text-theme-sm rw-dim">{inReaderAlphabet(entry.summary, "uz")}</span>
      )}
      <span className="mt-auto flex flex-wrap items-center gap-2 text-theme-xs rw-faint">
        {isLevel(entry.level) && (
          <Badge color={LEVEL_COLOR[entry.level]}>{t(locale, LEVEL_LABEL[entry.level])}</Badge>
        )}
        <span>
          {entry.reading_minutes} {t(locale, "learn.minutes")}
        </span>
        {uzbek && entry.subcategory && <span>{inReaderAlphabet(entry.subcategory, "uz")}</span>}
      </span>
    </Link>
  );
}
