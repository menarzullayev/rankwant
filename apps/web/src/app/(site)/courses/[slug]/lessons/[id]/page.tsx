import type { Metadata, Route } from "next";
import { cookies } from "next/headers";
import Link from "next/link";
import { notFound } from "next/navigation";

import { SignInGate } from "@/components/auth/SignInGate";
import { Badge } from "@/components/ui/Badge";
import { ButtonLink } from "@/components/ui/Button";
import { Markdown } from "@/components/ui/Markdown";
import {
  CompleteButton,
  FallbackNote,
  langQuery,
  lessonHref,
  lessonState,
  LessonVideo,
  Programme,
  ProgressBar,
  type CourseDetail,
  type LessonDetail,
} from "@/features/courses";
import { getLocale } from "@/i18n/server";
import { errorText, fill, t, type Locale, type MessageKey } from "@/i18n/messages";
import { ApiError } from "@/lib/api";
import { getWithSession } from "@/lib/api.server";
import { isOnServer } from "@/lib/flags";
import { SESSION_COOKIE } from "@/lib/home-cache";

export const dynamic = "force-dynamic";

type Props = { params: Promise<{ slug: string; id: string }> };

const SELF_COMPLETED = new Set(["text", "video"]);

async function course(slug: string, locale: Locale): Promise<CourseDetail> {
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

type Loaded = { lesson: LessonDetail } | { refused: ApiError };

async function lesson(slug: string, id: number, locale: Locale): Promise<Loaded> {
  const lang = langQuery(locale);
  try {
    return {
      lesson: await getWithSession<LessonDetail>(
        `/courses/${encodeURIComponent(slug)}/lessons/${id}/${lang ? `?${lang}` : ""}`,
      ),
    };
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    if (error instanceof ApiError && (error.status === 401 || error.status === 403)) {
      return { refused: error };
    }
    throw error;
  }
}

function lessonId(raw: string): number {
  const id = Number(raw);
  if (!Number.isInteger(id) || id <= 0) notFound();
  return id;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  if (!isOnServer("courses", undefined)) return { title: "404" };
  const { slug } = await params;
  return { title: (await course(slug, await getLocale())).title };
}

function Neighbour({
  slug,
  row,
  label,
  align,
}: {
  slug: string;
  row: LessonDetail["previous"];
  label: string;
  align: "start" | "end";
}) {
  if (!row) return <span />;
  const text = (
    <>
      <span className="block text-theme-xs rw-dim">{label}</span>
      <span className="block truncate text-theme-sm font-medium">{row.title}</span>
    </>
  );
  const cls = `min-h-11 min-w-0 max-w-[48%] rw-radius-sm px-3 py-2 ${align === "end" ? "text-right" : ""}`;
  if (lessonState(row.state) === "locked") {
    return <span className={`${cls} rw-faint`}>{text}</span>;
  }
  return (
    <Link href={lessonHref(slug, row.id)} className={`${cls} rw-strong rw-hover-bg rw-focus-ring`}>
      {text}
    </Link>
  );
}

function Task({ data, locale }: { data: LessonDetail; locale: Locale }) {
  if (data.kind === "problem") {
    return (
      <div className="space-y-3 rw-radius border rw-line rw-surface p-5">
        <p className="text-theme-sm rw-dim">{t(locale, "course.lesson.problemHint")}</p>
        {data.problem ? (
          <ButtonLink href={`/problems/${encodeURIComponent(data.problem.slug)}` as Route}>
            {t(locale, "course.lesson.openProblem")}
            {data.problem.code !== null ? ` #${data.problem.code}` : ""} · {data.problem.title}
          </ButtonLink>
        ) : (
          <p className="text-theme-sm rw-faint">{t(locale, "course.lesson.problemHidden")}</p>
        )}
      </div>
    );
  }
  if (data.kind === "quiz") {
    return (
      <div className="space-y-3 rw-radius border rw-line rw-surface p-5">
        <p className="text-theme-sm rw-dim">
          {fill(t(locale, "course.lesson.quizHint"), { percent: data.quiz_pass_percent })}
        </p>
        {data.quiz && (
          <ButtonLink href={`/quizzes/${encodeURIComponent(data.quiz.slug)}` as Route}>
            {t(locale, "course.lesson.openQuiz")} · {data.quiz.title}
          </ButtonLink>
        )}
      </div>
    );
  }
  if (data.kind === "video" && data.video) return <LessonVideo video={data.video} title={data.title} />;
  return null;
}

export default async function LessonPage({ params }: Props) {
  if (!isOnServer("courses", undefined)) notFound();
  const locale = await getLocale();
  const { slug, id: raw } = await params;
  const id = lessonId(raw);
  const signedIn = (await cookies()).has(SESSION_COOKIE);
  const [detail, loaded] = await Promise.all([
    course(slug, locale),
    signedIn ? lesson(slug, id, locale) : Promise.resolve(null),
  ]);
  const enrolled = detail.enrollment !== null;

  let main: React.ReactNode;
  if (!loaded) {
    main = <SignInGate reason="course" />;
  } else if ("refused" in loaded) {
    main = (
      <div className="space-y-3 rw-radius border border-dashed rw-line rw-surface p-5">
        <p className="text-theme-sm rw-strong">
          {errorText(locale, loaded.refused.code, loaded.refused.message)}
        </p>
        <ButtonLink href={`/courses/${encodeURIComponent(slug)}` as Route} variant="outline">
          {t(locale, "course.lesson.backToCourse")}
        </ButtonLink>
      </div>
    );
  } else {
    const data = loaded.lesson;
    main = (
      <article className="space-y-6">
        <header className="space-y-2">
          <div className="flex flex-wrap items-center gap-2">
            <Badge>{t(locale, `course.lesson.kind.${data.kind}` as MessageKey)}</Badge>
            {!data.is_required && <Badge>{t(locale, "course.lesson.optional")}</Badge>}
            {data.completed && <Badge color="success">{t(locale, "course.lesson.state.done")}</Badge>}
          </div>
          <h1 className="text-title-sm font-bold rw-strong">{data.title}</h1>
          <FallbackNote shown={data.locale} locale={locale} />
        </header>
        {data.body.trim() && <Markdown>{data.body}</Markdown>}
        <Task data={data} locale={locale} />
        {enrolled && !data.completed && SELF_COMPLETED.has(data.kind) && (
          <CompleteButton slug={slug} lessonId={data.id} />
        )}
        {!enrolled && (
          <p className="text-theme-sm rw-dim">{t(locale, "course.enrollToKeep")}</p>
        )}
        <nav
          aria-label={t(locale, "course.lesson.around")}
          className="flex items-stretch justify-between gap-3 border-t rw-line pt-4"
        >
          <Neighbour slug={slug} row={data.previous} label={t(locale, "course.lesson.previous")} align="start" />
          <Neighbour slug={slug} row={data.next} label={t(locale, "course.lesson.next")} align="end" />
        </nav>
      </article>
    );
  }

  return (
    <div className="grid gap-8 xl:grid-cols-[20rem_minmax(0,1fr)]">
      <aside className="order-2 space-y-4 xl:order-1 xl:sticky xl:top-[calc(var(--rw-header-h)+1rem)] xl:self-start">
        <Link
          href={`/courses/${encodeURIComponent(slug)}` as Route}
          className="flex min-h-11 items-center text-theme-sm font-semibold rw-accent-ink rw-focus-ring"
        >
          {detail.title}
        </Link>
        {enrolled && <ProgressBar progress={detail.progress} />}
        <Programme slug={slug} modules={detail.modules} current={id} />
      </aside>
      <div className="order-1 min-w-0 xl:order-2">{main}</div>
    </div>
  );
}
