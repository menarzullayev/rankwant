import { Badge } from "@/components/ui/Badge";
import { fill, t, type Locale, type MessageKey } from "@/i18n/messages";

import type { CourseCard } from "../api/courses";

/** Level, price and lesson count under a course card. No hooks: the
 *  catalogue is a server page and passes the locale in. */
export function CourseMeta({ course, locale }: { course: CourseCard; locale: Locale }) {
  return (
    <>
      <Badge>{t(locale, `course.level.${course.level}` as MessageKey)}</Badge>
      {course.access === "free" ? (
        <Badge color="success">{t(locale, "course.access.free")}</Badge>
      ) : course.access === "qvant" ? (
        <Badge color="brand">
          {fill(t(locale, "course.price.qvant"), { amount: course.price_qvant })}
        </Badge>
      ) : (
        <Badge color="warning">
          {fill(t(locale, "course.price.uzs"), {
            amount: (course.price_uzs ?? 0).toLocaleString("ru-RU"),
          })}
        </Badge>
      )}
      <span>{fill(t(locale, "course.lessons"), { count: course.lesson_count })}</span>
      {course.percent !== null && (
        <span className="rw-accent-ink">
          {fill(t(locale, "course.progress"), { percent: course.percent })}
        </span>
      )}
    </>
  );
}
