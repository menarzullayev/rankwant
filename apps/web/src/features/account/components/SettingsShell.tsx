"use client";

import type { Route } from "next";
import Link from "next/link";

import { AccountSettings } from "@/features/account";
import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t, type MessageKey } from "@/i18n/messages";
import { AppearanceSection } from "./AppearanceSection";
import { CareerSection } from "./CareerSection";
import { DeliveryCard, DetailsCard, PrivacyCard } from "./InfoSection";
import { NotificationsSection } from "./NotificationsSection";
import { CosmeticsCard, ProfileSection } from "./ProfileSection";
import { SaveBar, SaveBarProvider } from "./SaveBar";
import { Loading } from "./section-kit";
import { SECTIONS, type SectionId } from "./sections";
import { SecuritySection } from "./SecuritySection";
import { SkillsSection } from "./SkillsSection";
import { SocialSection } from "./SocialSection";
import { TeamsSection } from "./TeamsSection";

/** What each section, or each of its tabs, renders. */
const VIEWS: Record<SectionId, Record<string, () => React.ReactNode>> = {
  profil: { "": ProfileSection },
  ommaviy: {
    tashqi: SocialSection,
    konikmalar: SkillsSection,
    karyera: CareerSection,
    jamoalar: TeamsSection,
    bezaklar: CosmeticsCard,
  },
  malumotlar: { malumot: DetailsCard, maxfiylik: PrivacyCard, manzil: DeliveryCard },
  xavfsizlik: { "": SecuritySection },
  bildirishnomalar: { xabarlar: NotificationsSection, korinish: AppearanceSection },
  hisob: { "": AccountSettings },
};

const hrefOf = (section: SectionId, tab = "") =>
  (tab ? `/settings/${section}?tab=${tab}` : `/settings/${section}`) as Route;

/** Settings: sections on the left, the chosen one on the right.
 *
 *  On a phone the two are separate screens (decision of 2026-10-05):
 *  `/settings` is the list, a section is its own page with a way back. The
 *  earlier layout drew a select AND the full list above every section —
 *  about 400 px before any setting (measured on the live site).
 *
 *  `section` is `null` on `/settings` itself: the list on a phone, and on a
 *  wide screen the list beside the first section, as if it had been opened. */
export function SettingsShell({ section, tab }: { section: SectionId | null; tab: string }) {
  const locale = useLocale();
  const { user } = useSession();
  const shown = section ?? SECTIONS[0].id;
  const current = SECTIONS.find((s) => s.id === shown) ?? SECTIONS[0];
  const View = VIEWS[shown][tab] ?? Object.values(VIEWS[shown])[0];
  const index = section === null;

  /** A state worth seeing before the section is opened replaces its hint. */
  function hint(id: SectionId, fallback: MessageKey): { text: string; warn: boolean } {
    if (id === "xavfsizlik" && user?.email && !user.email_verified)
      return { text: t(locale, "settings.navHint.unverified"), warn: true };
    if (id === "hisob" && user?.deletion_scheduled_for)
      return { text: t(locale, "settings.navHint.deleting"), warn: true };
    return { text: t(locale, fallback), warn: false };
  }

  return (
    <SaveBarProvider>
      <div className="mx-auto max-w-5xl">
        {/* On a phone a section page is titled by the section, below. */}
        <h1 className={`text-title-sm font-bold rw-strong ${index ? "" : "hidden lg:block"}`}>
          {t(locale, "settings.title")}
        </h1>
        <div className="mt-6 grid gap-6 lg:grid-cols-[260px_minmax(0,1fr)]">
          <nav
            aria-label={t(locale, "settings.title")}
            className={index ? "" : "hidden lg:block"}
          >
            {/* The kit's vertical tabs. Hidden or shown by the `<nav>` around it,
                never by a class on the list itself: `.rw-kit-tabs` sets its own
                `display`, which is how the list once stayed visible on a phone
                under a `hidden` class. */}
            <ul
              className="rw-kit-tabs flex-col gap-2 lg:sticky lg:top-20 lg:gap-1"
              data-kit-tabs="vertical"
            >
              {SECTIONS.map((s) => {
                const state = hint(s.id, s.hint);
                const active = !index && s.id === shown;
                // On `/settings` a wide screen shows the first section beside
                // the list, so it is marked there; a phone shows the list alone.
                const first = index && s.id === shown;
                return (
                  <li key={s.id}>
                    <Link
                      href={hrefOf(s.id)}
                      aria-current={active ? "page" : undefined}
                      className={`flex min-h-14 items-center justify-between gap-3 rw-radius-sm border px-4 py-2 rw-focus-ring lg:border-transparent ${
                        active ? "rw-accent-soft" : "rw-line rw-surface rw-hover-bg"
                      } ${first ? "lg:[background:var(--rw-accent-soft)]" : ""}`}
                    >
                      <span className="min-w-0">
                        <span className="block text-theme-sm font-semibold rw-strong">
                          {t(locale, s.key)}
                        </span>
                        <span
                          className={`block truncate text-theme-xs ${state.warn ? "rw-warn-ink font-medium" : "rw-dim"}`}
                        >
                          {state.text}
                        </span>
                      </span>
                      <span aria-hidden="true" className="rw-dim lg:hidden">
                        ›
                      </span>
                    </Link>
                  </li>
                );
              })}
            </ul>
          </nav>

          <div className={`min-w-0 space-y-6 ${index ? "hidden lg:block" : ""}`}>
            <div>
              <Link
                href={"/settings" as Route}
                className="inline-flex min-h-11 items-center text-theme-sm rw-accent-ink hover:underline lg:hidden"
              >
                <span aria-hidden="true">‹ </span>
                {t(locale, "settings.title")}
              </Link>
              <div className="mb-2 hidden lg:block">
                <div className="rw-kit-tabs" data-kit-tabs="crumb">
                  <span className="rw-kit-tab">{t(locale, "settings.title")}</span>
                  <span className="rw-kit-tab" aria-current="page">
                    {t(locale, current.key)}
                  </span>
                </div>
              </div>
              <h2 className="text-theme-xl font-bold rw-strong">{t(locale, current.key)}</h2>
            </div>
            {current.tabs.length > 0 && (
              <nav
                aria-label={t(locale, current.key)}
                className="flex flex-wrap gap-1 border-b rw-divider"
              >
                {current.tabs.map((item) => (
                  <Link
                    key={item.id}
                    href={hrefOf(shown, item.id)}
                    aria-current={item.id === tab ? "page" : undefined}
                    className={`-mb-px inline-flex min-h-11 items-center border-b-2 px-3 text-theme-sm font-semibold rw-focus-ring ${
                      item.id === tab
                        ? "rw-accent-line rw-accent-ink"
                        : "border-transparent rw-dim rw-hover-strong"
                    }`}
                  >
                    {t(locale, item.key)}
                  </Link>
                ))}
              </nav>
            )}
            {user ? <View /> : <Loading />}
            <SaveBar />
          </div>
        </div>
      </div>
    </SaveBarProvider>
  );
}
