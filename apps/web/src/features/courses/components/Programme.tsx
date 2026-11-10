"use client";

import Link from "next/link";

import { Icon } from "@/components/ui/Icon";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t, type MessageKey } from "@/i18n/messages";

import {
  lessonHref,
  lessonState,
  type CourseLessonRow,
  type CourseModule,
  type LessonState,
} from "../api/courses";

const KIND_ICON: Record<string, string> = {
  text: "content.article",
  problem: "content.problem",
  quiz: "content.quiz",
  video: "content.video",
};

const STATE_ICON: Record<LessonState, string> = {
  done: "status.ok",
  open: "status.unlocked",
  locked: "status.locked",
};

function LessonLine({
  slug,
  row,
  current,
}: {
  slug: string;
  row: CourseLessonRow;
  current?: number;
}) {
  const locale = useLocale();
  const state = lessonState(row.state);
  const minutes = row.video_seconds ? Math.max(1, Math.round(row.video_seconds / 60)) : 0;
  const body = (
    <>
      <Icon name={KIND_ICON[row.kind] ?? "content.article"} size="sm" className="size-4 shrink-0 rw-dim" />
      <span className="min-w-0 flex-1 truncate">{row.title}</span>
      {!row.is_required && (
        <span className="text-theme-xs rw-faint">{t(locale, "course.lesson.optional")}</span>
      )}
      {row.is_preview && state !== "done" && (
        <span className="text-theme-xs rw-accent-ink">{t(locale, "course.lesson.preview")}</span>
      )}
      {minutes > 0 && (
        <span className="text-theme-xs rw-faint">
          {fill(t(locale, "course.minutes"), { count: minutes })}
        </span>
      )}
      <Icon
        name={STATE_ICON[state]}
        size="sm"
        className={`size-4 shrink-0 ${state === "done" ? "rw-ok-ink" : "rw-faint"}`}
      />
      <span className="sr-only">{t(locale, `course.lesson.state.${state}` as MessageKey)}</span>
    </>
  );
  const base = "flex min-h-11 items-center gap-2 rw-radius-sm px-2 text-theme-sm";
  if (state === "locked") {
    return <div className={`${base} rw-faint`}>{body}</div>;
  }
  return (
    <Link
      href={lessonHref(slug, row.id)}
      aria-current={current === row.id ? "page" : undefined}
      className={`${base} rw-strong rw-hover-bg rw-focus-ring ${
        current === row.id ? "rw-accent-soft" : ""
      }`}
    >
      {body}
    </Link>
  );
}

/** Modules → sections → lessons, each lesson with its state for this reader.
 *  A locked lesson is not a link: opening it would only answer 403. */
export function Programme({
  slug,
  modules,
  current,
}: {
  slug: string;
  modules: CourseModule[];
  /** The lesson on screen, marked in the list. */
  current?: number;
}) {
  return (
    <ol className="space-y-5">
      {modules.map((module, mi) => (
        <li key={module.id}>
          <h3 className="text-theme-sm font-semibold rw-strong">
            {mi + 1}. {module.title}
          </h3>
          <div className="mt-2 space-y-3">
            {module.sections.map((section) => (
              <section key={section.id}>
                {section.title && (
                  <h4 className="px-2 text-theme-xs font-medium rw-dim">
                    {section.title}
                  </h4>
                )}
                <ul className="mt-1">
                  {section.lessons.map((row) => (
                    <li key={row.id}>
                      <LessonLine slug={slug} row={row} current={current} />
                    </li>
                  ))}
                </ul>
              </section>
            ))}
          </div>
        </li>
      ))}
    </ol>
  );
}
