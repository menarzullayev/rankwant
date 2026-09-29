"use client";

import type { Route } from "next";
import Link from "next/link";

import { useLocale } from "@/i18n/LocaleProvider";
import { t, type MessageKey } from "@/i18n/messages";
import {
  buildProblemTabHref,
  PROBLEM_TABS,
  type ProblemTab,
} from "@/lib/problem-tabs";

/** Tab → mavjud tarjima kaliti.
 *
 *  Yangi kalit qo'shilmaydi: to'rttasi allaqachon bor
 *  (`statement`/`status`/`stats`/`solvers`), tahlil yorlig'i esa
 *  `editorial.title` — 10 tilda ham tarjima qilingan. Yangi kalit
 *  10 lug'atni qo'lda sinxronlashni talab qilardi (`check_i18n.py`).
 */
const LABEL: Record<ProblemTab, MessageKey> = {
  description: "problem.tab.statement",
  attempts: "problem.tab.status",
  editorial: "editorial.title",
  statistics: "problem.tab.stats",
  solvers: "problem.tab.solvers",
};

/** Masala bo'limlari — KEP va RoboContest'dagi kabi sahifa tepasida.
 *
 *  ROL TABLIST EMAS, va bu ataylab (`AuthTabs` dagi izoh bilan bir xil
 *  sabab): panellar SERVER komponenti, ya'ni klient fokusni panelga
 *  ko'chira olmaydi — yarim bajarilgan tablist (`←`/`→`, `tabpanel`
 *  siz) ekran o'quvchini chalg'itardi.
 *
 *  O'rniga oddiy havola: har biri HAQIQIY manzil (`?tab=...`), ya'ni
 *  o'rta tugma, yangi varaq va xatcho'p ishlaydi. Fokus oddiy Tab bilan
 *  yuriladi (`rw-focus-ring`), `aria-current` esa qaysi biri tanlanganini
 *  aytadi. `scroll={false}` — tab almashganda sahifa sakramaydi.
 */
export function ProblemTabs({
  slug,
  current,
  contest,
}: {
  slug: string;
  current: ProblemTab;
  contest?: string;
}) {
  const locale = useLocale();

  return (
    <nav
      aria-label={t(locale, "problem.tabsLabel")}
      className="rw-kit-tabs flex flex-wrap items-center gap-1 border-b rw-divider"
      data-kit-tabs="underline"
    >
      {PROBLEM_TABS.map((key) => (
        <Link
          key={key}
          href={buildProblemTabHref(slug, key, { contest }) as Route}
          scroll={false}
          aria-current={key === current ? "page" : undefined}
          className={`-mb-px border-b-2 px-3 py-2 text-theme-sm font-medium transition rw-focus-ring ${
            key === current
              ? "rw-accent-line rw-accent-ink"
              : "border-transparent rw-dim rw-hover-strong"
          }`}
        >
          {t(locale, LABEL[key])}
        </Link>
      ))}
    </nav>
  );
}
