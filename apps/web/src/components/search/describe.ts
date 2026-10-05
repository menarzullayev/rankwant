import { date, t, topicName, type Locale } from "@/i18n/messages";
import { kindLabelKey, type SearchHit } from "@/lib/search/model";

export type HitText = {
  title: string;
  /** Second line: what the hit is, and when or by whom. */
  subtitle: string;
  /** Right-hand number: difficulty or rating. */
  meta: string;
};

const DAY: Intl.DateTimeFormatOptions = {
  // Numeric on purpose: browsers without Uzbek month names print a
  // short month as "M10" (measured 2026-10-05).
  day: "2-digit",
  month: "2-digit",
  year: "numeric",
  // The site's day is Tashkent's; a server render in UTC would be a day
  // behind for anything published after 19:00.
  timeZone: "Asia/Tashkent",
};

function joined(...parts: (string | null | undefined)[]): string {
  return parts.filter(Boolean).join(" · ");
}

/** The words a hit is shown with — the palette and the results page agree. */
export function describeHit(hit: SearchHit, locale: Locale): HitText {
  const kindKey = kindLabelKey(hit);
  const kind = kindKey ? t(locale, kindKey) : "";
  const when = hit.date ? date(hit.date, locale, DAY) : "";
  switch (hit.type) {
    case "problem":
      return {
        title: hit.title,
        subtitle: hit.code ? `#${hit.code}` : "",
        meta: hit.meta ? String(hit.meta) : "",
      };
    case "user":
      return {
        title: `@${hit.key}`,
        subtitle: hit.subtitle ?? "",
        meta: hit.meta ? String(hit.meta) : "",
      };
    case "topic":
      return {
        title: topicName(
          {
            slug: hit.key,
            name_uz: hit.title,
            name_ru: hit.title_ru ?? "",
            name_en: hit.title_en ?? "",
          },
          locale,
        ),
        subtitle: t(locale, "search.topicProblems"),
        meta: "",
      };
    case "contest":
    case "news":
      return { title: hit.title, subtitle: joined(kind, when), meta: "" };
    case "learn":
      return { title: hit.title, subtitle: joined(kind, hit.subtitle), meta: "" };
  }
}
