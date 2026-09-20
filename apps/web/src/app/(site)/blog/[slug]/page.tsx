import type { Metadata } from "next";
import { Markdown } from "@/components/Markdown";
import { Card } from "@/components/ui/Card";
import { notFound } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { date, t } from "@/i18n/messages";
import { getLocale } from "@/i18n/server";

type Props = { params: Promise<{ slug: string }> };

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const locale = await getLocale();
  const { slug } = await params;
  try {
    const post = await api.post(slug);
    return { title: post.title, description: post.summary };
  } catch {
    return { title: t(locale, "error.not_found") };
  }
}

export default async function PostPage({ params }: Props) {
  const locale = await getLocale();
  const { slug } = await params;
  let post;
  try {
    post = await api.post(slug);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }

  return (
    <article className="mx-auto max-w-4xl space-y-6">
      <header>
        <h1 className="text-title-sm font-bold rw-strong">{post.title}</h1>
        <p className="mt-2 text-theme-sm rw-dim">
          {date(post.published_at, locale)}
          {post.author && ` · ${post.author}`}
        </p>
      </header>
      <Card>
        <Markdown>{post.body}</Markdown>
      </Card>
    </article>
  );
}
