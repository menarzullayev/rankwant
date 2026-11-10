"use client";

import type { Route } from "next";
import { useRouter } from "next/navigation";
import { useId, useState } from "react";

import { numericStamp } from "@rankwant/shared/format";

import { FM_INP, FM_LAB } from "@/components/form/chrome";
import { useConfirm } from "@/components/overlay/OverlayHost";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Field } from "@/components/ui/Field";
import { Markdown } from "@/components/ui/Markdown";
import { SelectField } from "@/components/ui/SelectField";
import { useLocale } from "@/i18n/LocaleProvider";
import { errorText, fill, t, type Locale, type MessageKey } from "@/i18n/messages";
import { ApiError } from "@/lib/api";

import {
  DIFFICULTY_MAX,
  DIFFICULTY_MIN,
  DIFFICULTY_STEP,
  draftStatus,
  reviewGaps,
  slugify,
  studioProblems,
  type DraftTest,
  type MineProblem,
  type ReviewGap,
} from "../api/problems";
import { DEFAULT_TAB, EDITOR_TABS, type EditorTab } from "../editor-tabs";
import { DraftPreview } from "./DraftPreview";
import { DraftTests } from "./DraftTests";


const TAB_LABEL: Record<EditorTab, MessageKey> = {
  statement: "studio.tab.statement",
  tests: "studio.tab.tests",
  editorial: "studio.tab.editorial",
  review: "studio.tab.review",
};

const GAP_LABEL: Record<ReviewGap, MessageKey> = {
  statement: "studio.review.check.statement",
  sample_test: "studio.review.check.sample",
  hidden_test: "studio.review.check.hidden",
};

const DIFFICULTIES = Array.from(
  { length: (DIFFICULTY_MAX - DIFFICULTY_MIN) / DIFFICULTY_STEP + 1 },
  (_, index) => String(DIFFICULTY_MIN + index * DIFFICULTY_STEP),
);

/** Defaults the server applies to a new problem — shown in the preview
 *  before the first save. `problems.models.Problem`. */
const NEW_LIMITS = { time_limit_ms: 1000, memory_limit_kb: 262144 };

type Draft = Pick<
  MineProblem,
  "title" | "statement" | "input_format" | "output_format" | "note" | "difficulty"
> & { slug: string };

function draftOf(problem: MineProblem | null): Draft {
  return {
    slug: problem?.slug ?? "",
    title: problem?.title ?? "",
    statement: problem?.statement ?? "",
    input_format: problem?.input_format ?? "",
    output_format: problem?.output_format ?? "",
    note: problem?.note ?? "",
    difficulty: problem?.difficulty ?? DIFFICULTY_MIN,
  };
}

function failure(locale: Locale, error: unknown): string {
  if (!(error instanceof ApiError)) return String(error);
  // A taken or malformed slug comes back as a field error; the generic
  // "invalid" text would not say which field.
  if (error.details && "slug" in error.details) return t(locale, "studio.error.slug");
  return errorText(locale, error.code);
}

/** A textarea with its label above — Markdown fields of the statement. */
function MarkdownField({
  label,
  value,
  onChange,
  rows,
  required = false,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  rows: number;
  required?: boolean;
}) {
  return (
    <label className="block">
      <span className={FM_LAB}>{label}</span>
      <textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        rows={rows}
        required={required}
        spellCheck={false}
        className={`${FM_INP} font-mono`}
      />
    </label>
  );
}

/** Title, statement sections and difficulty — with the preview beside it.
 *  The same form creates a draft (`problem` is null) and edits one. */
function StatementForm({
  problem,
  onSaved,
}: {
  problem: MineProblem | null;
  onSaved: (problem: MineProblem) => void;
}) {
  const locale = useLocale();
  const router = useRouter();
  const [saved, setSaved] = useState<Draft>(() => draftOf(problem));
  const [draft, setDraft] = useState<Draft>(saved);
  const [slugTouched, setSlugTouched] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [done, setDone] = useState(false);
  const creating = problem === null;
  const dirty = JSON.stringify(draft) !== JSON.stringify(saved);

  function set<K extends keyof Draft>(key: K, value: Draft[K]) {
    setDone(false);
    setDraft((prev) => {
      const next = { ...prev, [key]: value };
      if (creating && key === "title" && !slugTouched) next.slug = slugify(String(value));
      return next;
    });
  }

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      if (creating) {
        const made = await studioProblems.create(draft);
        router.replace(`/studio/problems/${encodeURIComponent(made.slug)}` as Route);
        return;
      }
      const { slug: _slug, ...fields } = draft;
      const updated = await studioProblems.update(problem.slug, fields);
      const next = draftOf(updated);
      setSaved(next);
      setDraft(next);
      setDone(true);
      onSaved(updated);
    } catch (err) {
      setError(failure(locale, err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={submit} className="space-y-4">
      <div className="grid gap-6 xl:grid-cols-2">
        <div className="space-y-4">
          <Field
            label={t(locale, "studio.field.title")}
            name="title"
            value={draft.title}
            onChange={(event) => set("title", event.target.value)}
            required
            maxLength={200}
          />
          <div className="grid gap-4 sm:grid-cols-[minmax(0,1fr)_10rem]">
            <Field
              label={t(locale, "studio.field.slug")}
              name="slug"
              value={draft.slug}
              onChange={(event) => {
                setSlugTouched(true);
                set("slug", event.target.value);
              }}
              disabled={!creating}
              required
              maxLength={100}
              pattern="[a-z0-9]+(?:-[a-z0-9]+)*"
              hint={t(locale, "studio.field.slugHint")}
            />
            <SelectField
              label={t(locale, "studio.col.difficulty")}
              options={DIFFICULTIES.map((value) => ({ value, label: value }))}
              value={String(draft.difficulty)}
              onChange={(value) => set("difficulty", Number(value))}
            />
          </div>
          <MarkdownField
            label={t(locale, "studio.tab.statement")}
            value={draft.statement}
            onChange={(value) => set("statement", value)}
            rows={12}
            required
          />
          <MarkdownField
            label={t(locale, "problem.inputFormat")}
            value={draft.input_format}
            onChange={(value) => set("input_format", value)}
            rows={4}
          />
          <MarkdownField
            label={t(locale, "problem.outputFormat")}
            value={draft.output_format}
            onChange={(value) => set("output_format", value)}
            rows={4}
          />
          <MarkdownField
            label={t(locale, "problem.comments")}
            value={draft.note}
            onChange={(value) => set("note", value)}
            rows={3}
          />
          <p className="text-theme-xs rw-faint">{t(locale, "studio.field.markdownHint")}</p>
        </div>
        <div>
          <p className={FM_LAB}>{t(locale, "studio.preview")}</p>
          <DraftPreview
            problem={{
              ...draft,
              ...(problem
                ? { time_limit_ms: problem.time_limit_ms, memory_limit_kb: problem.memory_limit_kb }
                : NEW_LIMITS),
            }}
          />
          <p className="mt-2 text-theme-xs rw-faint">{t(locale, "studio.previewHint")}</p>
        </div>
      </div>
      {error && (
        <p role="alert" className="text-theme-sm rw-bad-ink">
          {error}
        </p>
      )}
      <div className="sticky bottom-0 flex flex-wrap items-center justify-end gap-3 border-t rw-divider rw-surface py-3">
        <span aria-live="polite" className="me-auto text-theme-xs rw-dim">
          {done ? t(locale, "studio.saved") : dirty ? t(locale, "studio.unsaved") : ""}
        </span>
        {dirty && !creating && (
          <Button type="button" variant="outline" onClick={() => setDraft(saved)}>
            {t(locale, "studio.cancel")}
          </Button>
        )}
        <Button type="submit" busy={busy} disabled={!creating && !dirty}>
          {t(locale, creating ? "studio.create" : "studio.save")}
        </Button>
      </div>
    </form>
  );
}

function EditorialForm({
  problem,
  onSaved,
}: {
  problem: MineProblem;
  onSaved: (problem: MineProblem) => void;
}) {
  const locale = useLocale();
  const [saved, setSaved] = useState(problem.editorial);
  const [text, setText] = useState(problem.editorial);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const dirty = text !== saved;

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const updated = await studioProblems.update(problem.slug, { editorial: text });
      setSaved(updated.editorial);
      setText(updated.editorial);
      onSaved(updated);
    } catch (err) {
      setError(failure(locale, err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={submit} className="space-y-4">
      <p className="text-theme-sm rw-dim">{t(locale, "studio.editorial.intro")}</p>
      <div className="grid gap-6 xl:grid-cols-2">
        <MarkdownField
          label={t(locale, "studio.tab.editorial")}
          value={text}
          onChange={setText}
          rows={14}
        />
        <div>
          <p className={FM_LAB}>{t(locale, "studio.preview")}</p>
          <div className="rw-radius-sm border border-dashed rw-line rw-field-bg p-4">
            <Markdown>{text}</Markdown>
          </div>
        </div>
      </div>
      {error && (
        <p role="alert" className="text-theme-sm rw-bad-ink">
          {error}
        </p>
      )}
      <div className="flex flex-wrap justify-end gap-3">
        <Button type="submit" busy={busy} disabled={!dirty}>
          {t(locale, "studio.save")}
        </Button>
      </div>
    </form>
  );
}

function ReviewPanel({
  problem,
  onSaved,
}: {
  problem: MineProblem;
  onSaved: (problem: MineProblem) => void;
}) {
  const locale = useLocale();
  const router = useRouter();
  const confirm = useConfirm();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const gaps = reviewGaps(problem);
  const status = draftStatus(problem);

  async function send() {
    setBusy(true);
    setError("");
    try {
      onSaved(await studioProblems.review(problem.slug));
    } catch (err) {
      setError(failure(locale, err));
    } finally {
      setBusy(false);
    }
  }

  async function remove(origin: HTMLElement) {
    const ok = await confirm(fill(t(locale, "studio.deleteConfirm"), { title: problem.title }), {
      danger: true,
      confirmLabel: t(locale, "studio.delete"),
      origin,
    });
    if (!ok) return;
    try {
      await studioProblems.remove(problem.slug);
      router.replace("/studio/problems" as Route);
      router.refresh();
    } catch (err) {
      setError(failure(locale, err));
    }
  }

  if (status === "public") {
    return <p className="text-theme-sm rw-dim">{t(locale, "studio.review.public")}</p>;
  }

  const checks: ReviewGap[] = ["statement", "sample_test", "hidden_test"];
  return (
    <div className="space-y-5">
      <p className="text-theme-sm rw-dim">{t(locale, "studio.review.intro")}</p>
      <ul className="divide-y rw-divide">
        {checks.map((check) => {
          const ok = !gaps.includes(check);
          return (
            <li key={check} className="flex items-start gap-3 py-2.5 text-theme-sm">
              <span aria-hidden className={ok ? "rw-ok-ink font-bold" : "rw-bad-ink font-bold"}>
                {ok ? "✓" : "✕"}
              </span>
              <span className="rw-strong">
                {t(locale, GAP_LABEL[check])}
                <span className="sr-only">
                  {t(locale, ok ? "studio.review.done" : "studio.review.missing")}
                </span>
                {check === "hidden_test" && !ok && (
                  <span className="block text-theme-xs rw-dim">{t(locale, "studio.review.hiddenWhy")}</span>
                )}
              </span>
            </li>
          );
        })}
      </ul>
      {status === "review" && problem.review_requested_at ? (
        <p className="rw-radius-sm rw-warn-soft px-4 py-3 text-theme-sm rw-warn-ink">
          {fill(t(locale, "studio.review.sent"), { at: numericStamp(problem.review_requested_at) })}
          <span className="block text-theme-xs">{t(locale, "studio.review.sentHint")}</span>
        </p>
      ) : (
        <Button type="button" busy={busy} disabled={gaps.length > 0} onClick={() => void send()}>
          {t(locale, "studio.review.submit")}
        </Button>
      )}
      {error && (
        <p role="alert" className="text-theme-sm rw-bad-ink">
          {error}
        </p>
      )}
      <div className="border-t rw-divider pt-4">
        <Button
          type="button"
          variant="outline"
          className="rw-bad-ink"
          onClick={(event) => void remove(event.currentTarget)}
        >
          {t(locale, "studio.delete")}
        </Button>
      </div>
    </div>
  );
}

/** One draft: statement, tests, editorial and the review request. The tab
 *  is kept in `?tab=` (replaced, not pushed), so a reload or a shared link
 *  opens the same tab without each switch adding a history entry. */
export function ProblemEditor({
  initial,
  initialTests,
  initialTab,
}: {
  initial: MineProblem | null;
  initialTests: DraftTest[];
  initialTab: EditorTab;
}) {
  const locale = useLocale();
  const base = useId();
  const [problem, setProblem] = useState<MineProblem | null>(initial);
  const [tests, setTests] = useState<DraftTest[]>(initialTests);
  const [tab, setTab] = useState<EditorTab>(initial ? initialTab : DEFAULT_TAB);

  function choose(next: EditorTab) {
    setTab(next);
    const url = new URL(window.location.href);
    if (next === DEFAULT_TAB) url.searchParams.delete("tab");
    else url.searchParams.set("tab", next);
    window.history.replaceState(null, "", url);
  }

  function onKey(event: React.KeyboardEvent<HTMLButtonElement>) {
    const step = { ArrowRight: 1, ArrowLeft: -1 }[event.key];
    if (!step) return;
    event.preventDefault();
    const index = (EDITOR_TABS.indexOf(tab) + step + EDITOR_TABS.length) % EDITOR_TABS.length;
    const next = EDITOR_TABS[index] ?? DEFAULT_TAB;
    choose(next);
    document.getElementById(`${base}-${next}`)?.focus();
  }

  function withCounts(next: DraftTest[]) {
    setTests(next);
    setProblem((prev) =>
      prev && {
        ...prev,
        sample_count: next.filter((row) => row.is_sample).length,
        hidden_count: next.filter((row) => !row.is_sample).length,
      },
    );
  }

  const heading = problem ? problem.title : t(locale, "studio.problems.new");
  return (
    <div className="space-y-4">
      {/* No back link: the section tabs above already lead to the list. */}
      <h1 className="text-title-sm font-bold rw-strong">{heading}</h1>

      {problem ? (
        <>
          <div
            role="tablist"
            aria-label={heading}
            className="rw-kit-tabs !flex-wrap !overflow-x-visible shadow-[inset_0_-1px_0_var(--rw-divider)]"
            data-kit-tabs="scroll"
          >
            {EDITOR_TABS.map((name) => (
              <button
                key={name}
                id={`${base}-${name}`}
                type="button"
                role="tab"
                aria-selected={tab === name}
                aria-controls={`${base}-panel`}
                tabIndex={tab === name ? 0 : -1}
                onClick={() => choose(name)}
                onKeyDown={onKey}
                className={`rw-kit-tab ${tab === name ? "rw-accent-ink" : "rw-dim rw-hover-strong"}`}
              >
                {name === "tests"
                  ? fill(t(locale, "studio.tab.testsCount"), { count: tests.length })
                  : t(locale, TAB_LABEL[name])}
              </button>
            ))}
          </div>
          <Card>
            <div id={`${base}-panel`} role="tabpanel" aria-labelledby={`${base}-${tab}`}>
              {problem.is_public && tab !== "review" && tab !== "tests" ? (
                // Published: staff-ops edit it now (the API answers 403).
                <div className="space-y-4">
                  <p className="text-theme-sm rw-dim">{t(locale, "studio.review.public")}</p>
                  {tab === "statement" ? (
                    <DraftPreview problem={problem} />
                  ) : (
                    <Markdown>{problem.editorial}</Markdown>
                  )}
                </div>
              ) : (
                tab === "statement" && <StatementForm problem={problem} onSaved={setProblem} />
              )}
              {tab === "tests" && (
                <DraftTests slug={problem.slug} locked={problem.is_public} tests={tests} onChange={withCounts} />
              )}
              {tab === "editorial" && !problem.is_public && (
                <EditorialForm problem={problem} onSaved={setProblem} />
              )}
              {tab === "review" && <ReviewPanel problem={problem} onSaved={setProblem} />}
            </div>
          </Card>
        </>
      ) : (
        <Card>
          <StatementForm problem={null} onSaved={setProblem} />
        </Card>
      )}
    </div>
  );
}
