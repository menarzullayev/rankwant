import { inReaderAlphabet } from "@/i18n/alphabet";
import type { Metadata } from "next";
import { api } from "@/lib/api";
import { Badge } from "@/components/ui/Badge";
import { ListCard } from "@/components/ui/ListCard";
import { getLocale } from "@/i18n/server";
import { fill, t } from "@/i18n/messages";
import { EmptyState } from "@/components/ui/EmptyState";

export async function generateMetadata(): Promise<Metadata> {
  const locale = await getLocale();
  return {
    title: t(locale, "learn.title"),
    description: t(locale, "learn.description"),
  };
}

export const dynamic = "force-dynamic";

export default async function LearnPage() {
  const locale = await getLocale();
  const [articles, roadmaps] = await Promise.all([
    api.articles(),
    api.roadmaps(locale),
  ]);

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-title-sm font-bold rw-strong">
          {t(locale, "learn.title")}
        </h1>
        <p className="mt-2 max-w-2xl text-theme-sm rw-dim">{t(locale, "learn.intro")}
        </p>
      </header>

      {roadmaps.length > 0 && (
        <section>
          <h2 className="mb-3 text-theme-xl font-semibold rw-strong">
            {t(locale, "learn.roadmaps")}
          </h2>
          <ul className="grid gap-4 md:grid-cols-2">
            {roadmaps.map((r) => (
              <li key={r.slug}>
                <ListCard
                  title={inReaderAlphabet(r.title, r.locale)}
                  summary={inReaderAlphabet(r.description, r.locale)}
                  meta={
                    <Badge color="brand">
                      {fill(t(locale, "learn.stepCount"), { count: r.step_count })}
                    </Badge>
                  }
                />
              </li>
            ))}
          </ul>
        </section>
      )}

      <section>
        <h2 className="mb-3 text-theme-xl font-semibold rw-strong">
          {t(locale, "learn.articles")}
        </h2>
        <ul className="grid gap-4 md:grid-cols-2">
          {articles.results.map((a) => (
            <li key={a.slug}>
              <ListCard
                href={`/learn/${a.slug}`}
                title={inReaderAlphabet(a.title, a.locale)}
                summary={inReaderAlphabet(a.summary, a.locale)}
                meta={
                  <>
                    <Badge>
                      {a.reading_minutes} {t(locale, "learn.minutes")}
                    </Badge>
                    {a.problem_count > 0 && (
                      <Badge color="success">{a.problem_count} masala</Badge>
                    )}
                    {a.topics.map((topic) => (
                      <Badge key={topic} color="info">
                        {topic}
                      </Badge>
                    ))}
                  </>
                }
              />
            </li>
          ))}
        </ul>
        {articles.count === 0 && (
          <EmptyState variant="card" title={t(locale, "common.empty")} hint={t(locale, "common.emptyHint")} />
        )}
      </section>
    </div>
  );
}
