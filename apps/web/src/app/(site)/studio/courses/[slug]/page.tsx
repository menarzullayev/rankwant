import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { CourseEditor, type StudioCourse } from "@/features/studio";
import { ApiError } from "@/lib/api";
import { requireUser } from "@/lib/access.server";
import { getWithSession } from "@/lib/api.server";
import { isOnServer } from "@/lib/flags";

type Props = { params: Promise<{ slug: string }> };

export const dynamic = "force-dynamic";

/** Before the section opens (`courses` flag), only staff author courses:
 *  the team prepares the catalogue, nobody else sees the studio tab. */
async function guard(next: string) {
  const me = await requireUser(next);
  if (!isOnServer("courses", undefined) && !me.is_staff) notFound();
  return me;
}

/** Only courses the reader may edit: the API answers 404 for the rest. */
async function load(slug: string): Promise<StudioCourse> {
  try {
    return await getWithSession<StudioCourse>(`/studio/courses/${encodeURIComponent(slug)}/`);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  return { title: slug, robots: { index: false } };
}

export default async function StudioCoursePage({ params }: Props) {
  const { slug } = await params;
  await guard(`/studio/courses/${encodeURIComponent(slug)}`);
  return <CourseEditor initial={await load(slug)} />;
}
