"use client";

import type { Route } from "next";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";

/** Tablar alohida manzilda — `/users/<nom>/urinishlar`: havolani ulashish,
 *  orqaga qaytish va sahifa sarlavhasi to'g'ri ishlaydi. */
export const PROFILE_TABS = [
  { slug: "", key: "profile.tab.overview" },
  { slug: "shaxsiy", key: "profile.tab.about" },
  { slug: "faoliyat", key: "profile.tab.activity" },
  { slug: "urinishlar", key: "profile.tab.attempts" },
  { slug: "yechilganlar", key: "profile.tab.solved" },
  { slug: "musobaqalar", key: "profile.tab.contests" },
  { slug: "yutuqlar", key: "profile.tab.achievements" },
  { slug: "xaridlar", key: "profile.tab.purchases" },
] as const;

export function ProfileNav({ username }: { username: string }) {
  const locale = useLocale();
  const pathname = usePathname();
  const base = `/users/${username}`;
  const current = pathname.startsWith(base)
    ? pathname.slice(base.length).replace(/^\//, "").split("/")[0]
    : "";

  return (
    // Bitta qator va gorizontal aylanish: Robocontest'da tablar telefonda
    // ikki qatorga tushardi. Chiziq — ichki soya (`overflow` bilan border
    // vertikal aylantirish tugmasini chiqarardi, o'lchandi). `px-3` bilan
    // 1366 kenglikda sakkiz tab sig'adi (763 → 699 px, joy 719).
    <nav
      aria-label={t(locale, "profile.sections")}
      className="flex gap-1 overflow-x-auto overflow-y-hidden [scrollbar-width:thin] shadow-[inset_0_-1px_0_var(--rw-line)]"
    >
      {PROFILE_TABS.map((tab) => {
        const active = current === tab.slug;
        return (
          <Link
            key={tab.slug || "overview"}
            href={(tab.slug ? `${base}/${tab.slug}` : base) as Route}
            aria-current={active ? "page" : undefined}
            className={`shrink-0 border-b-2 px-3 py-2.5 text-theme-sm font-medium transition ${
              active ? "rw-accent-line rw-accent-ink" : "border-transparent rw-dim rw-hover-strong"
            }`}
          >
            {t(locale, tab.key)}
          </Link>
        );
      })}
    </nav>
  );
}
