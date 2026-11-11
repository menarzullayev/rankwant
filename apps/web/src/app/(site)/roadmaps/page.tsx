import { inReaderAlphabet } from "@/i18n/alphabet";
import type { Metadata, Route } from "next";

import { Badge } from "@/components/ui/Badge";
import { ListCard } from "@/components/ui/ListCard";
import { getLocale } from "@/i18n/server";
import { fill, t } from "@/i18n/messages";
import { api } from "@/lib/api";

export const dynamic = "force-dynamic";
export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "nav.roadmap") };
}

export default async function RoadmapsPage() {
  const locale = await getLocale();
  const roadmaps = await api.roadmaps(locale);
  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-title-sm font-bold rw-strong">
          {t(locale, "nav.roadmap")}
        </h1>
        <p className="mt-2 max-w-2xl text-theme-sm rw-dim">{t(locale, "roadmaps.intro")}
        </p>
      </header>
      <ul className="grid gap-4 md:grid-cols-2">
        {roadmaps.map((r) => (
          <li key={r.slug} id={r.slug} className="scroll-mt-24">
            <ListCard
              href={`/roadmaps/${r.slug}` as Route}
              title={inReaderAlphabet(r.title, r.locale)}
              summary={inReaderAlphabet(r.description, r.locale)}
              meta={
                <>
                  <Badge color="brand">
                    {fill(t(locale, "learn.stepCount"), { count: r.step_count })}
                  </Badge>
                  {r.section_count > 0 && (
                    <Badge color="neutral">
                      {fill(t(locale, "roadmaps.sections"), { count: r.section_count })}
                    </Badge>
                  )}
                </>
              }
            />
          </li>
        ))}
      </ul>
      {roadmaps.length === 0 && (
        <p className="text-theme-sm rw-faint">{t(locale, "common.empty")}</p>
      )}
    </div>
  );
}
