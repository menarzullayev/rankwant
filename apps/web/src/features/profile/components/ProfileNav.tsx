"use client";

import type { Route } from "next";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";

/** Tablar alohida manzilda — `/users/<nom>/attempts`: havolani ulashish,
 *  orqaga qaytish va sahifa sarlavhasi to'g'ri ishlaydi. */
export const PROFILE_TABS = [
  { slug: "", key: "profile.tab.overview" },
  { slug: "profile", key: "profile.tab.about" },
  { slug: "activity", key: "profile.tab.activity" },
  { slug: "attempts", key: "profile.tab.attempts" },
  { slug: "solved", key: "profile.tab.solved" },
  { slug: "contests", key: "profile.tab.contests" },
  { slug: "certificates", key: "profile.tab.certificates" },
  { slug: "achievements", key: "profile.tab.achievements" },
  { slug: "purchases", key: "profile.tab.purchases" },
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
    // vertikal aylantirish tugmasini chiqarardi, o'lchandi). Overlay
    // scroller joy yemaydi, shuning uchun nativ `thin` yo'l yo'q.
    <nav
      aria-label={t(locale, "profile.sections")}
      className="rw-kit-tabs shadow-[inset_0_-1px_0_var(--rw-divider)]"
      data-kit-tabs="scroll"
    >
      {PROFILE_TABS.map((tab) => {
        const active = current === tab.slug;
        return (
          <Link
            key={tab.slug || "overview"}
            href={(tab.slug ? `${base}/${tab.slug}` : base) as Route}
            aria-current={active ? "page" : undefined}
            className={`rw-kit-tab ${
              active ? "rw-accent-ink" : "rw-dim rw-hover-strong"
            }`}
          >
            {t(locale, tab.key)}
          </Link>
        );
      })}
    </nav>
  );
}
