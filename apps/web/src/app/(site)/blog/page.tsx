import type { Metadata } from "next";
import { api } from "@/lib/api";
import { Badge } from "@/components/ui/Badge";
import { ListCard } from "@/components/ui/ListCard";
import { getLocale } from "@/i18n/server";
import { inReaderAlphabet } from "@/i18n/alphabet";
import { date, t } from "@/i18n/messages";
import { EmptyState } from "@/components/ui/EmptyState";

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "blog.title") };
}
export const dynamic = "force-dynamic";

export default async function BlogPage() {
  const locale = await getLocale();
  const data = await api.posts();

  return (
    <div className="space-y-6">
      <h1 className="text-title-sm font-bold rw-strong">
        {t(locale, "blog.title")}
      </h1>
      <ul className="grid gap-4 md:grid-cols-2">
        {data.results.map((post) => (
          <li key={post.slug}>
            <ListCard
              href={`/blog/${post.slug}`}
              title={inReaderAlphabet(post.title, post.locale)}
              summary={inReaderAlphabet(post.summary, post.locale)}
              meta={
                <>
                  <span>
                    {date(post.published_at, locale)}
                  </span>
                  {post.author && <Badge>{post.author}</Badge>}
                </>
              }
            />
          </li>
        ))}
      </ul>
      {data.count === 0 && (
        <EmptyState variant="card" title={t(locale, "common.empty")} hint={t(locale, "common.emptyHint")} />
      )}
    </div>
  );
}
