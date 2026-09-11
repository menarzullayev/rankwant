import type { Route } from "next";
import Link from "next/link";

import { t, type Locale } from "@/i18n/messages";

export const TABS = [
  "about",
  "rating",
  "activity",
  "achievements",
  "purchases",
] as const;

export type Tab = (typeof TABS)[number] | "followers" | "following";

export const isTab = (value: string | undefined): value is Tab =>
  !!value &&
  ([...TABS, "followers", "following"] as readonly string[]).includes(value);

/** Bo'limlar `?tab=` bilan — har biri server'da chiziladi va havolasi
 *  ulashiladi; JavaScript'siz ham ishlaydi. */
export function ProfileTabs({
  username,
  active,
  locale,
}: {
  username: string;
  active: Tab;
  locale: Locale;
}) {
  return (
    <nav
      aria-label={t(locale, "profile.sections")}
      className="flex gap-1 overflow-x-auto border-b rw-line"
    >
      {TABS.map((tab) => (
        <Link
          key={tab}
          href={`/users/${username}?tab=${tab}` as Route}
          aria-current={active === tab ? "page" : undefined}
          className={`-mb-px shrink-0 border-b-2 px-4 py-2.5 text-theme-sm font-medium transition ${
            active === tab
              ? "rw-accent-line rw-accent-ink"
              : "border-transparent rw-dim rw-hover-strong"
          }`}
        >
          {t(locale, `profile.tab.${tab}`)}
        </Link>
      ))}
    </nav>
  );
}
