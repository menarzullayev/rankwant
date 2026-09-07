import Link from "next/link";
import { Markdown } from "@/components/Markdown";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
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
    <article className="mx-auto max-w-4xl space-y-6">
      <header>
        <h1 className="text-title-sm font-bold rw-strong">{article.title}</h1>
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <Badge>
            {article.reading_minutes} {t(locale, "learn.minutes")}
          </Badge>
          {article.author && <Badge color="brand">{article.author}</Badge>}
          {article.topics.map((topic) => (
            <Badge key={topic} color="info">
              {topic}
            </Badge>
          ))}
        </div>
      </header>

      <Card>
        <Markdown>{article.body}</Markdown>
      </Card>

      {article.problems.length > 0 && (
        <Card title={t(locale, "learn.practice")}>
          <div className="flex flex-wrap gap-2">
            {article.problems.map((p) => (
              <Link
                key={`${p.slug}-${p.role}`}
                href={`/problems/${p.slug}`}
                className="rw-radius-sm border rw-line px-3 py-1.5 text-theme-sm rw-strong transition rw-hover-line"
              >
                {p.title}
              </Link>
            ))}
          </div>
        </Card>
      )}
    </article>
  );
}
