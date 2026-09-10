"use client";

import type { Route } from "next";
import Link from "next/link";

import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { VERDICT_FILTERS } from "@/lib/api";

/** Urinishlar oqimining filtrlari.
 *
 * Ommabop masalada urinish minglab bo'ladi va filtrsiz ro'yxat o'qib
 * bo'lmaydigan oqimga aylanadi — KEP ham shu uchtasini beradi: verdikt,
 * til va «faqat meniki».
 *
 * Havolalar, tugma emas: holat URL da qoladi, ya'ni sahifani ulashsa
 * ham, orqaga qaytsa ham o'sha ro'yxat ochiladi.
 */
export function AttemptFilters({
  slug,
  languages,
  verdict,
  language,
  mine,
}: {
  slug: string;
  languages: string[];
  verdict?: string;
  language?: string;
  mine: boolean;
}) {
  const locale = useLocale();
  const { user, ready } = useSession();

  const href = (next: Record<string, string | undefined>): Route => {
    const params = new URLSearchParams();
    const merged = {
      verdict,
      language,
      mine: mine ? "true" : undefined,
      ...next,
    };
    for (const [key, value] of Object.entries(merged)) {
      if (value) params.set(key, value);
    }
    return `/problems/${slug}/status${params.size ? `?${params}` : ""}` as Route;
  };

  const chip = (active: boolean) =>
    `rw-radius-sm px-2.5 py-1 text-theme-xs font-medium transition ${
      active ? "rw-accent-soft rw-accent-ink" : "rw-dim rw-hover-bg"
    }`;

  return (
    <div className="flex flex-wrap items-center gap-1.5">
      <Link href={href({ verdict: undefined })} className={chip(!verdict)}>
        {t(locale, "attempts.allVerdicts")}
      </Link>
      {VERDICT_FILTERS.map(([value, key]) => (
        <Link
          key={value}
          href={href({ verdict: value })}
          className={chip(verdict === value)}
        >
          {t(locale, key)}
        </Link>
      ))}

      {languages.length > 1 && (
        <>
          <span className="mx-1 rw-faint">·</span>
          <Link
            href={href({ language: undefined })}
            className={chip(!language)}
          >
            Hamma til
          </Link>
          {languages.map((code) => (
            <Link
              key={code}
              href={href({ language: code })}
              className={chip(language === code)}
            >
              {code}
            </Link>
          ))}
        </>
      )}

      {ready && user && (
        <Link
          href={href({ mine: mine ? undefined : "true" })}
          className={`ml-auto ${chip(mine)}`}
        >
          Faqat meniki
        </Link>
      )}
    </div>
  );
}
