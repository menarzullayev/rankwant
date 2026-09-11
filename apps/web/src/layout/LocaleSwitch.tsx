"use client";

import { useRouter } from "next/navigation";
import { useTransition } from "react";

import { useLocale } from "@/i18n/LocaleProvider";
import { LOCALES, LOCALE_NAMES, type Locale } from "@/i18n/messages";
import { announcePrefs } from "@/lib/prefs";

/** Til tanlash — cookie'ga yozadi va sahifani serverdan qayta oladi.
 *
 * Cookie bir yil yashaydi va `SameSite=Lax`: bu shaxsiy ma'lumot emas,
 * lekin boshqa saytdan o'zgartirilishiga ham hojat yo'q.
 */
export function LocaleSwitch() {
  const locale = useLocale();
  const router = useRouter();
  const [pending, startTransition] = useTransition();

  function choose(next: string) {
    document.cookie = `rw_locale=${next}; path=/; max-age=31536000; samesite=lax`;
    // Hisobga ham — xatlar shu tilda yuboriladi.
    announcePrefs({ locale: next });
    startTransition(() => router.refresh());
  }

  return (
    <label className="inline-flex items-center">
      <span className="sr-only">Til / Language</span>
      <select
        value={locale}
        disabled={pending}
        onChange={(event) => choose(event.target.value)}
        className="rw-radius-sm border rw-line rw-field-bg px-2 py-1 text-theme-xs rw-dim
          transition rw-hover-strong disabled:opacity-60"
      >
        {LOCALES.map((code: Locale) => (
          <option key={code} value={code}>
            {LOCALE_NAMES[code]}
          </option>
        ))}
      </select>
    </label>
  );
}
