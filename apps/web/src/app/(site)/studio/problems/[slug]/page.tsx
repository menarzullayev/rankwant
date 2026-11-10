import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { ProblemEditor, editorTab, type DraftTest, type MineProblem } from "@/features/studio";
import { ApiError } from "@/lib/api";
import { requireUser } from "@/lib/access.server";
import { getWithSession } from "@/lib/api.server";

type Props = {
  params: Promise<{ slug: string }>;
  searchParams: Promise<{ tab?: string }>;
};

export const dynamic = "force-dynamic";

/** Only the author's own drafts: `problems/mine/` answers 404 for anybody
 *  else's, and so does this page. */
async function load(slug: string): Promise<MineProblem> {
  try {
    return await getWithSession<MineProblem>(`/problems/mine/${encodeURIComponent(slug)}/`);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  return { title: slug, robots: { index: false } };
}

export default async function StudioProblemPage({ params, searchParams }: Props) {
  const { slug } = await params;
  const { tab } = await searchParams;
  await requireUser(`/studio/problems/${encodeURIComponent(slug)}`);
  const problem = await load(slug);
  // A published problem's tests belong to staff-ops: the endpoint answers
  // 403 to its author, and the tab shows that instead of a list.
  const tests = problem.is_public
    ? []
    : await getWithSession<DraftTest[]>(`/staff/problems/${encodeURIComponent(slug)}/tests/`);
  return <ProblemEditor initial={problem} initialTests={tests} initialTab={editorTab(tab)} />;
}
