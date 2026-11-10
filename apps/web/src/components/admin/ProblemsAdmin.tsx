"use client";

import { useCallback, useEffect, useState } from "react";

import { numericStamp } from "@rankwant/shared/format";

import { FormCheck } from "@/components/form/FormKit";
import { FM_INP } from "@/components/form/chrome";
import { CrudPage, type FieldDef } from "@/components/admin/CrudPage";
import { ProblemTranslations } from "@/components/problems/ProblemTranslations";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Status } from "@/components/ui/Status";
import { useConfirm } from "@/components/overlay/OverlayHost";
import { useLocale } from "@/i18n/LocaleProvider";
import { t, errorText } from "@/i18n/messages";
import { api, ApiError, type Language } from "@/lib/api";
import { staff } from "@/lib/staff";

type StaffProblem = {
  id: number;
  /** Tizim beradigan ommaviy raqam — e'lon qilinganda paydo bo'ladi. */
  code: number | null;
  slug: string;
  title: string;
  statement: string;
  input_format: string;
  output_format: string;
  note: string;
  editorial: string;
  editorial_price: number;
  statement_locale: string;
  difficulty: number;
  topics: string[];
  time_limit_ms: number;
  memory_limit_kb: number;
  checker_type: "standard" | "special" | "interactive" | "scorer";
  task_kind: "program" | "function" | "answer" | "two_pass" | "sql";
  manager_source: string;
  manager_language: string | null;
  interactor_source: string;
  interactor_language: string | null;
  checker_source: string;
  checker_language: string | null;
  is_public: boolean;
  source: string;
  source_url: string;
  solved_count: number;
  attempt_count: number;
  test_count: number;
  /** Usernames — who wrote the draft in `/studio`. */
  authors: string[];
  /** When the author asked for a review; `null` — not asked. */
  review_requested_at: string | null;
  [key: string]: unknown;
};

type StaffTopic = {
  id: number;
  slug: string;
  name_uz: string;
  name_ru: string;
  name_en: string;
  parent: string | null;
  [key: string]: unknown;
};

type StaffTestCase = {
  id: number;
  order: number;
  is_sample: boolean;
  points: number;
  input_ref: string;
  output_ref: string;
};

const PROBLEM_FIELDS: FieldDef[] = [
  {
    name: "slug",
    labelKey: "admin.label.text.slug",
    type: "slug",
    required: true,
    readonlyOnEdit: true,
  },
  { name: "title", labelKey: "admin.label.text.title", required: true },
  {
    name: "difficulty",
    labelKey: "admin.label.value.difficultyRange",
    type: "number",
    required: true,
    min: 800,
    max: 3500,
    step: 100,
  },
  {
    name: "statement_locale",
    labelKey: "admin.label.name.language",
    helpKey: "admin.help.localeDefaultUz",
  },
  {
    name: "statement",
    labelKey: "admin.label.text.statementLatex",
    type: "textarea",
    required: true,
    rows: 12,
  },
  {
    name: "input_format",
    labelKey: "admin.label.tech.input",
    type: "textarea",
    rows: 4,
    helpKey: "admin.help.inputFormatSection",
  },
  {
    name: "output_format",
    labelKey: "admin.label.tech.output",
    type: "textarea",
    rows: 4,
  },
  {
    name: "note",
    labelKey: "admin.label.text.comment",
    type: "textarea",
    rows: 4,
    helpKey: "admin.help.noteExplainsSamples",
  },
  {
    name: "editorial",
    labelKey: "admin.label.text.editorial",
    type: "textarea",
    rows: 8,
    helpKey: "admin.help.editorialFreeForSolvers",
  },
  {
    name: "editorial_price",
    labelKey: "admin.label.value.analysisPriceQvant",
    type: "number",
    min: 0,
    helpKey: "admin.help.editorialPrice",
  },
  { name: "topics", labelKey: "admin.label.tech.topicsSlug", type: "list" },
  { name: "time_limit_ms", labelKey: "admin.label.value.timeLimit", type: "number", min: 100 },
  {
    name: "memory_limit_kb",
    labelKey: "admin.label.value.memoryLimit",
    type: "number",
    min: 1024,
  },
  {
    // What the solver submits (ADR-0053). The per-language harness of a
    // function problem is edited in the languages panel under the row.
    name: "task_kind",
    labelKey: "admin.label.text.taskKind",
    type: "select",
    required: true,
    options: [
      { value: "program", labelKey: "admin.label.value.wholeProgram" },
      { value: "function", labelKey: "admin.label.value.functionOnly" },
      { value: "answer", labelKey: "admin.label.value.answerFiles" },
      { value: "two_pass", labelKey: "admin.label.value.twoPass" },
      { value: "sql", labelKey: "admin.label.value.sqlQuery" },
    ],
  },
  {
    name: "checker_type",
    labelKey: "admin.label.text.checker",
    type: "select",
    required: true,
    options: [
      { value: "standard", labelKey: "admin.label.text.standard" },
      { value: "special", labelKey: "admin.label.text.special" },
      { value: "interactive", labelKey: "admin.label.text.interactive" },
      // Modelda bor edi, ro'yxatda esa yo'q — ya'ni tanlab bo'lmasdi.
      { value: "scorer", labelKey: "admin.label.value.scoring" },
    ],
  },
  {
    name: "manager_language",
    labelKey: "admin.label.tech.managerLanguage",
    helpKey: "admin.help.managerOnlyTwoPass",
  },
  {
    name: "manager_source",
    labelKey: "admin.label.tech.managerSource",
    type: "textarea",
    rows: 8,
  },
  {
    name: "interactor_language",
    labelKey: "admin.label.tech.interactorLanguage",
    helpKey: "admin.help.interactorOnlyInteractive",
  },
  {
    name: "interactor_source",
    labelKey: "admin.label.tech.interactorSource",
    type: "textarea",
    rows: 8,
  },
  {
    name: "checker_language",
    labelKey: "admin.label.tech.checkerLanguage",
    helpKey: "admin.help.checkerRequired",
  },
  {
    name: "checker_source",
    labelKey: "admin.label.tech.checkerSource",
    type: "textarea",
    rows: 8,
    helpKey: "admin.help.testlibInvocation",
  },
  { name: "source", labelKey: "admin.label.text.source" },
  { name: "source_url", labelKey: "admin.label.tech.sourceUrl" },
  { name: "is_public", labelKey: "admin.label.flag.public", type: "checkbox" },
];

const TOPIC_FIELDS: FieldDef[] = [
  {
    name: "slug",
    labelKey: "admin.label.text.slug",
    type: "slug",
    required: true,
    readonlyOnEdit: true,
  },
  { name: "name_uz", labelKey: "admin.label.name.uz", required: true },
  { name: "name_ru", labelKey: "admin.label.name.ru" },
  { name: "name_en", labelKey: "admin.label.name.en" },
  { name: "parent", labelKey: "admin.label.tech.parentTopic", helpKey: "admin.help.parentEmptyRoot" },
];

const input = FM_INP;

/** Masala testlari — S3 ga yuklanadi, DB da faqat havola (05-domain-model). */
function ProblemTestsPanel({
  problem,
  reload,
}: {
  problem: StaffProblem;
  reload: () => void;
}) {
  const locale = useLocale();
  const confirm = useConfirm();
  const path = `/staff/problems/${problem.slug}/tests/`;
  const [tests, setTests] = useState<StaffTestCase[]>([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [saved, setSaved] = useState(false);

  const load = useCallback(async () => {
    try {
      setTests(await staff.get<StaffTestCase[]>(path));
      setError("");
    } catch (e) {
      setError(
        e instanceof ApiError
          ? errorText(locale, e.code, e.message)
          : String(e),
      );
    }
  }, [path, locale]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void load();
  }, [load]);

  const nextOrder = tests.reduce((m, tc) => Math.max(m, tc.order), 0) + 1;

  async function upload(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const formEl = e.currentTarget;
    const form = new FormData(formEl);
    setBusy(true);
    setError("");
    setSaved(false);
    try {
      await staff.action(path, {
        order: Number(form.get("order")),
        input: String(form.get("input") ?? ""),
        expected: String(form.get("expected") ?? ""),
        is_sample: form.get("is_sample") === "on",
        points: Number(form.get("points") || 0),
      });
      formEl.reset();
      setSaved(true);
      await load();
      reload();
    } catch (err) {
      setError(
        err instanceof ApiError
          ? errorText(locale, err.code, err.message)
          : String(err),
      );
    } finally {
      setBusy(false);
    }
  }

  async function remove(tc: StaffTestCase) {
    if (!(await confirm(t(locale, "admin.confirmDelete"), { danger: true })))
      return;
    try {
      await staff.remove(`${path}${tc.order}/`);
      await load();
      reload();
    } catch (err) {
      setError(
        err instanceof ApiError
          ? errorText(locale, err.code, err.message)
          : String(err),
      );
    }
  }

  return (
    <div className="space-y-3">
      <p className="text-theme-xs rw-dim">
        {t(locale, "admin.help.testsStoredRemotely")}
      </p>

      {error && <Status status="bad" variant="alert" alert label={error} />}

      <table className="min-w-full text-left text-theme-xs">
        <thead className="rw-dim uppercase">
          <tr>
            <th className="px-2 py-1">#</th>
            <th className="px-2 py-1">{t(locale, "col.sample")}</th>
            <th className="px-2 py-1">{t(locale, "col.points")}</th>
            <th className="px-2 py-1">{t(locale, "col.input")}</th>
            <th className="px-2 py-1">{t(locale, "col.output")}</th>
            <th className="px-2 py-1 text-right">
              {t(locale, "admin.actions")}
            </th>
          </tr>
        </thead>
        <tbody className="divide-y rw-divide">
          {tests.map((tc) => (
            <tr key={tc.id}>
              <td className="px-2 py-1 font-medium">{tc.order}</td>
              <td className="px-2 py-1">
                {tc.is_sample ? <Badge>{t(locale, "admin.text.badgeSample")}</Badge> : "—"}
              </td>
              <td className="px-2 py-1">{tc.points}</td>
              <td className="px-2 py-1 font-mono rw-dim">{tc.input_ref}</td>
              <td className="px-2 py-1 font-mono rw-dim">{tc.output_ref}</td>
              <td className="px-2 py-1 text-right">
                <button
                  type="button"
                  onClick={() => remove(tc)}
                  className="rw-bad-ink hover:underline"
                >
                  {t(locale, "admin.delete")}
                </button>
              </td>
            </tr>
          ))}
          {tests.length === 0 && (
            <tr>
              <td colSpan={6} className="px-2 py-3 text-center rw-faint">
                {t(locale, "admin.text.noTestsYet")}
              </td>
            </tr>
          )}
        </tbody>
      </table>

      <form
        key={`${problem.slug}-${tests.length}`}
        onSubmit={upload}
        className="grid gap-3 md:grid-cols-2"
      >
        <p className="text-theme-sm font-medium rw-strong md:col-span-2">
          {t(locale, "admin.text.addTest")}
        </p>
        <label className="block">
          <span className="mb-1 block text-theme-xs rw-dim-2">
            {t(locale, "admin.text.orderNumber")}
          </span>
          <input
            name="order"
            type="number"
            min={1}
            required
            defaultValue={nextOrder}
            className={`${input} h-9`}
          />
        </label>
        <label className="block">
          <span className="mb-1 block text-theme-xs rw-dim-2">{t(locale, "col.points")}</span>
          <input
            name="points"
            type="number"
            min={0}
            defaultValue={0}
            className={`${input} h-9`}
          />
        </label>
        <label className="block">
          <span className="mb-1 block text-theme-xs rw-dim-2">
            Kirish (input)
          </span>
          <textarea
            name="input"
            rows={6}
            className={`${input} py-2 font-mono`}
            spellCheck={false}
          />
        </label>
        <label className="block">
          <span className="mb-1 block text-theme-xs rw-dim-2">
            Kutilgan chiqish (expected)
          </span>
          <textarea
            name="expected"
            rows={6}
            className={`${input} py-2 font-mono`}
            spellCheck={false}
          />
        </label>
        <FormCheck
          name="is_sample"
          label={t(locale, "admin.text.sampleTest")}
        />
        <div className="flex items-center justify-end gap-2">
          {saved && (
            <span className="text-theme-xs rw-ok-ink">
              {t(locale, "admin.saved")}
            </span>
          )}
          <Button type="submit" className="h-9" disabled={busy}>
            {t(locale, "admin.save")}
          </Button>
        </div>
      </form>
    </div>
  );
}

type StaffProblemLanguage = {
  language: string;
  language_name: string;
  time_limit_ms: number | null;
  memory_limit_kb: number | null;
  code_template: string;
  harness: string;
};

/** Per-language rows: limit overrides, editor template and — for a function
 *  problem — the harness (audit Q-12). The harness used to be editable only
 *  in the Django admin, which production does not route. */
function ProblemLanguagesPanel({ problem }: { problem: StaffProblem }) {
  const locale = useLocale();
  const confirm = useConfirm();
  const path = `/staff/problems/${problem.slug}/languages/`;
  const isFunction = problem.task_kind === "function";
  const [rows, setRows] = useState<StaffProblemLanguage[]>([]);
  const [catalogue, setCatalogue] = useState<Language[]>([]);
  const [editing, setEditing] = useState<StaffProblemLanguage | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [saved, setSaved] = useState(false);

  const fail = useCallback(
    (e: unknown) =>
      setError(e instanceof ApiError ? errorText(locale, e.code, e.message) : String(e)),
    [locale],
  );

  const load = useCallback(async () => {
    try {
      setRows(await staff.get<StaffProblemLanguage[]>(path));
      setError("");
    } catch (e) {
      fail(e);
    }
  }, [path, fail]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void load();
    api
      .languages()
      .then((page) => setCatalogue(page.results))
      .catch(() => setCatalogue([]));
  }, [load]);

  async function save(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const code = String(form.get("language") ?? "");
    if (!code) return;
    const number = (name: string) => {
      const raw = String(form.get(name) ?? "").trim();
      return raw ? Number(raw) : null;
    };
    setBusy(true);
    setError("");
    setSaved(false);
    try {
      await staff.put(`${path}${code}/`, {
        time_limit_ms: number("time_limit_ms"),
        memory_limit_kb: number("memory_limit_kb"),
        code_template: String(form.get("code_template") ?? ""),
        harness: isFunction ? String(form.get("harness") ?? "") : "",
      });
      setSaved(true);
      setEditing(null);
      await load();
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  }

  async function remove(row: StaffProblemLanguage) {
    if (!(await confirm(t(locale, "admin.confirmDelete"), { danger: true }))) return;
    try {
      await staff.remove(`${path}${row.language}/`);
      await load();
    } catch (err) {
      fail(err);
    }
  }

  const current = editing;
  return (
    <div className="space-y-3">
      <p className="text-theme-sm font-medium rw-strong">
        {t(locale, "admin.text.problemLanguages")}
      </p>
      <p className="text-theme-xs rw-dim">{t(locale, "admin.help.problemLanguages")}</p>
      {isFunction && (
        <p className="text-theme-xs rw-dim">
          {t(locale, "admin.help.harness")}{" "}
          <code className="font-mono">{"{{SOLUTION}}"}</code>
        </p>
      )}

      {error && <Status status="bad" variant="alert" alert label={error} />}

      <table className="min-w-full text-left text-theme-xs">
        <thead className="rw-dim uppercase">
          <tr>
            <th className="px-2 py-1">{t(locale, "admin.label.text.language")}</th>
            <th className="px-2 py-1">{t(locale, "admin.label.value.timeLimit")}</th>
            <th className="px-2 py-1">{t(locale, "admin.label.value.memoryLimit")}</th>
            <th className="px-2 py-1">{t(locale, "admin.text.harness")}</th>
            <th className="px-2 py-1 text-right">{t(locale, "admin.actions")}</th>
          </tr>
        </thead>
        <tbody className="divide-y rw-divide">
          {rows.map((row) => (
            <tr key={row.language}>
              <td className="px-2 py-1 font-medium">{row.language_name}</td>
              <td className="px-2 py-1 tabular-nums">{row.time_limit_ms ?? "—"}</td>
              <td className="px-2 py-1 tabular-nums">{row.memory_limit_kb ?? "—"}</td>
              <td className="px-2 py-1">{row.harness ? "✓" : "—"}</td>
              <td className="px-2 py-1 text-right">
                <button
                  type="button"
                  onClick={() => setEditing(row)}
                  className="mr-3 hover:underline"
                >
                  {t(locale, "admin.edit")}
                </button>
                <button
                  type="button"
                  onClick={() => remove(row)}
                  className="rw-bad-ink hover:underline"
                >
                  {t(locale, "admin.delete")}
                </button>
              </td>
            </tr>
          ))}
          {rows.length === 0 && (
            <tr>
              <td colSpan={5} className="px-2 py-3 text-center rw-faint">
                {t(locale, "admin.text.noLanguageRows")}
              </td>
            </tr>
          )}
        </tbody>
      </table>

      <form
        key={`${problem.slug}-${current?.language ?? "new"}-${rows.length}`}
        onSubmit={save}
        className="grid gap-3 md:grid-cols-3"
      >
        <label className="block">
          <span className="mb-1 block text-theme-xs rw-dim-2">
            {t(locale, "admin.label.text.language")}
          </span>
          <select
            name="language"
            required
            defaultValue={current?.language ?? ""}
            className={`${input} h-9`}
          >
            <option value="" disabled>
              —
            </option>
            {catalogue.map((lang) => (
              <option key={lang.code} value={lang.code}>
                {lang.name} {lang.version}
              </option>
            ))}
          </select>
        </label>
        <label className="block">
          <span className="mb-1 block text-theme-xs rw-dim-2">
            {t(locale, "admin.label.value.timeLimit")}
          </span>
          <input
            name="time_limit_ms"
            type="number"
            min={100}
            defaultValue={current?.time_limit_ms ?? ""}
            className={`${input} h-9`}
          />
        </label>
        <label className="block">
          <span className="mb-1 block text-theme-xs rw-dim-2">
            {t(locale, "admin.label.value.memoryLimit")}
          </span>
          <input
            name="memory_limit_kb"
            type="number"
            min={1024}
            defaultValue={current?.memory_limit_kb ?? ""}
            className={`${input} h-9`}
          />
        </label>
        <label className="block md:col-span-3">
          <span className="mb-1 block text-theme-xs rw-dim-2">
            {t(locale, "admin.text.codeTemplate")}
          </span>
          <textarea
            name="code_template"
            rows={5}
            defaultValue={current?.code_template ?? ""}
            className={`${input} py-2 font-mono`}
            spellCheck={false}
          />
        </label>
        {isFunction && (
          <label className="block md:col-span-3">
            <span className="mb-1 block text-theme-xs rw-dim-2">
              {t(locale, "admin.text.harness")}
            </span>
            <textarea
              name="harness"
              rows={10}
              required
              defaultValue={current?.harness ?? ""}
              className={`${input} py-2 font-mono`}
              spellCheck={false}
            />
          </label>
        )}
        <div className="flex items-center justify-end gap-2 md:col-span-3">
          {saved && (
            <span className="text-theme-xs rw-ok-ink">{t(locale, "admin.saved")}</span>
          )}
          {current && (
            <Button type="button" variant="outline" className="h-9" onClick={() => setEditing(null)}>
              {t(locale, "admin.cancel")}
            </Button>
          )}
          <Button type="submit" className="h-9" disabled={busy}>
            {t(locale, "admin.save")}
          </Button>
        </div>
      </form>
    </div>
  );
}

/** Review queue switch: every problem, or only the drafts whose author
 *  asked for a review (`/studio`, 2026-11-10). */
const QUEUE_FILTERS = [
  { review: false, key: "admin.filter.all" },
  { review: true, key: "admin.filter.reviewQueue" },
] as const;

export function ProblemsAdmin({ review: initialReview = false }: { review?: boolean }) {
  const locale = useLocale();
  const [review, setReview] = useState(initialReview);
  return (
    <div className="space-y-6">
      <div role="group" aria-label={t(locale, "admin.filter.reviewQueue")} className="flex flex-wrap gap-2">
        {QUEUE_FILTERS.map((filter) => (
          <Button
            key={filter.key}
            type="button"
            variant={review === filter.review ? "primary" : "outline"}
            aria-pressed={review === filter.review}
            onClick={() => {
              setReview(filter.review);
              // Keep the view in the address, so a reload shows the same list.
              const url = new URL(window.location.href);
              if (filter.review) url.searchParams.set("review", "1");
              else url.searchParams.delete("review");
              window.history.replaceState(null, "", url);
            }}
          >
            {t(locale, filter.key)}
          </Button>
        ))}
      </div>
      <CrudPage<StaffProblem>
        key={review ? "review" : "all"}
        title={t(locale, "admin.section.problems")}
        path="/staff/problems/"
        idField="slug"
        ordering="-pk"
        params={review ? { review: "1" } : undefined}
        columns={[
          {
            key: "code",
            labelKey: "admin.label.text.num",
            render: (p) =>
              p.code === null ? "—" : `#${String(p.code).padStart(4, "0")}`,
          },
          { key: "slug", labelKey: "admin.label.text.slug" },
          { key: "title", labelKey: "admin.label.text.title" },
          { key: "difficulty", labelKey: "admin.label.value.difficulty", align: "right" },
          {
            key: "topics",
            labelKey: "admin.label.misc.topics",
            render: (p) => (p.topics.length ? p.topics.join(", ") : "—"),
          },
          { key: "test_count", labelKey: "admin.label.misc.tests", align: "right" },
          {
            key: "authors",
            labelKey: "admin.label.misc.authors",
            render: (p) => (p.authors.length ? p.authors.map((name) => `@${name}`).join(", ") : "—"),
          },
          {
            key: "review_requested_at",
            labelKey: "admin.label.date.reviewRequested",
            render: (p) => (p.review_requested_at ? numericStamp(p.review_requested_at) : "—"),
          },
          {
            key: "is_public",
            labelKey: "admin.label.text.status",
            render: (p, _reload, locale) => (
              <Badge>
              {p.is_public
                ? t(locale, "admin.text.badgePublic")
                : t(locale, "admin.text.badgeHidden")}
            </Badge>
            ),
          },
        ]}
        fields={PROBLEM_FIELDS}
        toPayload={(values) => ({
          ...values,
          statement_locale: values.statement_locale || "uz",
          interactor_language: values.interactor_language || null,
          manager_language: values.manager_language || null,
          time_limit_ms: values.time_limit_ms ?? 1000,
          memory_limit_kb: values.memory_limit_kb ?? 262144,
        })}
        rowExtra={(p, reload) => (
          <div className="space-y-6">
            <ProblemTestsPanel problem={p} reload={reload} />
            <ProblemLanguagesPanel problem={p} />
            <div className="space-y-3">
              <p className="text-theme-sm font-medium rw-strong">
                {t(locale, "studio.tab.translations")}
              </p>
              <ProblemTranslations
                base={`/staff/problems/${encodeURIComponent(p.slug)}/`}
                baseLocale={p.statement_locale || "uz"}
              />
            </div>
          </div>
        )}
      />

      <CrudPage<StaffTopic>
        title={t(locale, "admin.title.topics")}
        path="/staff/topics/"
        idField="slug"
        ordering="slug"
        columns={[
          { key: "slug", labelKey: "admin.label.text.slug" },
          { key: "name_uz", labelKey: "admin.label.text.name" },
          { key: "parent", labelKey: "admin.label.tech.parent", render: (tp) => tp.parent ?? "—" },
        ]}
        fields={TOPIC_FIELDS}
        toPayload={(values) => ({ ...values, parent: values.parent || null })}
      />
    </div>
  );
}
