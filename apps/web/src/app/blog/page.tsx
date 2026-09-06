import Link from "next/link";
import type { Metadata } from "next";
import { api } from "@/lib/api";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";

export const metadata: Metadata = { title: "Yangiliklar" };
export const dynamic = "force-dynamic";

export default async function BlogPage() {
  const locale = DEFAULT_LOCALE;
  const data = await api.posts();

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold">{t(locale, "blog.title")}</h1>
      <ul className="space-y-3">
        {data.results.map((post) => (
          <li
            key={post.slug}
            className="rounded-lg border p-4"
            style={{ borderColor: "var(--border)", background: "var(--surface)" }}
          >
            <Link href={`/blog/${post.slug}`} className="font-medium hover:underline">
              {post.title}
            </Link>
            {post.summary && (
              <p className="mt-1 text-sm" style={{ color: "var(--muted)" }}>
                {post.summary}
              </p>
            )}
            <p className="mt-2 text-xs" style={{ color: "var(--muted)" }}>
              {new Date(post.published_at).toLocaleDateString(locale)}
              {post.author && ` · ${post.author}`}
            </p>
          </li>
        ))}
      </ul>
      {data.count === 0 && <p style={{ color: "var(--muted)" }}>{t(locale, "empty")}</p>}
    </div>
  );
}
