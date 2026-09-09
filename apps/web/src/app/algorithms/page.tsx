import type { Metadata } from "next";

import { Badge, DifficultyBadge } from "@/components/ui/Badge";
import { ListCard } from "@/components/ui/ListCard";
import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";
import { api } from "@/lib/api";

export const dynamic = "force-dynamic";
export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "nav.algorithms") };
}

export default async function AlgorithmsPage() {
  const locale = await getLocale();
  const data = await api.algorithms();
  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-title-sm font-bold rw-strong">
          {t(locale, "nav.algorithms")}
        </h1>
        <p className="mt-2 max-w-2xl text-theme-sm rw-dim">
          Qisqa ma&apos;lumotnoma: g&apos;oya, murakkablik, kod, mashq
          masalalari.
        </p>
      </header>
      <ul className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {data.results.map((a) => (
          <li key={a.slug}>
            <ListCard
              href={`/learn/${a.slug}`}
              title={a.title}
              summary={a.summary}
              meta={
                <>
                  <DifficultyBadge value={a.difficulty} />
                  {a.topics.map((tp) => (
                    <Badge key={tp} color="info">
                      {tp}
                    </Badge>
                  ))}
                </>
              }
            />
          </li>
        ))}
      </ul>
      {data.count === 0 && (
        <p className="text-theme-sm rw-faint">{t(locale, "empty")}</p>
      )}
    </div>
  );
}
