import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { CourseList, type StudioCourse } from "@/features/studio";
import { t } from "@/i18n/messages";
import { getLocale } from "@/i18n/server";
import type { Paginated } from "@/lib/api";
import { requireUser } from "@/lib/access.server";
import { getWithSession } from "@/lib/api.server";
import { isOnServer } from "@/lib/flags";

export const dynamic = "force-dynamic";

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "studio.nav.courses"), robots: { index: false } };
}

/** Before the section opens (`courses` flag), only staff author courses:
 *  the team prepares the catalogue, nobody else sees the studio tab. */
async function guard(next: string) {
  const me = await requireUser(next);
  if (!isOnServer("courses", undefined) && !me.is_staff) notFound();
  return me;
}

export default async function StudioCoursesPage() {
  const me = await guard("/studio/courses");
  const locale = await getLocale();
  // An author holds at most three unpublished courses; staff see every
  // course here, well inside one page of 100.
  const page = await getWithSession<Paginated<StudioCourse>>("/studio/courses/?page_size=100");
  return <CourseList rows={page.results} locale={locale} staff={Boolean(me.is_staff)} />;
}
