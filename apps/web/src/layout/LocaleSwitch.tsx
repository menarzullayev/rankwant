"use client";

import type { Route } from "next";
import { useRouter } from "next/navigation";
import { useCallback, useRef, useState, useTransition } from "react";

import { Dropdown, type DropdownOption } from "@/components/ui/Dropdown";
import { toNewAlphabet } from "@rankwant/shared/alphabet";

import {
  ALPHABET_LOCALE,
  DEFAULT_ALPHABET,
  OLD_ALPHABET,
  alphabetCookieLine,
} from "@/i18n/alphabet";
import { useAlphabet, useLocale, useLocaleAuto } from "@/i18n/LocaleProvider";
import { LOCALE_PARAM } from "@/i18n/locale-params";
import {
  LOCALES,
  LOCALE_NAMES,
  hasContentNames,
  t,
  type Locale,
} from "@/i18n/messages";
import { announcePrefs } from "@/lib/prefs";

import { LocaleFlag } from "./LocaleFlag";

/** «Avtomatik» — cookie o'chiriladi va til yana sarlavhadan aniqlanadi. */
const AUTO = "__auto__";
/** Uzbek in the old alphabet (ADR-0059) — a second entry for the same locale. */
const UZ_OLD = "uz~old";

/** A language's own name; Uzbek in the alphabet it is shown in. */
function nativeName(code: Locale, old = false): string {
  if (code !== ALPHABET_LOCALE) return LOCALE_NAMES[code];
  return old ? LOCALE_NAMES[code] : toNewAlphabet(LOCALE_NAMES[code]);
}

/** Ro'yxat guruhlari va guruh ichidagi tartib.
 *
 * ⚠️ Bu yerda ataylab `LOCALES` ning TO'LIQ nusxasi yo'q (2026-09-24,
 * RW-ARCH-013). Ilgari guruhlar o'nta tilni qo'lda sanab chiqardi:
 * o'n birinchi til qo'shilganda u jimgina ro'yxatdan tushib qolardi —
 * chunki `tsc` bu massivni `LOCALES` bilan bog'lamaydi.
 *
 * Endi guruhlar — bu TARTIB bayoni, to'liqlik esa quyida RUNTIME
 * tekshiruvi bilan kafolatlanadi. Yangi til `LOCALES` ga qo'shilsa,
 * ilova ishga tushishida xato beriladi — jim yo'qolmaydi. */
const GROUPS: {
  key: "locale.group.core" | "locale.group.region" | "locale.group.broad";
  locales: Locale[];
}[] = [
  { key: "locale.group.core", locales: ["uz", "ru", "en", "kaa"] },
  { key: "locale.group.region", locales: ["kk", "ky", "tg", "tr"] },
  { key: "locale.group.broad", locales: ["zh", "es"] },
];

/** Har bir til AYNAN bitta guruhda turishini kafolatlaydi.
 *
 * Nega: guruhlar — qo'lda yozilgan tartib, ya'ni ular `LOCALES` dan
 * orqada qolishi mumkin. Bu tekshiruv shu farqni jim qoldirmaydi:
 * tushib qolgan til — uni hech qachon ko'rmaydigan foydalanuvchidir. */
{
  const grouped = new Set(GROUPS.flatMap((group) => group.locales));
  const missing = LOCALES.filter((locale) => !grouped.has(locale));
  const extra = [...grouped].filter(
    (locale) => !(LOCALES as readonly string[]).includes(locale),
  );
  if (missing.length || extra.length) {
    throw new Error(
      `i18n: LocaleSwitch guruhlari LOCALES bilan mos emas — ` +
        `yetishmaydi: [${missing.join(", ")}], ortiqcha: [${extra.join(", ")}]`,
    );
  }
}

/** Endonim yonidagi inglizcha nom — qidiruv kaliti, tarjima emas. */
const ENGLISH_NAMES: Record<Locale, string> = {
  uz: "Uzbek",
  kaa: "Karakalpak",
  ru: "Russian",
  en: "English",
  kk: "Kazakh",
  ky: "Kyrgyz",
  tg: "Tajik",
  tr: "Turkish",
  zh: "Chinese",
  es: "Spanish",
};

/** Panel kengligi (`w-64`) va chekka.
 *
 *  Tor ekran sharti shu ikkisidan chiqadi, ekran kengligidan emas: panel
 *  tugmaning o'ng chetidan 256px chapga osiladi, ya'ni tugma chetidan
 *  256px sig'masa — panel viewport'dan chiqib ketadi.
 */
const PANEL_W = 256;
const PANEL_GAP = 8;

/** Til tanlagich — yagona qidiruvli `Dropdown`.
 *
 *  Almashtirish ARXITEKTURASI o'zgarmaydi: cookie + `router.refresh()`.
 *  Ko'rinish endi input trigger: yozilganda ro'yxat filtrlanaveradi.
 *  Triggerdagi endonim tor ekranda `Dropdown` header inputida
 *  `max-w-[3rem]` bilan qirqiladi — 320 px da header toshmasin.
 */
export function LocaleSwitch() {
  const locale = useLocale();
  const auto = useLocaleAuto();
  const alphabet = useAlphabet();
  const router = useRouter();
  const [pending, startTransition] = useTransition();
  const [optimistic, setOptimistic] = useState<string | null>(null);
  const settled = auto
    ? AUTO
    : locale === ALPHABET_LOCALE && alphabet === "old"
      ? UZ_OLD
      : locale;
  const current: string =
    optimistic !== null && optimistic !== settled ? optimistic : settled;
  const shown: Locale =
    current === AUTO
      ? locale
      : current === UZ_OLD
        ? ALPHABET_LOCALE
        : (current as Locale);
  const currentLabel = nativeName(shown, alphabet === "old");
  const currentCode = current === AUTO || current === UZ_OLD ? shown : current;
  const rootRef = useRef<HTMLDivElement>(null);
  const [narrowBox, setNarrowBox] = useState<{ top: number } | null>(null);

  const placePanel = useCallback(() => {
    const rect = rootRef.current?.getBoundingClientRect();
    let box: { top: number } | null = null;
    if (rect && rect.right < PANEL_W + PANEL_GAP) {
      box = { top: rect.bottom + 4 };
    }
    setNarrowBox((prev) => {
      if (box === null && prev === null) return prev;
      if (box && prev && prev.top === box.top) return prev;
      return box;
    });
  }, []);

  const choose = useCallback(
    (choice: string) => {
      let next = choice;
      if (!next) return;
      setOptimistic(next);

      // The alphabet changes the dictionary file itself, so the page is
      // loaded again rather than refreshed (ADR-0059).
      const wantOld = next === UZ_OLD;
      if (next === UZ_OLD || next === ALPHABET_LOCALE) {
        if (wantOld !== (alphabet === "old")) {
          document.cookie = `rw_locale=${ALPHABET_LOCALE}; path=/; max-age=31536000; samesite=lax`;
          document.cookie = alphabetCookieLine(wantOld ? OLD_ALPHABET : DEFAULT_ALPHABET);
          announcePrefs({ locale: ALPHABET_LOCALE });
          const url = new URL(window.location.href);
          url.searchParams.delete(LOCALE_PARAM);
          window.location.assign(url.toString());
          return;
        }
        next = ALPHABET_LOCALE;
      }

      if (next === AUTO) {
        document.cookie =
          "rw_locale=auto; path=/; max-age=31536000; samesite=lax";
        announcePrefs({ locale: null });
      } else {
        document.cookie = `rw_locale=${next}; path=/; max-age=31536000; samesite=lax`;
        announcePrefs({ locale: next });
      }
      const url = new URL(window.location.href);
      if (url.searchParams.has(LOCALE_PARAM)) {
        url.searchParams.delete(LOCALE_PARAM);
        const nextUrl = `${url.pathname}${url.search}${url.hash}`;
        startTransition(() => {
          router.replace(nextUrl as Route);
          router.refresh();
        });
        return;
      }
      startTransition(() => router.refresh());
    },
    [router, alphabet],
  );

  const options: DropdownOption[] = [
    {
      value: AUTO,
      label: t(locale, "locale.auto"),
      hint: nativeName(locale, alphabet === "old"),
      leading: <LocaleFlag code={locale} />,
      keywords: `auto ${locale} ${LOCALE_NAMES[locale]}`,
    },
    ...GROUPS.flatMap((group) =>
      group.locales
        .flatMap((code) => (code === ALPHABET_LOCALE ? [code, UZ_OLD] : [code]))
        .map((value) => {
          const code: Locale =
            value === UZ_OLD ? ALPHABET_LOCALE : (value as Locale);
          const old = value === UZ_OLD;
          return {
            value,
            label: nativeName(code, old),
            hint:
              code === ALPHABET_LOCALE
                ? t(locale, old ? "locale.alphabetOld" : "locale.alphabetNew")
                : LOCALE_NAMES[code] !== ENGLISH_NAMES[code]
                  ? ENGLISH_NAMES[code]
                  : undefined,
            group: t(locale, group.key),
            leading: <LocaleFlag code={code} />,
            keywords: `${ENGLISH_NAMES[code]} ${code} ${LOCALE_NAMES[code]}${old ? " old eski" : ""}`,
            trailing: !hasContentNames(code) ? (
              <span
                title={t(locale, "content.uzOnly")}
                className="shrink-0 rounded rw-chip px-1 text-theme-xs rw-dim-2"
              >
                {t(locale, "locale.contentUz")}
              </span>
            ) : undefined,
          };
        }),
    ),
  ];

  return (
    <div
      ref={rootRef}
      className="relative inline-block"
      aria-label={`${currentLabel} (${currentCode}) — ${t(locale, "locale.switchLabel")}`}
      data-tip={t(locale, "locale.switchLabel")}
      data-tip-kind="flip"
    >
      <Dropdown
        size="header"
        hideLabel
        label={`${currentLabel} (${currentCode}) — ${t(locale, "locale.switchLabel")}`}
        value={current}
        onChange={choose}
        options={options}
        disabled={pending}
        loading={pending}
        placeholder={t(locale, "locale.switchLabel")}
        onOpen={placePanel}
        optionsClassName={
          narrowBox === null
            ? "absolute top-full right-0 mt-1 w-64"
            : "fixed mt-1"
        }
        optionsStyle={
          narrowBox === null
            ? undefined
            : { top: narrowBox.top, left: PANEL_GAP, right: PANEL_GAP }
        }
      />
    </div>
  );
}

if (GROUPS.flatMap((g) => g.locales).length !== LOCALES.length) {
  throw new Error("LocaleSwitch: GROUPS every locale must appear exactly once");
}
