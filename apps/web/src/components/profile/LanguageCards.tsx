import { Card } from "@/components/ui/Card";
import { t, type Locale } from "@/i18n/messages";
import type { LanguageStat } from "@/lib/api";
import { BrandIcon, languageIcon } from "@/lib/tech-icons";
import { SectionHint } from "./SectionHint";

/** Tillar — ko'p ishlatilgani birinchi (API shu tartibda beradi). */
export function LanguageCards({
  languages,
  locale,
}: {
  languages: LanguageStat[];
  locale: Locale;
}) {
  return (
    <Card title={t(locale, "profile.languagesTitle")} bodyClassName="space-y-4">
      <SectionHint>{t(locale, "profile.languagesHint")}</SectionHint>
      {languages.length === 0 ? (
        <p className="text-theme-sm rw-faint">{t(locale, "empty")}</p>
      ) : (
        <ul className="grid gap-3 sm:grid-cols-2">
          {languages.map((language) => {
            const icon = languageIcon(language.code);
            return (
              <li
                key={language.code}
                className="flex items-center gap-3 rw-radius border rw-line px-4 py-3"
              >
                <span className="flex size-9 shrink-0 items-center justify-center rw-radius-sm rw-chip">
                  {icon ? (
                    <BrandIcon icon={icon} className="size-5" />
                  ) : (
                    <span className="text-theme-xs font-bold">{language.name.slice(0, 2)}</span>
                  )}
                </span>
                <span className="min-w-0 flex-1">
                  <span className="block truncate font-medium rw-strong">{language.name}</span>
                  <span className="text-theme-xs rw-faint">{language.code}</span>
                </span>
                <span className="text-right text-theme-xs tabular-nums">
                  <span className="block rw-ok-ink">
                    ✓ {language.accepted} {t(locale, "profile.accepted")}
                  </span>
                  <span className="block rw-bad-ink">
                    ✕ {language.errors} {t(locale, "profile.errors")}
                  </span>
                </span>
              </li>
            );
          })}
        </ul>
      )}
    </Card>
  );
}
