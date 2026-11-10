"use client";

import { numericDate } from "@rankwant/shared/format";
import type { Route } from "next";
import Link from "next/link";
import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/Badge";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";
import { getJson } from "@/lib/api";
import type { components } from "@/lib/api/generated/schema";

type Report = components["schemas"]["ClassCourseReport"];
type Student = components["schemas"]["ClassCourseStudent"];

/** The teacher's view of a course given to the class: one row per student
 *  (lessons, percent, final quiz, certificate, last activity); a row opens
 *  to show every lesson by module. A list of rows rather than a lesson grid,
 *  so a long course does not need a sideways scroll on a phone. */
export function ClassCourseReport({ slug, assignmentId }: { slug: string; assignmentId: number }) {
  const locale = useLocale();
  const [report, setReport] = useState<Report | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    getJson<Report>(`/classrooms/${encodeURIComponent(slug)}/assignments/${assignmentId}/course/`)
      .then(setReport)
      .catch(() => setFailed(true));
  }, [slug, assignmentId]);

  if (failed) {
    return (
      <p role="alert" className="text-theme-sm rw-bad-ink">
        {t(locale, "error.error")}
      </p>
    );
  }
  if (!report) return null;
  if (report.students.length === 0) {
    return <p className="text-theme-sm rw-faint">{t(locale, "classroom.course.noStudents")}</p>;
  }

  const enrolled = report.students.filter((s) => s.enrolled).length;
  const completed = report.students.filter((s) => s.completed_at).length;
  const certificates = report.students.filter((s) => s.certificate).length;

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-2">
        <Badge>{fill(t(locale, "classroom.course.enrolled"), { count: enrolled, total: report.students.length })}</Badge>
        <Badge>{fill(t(locale, "classroom.course.completed"), { count: completed })}</Badge>
        <Badge>{fill(t(locale, "classroom.course.certificates"), { count: certificates })}</Badge>
      </div>
      <ul className="divide-y rw-divide rw-radius border rw-line">
        {report.students.map((student) => (
          <li key={student.username}>
            <StudentRow student={student} report={report} />
          </li>
        ))}
      </ul>
    </div>
  );
}

function StudentRow({ student, report }: { student: Student; report: Report }) {
  const locale = useLocale();
  const done = new Set(student.lessons);
  const label = fill(t(locale, "course.progress"), { percent: student.percent });
  return (
    <details className="group">
      <summary className="flex min-h-11 cursor-pointer list-none flex-wrap items-center gap-x-4 gap-y-2 px-4 py-3 rw-focus-ring">
        <span aria-hidden="true" className="text-theme-xs rw-faint transition-transform group-open:rotate-180">
          ▾
        </span>
        <span className="min-w-0 flex-1 basis-40">
          <span className="block truncate font-medium rw-strong">
            {student.display_name || student.username}
          </span>
          <span className="block truncate text-theme-xs rw-faint">@{student.username}</span>
        </span>
        {student.enrolled ? (
          <span className="flex basis-48 items-center gap-2">
            <span
              role="progressbar"
              aria-valuemin={0}
              aria-valuemax={100}
              aria-valuenow={student.percent}
              aria-label={label}
              className="h-2 flex-1 overflow-hidden rounded-full rw-chip"
            >
              <span
                className={`block h-full rounded-full ${student.completed_at ? "bg-[var(--rw-ok-ink)]" : "rw-accent-bg"}`}
                style={{ width: `${student.percent}%` }}
              />
            </span>
            <span className="text-theme-xs tabular-nums rw-dim">
              {fill(t(locale, "course.progressDetail"), { done: student.done, total: student.total })}
            </span>
          </span>
        ) : (
          <Badge>{t(locale, "classroom.course.notEnrolled")}</Badge>
        )}
        {report.has_final_quiz && (
          <span className="text-theme-xs rw-dim">
            {student.final_score === null
              ? t(locale, "classroom.course.noQuiz")
              : fill(t(locale, "cert.finalScore"), { percent: student.final_score })}
          </span>
        )}
        {student.certificate && (
          <Link
            href={`/certificates/${student.certificate}` as Route}
            className="text-theme-xs rw-accent-ink hover:underline"
          >
            {t(locale, "course.certificateView")}
          </Link>
        )}
        {student.last_activity && (
          <span className="text-theme-xs rw-faint">
            {fill(t(locale, "classroom.course.lastActivity"), { date: numericDate(student.last_activity) })}
          </span>
        )}
      </summary>
      <div className="space-y-3 px-4 pb-4">
        {report.modules.map((module) => (
          <div key={module.id}>
            <p className="text-theme-xs font-semibold rw-dim">{module.title}</p>
            <ul className="mt-1 flex flex-wrap gap-1.5">
              {module.lessons.map((lesson) => {
                const finished = done.has(lesson.id);
                return (
                  <li
                    key={lesson.id}
                    className={`rounded border px-2 py-0.5 text-theme-xs ${finished ? "rw-line rw-ok-ink" : "rw-line rw-faint"}`}
                  >
                    <span aria-hidden="true">{finished ? "✓ " : "○ "}</span>
                    {lesson.title}
                    <span className="sr-only">
                      {" — "}
                      {t(locale, finished ? "classroom.course.lessonDone" : "classroom.course.lessonOpen")}
                    </span>
                    {!lesson.is_required && (
                      <span className="rw-faint"> · {t(locale, "classroom.course.optional")}</span>
                    )}
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </div>
    </details>
  );
}
