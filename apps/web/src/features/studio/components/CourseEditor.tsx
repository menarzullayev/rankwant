"use client";

import type { Route } from "next";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { numericStamp } from "@rankwant/shared/format";

import { FM_INP, FM_LAB } from "@/components/form/chrome";
import { useConfirm } from "@/components/overlay/OverlayHost";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Field } from "@/components/ui/Field";
import { Icon } from "@/components/ui/Icon";
import { Checkbox, SelectField } from "@/components/ui/SelectField";
import { useLocale } from "@/i18n/LocaleProvider";
import { errorText, fill, LOCALE_NAMES, t, type Locale, type MessageKey } from "@/i18n/messages";
import { ApiError } from "@/lib/api";

import {
  CONTENT_LOCALES,
  COURSE_GAPS,
  courseStatus,
  reorder,
  studioCourses,
  textOf,
  type ContentLocale,
  type StudioCourse,
  type StudioLesson,
  type StudioModule,
  type StudioSection,
} from "../api/courses";
import { CourseStatusBadge, courseTitle } from "./CourseList";

const KINDS = ["text", "problem", "quiz", "video"] as const;
const PROVIDERS = ["youtube", "vimeo", "hls"] as const;
const LEVELS = ["beginner", "intermediate", "advanced"] as const;

function failure(locale: Locale, error: unknown): string {
  if (!(error instanceof ApiError)) return String(error);
  const first = error.details ? Object.values(error.details)[0] : undefined;
  if (error.code === "invalid" && Array.isArray(first) && typeof first[0] === "string") {
    return `${errorText(locale, error.code)} ${first[0]}`;
  }
  return errorText(locale, error.code);
}

/** One write at a time per block, with its error beside it. */
function useRun(onDone: () => Promise<void>) {
  const locale = useLocale();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  async function run(write: () => Promise<unknown>) {
    setBusy(true);
    setError("");
    try {
      await write();
      await onDone();
    } catch (err) {
      setError(failure(locale, err));
    } finally {
      setBusy(false);
    }
  }
  return { busy, error, run };
}

function ErrorLine({ text }: { text: string }) {
  if (!text) return null;
  return (
    <p role="alert" className="text-theme-sm rw-bad-ink">
      {text}
    </p>
  );
}

function TextArea({
  label,
  value,
  onChange,
  rows = 4,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  rows?: number;
}) {
  return (
    <label className="block">
      <span className={FM_LAB}>{label}</span>
      <textarea
        value={value}
        rows={rows}
        spellCheck={false}
        onChange={(event) => onChange(event.target.value)}
        className={`${FM_INP} font-mono`}
      />
    </label>
  );
}

function IconButton({
  icon,
  label,
  onClick,
  disabled,
}: {
  icon: string;
  label: string;
  onClick: () => void;
  disabled?: boolean;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      aria-label={label}
      title={label}
      className="inline-flex size-11 shrink-0 items-center justify-center rw-radius-sm rw-dim rw-hover-bg rw-focus-ring disabled:opacity-40"
    >
      <Icon name={icon} size="sm" className="size-4" />
    </button>
  );
}

const COURSE_FIELDS = ["title", "summary", "description", "outcomes", "requirements", "audience"] as const;
type CourseField = (typeof COURSE_FIELDS)[number];

/** The course's own text in one language. Remounted per language (`key`). */
function CourseText({
  course,
  lang,
  onSaved,
}: {
  course: StudioCourse;
  lang: ContentLocale;
  onSaved: (course: StudioCourse) => void;
}) {
  const locale = useLocale();
  const row = textOf(course.texts, lang);
  const [draft, setDraft] = useState<Record<CourseField, string>>(() => ({
    title: row?.title ?? "",
    summary: row?.summary ?? "",
    description: row?.description ?? "",
    outcomes: row?.outcomes ?? "",
    requirements: row?.requirements ?? "",
    audience: row?.audience ?? "",
  }));
  const [saved, setSaved] = useState(false);
  const { busy, error, run } = useRun(async () => {});
  const set = (key: CourseField, value: string) => {
    setSaved(false);
    setDraft((old) => ({ ...old, [key]: value }));
  };
  return (
    <form
      className="space-y-4"
      onSubmit={(event) => {
        event.preventDefault();
        void run(async () => {
          onSaved(await studioCourses.text(course.slug, { target: "course", locale: lang, ...draft }));
          setSaved(true);
        });
      }}
    >
      <Field
        name={`title-${lang}`}
        label={t(locale, "studio.field.title")}
        value={draft.title}
        maxLength={200}
        onChange={(event) => set("title", event.target.value)}
      />
      <Field
        name={`summary-${lang}`}
        label={t(locale, "studio.course.summary")}
        hint={t(locale, "studio.course.summaryHint")}
        value={draft.summary}
        maxLength={300}
        onChange={(event) => set("summary", event.target.value)}
      />
      <TextArea label={t(locale, "course.about")} value={draft.description} onChange={(v) => set("description", v)} rows={6} />
      <TextArea label={t(locale, "course.outcomes")} value={draft.outcomes} onChange={(v) => set("outcomes", v)} />
      <TextArea label={t(locale, "course.requirements")} value={draft.requirements} onChange={(v) => set("requirements", v)} rows={3} />
      <TextArea label={t(locale, "course.audience")} value={draft.audience} onChange={(v) => set("audience", v)} rows={3} />
      <p className="text-theme-xs rw-faint">{t(locale, "studio.field.markdownHint")}</p>
      <ErrorLine text={error} />
      <div className="flex flex-wrap items-center gap-3">
        <Button type="submit" busy={busy}>
          {t(locale, "studio.course.saveText")}
        </Button>
        {saved && <span className="text-theme-sm rw-ok-ink">{t(locale, "studio.course.saved")}</span>}
      </div>
    </form>
  );
}

function Settings({ course, onSaved }: { course: StudioCourse; onSaved: (c: StudioCourse) => void }) {
  const locale = useLocale();
  const [level, setLevel] = useState(course.level ?? "beginner");
  const [base, setBase] = useState(course.base_locale ?? "uz");
  const [sequential, setSequential] = useState(course.sequential ?? true);
  const [threshold, setThreshold] = useState(String(course.certificate_threshold ?? 70));
  const [quiz, setQuiz] = useState(course.final_quiz ?? "");
  const [cover, setCover] = useState(course.cover_url ?? "");
  const { busy, error, run } = useRun(async () => {});
  const locked = !course.structure_open;
  return (
    <form
      className="space-y-4"
      onSubmit={(event) => {
        event.preventDefault();
        void run(async () =>
          onSaved(
            await studioCourses.update(course.slug, {
              level: level as StudioCourse["level"],
              base_locale: base as StudioCourse["base_locale"],
              sequential,
              certificate_threshold: Number(threshold) || 70,
              final_quiz: quiz.trim() || null,
              cover_url: cover.trim(),
            }),
          ),
        );
      }}
    >
      {locked && <p className="text-theme-sm rw-dim">{t(locale, "studio.course.locked")}</p>}
      <fieldset disabled={locked} className="grid gap-4 sm:grid-cols-2">
        <SelectField
          name="level"
          label={t(locale, "course.filter.level")}
          options={LEVELS.map((value) => ({ value, label: t(locale, `course.level.${value}` as MessageKey) }))}
          value={level}
          onChange={(value) => setLevel(value as typeof level)}
          disabled={locked}
        />
        <SelectField
          name="base_locale"
          label={t(locale, "studio.course.baseLocale")}
          hint={t(locale, "studio.course.baseLocaleHint")}
          options={CONTENT_LOCALES.map((value) => ({ value, label: LOCALE_NAMES[value] }))}
          value={base}
          onChange={(value) => setBase(value as typeof base)}
          disabled={locked}
        />
        <Field
          name="final_quiz"
          label={t(locale, "studio.course.finalQuiz")}
          hint={t(locale, "studio.course.finalQuizHint")}
          value={quiz}
          onChange={(event) => setQuiz(event.target.value)}
        />
        <Field
          name="certificate_threshold"
          type="number"
          min={1}
          max={100}
          label={t(locale, "studio.course.threshold")}
          value={threshold}
          onChange={(event) => setThreshold(event.target.value)}
        />
        <Field
          name="cover_url"
          label={t(locale, "studio.course.cover")}
          hint={t(locale, "studio.course.coverHint")}
          value={cover}
          onChange={(event) => setCover(event.target.value)}
        />
        <div className="flex items-end">
          <Checkbox checked={sequential} onChange={(event) => setSequential(event.target.checked)}>
            {t(locale, "course.sequential")}
          </Checkbox>
        </div>
      </fieldset>
      <ErrorLine text={error} />
      {!locked && (
        <Button type="submit" busy={busy}>
          {t(locale, "studio.course.saveSettings")}
        </Button>
      )}
    </form>
  );
}

/** A title in the chosen language, saved with its own button. */
function TitleEditor({
  initial,
  label,
  onSave,
}: {
  initial: string;
  label: string;
  onSave: (title: string) => Promise<void>;
}) {
  const locale = useLocale();
  const [value, setValue] = useState(initial);
  const { busy, error, run } = useRun(async () => {});
  return (
    <form
      className="flex min-w-0 flex-1 flex-wrap items-center gap-2"
      onSubmit={(event) => {
        event.preventDefault();
        void run(() => onSave(value));
      }}
    >
      <input
        aria-label={label}
        value={value}
        maxLength={200}
        placeholder={label}
        onChange={(event) => setValue(event.target.value)}
        className={`${FM_INP} min-w-0 flex-1`}
      />
      <Button type="submit" variant="outline" busy={busy} disabled={value === initial}>
        {t(locale, "studio.course.save")}
      </Button>
      <ErrorLine text={error} />
    </form>
  );
}

function LessonEditor({
  course,
  lesson,
  lang,
  index,
  siblings,
  run,
}: {
  course: StudioCourse;
  lesson: StudioLesson;
  lang: ContentLocale;
  index: number;
  siblings: StudioLesson[];
  run: (write: () => Promise<unknown>) => Promise<void>;
}) {
  const locale = useLocale();
  const confirm = useConfirm();
  const row = textOf(lesson.texts, lang);
  const [title, setTitle] = useState(row?.title ?? "");
  const [body, setBody] = useState(row?.body ?? "");
  const [kind, setKind] = useState(lesson.kind ?? "text");
  const [required, setRequired] = useState(lesson.is_required ?? true);
  const [preview, setPreview] = useState(lesson.is_preview ?? false);
  const [problem, setProblem] = useState(lesson.problem ?? "");
  const [quiz, setQuiz] = useState(lesson.quiz ?? "");
  const [pass, setPass] = useState(String(lesson.quiz_pass_percent ?? 70));
  const [provider, setProvider] = useState(lesson.video_provider || "youtube");
  const [ref, setRef] = useState(lesson.video_ref ?? "");
  const [seconds, setSeconds] = useState(String(lesson.video_seconds ?? 0));
  const open = course.structure_open;
  const shown = textOf(lesson.texts, lang)?.title || textOf(lesson.texts, course.base_locale ?? "uz")?.title;

  const move = (by: -1 | 1) =>
    run(async () => {
      for (const item of reorder(siblings, index, by)) {
        await studioCourses.updateLesson(course.slug, item.id, { order: item.order });
      }
    });

  return (
    <li className="rw-radius-sm border rw-line">
      <div className="flex items-center gap-1 px-2">
        <Badge>{t(locale, `course.lesson.kind.${lesson.kind ?? "text"}` as MessageKey)}</Badge>
        <span className={`min-w-0 flex-1 truncate text-theme-sm ${shown ? "rw-strong" : "rw-faint"}`}>
          {shown || t(locale, "studio.course.untitled")}
        </span>
        {open && (
          <>
            <IconButton icon="nav.expandUp" label={t(locale, "studio.course.moveUp")} disabled={index === 0} onClick={() => void move(-1)} />
            <IconButton icon="nav.expandDown" label={t(locale, "studio.course.moveDown")} disabled={index === siblings.length - 1} onClick={() => void move(1)} />
            <IconButton
              icon="action.delete"
              label={t(locale, "studio.course.removeLesson")}
              onClick={() =>
                void (async () => {
                  const ok = await confirm(t(locale, "studio.course.removeLessonConfirm"), { danger: true });
                  if (ok) await run(() => studioCourses.removeLesson(course.slug, lesson.id));
                })()
              }
            />
          </>
        )}
      </div>
      <details className="border-t rw-line">
        <summary className="flex min-h-11 cursor-pointer items-center px-3 text-theme-sm rw-accent-ink rw-focus-ring">
          {t(locale, "studio.course.editLesson")}
        </summary>
        <div className="space-y-5 p-3">
          <form
            className="space-y-3"
            onSubmit={(event) => {
              event.preventDefault();
              void run(() =>
                studioCourses.text(course.slug, { target: "lesson", id: lesson.id, locale: lang, title, body }),
              );
            }}
          >
            <Field name={`lesson-title-${lesson.id}`} label={t(locale, "studio.field.title")} value={title} maxLength={200} onChange={(e) => setTitle(e.target.value)} />
            <TextArea label={t(locale, "studio.course.lessonBody")} value={body} onChange={setBody} rows={8} />
            <Button type="submit" variant="outline">
              {t(locale, "studio.course.saveText")}
            </Button>
          </form>
          {open && (
            <form
              className="space-y-3 border-t rw-divider pt-4"
              onSubmit={(event) => {
                event.preventDefault();
                void run(() =>
                  studioCourses.updateLesson(course.slug, lesson.id, {
                    kind: kind as StudioLesson["kind"],
                    is_required: required,
                    is_preview: preview,
                    problem: kind === "problem" ? problem.trim() || null : null,
                    quiz: kind === "quiz" ? quiz.trim() || null : null,
                    quiz_pass_percent: Number(pass) || 70,
                    video_provider: kind === "video" ? (provider as StudioLesson["video_provider"]) : "",
                    video_ref: kind === "video" ? ref.trim() : "",
                    video_seconds: kind === "video" ? Number(seconds) || 0 : 0,
                  }),
                );
              }}
            >
              <div className="grid gap-3 sm:grid-cols-2">
                <SelectField
                  name={`kind-${lesson.id}`}
                  label={t(locale, "studio.course.kind")}
                  options={KINDS.map((value) => ({ value, label: t(locale, `course.lesson.kind.${value}` as MessageKey) }))}
                  value={kind}
                  onChange={(value) => setKind(value as typeof kind)}
                />
                <div className="flex flex-col justify-end gap-1">
                  <Checkbox checked={required} onChange={(e) => setRequired(e.target.checked)}>
                    {t(locale, "studio.course.required")}
                  </Checkbox>
                  <Checkbox checked={preview} onChange={(e) => setPreview(e.target.checked)}>
                    {t(locale, "course.lesson.preview")}
                  </Checkbox>
                </div>
                {kind === "problem" && (
                  <Field name={`problem-${lesson.id}`} label={t(locale, "studio.course.problem")} hint={t(locale, "studio.course.problemHint")} value={problem} onChange={(e) => setProblem(e.target.value)} />
                )}
                {kind === "quiz" && (
                  <>
                    <Field name={`quiz-${lesson.id}`} label={t(locale, "studio.course.quiz")} hint={t(locale, "studio.course.quizHint")} value={quiz} onChange={(e) => setQuiz(e.target.value)} />
                    <Field name={`pass-${lesson.id}`} type="number" min={1} max={100} label={t(locale, "studio.course.passPercent")} value={pass} onChange={(e) => setPass(e.target.value)} />
                  </>
                )}
                {kind === "video" && (
                  <>
                    <SelectField
                      name={`provider-${lesson.id}`}
                      label={t(locale, "studio.course.videoProvider")}
                      options={PROVIDERS.map((value) => ({ value, label: t(locale, `studio.course.provider.${value}` as MessageKey) }))}
                      value={provider}
                      onChange={(value) => setProvider(value as typeof provider)}
                    />
                    <Field name={`ref-${lesson.id}`} label={t(locale, "studio.course.videoRef")} hint={t(locale, "studio.course.videoRefHint")} value={ref} onChange={(e) => setRef(e.target.value)} />
                    <Field name={`seconds-${lesson.id}`} type="number" min={0} label={t(locale, "studio.course.videoSeconds")} value={seconds} onChange={(e) => setSeconds(e.target.value)} />
                  </>
                )}
              </div>
              <Button type="submit" variant="outline">
                {t(locale, "studio.course.saveLesson")}
              </Button>
            </form>
          )}
        </div>
      </details>
    </li>
  );
}

function SectionEditor({
  course,
  section,
  lang,
  index,
  siblings,
  run,
}: {
  course: StudioCourse;
  section: StudioSection;
  lang: ContentLocale;
  index: number;
  siblings: StudioSection[];
  run: (write: () => Promise<unknown>) => Promise<void>;
}) {
  const locale = useLocale();
  const confirm = useConfirm();
  const [kind, setKind] = useState<(typeof KINDS)[number]>("text");
  const open = course.structure_open;
  const lessons = section.lessons;
  return (
    <li className="space-y-2 border-l-2 rw-line pl-3">
      <div className="flex flex-wrap items-center gap-1">
        <TitleEditor
          key={`${section.id}-${lang}`}
          initial={textOf(section.texts, lang)?.title ?? ""}
          label={t(locale, "studio.course.sectionTitle")}
          onSave={(title) =>
            run(() => studioCourses.text(course.slug, { target: "section", id: section.id, locale: lang, title }))
          }
        />
        {open && (
          <>
            <IconButton icon="nav.expandUp" label={t(locale, "studio.course.moveUp")} disabled={index === 0} onClick={() => void run(async () => { for (const i of reorder(siblings, index, -1)) await studioCourses.updateSection(course.slug, i.id, { order: i.order }); })} />
            <IconButton icon="nav.expandDown" label={t(locale, "studio.course.moveDown")} disabled={index === siblings.length - 1} onClick={() => void run(async () => { for (const i of reorder(siblings, index, 1)) await studioCourses.updateSection(course.slug, i.id, { order: i.order }); })} />
            <IconButton
              icon="action.delete"
              label={t(locale, "studio.course.removeSection")}
              onClick={() =>
                void (async () => {
                  const ok = await confirm(t(locale, "studio.course.removeSectionConfirm"), { danger: true });
                  if (ok) await run(() => studioCourses.removeSection(course.slug, section.id));
                })()
              }
            />
          </>
        )}
      </div>
      <ul className="space-y-2">
        {lessons.map((lesson, i) => (
          <LessonEditor
            key={`${lesson.id}-${lang}`}
            course={course}
            lesson={lesson}
            lang={lang}
            index={i}
            siblings={lessons}
            run={run}
          />
        ))}
      </ul>
      {open && (
        <div className="flex flex-wrap items-end gap-2">
          <SelectField
            name={`new-kind-${section.id}`}
            label={t(locale, "studio.course.kind")}
            size="sm"
            options={KINDS.map((value) => ({ value, label: t(locale, `course.lesson.kind.${value}` as MessageKey) }))}
            value={kind}
            onChange={(value) => setKind(value as typeof kind)}
          />
          <Button
            type="button"
            variant="outline"
            onClick={() =>
              void run(() =>
                studioCourses.addLesson(course.slug, { section: section.id, kind, order: lessons.length + 1 }),
              )
            }
          >
            {t(locale, "studio.course.addLesson")}
          </Button>
        </div>
      )}
    </li>
  );
}

function ModuleEditor({
  course,
  module,
  lang,
  index,
  run,
}: {
  course: StudioCourse;
  module: StudioModule;
  lang: ContentLocale;
  index: number;
  run: (write: () => Promise<unknown>) => Promise<void>;
}) {
  const locale = useLocale();
  const confirm = useConfirm();
  const open = course.structure_open;
  const siblings = course.modules;
  return (
    <li className="space-y-3 rw-radius border rw-line rw-surface p-4">
      <div className="flex flex-wrap items-center gap-1">
        <span className="text-theme-sm font-semibold rw-dim">{index + 1}.</span>
        <TitleEditor
          key={`${module.id}-${lang}`}
          initial={textOf(module.texts, lang)?.title ?? ""}
          label={t(locale, "studio.course.moduleTitle")}
          onSave={(title) =>
            run(() => studioCourses.text(course.slug, { target: "module", id: module.id, locale: lang, title }))
          }
        />
        {open && (
          <>
            <IconButton icon="nav.expandUp" label={t(locale, "studio.course.moveUp")} disabled={index === 0} onClick={() => void run(async () => { for (const i of reorder(siblings, index, -1)) await studioCourses.updateModule(course.slug, i.id, { order: i.order }); })} />
            <IconButton icon="nav.expandDown" label={t(locale, "studio.course.moveDown")} disabled={index === siblings.length - 1} onClick={() => void run(async () => { for (const i of reorder(siblings, index, 1)) await studioCourses.updateModule(course.slug, i.id, { order: i.order }); })} />
            <IconButton
              icon="action.delete"
              label={t(locale, "studio.course.removeModule")}
              onClick={() =>
                void (async () => {
                  const ok = await confirm(t(locale, "studio.course.removeModuleConfirm"), { danger: true });
                  if (ok) await run(() => studioCourses.removeModule(course.slug, module.id));
                })()
              }
            />
          </>
        )}
      </div>
      <ul className="space-y-4">
        {module.sections.map((section, i) => (
          <SectionEditor
            key={section.id}
            course={course}
            section={section}
            lang={lang}
            index={i}
            siblings={module.sections}
            run={run}
          />
        ))}
      </ul>
      {open && (
        <Button
          type="button"
          variant="outline"
          onClick={() =>
            void run(() =>
              studioCourses.addSection(course.slug, { module: module.id, order: module.sections.length + 1 }),
            )
          }
        >
          {t(locale, "studio.course.addSection")}
        </Button>
      )}
    </li>
  );
}

function ReviewPanel({ course, onSaved }: { course: StudioCourse; onSaved: (c: StudioCourse) => void }) {
  const locale = useLocale();
  const router = useRouter();
  const confirm = useConfirm();
  const { busy, error, run } = useRun(async () => {});
  const status = courseStatus(course);
  if (status === "published") {
    return <p className="text-theme-sm rw-dim">{t(locale, "studio.course.published")}</p>;
  }
  const gaps = new Set(course.gaps);
  return (
    <div className="space-y-4">
      <p className="text-theme-sm rw-dim">{t(locale, "studio.course.reviewIntro")}</p>
      <ul className="divide-y rw-divide">
        {COURSE_GAPS.map((gap) => {
          const ok = !gaps.has(gap);
          return (
            <li key={gap} className="flex items-start gap-3 py-2.5 text-theme-sm">
              <span aria-hidden className={ok ? "rw-ok-ink font-bold" : "rw-bad-ink font-bold"}>
                {ok ? "✓" : "✕"}
              </span>
              <span className="rw-strong">
                {t(locale, `studio.course.gap.${gap}` as MessageKey)}
                <span className="sr-only">{t(locale, ok ? "studio.review.done" : "studio.review.missing")}</span>
              </span>
            </li>
          );
        })}
      </ul>
      {status === "review" && course.review_requested_at ? (
        <p className="rw-radius-sm rw-warn-soft px-4 py-3 text-theme-sm rw-warn-ink">
          {fill(t(locale, "studio.review.sent"), { at: numericStamp(course.review_requested_at) })}
          <span className="block text-theme-xs">{t(locale, "studio.review.sentHint")}</span>
        </p>
      ) : (
        <Button type="button" busy={busy} disabled={gaps.size > 0} onClick={() => void run(async () => onSaved(await studioCourses.review(course.slug)))}>
          {t(locale, "studio.review.submit")}
        </Button>
      )}
      <ErrorLine text={error} />
      <div className="border-t rw-divider pt-4">
        <Button
          type="button"
          variant="outline"
          className="rw-bad-ink"
          onClick={() =>
            void (async () => {
              const ok = await confirm(fill(t(locale, "studio.course.deleteConfirm"), { title: courseTitle(course) }), {
                danger: true,
                confirmLabel: t(locale, "studio.course.delete"),
              });
              if (!ok) return;
              await run(async () => {
                await studioCourses.remove(course.slug);
                router.replace("/studio/courses" as Route);
                router.refresh();
              });
            })()
          }
        >
          {t(locale, "studio.course.delete")}
        </Button>
      </div>
    </div>
  );
}

function Block({ id, title, children }: { id: string; title: string; children: React.ReactNode }) {
  return (
    <section aria-labelledby={id} className="space-y-4">
      <h2 id={id} className="text-theme-lg font-semibold rw-strong">
        {title}
      </h2>
      {children}
    </section>
  );
}

/** The whole course on one page: text per language, settings, programme
 *  and review. Every write re-reads the course, so the page never shows a
 *  state the server does not hold. */
export function CourseEditor({ initial }: { initial: StudioCourse }) {
  const locale = useLocale();
  const [course, setCourse] = useState(initial);
  const [lang, setLang] = useState<ContentLocale>(
    CONTENT_LOCALES.find((code) => code === initial.base_locale) ?? "uz",
  );
  const programme = useRun(async () => setCourse(await studioCourses.get(course.slug)));
  const open = course.structure_open;

  return (
    <div className="space-y-10">
      <header className="space-y-2">
        <p className="text-theme-sm">
          <Link href={"/studio/courses" as Route} className="inline-flex min-h-11 items-center rw-accent-ink rw-focus-ring">
            {t(locale, "studio.nav.courses")}
          </Link>
        </p>
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="text-title-sm font-bold rw-strong">{courseTitle(course)}</h1>
          <CourseStatusBadge course={course} locale={locale} />
        </div>
        {course.is_published && (
          <Link
            href={`/courses/${encodeURIComponent(course.slug)}` as Route}
            className="inline-flex min-h-11 items-center text-theme-sm rw-accent-ink rw-focus-ring"
          >
            {t(locale, "studio.course.openPublic")}
          </Link>
        )}
      </header>

      <nav aria-label={t(locale, "studio.course.language")} className="flex flex-wrap gap-2">
        {CONTENT_LOCALES.map((code) => (
          <button
            key={code}
            type="button"
            aria-pressed={lang === code}
            onClick={() => setLang(code)}
            className={`inline-flex min-h-11 items-center gap-2 rounded-full border px-4 text-theme-sm rw-focus-ring ${
              lang === code ? "rw-accent-soft rw-accent-ink border-[var(--rw-accent)]" : "rw-line rw-dim rw-hover-bg"
            }`}
          >
            {LOCALE_NAMES[code]}
            {code === course.base_locale && (
              <span className="text-theme-xs rw-faint">{t(locale, "studio.course.baseMark")}</span>
            )}
          </button>
        ))}
      </nav>

      <Block id="course-text" title={t(locale, "studio.course.text")}>
        <CourseText key={lang} course={course} lang={lang} onSaved={setCourse} />
      </Block>

      <Block id="course-programme" title={t(locale, "course.programme")}>
        {course.is_published && <p className="text-theme-sm rw-dim">{t(locale, open ? "studio.course.staffEdits" : "studio.course.locked")}</p>}
        <ol className="space-y-4">
          {course.modules.map((module, i) => (
            <ModuleEditor key={module.id} course={course} module={module} lang={lang} index={i} run={programme.run} />
          ))}
        </ol>
        <ErrorLine text={programme.error} />
        {open && (
          <Button
            type="button"
            busy={programme.busy}
            onClick={() =>
              void programme.run(() => studioCourses.addModule(course.slug, { order: course.modules.length + 1 }))
            }
          >
            {t(locale, "studio.course.addModule")}
          </Button>
        )}
      </Block>

      <Block id="course-settings" title={t(locale, "studio.course.settings")}>
        <Settings key={String(course.structure_open)} course={course} onSaved={setCourse} />
      </Block>

      <Block id="course-review" title={t(locale, "studio.tab.review")}>
        <ReviewPanel course={course} onSaved={setCourse} />
      </Block>
    </div>
  );
}
