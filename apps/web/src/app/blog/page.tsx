import Link from "next/link";
import type { Metadata } from "next";
import { api } from "@/lib/api";
import { Badge } from "@/components/ui/Badge";
import { ListCard } from "@/components/ui/ListCard";
import { getLocale } from "@/i18n/server";
import { date, t } from "@/i18n/messages";

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
              title={post.title}
              summary={post.summary}
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
        <p className="text-theme-sm rw-faint">{t(locale, "empty")}</p>
      )}
    </div>
  );
}
