import type { Route } from "next";
import Link from "next/link";

import { numericStamp } from "@rankwant/shared/format";

import { Badge, type BadgeColor } from "@/components/ui/Badge";
import { EmptyState } from "@/components/ui/EmptyState";
import { TBody, TD, TH, THead, TR, Table } from "@/components/ui/Table";
import { fill, t, type Locale, type MessageKey } from "@/i18n/messages";

import { COURSE_DRAFT_LIMIT, courseStatus, textOf, type CourseStatus, type StudioCourse } from "../api/courses";
import { NewCourseForm } from "./NewCourseForm";

const STATUS: Record<CourseStatus, { key: MessageKey; color: BadgeColor }> = {
  draft: { key: "studio.status.draft", color: "neutral" },
  review: { key: "studio.status.review", color: "warning" },
  published: { key: "studio.status.public", color: "success" },
};

export function CourseStatusBadge({ course, locale }: { course: StudioCourse; locale: Locale }) {
  const status = STATUS[courseStatus(course)];
  return <Badge color={status.color}>{t(locale, status.key)}</Badge>;
}

export const courseTitle = (course: StudioCourse) =>
  textOf(course.texts, course.base_locale ?? "uz")?.title || course.slug;

const lessonCount = (course: StudioCourse) =>
  course.modules.reduce(
    (sum, m) => sum + m.sections.reduce((n, s) => n + s.lessons.length, 0),
    0,
  );

/** The author's courses and the form for a new one. Staff see every course
 *  here (they may edit any), authors only their own. */
export function CourseList({
  rows,
  locale,
  staff,
}: {
  rows: StudioCourse[];
  locale: Locale;
  staff: boolean;
}) {
  const drafts = rows.filter((row) => !row.is_published).length;
  const full = !staff && drafts >= COURSE_DRAFT_LIMIT;

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-title-sm font-bold rw-strong">{t(locale, "studio.nav.courses")}</h1>
        <p className="mt-1 max-w-2xl text-theme-sm rw-dim">{t(locale, "studio.courses.intro")}</p>
      </header>

      {rows.length === 0 ? (
        <EmptyState variant="card" title={t(locale, "studio.courses.empty")} hint={t(locale, "studio.courses.emptyHint")} />
      ) : (
        <Table>
          <THead>
            <TH>{t(locale, "studio.courses.col.course")}</TH>
            <TH className="hidden @lg:table-cell">{t(locale, "studio.courses.col.lessons")}</TH>
            <TH>{t(locale, "studio.col.status")}</TH>
            <TH className="hidden @2xl:table-cell">{t(locale, "studio.courses.col.published")}</TH>
          </THead>
          <TBody>
            {rows.map((row) => (
              <TR key={row.slug}>
                <TD>
                  <Link
                    href={`/studio/courses/${encodeURIComponent(row.slug)}` as Route}
                    className="font-medium rw-strong hover:underline"
                  >
                    {courseTitle(row)}
                  </Link>
                  <span className="block font-mono text-theme-xs rw-faint">{row.slug}</span>
                </TD>
                <TD className="hidden tabular-nums @lg:table-cell">{lessonCount(row)}</TD>
                <TD>
                  <CourseStatusBadge course={row} locale={locale} />
                </TD>
                <TD className="hidden whitespace-nowrap font-mono text-theme-xs rw-dim @2xl:table-cell">
                  {row.published_at ? numericStamp(row.published_at) : "—"}
                </TD>
              </TR>
            ))}
          </TBody>
        </Table>
      )}

      {!staff && (
        <p className="text-theme-xs rw-faint">
          {fill(t(locale, full ? "studio.courses.full" : "studio.courses.count"), {
            count: drafts,
            limit: COURSE_DRAFT_LIMIT,
          })}
        </p>
      )}
      {!full && <NewCourseForm />}
    </div>
  );
}
