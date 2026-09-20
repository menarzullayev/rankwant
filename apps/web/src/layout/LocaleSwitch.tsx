"use client";

import type { Route } from "next";
import { useRouter } from "next/navigation";
import { useCallback, useRef, useState, useTransition } from "react";

import { Dropdown, type DropdownOption } from "@/components/ui/Dropdown";
import { useLocale, useLocaleAuto } from "@/i18n/LocaleProvider";
import { LOCALE_PARAM } from "@/i18n/locale-params";
import { LOCALES, LOCALE_NAMES, hasContentNames, t, type Locale } from "@/i18n/messages";
import { announcePrefs } from "@/lib/prefs";

import { LocaleFlag } from "./LocaleFlag";

/** «Avtomatik» — cookie o'chiriladi va til yana sarlavhadan aniqlanadi. */
const AUTO = "__auto__";

/** Ro'yxat guruhlari va guruh ichidagi tartib. */
const GROUPS: { key: "locale.group.core" | "locale.group.region" | "locale.group.broad"; locales: Locale[] }[] = [
  { key: "locale.group.core", locales: ["uz", "ru", "en", "kaa"] },
  { key: "locale.group.region", locales: ["kk", "ky", "tg", "tr"] },
  { key: "locale.group.broad", locales: ["zh", "es"] },
];

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
 *  Triggerdagi endonim tor ekranda `max-w-[3rem]` bilan qirqiladi —
 *  320 px da header toshmasin.
 */
export function LocaleSwitch() {
  const locale = useLocale();
  const auto = useLocaleAuto();
  const router = useRouter();
  const [pending, startTransition] = useTransition();
  const [optimistic, setOptimistic] = useState<string | null>(null);
  if (optimistic !== null && optimistic === (auto ? AUTO : locale)) {
    setOptimistic(null);
  }
  const current: string = optimistic ?? (auto ? AUTO : locale);
  const shown: Locale = current === AUTO ? locale : (current as Locale);
  const currentLabel = LOCALE_NAMES[shown];
  const currentCode = current === AUTO ? locale : current;
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
    (next: string) => {
      if (!next) return;
      setOptimistic(next);

      if (next === AUTO) {
        document.cookie = "rw_locale=auto; path=/; max-age=31536000; samesite=lax";
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
    [router],
  );

  const options: DropdownOption[] = [
    {
      value: AUTO,
      label: t(locale, "locale.auto"),
      hint: LOCALE_NAMES[locale],
      leading: <LocaleFlag code={locale} />,
      keywords: `auto ${locale} ${LOCALE_NAMES[locale]}`,
    },
    ...GROUPS.flatMap((group) =>
      group.locales.map((code) => ({
        value: code,
        label: LOCALE_NAMES[code],
        hint: LOCALE_NAMES[code] !== ENGLISH_NAMES[code] ? ENGLISH_NAMES[code] : undefined,
        group: t(locale, group.key),
        leading: <LocaleFlag code={code} />,
        keywords: `${ENGLISH_NAMES[code]} ${code}`,
        trailing: !hasContentNames(code) ? (
          <span
            title={t(locale, "content.uzOnly")}
            className="shrink-0 rounded rw-chip px-1 text-theme-xs rw-dim-2"
          >
            {t(locale, "locale.contentUz")}
          </span>
        ) : undefined,
      })),
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
          narrowBox === null ? "absolute top-full right-0 mt-1 w-64" : "fixed mt-1"
        }
        optionsStyle={
          narrowBox === null
            ? undefined
            : { top: narrowBox.top, left: PANEL_GAP, right: PANEL_GAP }
        }
      />
      <span hidden className="min-w-0 max-w-[3rem] truncate text-theme-xs sm:max-w-[7.5rem]">
        {currentLabel}
        </span>
    </div>
  );
}

if (GROUPS.flatMap((g) => g.locales).length !== LOCALES.length) {
  throw new Error("LocaleSwitch: GROUPS every locale must appear exactly once");
}
