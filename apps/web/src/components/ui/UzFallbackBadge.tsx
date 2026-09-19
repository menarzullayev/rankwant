import { localNameInfo, t, type Locale } from "@/i18n/messages";

/** Marker shown when a content name has no text in the active language.
 *
 *  Topic/skill names live in `name_uz` / `name_ru` / `name_en` only.
 *  Other locales must not inherit Uzbek — they show the English
 *  property (the slug). The marker tells the reader that this is an
 *  identifier, not a translated title.
 */
export type NameRow = { name_uz: string; name_ru: string; name_en: string };

/** Name plus marker — for page copy. */
export function ContentName({ row, locale }: { row: NameRow; locale: Locale }) {
  const info = localNameInfo(row, locale);
  return (
    <>
      {info.text}
      {info.locale === null && <UzFallbackBadge locale={locale} />}
    </>
  );
}

/** Name plus marker — for plain-text contexts such as `<option>`. */
export function contentNameText(row: NameRow, locale: Locale): string {
  const info = localNameInfo(row, locale);
  return info.locale === null
    ? `${info.text} · ${t(locale, "locale.contentUz")}`
    : info.text;
}

export function UzFallbackBadge({ locale }: { locale: Locale }) {
  const label = t(locale, "content.uzOnly");
  const chip = t(locale, "locale.contentUz");
  return (
    <>
      <span
        title={label}
        aria-hidden="true"
        className="ml-1.5 shrink-0 rounded rw-chip px-1 align-middle
 text-theme-xs font-semibold rw-dim-2"
      >
        {chip}
      </span>
      <span className="sr-only"> ({label})</span>
    </>
  );
}
