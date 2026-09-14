"use client";

import { useCallback, useEffect, useState } from "react";

import { CrudPage, type FieldDef } from "@/components/admin/CrudPage";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { useLocale } from "@/i18n/LocaleProvider";
import { t, errorText } from "@/i18n/messages";
import { ApiError } from "@/lib/api";
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
    helpKey: "admin.help.twoLetterDefaultUz",
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

const input =
  "w-full rw-radius-sm border rw-line rw-surface px-3 text-theme-sm outline-none " +
  "rw-focus-line rw-field-bg ";

/** Masala testlari — S3 ga yuklanadi, DB da faqat havola (05-domain-model). */
function ProblemTestsPanel({
  problem,
  reload,
}: {
  problem: StaffProblem;
  reload: () => void;
}) {
  const locale = useLocale();
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
    if (!window.confirm(t(locale, "admin.confirmDelete"))) return;
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
        Judge testlarni DB dan emas, S3 dan o&apos;qiydi: matn yuklanganda{" "}
        <code>tests/{problem.slug}/&lt;order&gt;.in/.out</code> sifatida
        saqlanadi, bu yerda faqat havola ko&apos;rinadi. Bir xil tartib raqami
        qayta yuklansa — ustiga yoziladi.
      </p>

      {error && (
        <p className="rw-radius-sm rw-bad-soft px-3 py-2 text-theme-sm rw-bad-ink">
          {error}
        </p>
      )}

      <table className="min-w-full text-left text-theme-xs">
        <thead className="rw-dim uppercase">
          <tr>
            <th className="px-2 py-1">#</th>
            <th className="px-2 py-1">Namuna</th>
            <th className="px-2 py-1">Ball</th>
            <th className="px-2 py-1">Kirish</th>
            <th className="px-2 py-1">Chiqish</th>
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
                Hali test yo&apos;q — yechimlar tekshirilmaydi.
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
          Test qo&apos;shish
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
          <span className="mb-1 block text-theme-xs rw-dim-2">Ball</span>
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
        <label className="flex items-center gap-2 text-theme-xs rw-dim-2">
          <input name="is_sample" type="checkbox" className="size-4" />
          Namuna test (shartda ko&apos;rsatiladi)
        </label>
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

export function ProblemsAdmin() {
  const locale = useLocale();
  return (
    <div className="space-y-6">
      <CrudPage<StaffProblem>
        title={t(locale, "admin.section.problems")}
        path="/staff/problems/"
        idField="slug"
        ordering="-pk"
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
          time_limit_ms: values.time_limit_ms ?? 1000,
          memory_limit_kb: values.memory_limit_kb ?? 262144,
        })}
        rowExtra={(p, reload) => (
          <ProblemTestsPanel problem={p} reload={reload} />
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
