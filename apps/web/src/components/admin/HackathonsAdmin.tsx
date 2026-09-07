"use client";

import { useCallback, useEffect, useState } from "react";

import {
  CrudPage,
  type ColumnDef,
  type FieldDef,
} from "@/components/admin/CrudPage";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import {
  EmptyRow,
  TBody,
  TD,
  TH,
  THead,
  TR,
  Table,
} from "@/components/ui/Table";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";
import { ApiError } from "@/lib/api";
import { staff } from "@/lib/staff";

type Hackathon = {
  slug: string;
  title: string;
  description: string;
  start_at: string;
  submission_deadline: string;
  end_at: string;
  is_public: boolean;
  created_at: string;
  submission_count: number;
  accepts_submissions: boolean;
  is_finished: boolean;
  [key: string]: unknown;
};

type Submission = {
  id: number;
  username: string;
  team_name: string;
  title: string;
  description: string;
  repo_url: string;
  demo_url: string;
  submitted_at: string;
  score: number | null;
  feedback: string;
  scored_by: string | null;
  scored_at: string | null;
};

const PATH = "/staff/hackathons/";

const FIELDS: FieldDef[] = [
  {
    name: "slug",
    label: "Slug",
    type: "slug",
    required: true,
    readonlyOnEdit: true,
  },
  { name: "title", label: "Sarlavha", type: "text", required: true },
  { name: "start_at", label: "Boshlanish", type: "datetime", required: true },
  {
    name: "submission_deadline",
    label: "Topshirish muddati",
    type: "datetime",
    required: true,
    help: "Shu vaqtdan keyin topshirish yopiladi va loyihalar hammaga ochiladi",
  },
  {
    name: "end_at",
    label: "Natijalar e'loni",
    type: "datetime",
    required: true,
  },
  { name: "is_public", label: "Ommaviy", type: "checkbox" },
  {
    name: "description",
    label: "Tavsif (Markdown)",
    type: "textarea",
    rows: 10,
    help: "Shartlar, mezonlar, sovrin",
  },
];

function fmt(iso: string): string {
  return new Date(iso).toLocaleString();
}

function status(h: Hackathon): {
  label: string;
  color: "success" | "warning" | "neutral" | "info";
} {
  if (h.is_finished) return { label: "Yakunlangan", color: "neutral" };
  if (h.accepts_submissions)
    return { label: "Topshirish ochiq", color: "success" };
  if (new Date(h.start_at) > new Date())
    return { label: "Kutilmoqda", color: "info" };
  return { label: "Baholanmoqda", color: "warning" };
}

const COLUMNS: ColumnDef<Hackathon>[] = [
  { key: "slug", label: "Slug" },
  { key: "title", label: "Sarlavha" },
  { key: "start_at", label: "Boshlanish", render: (h) => fmt(h.start_at) },
  {
    key: "submission_deadline",
    label: "Muddat",
    render: (h) => fmt(h.submission_deadline),
  },
  { key: "end_at", label: "Yakun", render: (h) => fmt(h.end_at) },
  {
    key: "status",
    label: "Holat",
    render: (h) => {
      const s = status(h);
      return <Badge color={s.color}>{s.label}</Badge>;
    },
  },
  {
    key: "is_public",
    label: "Ommaviy",
    render: (h) => (
      <Badge color={h.is_public ? "success" : "neutral"}>
        {h.is_public ? "ha" : "yo'q"}
      </Badge>
    ),
  },
  { key: "submission_count", label: "Loyihalar", align: "right" },
];

const INPUT =
  "h-9 rounded-lg border border-gray-200 bg-white px-2 text-theme-sm outline-none " +
  "focus:border-brand-400 dark:border-[#232936] dark:bg-[#0b0d12] dark:text-white/90";

/** Bitta loyiha uchun ball (0–100) + fikr formasi. */
function ScoreForm({
  slug,
  entry,
  onSaved,
}: {
  slug: string;
  entry: Submission;
  onSaved: () => Promise<void>;
}) {
  const locale = DEFAULT_LOCALE;
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);

  async function submit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setBusy(true);
    setError("");
    setSaved(false);
    const form = new FormData(e.currentTarget);
    try {
      await staff.action(`${PATH}${slug}/submissions/${entry.id}/score/`, {
        score: Number(form.get("score")),
        feedback: String(form.get("feedback") ?? ""),
      });
      setSaved(true);
      await onSaved();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={submit} className="flex flex-wrap items-center gap-2">
      <input
        name="score"
        type="number"
        min={0}
        max={100}
        required
        defaultValue={entry.score ?? ""}
        placeholder="0–100"
        className={`${INPUT} w-20`}
      />
      <input
        name="feedback"
        type="text"
        defaultValue={entry.feedback}
        placeholder="Fikr"
        className={`${INPUT} w-48`}
      />
      <Button type="submit" disabled={busy} className="h-9 px-3">
        {t(locale, "admin.save")}
      </Button>
      {saved && <Badge color="success">{t(locale, "admin.saved")}</Badge>}
      {error && <span className="text-theme-xs text-error-500">{error}</span>}
    </form>
  );
}

/** Hakatonning BARCHA loyihalari (muddatdan qat'i nazar) + har qatorda baholash. */
function SubmissionsPanel({
  slug,
  reload,
}: {
  slug: string;
  reload: () => void;
}) {
  const locale = DEFAULT_LOCALE;
  const [rows, setRows] = useState<Submission[]>([]);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    try {
      const data = await staff.get<{ results: Submission[] }>(
        `${PATH}${slug}/submissions/`,
      );
      setRows(data.results);
      setError("");
    } catch (e) {
      setError(e instanceof ApiError ? e.message : String(e));
    }
  }, [slug]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void load();
  }, [load]);

  async function onSaved() {
    await load();
    reload(); // ota jadvaldagi hisoblagichlar yangilansin
  }

  return (
    <div className="space-y-2">
      {error && <p className="text-theme-xs text-error-500">{error}</p>}
      <Table>
        <THead>
          <TH>Foydalanuvchi</TH>
          <TH>Jamoa</TH>
          <TH>Loyiha</TH>
          <TH>Havolalar</TH>
          <TH align="right">Ball</TH>
          <TH>Baholash</TH>
        </THead>
        <TBody>
          {rows.map((s) => (
            <TR key={s.id}>
              <TD>@{s.username}</TD>
              <TD>{s.team_name || "—"}</TD>
              <TD>
                <span className="font-medium text-gray-800 dark:text-white/90">
                  {s.title}
                </span>
                <span className="block text-theme-xs text-gray-400">
                  {fmt(s.submitted_at)}
                </span>
              </TD>
              <TD>
                <span className="flex gap-3 text-theme-xs">
                  <a
                    href={s.repo_url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-brand-500 hover:underline"
                  >
                    repo
                  </a>
                  {s.demo_url && (
                    <a
                      href={s.demo_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-brand-500 hover:underline"
                    >
                      demo
                    </a>
                  )}
                </span>
              </TD>
              <TD align="right">
                {s.score === null ? (
                  <Badge>—</Badge>
                ) : (
                  <span title={s.scored_by ? `@${s.scored_by}` : undefined}>
                    <Badge color="brand">{s.score}/100</Badge>
                  </span>
                )}
              </TD>
              <TD>
                <ScoreForm slug={slug} entry={s} onSaved={onSaved} />
              </TD>
            </TR>
          ))}
          {rows.length === 0 && (
            <EmptyRow colSpan={6}>{t(locale, "admin.noRows")}</EmptyRow>
          )}
        </TBody>
      </Table>
    </div>
  );
}

export function HackathonsAdmin() {
  return (
    <CrudPage<Hackathon>
      title="Hakatonlar"
      path={PATH}
      idField="slug"
      columns={COLUMNS}
      fields={FIELDS}
      ordering="-start_at"
      rowExtra={(h, reload) => (
        <SubmissionsPanel slug={h.slug} reload={reload} />
      )}
    />
  );
}
