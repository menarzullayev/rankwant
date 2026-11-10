import type { Metadata } from "next";

import { CourseReview, type StaffCourse } from "@/features/studio";
import { t } from "@/i18n/messages";
import { getLocale } from "@/i18n/server";
import type { Paginated } from "@/lib/api";
import { getWithSession } from "@/lib/api.server";

export const dynamic = "force-dynamic";

type Props = { searchParams: Promise<{ review?: string }> };

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "admin.section.courses"), robots: { index: false } };
}

/** Staff-content review of courses (ADR-0056, part 4). Not behind the
 *  `courses` flag: the team prices and publishes before the section opens.
 *  The admin layout already turns away anyone who is not staff. */
export default async function AdminCoursesPage({ searchParams }: Props) {
  const queue = (await searchParams).review === "1";
  const page = await getWithSession<Paginated<StaffCourse>>(
    `/staff/courses/?page_size=100${queue ? "&review=1" : ""}`,
  );
  return <CourseReview key={String(queue)} rows={page.results} queue={queue} />;
}
