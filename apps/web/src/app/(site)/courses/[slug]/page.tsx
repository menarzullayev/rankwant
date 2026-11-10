import type { Metadata, Route } from "next";
import { cookies } from "next/headers";
import Link from "next/link";
import { notFound } from "next/navigation";

import { SignInGate } from "@/components/auth/SignInGate";
import { ButtonLink } from "@/components/ui/Button";
import { Markdown } from "@/components/ui/Markdown";
import {
  CourseMeta,
  EnrollButton,
  FallbackNote,
  langQuery,
  lessonHref,
  nextLesson,
  Programme,
  ProgressBar,
  UnlockButton,
  type CourseDetail,
} from "@/features/courses";
import { groupDigits } from "@/features/billing";
import { getLocale } from "@/i18n/server";
import { fill, t, type Locale } from "@/i18n/messages";
import { ApiError } from "@/lib/api";
import { getWithSession } from "@/lib/api.server";
import { isOnServer } from "@/lib/flags";
import { SESSION_COOKIE } from "@/lib/home-cache";

export const dynamic = "force-dynamic";

type Props = { params: Promise<{ slug: string }> };

async function load(slug: string, locale: Locale): Promise<CourseDetail> {
  const lang = langQuery(locale);
  try {
    return await getWithSession<CourseDetail>(
      `/courses/${encodeURIComponent(slug)}/${lang ? `?${lang}` : ""}`,
    );
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  if (!isOnServer("courses", undefined)) return { title: "404" };
  const { slug } = await params;
  const course = await load(slug, await getLocale());
  return { title: course.title, description: course.summary || undefined };
}

function Join({ course, locale, signedIn }: { course: CourseDetail; locale: Locale; signedIn: boolean }) {
  const next = nextLesson(course);
  if (course.enrollment) {
    return (
      <div className="space-y-4">
        <ProgressBar progress={course.progress} />
        {course.progress.completed ? (
          <div className="space-y-3">
            <p className="text-theme-sm font-medium rw-ok-ink">{t(locale, "course.completed")}</p>
            {course.enrollment.certificate ? (
              <ButtonLink href={`/certificates/${course.enrollment.certificate}` as Route}>
                {t(locale, "course.certificateView")}
              </ButtonLink>
            ) : (
              course.final_quiz_slug && (
                <div className="space-y-2">
                  <p className="text-theme-sm rw-dim">
                    {fill(t(locale, "course.certificatePending"), { percent: course.certificate_threshold })}
                  </p>
                  <ButtonLink
                    href={`/quizzes/${encodeURIComponent(course.final_quiz_slug)}` as Route}
                    variant="outline"
                  >
                    {t(locale, "course.lesson.openQuiz")}
                  </ButtonLink>
                </div>
              )
            )}
          </div>
        ) : (
          next && (
            <ButtonLink href={lessonHref(course.slug, next.id)}>
              {course.progress.done ? t(locale, "course.continue") : t(locale, "course.start")}
            </ButtonLink>
          )
        )}
      </div>
    );
  }
  if (!signedIn) return <SignInGate reason="course" />;
  if (course.access === "free") return <EnrollButton slug={course.slug} />;
  if (course.access === "qvant") return <UnlockButton slug={course.slug} price={course.price_qvant ?? 0} />;
  // A paid course (ADR-0057): open through a plan that covers it, or bought.
  if (course.plan_covers) {
    return (
      <div className="space-y-2">
        <p className="text-theme-sm font-medium rw-ok-ink">{t(locale, "course.includedInPlan")}</p>
        <EnrollButton slug={course.slug} />
      </div>
    );
  }
  if (!isOnServer("billing", undefined) || !course.price_uzs) {
    return <p className="text-theme-sm rw-dim">{t(locale, "course.soonPaid")}</p>;
  }
  return (
    <div className="space-y-3">
      <ButtonLink href={`/checkout?course=${encodeURIComponent(course.slug)}` as Route}>
        {fill(t(locale, "course.buy"), { price: groupDigits(course.price_uzs) })}
      </ButtonLink>
      <p className="text-theme-sm">
        <Link href={"/plans" as Route} className="inline-flex min-h-11 items-center rw-accent-ink hover:underline">
          {t(locale, "course.orPro")}
        </Link>
      </p>
    </div>
  );
}

function Block({ title, text }: { title: string; text: string }) {
  if (!text.trim()) return null;
  return (
    <section className="space-y-2">
      <h2 className="text-theme-base font-semibold rw-strong">{title}</h2>
      <Markdown>{text}</Markdown>
    </section>
  );
}

export default async function CoursePage({ params }: Props) {
  if (!isOnServer("courses", undefined)) notFound();
  const locale = await getLocale();
  const { slug } = await params;
  const [course, jar] = await Promise.all([load(slug, locale), cookies()]);
  const signedIn = jar.has(SESSION_COOKIE);

  return (
    <div className="grid gap-8 xl:grid-cols-[minmax(0,1fr)_22rem]">
      <div className="min-w-0 space-y-8">
        <header className="space-y-3">
          <p className="text-theme-sm">
            <Link href={"/courses" as Route} className="inline-flex min-h-11 items-center rw-accent-ink rw-focus-ring">
              {t(locale, "nav.courses")}
            </Link>
          </p>
          <h1 className="text-title-sm font-bold rw-strong">{course.title}</h1>
          {course.summary && <p className="text-theme-base rw-dim">{course.summary}</p>}
          <div className="flex flex-wrap items-center gap-2 text-theme-xs rw-faint">
            <CourseMeta course={course} locale={locale} />
            <span>{fill(t(locale, "course.modules"), { count: course.module_count })}</span>
          </div>
          <FallbackNote shown={course.locale} locale={locale} />
        </header>

        <Block title={t(locale, "course.about")} text={course.description} />
        <Block title={t(locale, "course.outcomes")} text={course.outcomes} />
        <Block title={t(locale, "course.requirements")} text={course.requirements} />
        <Block title={t(locale, "course.audience")} text={course.audience} />

        <section aria-labelledby="programme" className="space-y-3">
          <h2 id="programme" className="text-theme-lg font-semibold rw-strong">
            {t(locale, "course.programme")}
          </h2>
          {course.sequential && (
            <p className="text-theme-xs rw-dim">{t(locale, "course.sequential")}</p>
          )}
          <Programme slug={course.slug} modules={course.modules} />
        </section>
      </div>

      <aside className="space-y-4 xl:sticky xl:top-[calc(var(--rw-header-h)+1rem)] xl:self-start">
        <div className="space-y-4 rw-radius border rw-line rw-surface p-5">
          <Join course={course} locale={locale} signedIn={signedIn} />
          {course.has_final_quiz && (
            <p className="text-theme-xs rw-dim">
              {fill(t(locale, "course.certificate"), { percent: course.certificate_threshold })}
            </p>
          )}
        </div>
        {course.authors.length > 0 && (
          <div className="space-y-2 rw-radius border rw-line rw-surface p-5">
            <h2 className="text-theme-sm font-semibold rw-strong">{t(locale, "course.authors")}</h2>
            <ul className="space-y-1 text-theme-sm">
              {course.authors.map((author) => (
                <li key={author.username}>
                  <Link
                    href={`/users/${encodeURIComponent(author.username)}` as Route}
                    className="inline-flex min-h-11 items-center rw-accent-ink rw-focus-ring"
                  >
                    {author.display_name || author.username}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        )}
      </aside>
    </div>
  );
}
