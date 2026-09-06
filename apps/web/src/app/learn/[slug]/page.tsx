import Link from "next/link";
import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";

type Props = { params: Promise<{ slug: string }> };

export const dynamic = "force-dynamic";

/** SSR + metadata — o'z kontent differensiatori qidiruvda topilishi shart. */
export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  try {
    const article = await api.article(slug);
    return { title: article.title, description: article.summary };
  } catch {
    return { title: "Maqola topilmadi" };
  }
}

export default async function ArticlePage({ params }: Props) {
  const { slug } = await params;
  const locale = DEFAULT_LOCALE;

  let article;
  try {
    article = await api.article(slug);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }

  return (
    <article>
      <h1 className="text-2xl font-bold">{article.title}</h1>
      <p className="mt-1 text-sm" style={{ color: "var(--muted)" }}>
        {article.reading_minutes} {t(locale, "learn.minutes")}
        {article.author && ` · ${article.author}`}
        {article.topics.length > 0 && ` · ${article.topics.join(", ")}`}
      </p>

      <div className="mt-6 whitespace-pre-wrap leading-relaxed">{article.body}</div>

      {article.problems.length > 0 && (
        <section className="mt-10">
          <h2 className="mb-3 text-lg font-medium">{t(locale, "learn.practice")}</h2>
          <div className="flex flex-wrap gap-2">
            {article.problems.map((p) => (
              <Link
                key={`${p.slug}-${p.role}`}
                href={`/problems/${p.slug}`}
                className="rounded border px-3 py-1 text-sm"
                style={{ borderColor: "var(--border)", background: "var(--surface)" }}
              >
                {p.title}
              </Link>
            ))}
          </div>
        </section>
      )}
    </article>
  );
}
