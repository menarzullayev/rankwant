"use client";

import { useState } from "react";

import { CrudPage, type FieldDef } from "@/components/admin/CrudPage";
import { Badge, DifficultyBadge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { useLocale } from "@/i18n/LocaleProvider";
import { DEFAULT_LOCALE, t, errorText } from "@/i18n/messages";
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

const KIND_LABEL: Record<Article["kind"], string> = {
  article: "Maqola",
  algorithm: "Algoritm",
};

const ROLES: { value: ProblemLink["role"]; label: string }[] = [
  { value: "practice", label: "Mashq uchun" },
  { value: "example", label: "Maqoladagi misol" },
  { value: "editorial", label: "Yechim tushuntirishi" },
];

const FIELDS: FieldDef[] = [
  {
    name: "slug",
    label: "Slug",
    type: "slug",
    required: true,
    readonlyOnEdit: true,
  },
  {
    name: "kind",
    label: "Turi",
    type: "select",
    required: true,
    options: [
      { value: "article", label: "Maqola" },
      { value: "algorithm", label: "Algoritm" },
    ],
  },
  { name: "title", label: "Sarlavha", type: "text", required: true },
  { name: "locale", label: "Til", type: "text", help: "uz / ru / en" },
  { name: "summary", label: "Qisqacha", type: "text" },
  {
    name: "difficulty",
    label: "Qiyinlik",
    type: "number",
    min: 800,
    max: 3500,
    step: 100,
  },
  {
    name: "topics",
    label: "Mavzular",
    type: "list",
    help: "Topic sluglari, vergul bilan",
  },
  {
    name: "reading_minutes",
    label: "O'qish (daqiqa)",
    type: "number",
    min: 0,
    help: "0 = avtomatik",
  },
  {
    name: "body",
    label: "Matn (Markdown + LaTeX)",
    type: "textarea",
    required: true,
    rows: 14,
  },
  { name: "is_published", label: "Nashr qilingan", type: "checkbox" },
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
        {"Bog'langan masalalar"}
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
            title="Tartib"
          />
          <input
            value={l.problem}
            placeholder="masala slugi"
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
                {r.label}
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
          + Masala
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
      title="Maqolalar"
      path="/staff/articles/"
      idField="slug"
      ordering="-updated_at"
      columns={[
        {
          key: "slug",
          label: "Slug",
          render: (a) => <span className="font-mono">{a.slug}</span>,
        },
        {
          key: "kind",
          label: "Turi",
          render: (a) => (
            <Badge color={a.kind === "algorithm" ? "info" : "neutral"}>
              {KIND_LABEL[a.kind]}
            </Badge>
          ),
        },
        { key: "title", label: "Sarlavha" },
        {
          key: "difficulty",
          label: "Qiyinlik",
          render: (a) => <DifficultyBadge value={a.difficulty} />,
        },
        { key: "locale", label: "Til" },
        { key: "problem_count", label: "Masalalar", align: "right" },
        {
          key: "is_published",
          label: "Holat",
          render: (a) => (
            <Badge color={a.is_published ? "success" : "warning"}>
              {a.is_published ? "Nashr" : "Qoralama"}
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
