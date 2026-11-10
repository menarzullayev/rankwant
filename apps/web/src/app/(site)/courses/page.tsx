import type { Metadata, Route } from "next";
import Link from "next/link";
import { cookies } from "next/headers";
import { notFound } from "next/navigation";

import { ListCard } from "@/components/ui/ListCard";
import {
  CourseMeta,
  langQuery,
  type CourseAccess,
  type CourseCard,
  type CourseLevel,
  type MyCourse,
} from "@/features/courses";
import { getLocale } from "@/i18n/server";
import { fill, t, type MessageKey } from "@/i18n/messages";
import type { Paginated } from "@/lib/api";
import { getWithSession } from "@/lib/api.server";
import { isOnServer } from "@/lib/flags";
import { SESSION_COOKIE } from "@/lib/home-cache";

export const dynamic = "force-dynamic";

const LEVELS: CourseLevel[] = ["beginner", "intermediate", "advanced"];
const ACCESSES: CourseAccess[] = ["free", "qvant", "paid"];

type Props = { searchParams: Promise<{ level?: string; access?: string }> };

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "nav.courses") };
}

function query(parts: Record<string, string | undefined>): string {
  const q = new URLSearchParams();
  for (const [key, value] of Object.entries(parts)) if (value) q.set(key, value);
  const s = q.toString();
  return s ? `?${s}` : "";
}

function Chip({ href, active, children }: { href: string; active: boolean; children: string }) {
  return (
    <Link
      href={href as Route}
      aria-current={active ? "page" : undefined}
      className={`inline-flex min-h-11 items-center rounded-full border px-4 text-theme-sm rw-focus-ring ${
        active ? "rw-accent-soft rw-accent-ink border-[var(--rw-accent)]" : "rw-line rw-dim rw-hover-bg"
      }`}
    >
      {children}
    </Link>
  );
}

export default async function CoursesPage({ searchParams }: Props) {
  if (!isOnServer("courses", undefined)) notFound();
  const locale = await getLocale();
  const params = await searchParams;
  const level = LEVELS.find((v) => v === params.level);
  const access = ACCESSES.find((v) => v === params.access);
  const lang = langQuery(locale);

  const signedIn = (await cookies()).has(SESSION_COOKIE);
  const [data, mine] = await Promise.all([
    getWithSession<Paginated<CourseCard>>(
      `/courses/${query({ level, access, lang: lang ? locale : undefined, page_size: "100" })}`,
    ),
    signedIn
      ? getWithSession<Paginated<MyCourse>>(`/me/courses/${lang ? `?${lang}` : ""}`).catch(() => null)
      : Promise.resolve(null),
  ]);

  return (
    <div className="space-y-8">
      <header className="space-y-2">
        <h1 className="text-title-sm font-bold rw-strong">{t(locale, "nav.courses")}</h1>
        <p className="text-theme-sm rw-dim">{t(locale, "course.subtitle")}</p>
      </header>

      {mine && mine.results.length > 0 && (
        <section aria-labelledby="my-courses" className="space-y-3">
          <h2 id="my-courses" className="text-theme-lg font-semibold rw-strong">
            {t(locale, "course.mine")}
          </h2>
          <ul className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {mine.results.map((row) => (
              <li key={row.course.slug}>
                <ListCard
                  href={`/courses/${row.course.slug}` as Route}
                  title={row.course.title}
                  summary={
                    row.progress.completed
                      ? t(locale, "course.completed")
                      : fill(t(locale, "course.progressDetail"), {
                          done: row.progress.done,
                          total: row.progress.total,
                        })
                  }
                  meta={<CourseMeta course={row.course} locale={locale} />}
                />
              </li>
            ))}
          </ul>
        </section>
      )}

      <section aria-labelledby="all-courses" className="space-y-4">
        <h2 id="all-courses" className="text-theme-lg font-semibold rw-strong">
          {t(locale, "course.all")}
        </h2>
        <nav aria-label={t(locale, "course.filter.level")} className="flex flex-wrap gap-2">
          <Chip href={`/courses${query({ access })}`} active={!level}>
            {t(locale, "course.filter.anyLevel")}
          </Chip>
          {LEVELS.map((value) => (
            <Chip key={value} href={`/courses${query({ level: value, access })}`} active={level === value}>
              {t(locale, `course.level.${value}` as MessageKey)}
            </Chip>
          ))}
        </nav>
        <nav aria-label={t(locale, "course.filter.access")} className="flex flex-wrap gap-2">
          <Chip href={`/courses${query({ level })}`} active={!access}>
            {t(locale, "course.filter.anyAccess")}
          </Chip>
          {ACCESSES.map((value) => (
            <Chip key={value} href={`/courses${query({ level, access: value })}`} active={access === value}>
              {t(locale, `course.access.${value}` as MessageKey)}
            </Chip>
          ))}
        </nav>
        {data.results.length > 0 ? (
          <ul className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {data.results.map((course) => (
              <li key={course.slug}>
                <ListCard
                  href={`/courses/${course.slug}` as Route}
                  title={course.title}
                  summary={course.summary}
                  meta={<CourseMeta course={course} locale={locale} />}
                />
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-theme-sm rw-faint">{t(locale, "course.empty")}</p>
        )}
      </section>
    </div>
  );
}
