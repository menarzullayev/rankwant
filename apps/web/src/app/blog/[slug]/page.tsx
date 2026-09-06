import type { Metadata } from "next";
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
    <article>
      <h1 className="text-2xl font-bold">{post.title}</h1>
      <p className="mt-1 text-sm" style={{ color: "var(--muted)" }}>
        {new Date(post.published_at).toLocaleDateString(DEFAULT_LOCALE)}
        {post.author && ` · ${post.author}`}
      </p>
      <div className="mt-6 whitespace-pre-wrap leading-relaxed">{post.body}</div>
    </article>
  );
}
