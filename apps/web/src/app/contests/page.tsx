import Link from "next/link";
import type { Metadata } from "next";

import { Badge, type BadgeColor } from "@/components/ui/Badge";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";
import { ContestIcon } from "@/icons";
import { api } from "@/lib/api";

// Jonli ma'lumot: har so'rovda serverda render qilinadi.
// Build vaqtida prerender qilinmaydi — CI da API ishlamaydi, va reyting
// jadvali baribir keshlanmasligi kerak. SSR SEO uchun yetarli (ADR-0003);
// ISR keyinroq optimizatsiya sifatida qo'shilishi mumkin.
export const dynamic = "force-dynamic";

export const metadata: Metadata = { title: "Musobaqalar" };

function status(c: { is_running: boolean; is_finished: boolean }): {
  key: string;
  color: BadgeColor;
} {
  if (c.is_running) return { key: "contests.running", color: "success" };
  if (c.is_finished) return { key: "contests.finished", color: "neutral" };
  return { key: "contests.upcoming", color: "info" };
}

export default async function ContestsPage() {
  const locale = DEFAULT_LOCALE;
  const data = await api.contests();

  return (
    <div className="space-y-6">
      <h1 className="text-title-sm font-bold text-gray-800 dark:text-white/90">
        {t(locale, "contests.title")}
      </h1>

      {/* `<li><a>` tuzilmasi saqlanadi — E2E `li a` selektoriga tayanadi. */}
      <ul className="grid gap-4 md:grid-cols-2">
        {data.results.map((c) => {
          const s = status(c);
          return (
            <li key={c.slug}>
              <Link
                href={`/contests/${c.slug}`}
                className="flex h-full gap-4 rounded-2xl border border-gray-200 bg-white p-5
                  shadow-theme-xs transition hover:border-brand-400
                  dark:border-[#232936] dark:bg-[#141821]"
              >
                <span
                  className="flex size-11 shrink-0 items-center justify-center rounded-xl
                    bg-brand-50 text-brand-600 dark:bg-brand-500/12 dark:text-brand-400"
                >
                  <ContestIcon />
                </span>
                <span className="min-w-0">
                  <span className="block font-semibold text-gray-800 dark:text-white/90">
                    {c.title}
                  </span>
                  <span className="mt-2 flex flex-wrap items-center gap-2">
                    <Badge color={s.color}>{t(locale, s.key)}</Badge>
                    {c.is_rated && <Badge color="brand">{t(locale, "contests.rated")}</Badge>}
                  </span>
                  <span className="mt-2 block text-theme-xs text-gray-500 dark:text-gray-400">
                    {new Date(c.start_at).toLocaleString(locale)}
                  </span>
                </span>
              </Link>
            </li>
          );
        })}
      </ul>
      {data.count === 0 && (
        <p className="text-theme-sm text-gray-400">{t(locale, "empty")}</p>
      )}
    </div>
  );
}
