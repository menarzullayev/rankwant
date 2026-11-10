import type { Metadata } from "next";
import { notFound } from "next/navigation";

import {
  ContestEditor,
  contestTab,
  type ContestParticipant,
  type MineContest,
  type MineProblem,
} from "@/features/studio";
import { ApiError, type Paginated } from "@/lib/api";
import { requireUser } from "@/lib/access.server";
import { getWithSession } from "@/lib/api.server";

type Props = {
  params: Promise<{ slug: string }>;
  searchParams: Promise<{ tab?: string }>;
};

export const dynamic = "force-dynamic";

/** Only the organizer's own contests: `contests/mine/` answers 404 for
 *  anybody else's, and so does this page. */
async function load(slug: string): Promise<MineContest> {
  try {
    return await getWithSession<MineContest>(`/contests/mine/${encodeURIComponent(slug)}/`);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  return { title: slug, robots: { index: false } };
}

export default async function StudioContestPage({ params, searchParams }: Props) {
  const { slug } = await params;
  const { tab } = await searchParams;
  await requireUser(`/studio/contests/${encodeURIComponent(slug)}`);
  const contest = await load(slug);
  const [mine, participants] = await Promise.all([
    getWithSession<Paginated<MineProblem>>("/problems/mine/?page_size=100"),
    getWithSession<ContestParticipant[]>(
      `/contests/mine/${encodeURIComponent(slug)}/participants/`,
    ),
  ]);
  // Only unpublished problems can join a contest (the API refuses the rest).
  const drafts = mine.results.filter((problem) => !problem.is_public);
  return (
    <ContestEditor
      initial={contest}
      drafts={drafts}
      participants={participants}
      initialTab={contestTab(tab)}
    />
  );
}
