import type { Metadata } from "next";
import { Markdown } from "@/components/Markdown";
import { Card } from "@/components/ui/Card";
import { notFound } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { DEFAULT_LOCALE } from "@/i18n/messages";

type Props = { params: Promise<{ slug: string }> };

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  try {
    const post = await api.post(slug);
    return { title: post.title, description: post.summary };
  } catch {
    return { title: "Topilmadi" };
  }
}

export default async function PostPage({ params }: Props) {
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
          {new Date(post.published_at).toLocaleDateString(DEFAULT_LOCALE)}
          {post.author && ` · ${post.author}`}
        </p>
      </header>
      <Card>
        <Markdown>{post.body}</Markdown>
      </Card>
    </article>
  );
}
