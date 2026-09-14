"use client";

import { useState } from "react";

import { CrudPage, type FieldDef } from "@/components/admin/CrudPage";
import { Badge, DifficultyBadge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { useLocale } from "@/i18n/LocaleProvider";
import { DEFAULT_LOCALE, t, type MessageKey, errorText } from "@/i18n/messages";
import { ApiError } from "@/lib/api";
import { staff } from "@/lib/staff";

type ProblemLink = {
  problem: string;
  role: "practice" | "example" | "editorial";
  order: number;
};

type Article = {
  slug: string;
  kind: "article" | "algorithm";
  title: string;
  summary: string;
  body: string;
  locale: string;
  difficulty: number;
  topics: string[];
  is_published: boolean;
  reading_minutes: number;
  problems: ProblemLink[];
  problem_count: number;
  author: string | null;
  published_at: string | null;
  [key: string]: unknown;
};

const KIND_LABEL: Record<Article["kind"], MessageKey> = {
  article: "admin.label.text.article",
  algorithm: "admin.label.text.problemExample",
};

const ROLES: { value: ProblemLink["role"]; labelKey: MessageKey }[] = [
  { value: "practice", labelKey: "admin.label.text.problemTraining" },
  { value: "example", labelKey: "admin.label.text.articleExample" },
  { value: "editorial", labelKey: "admin.label.text.solutionExplanation" },
];

const FIELDS: FieldDef[] = [
  {
    name: "slug",
    labelKey: "admin.label.text.slug",
    type: "slug",
    required: true,
    readonlyOnEdit: true,
  },
  {
    name: "kind",
    labelKey: "admin.label.text.kind",
    type: "select",
    required: true,
    options: [
      { value: "article", labelKey: "admin.label.text.article" },
      { value: "algorithm", labelKey: "admin.label.text.problemExample" },
    ],
  },
  { name: "title", labelKey: "admin.label.text.title", type: "text", required: true },
  { name: "locale", labelKey: "admin.label.text.language", type: "text", helpKey: "admin.help.languageCodes" },
  { name: "summary", labelKey: "admin.label.text.summary", type: "text" },
  {
    name: "difficulty",
    labelKey: "admin.label.value.difficulty",
    type: "number",
    min: 800,
    max: 3500,
    step: 100,
  },
  {
    name: "topics",
    labelKey: "admin.label.misc.topics",
    type: "list",
    helpKey: "admin.help.topicsSlug",
  },
  {
    name: "reading_minutes",
    labelKey: "admin.label.duration.readMin",
    type: "number",
    min: 0,
    helpKey: "admin.help.zeroAuto",
  },
  {
    name: "body",
    labelKey: "admin.label.text.markdownLatex",
    type: "textarea",
    required: true,
    rows: 14,
  },
  { name: "is_published", labelKey: "admin.label.flag.published", type: "checkbox" },
];

const input =
  "h-9 rw-radius-sm border rw-line rw-surface px-2 text-theme-sm outline-none " +
  "rw-focus-line rw-field-bg ";

/** Maqola ↔ masala bog'lanishlari — PATCH `problems` butun ro'yxatni almashtiradi. */
function ProblemLinksEditor({
  article,
  reload,
}: {
  article: Article;
  reload: () => void;
}) {
  const locale = useLocale();
  const [links, setLinks] = useState<ProblemLink[]>(article.problems ?? []);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);
  const [busy, setBusy] = useState(false);

  function patch(i: number, change: Partial<ProblemLink>) {
    setLinks((prev) => prev.map((l, j) => (j === i ? { ...l, ...change } : l)));
    setSaved(false);
  }

  async function save() {
    setBusy(true);
    setError("");
    try {
      const data = await staff.update<Article>(
        `/staff/articles/${article.slug}/`,
        { problems: links },
      );
      setLinks(data.problems);
      setSaved(true);
      reload();
    } catch (e) {
      setError(
        e instanceof ApiError
          ? errorText(locale, e.code, e.message)
          : String(e),
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-2">
      <p className="text-theme-xs font-medium rw-dim uppercase">
        {t(locale, "admin.text.linkedProblems")}
      </p>
      {error && <p className="text-theme-xs rw-bad-ink">{error}</p>}
      {links.map((l, i) => (
        <div key={i} className="flex flex-wrap items-center gap-2">
          <input
            value={l.order}
            type="number"
            min={0}
            onChange={(e) => patch(i, { order: Number(e.target.value) })}
            className={`${input} w-16`}
            title={t(locale, "admin.title.order")}
          />
          <input
            value={l.problem}
            placeholder={t(locale, "admin.placeholder.problemSlug")}
            onChange={(e) => patch(i, { problem: e.target.value })}
            className={`${input} w-48 font-mono`}
          />
          <select
            value={l.role}
            onChange={(e) =>
              patch(i, { role: e.target.value as ProblemLink["role"] })
            }
            className={input}
          >
            {ROLES.map((r) => (
              <option key={r.value} value={r.value}>
                {t(locale, r.labelKey)}
              </option>
            ))}
          </select>
          <button
            type="button"
            onClick={() => {
              setLinks((prev) => prev.filter((_, j) => j !== i));
              setSaved(false);
            }}
            className="text-theme-xs rw-bad-ink hover:underline"
          >
            {t(locale, "admin.delete")}
          </button>
        </div>
      ))}
      <div className="flex items-center gap-2">
        <Button
          type="button"
          variant="outline"
          className="h-9"
          onClick={() => {
            setLinks((prev) => [
              ...prev,
              { problem: "", role: "practice", order: prev.length + 1 },
            ]);
            setSaved(false);
          }}
        >
          {t(locale, "admin.text.addProblem")}
        </Button>
        <Button type="button" className="h-9" disabled={busy} onClick={save}>
          {t(locale, "admin.save")}
        </Button>
        {saved && (
          <span className="text-theme-xs rw-ok-ink">
            {t(locale, "admin.saved")}
          </span>
        )}
      </div>
    </div>
  );
}

export function ArticlesAdmin() {
  const locale = useLocale();
  return (
    <CrudPage<Article>
      title={t(locale, "admin.section.articles")}
      path="/staff/articles/"
      idField="slug"
      ordering="-updated_at"
      columns={[
        {
          key: "slug",
          labelKey: "admin.label.text.slug",
          render: (a) => <span className="font-mono">{a.slug}</span>,
        },
        {
          key: "kind",
          labelKey: "admin.label.text.kind",
          render: (a) => (
            <Badge color={a.kind === "algorithm" ? "info" : "neutral"}>
              {t(locale, KIND_LABEL[a.kind])}
            </Badge>
          ),
        },
        { key: "title", labelKey: "admin.label.text.title" },
        {
          key: "difficulty",
          labelKey: "admin.label.value.difficulty",
          render: (a) => <DifficultyBadge value={a.difficulty} />,
        },
        { key: "locale", labelKey: "admin.label.text.language" },
        { key: "problem_count", labelKey: "admin.label.misc.problems", align: "right" },
        {
          key: "is_published",
          labelKey: "admin.label.text.status",
          render: (a) => (
            <Badge color={a.is_published ? "success" : "warning"}>
              {a.is_published ? t(locale, "admin.text.publish") : t(locale, "admin.label.status.draft")}
            </Badge>
          ),
        },
      ]}
      fields={FIELDS}
      toPayload={(values) => ({
        ...values,
        // bo'sh raqam → model defaultlari (800, avtomatik hisob)
        difficulty: values.difficulty ?? 800,
        reading_minutes: values.reading_minutes ?? 0,
        locale: values.locale || "uz",
      })}
      rowExtra={(item, reload) => (
        <ProblemLinksEditor key={item.slug} article={item} reload={reload} />
      )}
    />
  );
}
