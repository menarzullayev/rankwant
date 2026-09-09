import type { Metadata } from "next";

import { Badge } from "@/components/ui/Badge";
import { ListCard } from "@/components/ui/ListCard";
import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";
import { api } from "@/lib/api";

export const dynamic = "force-dynamic";
export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "nav.roadmap") };
}

export default async function RoadmapsPage() {
  const locale = await getLocale();
  const roadmaps = await api.roadmaps();
  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-title-sm font-bold rw-strong">
          {t(locale, "nav.roadmap")}
        </h1>
        <p className="mt-2 max-w-2xl text-theme-sm rw-dim">
          Noldan cho&apos;qqigacha bosqichma-bosqich: maqola → masala → maqola.
        </p>
      </header>
      <ul className="grid gap-4 md:grid-cols-2">
        {roadmaps.map((r) => (
          <li key={r.slug}>
            <ListCard
              href="/learn"
              title={r.title}
              summary={r.description}
              meta={<Badge color="brand">{r.step_count} qadam</Badge>}
            />
          </li>
        ))}
      </ul>
      {roadmaps.length === 0 && (
        <p className="text-theme-sm rw-faint">{t(locale, "empty")}</p>
      )}
    </div>
  );
}
