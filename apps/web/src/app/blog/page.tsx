import Link from "next/link";
import type { Metadata } from "next";
import { api } from "@/lib/api";
import { Badge } from "@/components/ui/Badge";
import { ListCard } from "@/components/ui/ListCard";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";

export const metadata: Metadata = { title: "Yangiliklar" };
export const dynamic = "force-dynamic";

export default async function BlogPage() {
  const locale = DEFAULT_LOCALE;
  const data = await api.posts();

  return (
    <div className="space-y-6">
      <h1 className="text-title-sm font-bold text-gray-800 dark:text-white/90">
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
                  <span>{new Date(post.published_at).toLocaleDateString(locale)}</span>
                  {post.author && <Badge>{post.author}</Badge>}
                </>
              }
            />
          </li>
        ))}
      </ul>
      {data.count === 0 && <p className="text-theme-sm text-gray-400">{t(locale, "empty")}</p>}
    </div>
  );
}
