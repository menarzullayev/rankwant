import { fill, LOCALE_NAMES, t, type Locale } from "@/i18n/messages";

/** Says so when the reader's language is not written yet and the course's
 *  own language is shown instead. */
export function FallbackNote({ shown, locale }: { shown: string; locale: Locale }) {
  if (shown === locale) return null;
  const name = (code: string) => LOCALE_NAMES[code as Locale] ?? code;
  return (
    <p className="text-theme-xs rw-faint">
      {fill(t(locale, "course.fallback"), { locale: name(locale), shown: name(shown) })}
    </p>
  );
}
