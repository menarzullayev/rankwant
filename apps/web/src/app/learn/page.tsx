import Link from "next/link";
import type { Metadata } from "next";
import { api } from "@/lib/api";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";

export const metadata: Metadata = {
  title: "O'quv materiallari",
  description:
    "O'zbek tilida sport dasturlash bo'yicha maqolalar va yo'l xaritalari — " +
    "har bir mavzu mashq masalalari bilan.",
};

export const dynamic = "force-dynamic";

export default async function LearnPage() {
  const locale = DEFAULT_LOCALE;
  const [articles, roadmaps] = await Promise.all([api.articles(), api.roadmaps()]);

  return (
    <div className="space-y-10">
      <header>
        <h1 className="text-2xl font-bold">{t(locale, "learn.title")}</h1>
        <p className="mt-1 text-sm" style={{ color: "var(--muted)" }}>
          Har bir maqola mashq masalalari bilan bog&apos;langan — o&apos;qish va
          yechish bir joyda.
        </p>
      </header>

      {roadmaps.length > 0 && (
        <section>
          <h2 className="mb-3 text-lg font-medium">{t(locale, "learn.roadmaps")}</h2>
          <div className="grid gap-3 sm:grid-cols-2">
            {roadmaps.map((r) => (
              <div
                key={r.slug}
                className="rounded-lg border p-4"
                style={{ borderColor: "var(--border)", background: "var(--surface)" }}
              >
                <p className="font-medium">{r.title}</p>
                <p className="mt-1 text-sm" style={{ color: "var(--muted)" }}>
                  {r.description}
                </p>
                <p className="mt-2 text-xs" style={{ color: "var(--muted)" }}>
                  {r.step_count} qadam
                </p>
              </div>
            ))}
          </div>
        </section>
      )}

      <section>
        <h2 className="mb-3 text-lg font-medium">{t(locale, "learn.articles")}</h2>
        <ul className="space-y-3">
          {articles.results.map((a) => (
            <li
              key={a.slug}
              className="rounded-lg border p-4"
              style={{ borderColor: "var(--border)", background: "var(--surface)" }}
            >
              <Link href={`/learn/${a.slug}`} className="font-medium hover:underline">
                {a.title}
              </Link>
              {a.summary && (
                <p className="mt-1 text-sm" style={{ color: "var(--muted)" }}>
                  {a.summary}
                </p>
              )}
              <p className="mt-2 text-xs" style={{ color: "var(--muted)" }}>
                {a.reading_minutes} {t(locale, "learn.minutes")}
                {a.problem_count > 0 && ` · ${a.problem_count} masala`}
                {a.topics.length > 0 && ` · ${a.topics.join(", ")}`}
              </p>
            </li>
          ))}
        </ul>
        {articles.count === 0 && (
          <p style={{ color: "var(--muted)" }}>{t(locale, "empty")}</p>
        )}
      </section>
    </div>
  );
}
