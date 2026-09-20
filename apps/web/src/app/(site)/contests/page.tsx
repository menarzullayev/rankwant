import Link from "next/link";
import type { Metadata } from "next";

import { Badge, type BadgeColor } from "@/components/ui/Badge";
import { getLocale } from "@/i18n/server";
import { dateTime, t } from "@/i18n/messages";
import { Icon } from "@/components/ui/Icon";
import { api } from "@/lib/api";
import { EmptyState } from "@/components/ui/EmptyState";

// Jonli ma'lumot: har so'rovda serverda render qilinadi.
// Build vaqtida prerender qilinmaydi — CI da API ishlamaydi, va reyting
// jadvali baribir keshlanmasligi kerak. SSR SEO uchun yetarli (ADR-0003);
// ISR keyinroq optimizatsiya sifatida qo'shilishi mumkin.
export const dynamic = "force-dynamic";

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "contests.title") };
}

function status(c: { is_running: boolean; is_finished: boolean }): {
  key: string;
  color: BadgeColor;
} {
  if (c.is_running) return { key: "contests.running", color: "success" };
  if (c.is_finished) return { key: "contests.finished", color: "neutral" };
  return { key: "contests.upcoming", color: "info" };
}

export default async function ContestsPage() {
  const locale = await getLocale();
  const data = await api.contests();

  return (
    <div className="space-y-6">
      <h1 className="text-title-sm font-bold rw-strong">
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
                className="flex h-full gap-4 rw-radius border rw-line rw-surface p-5 rw-shadow transition rw-hover-line"
              >
                <span className="flex size-11 shrink-0 items-center justify-center rw-radius rw-accent-soft rw-accent-ink">
                  <Icon name="ranking.trophy" />
                </span>
                <span className="min-w-0">
                  <span className="block font-semibold rw-strong">
                    {c.title}
                  </span>
                  <span className="mt-2 flex flex-wrap items-center gap-2">
                    <Badge color={s.color}>{t(locale, s.key)}</Badge>
                    {c.is_rated && (
                      <Badge color="brand">{t(locale, "contests.rated")}</Badge>
                    )}
                  </span>
                  <span className="mt-2 block text-theme-xs rw-dim">
                    {dateTime(c.start_at, locale)}
                  </span>
                </span>
              </Link>
            </li>
          );
        })}
      </ul>
      {data.count === 0 && (
        <EmptyState variant="card" title={t(locale, "common.empty")} hint={t(locale, "common.emptyHint")} />
      )}
    </div>
  );
}
