"use client";

import { useCallback, useEffect, useState } from "react";

import { FM_INP } from "@/components/form/chrome";
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
import { useLocale } from "@/i18n/LocaleProvider";
import { dateTime, t, type Locale, type MessageKey, errorText } from "@/i18n/messages";
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
    labelKey: "admin.label.text.slug",
    type: "slug",
    required: true,
    readonlyOnEdit: true,
  },
  { name: "title", labelKey: "admin.label.text.title", type: "text", required: true },
  { name: "start_at", labelKey: "admin.label.date.start", type: "datetime", required: true },
  {
    name: "submission_deadline",
    labelKey: "admin.label.date.deadline",
    type: "datetime",
    required: true,
    helpKey: "admin.help.submissionClose",
  },
  {
    name: "end_at",
    labelKey: "admin.label.flag.resultsAnnounced",
    type: "datetime",
    required: true,
  },
  { name: "is_public", labelKey: "admin.label.flag.public", type: "checkbox" },
  {
    name: "description",
    labelKey: "admin.label.text.descriptionMarkdown",
    type: "textarea",
    rows: 10,
    helpKey: "admin.help.rulesAndPrizes",
  },
];

function fmt(iso: string, locale: Locale): string {
  return dateTime(iso, locale);
}

function status(h: Hackathon): {
  labelKey: MessageKey;
  color: "success" | "warning" | "neutral" | "info";
} {
  if (h.is_finished) return { labelKey: "admin.label.status.completed", color: "neutral" };
  if (h.accepts_submissions)
    return { labelKey: "admin.label.flag.submissionsOpen", color: "success" };
  if (new Date(h.start_at) > new Date())
    return { labelKey: "admin.label.status.pending", color: "info" };
  return { labelKey: "admin.label.status.evaluating", color: "warning" };
}

const COLUMNS: ColumnDef<Hackathon>[] = [
  { key: "slug", labelKey: "admin.label.text.slug" },
  { key: "title", labelKey: "admin.label.text.title" },
  { key: "start_at", labelKey: "admin.label.date.start", render: (h, _reload, locale) => fmt(h.start_at, locale) },
  {
    key: "submission_deadline",
    labelKey: "admin.label.text.deadline",
    render: (h, _reload, locale) => fmt(h.submission_deadline, locale),
  },
  { key: "end_at", labelKey: "admin.label.text.end", render: (h, _reload, locale) => fmt(h.end_at, locale) },
  {
    key: "status",
    labelKey: "admin.label.text.status",
    render: (h, _reload, locale) => {
      const s = status(h);
      return <Badge color={s.color}>{t(locale, s.labelKey)}</Badge>;
    },
  },
  {
    key: "is_public",
    labelKey: "admin.label.flag.public",
    render: (h, _reload, locale) => (
      <Badge color={h.is_public ? "success" : "neutral"}>
        {h.is_public ? t(locale, "admin.text.yes") : t(locale, "admin.text.no")}
      </Badge>
    ),
  },
  { key: "submission_count", labelKey: "admin.label.misc.projects", align: "right" },
];

const INPUT = FM_INP;

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
  const locale = useLocale();
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
      setError(
        err instanceof ApiError
          ? errorText(locale, err.code, err.message)
          : String(err),
      );
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
        placeholder={t(locale, "admin.placeholder.comment")}
        className={`${INPUT} w-48`}
      />
      <Button type="submit" disabled={busy} className="h-9 px-3">
        {t(locale, "admin.save")}
      </Button>
      {saved && <Badge color="success">{t(locale, "admin.saved")}</Badge>}
      {error && <span className="text-theme-xs rw-bad-ink">{error}</span>}
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
  const locale = useLocale();
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
      setError(
        e instanceof ApiError
          ? errorText(locale, e.code, e.message)
          : String(e),
      );
    }
  }, [slug, locale]);

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
      {error && <p className="text-theme-xs rw-bad-ink">{error}</p>}
      <Table>
        <THead>
          <TH>{t(locale, "standings.user")}</TH>
          <TH>{t(locale, "nav.team")}</TH>
          <TH>{t(locale, "col.project")}</TH>
          <TH>{t(locale, "col.links")}</TH>
          <TH align="right">{t(locale, "col.points")}</TH>
          <TH>{t(locale, "col.score")}</TH>
        </THead>
        <TBody>
          {rows.map((s) => (
            <TR key={s.id}>
              <TD>@{s.username}</TD>
              <TD>{s.team_name || "—"}</TD>
              <TD>
                <span className="font-medium rw-strong">{s.title}</span>
                <span className="block text-theme-xs rw-faint">
                  {fmt(s.submitted_at, locale)}
                </span>
              </TD>
              <TD>
                <span className="flex gap-3 text-theme-xs">
                  <a
                    href={s.repo_url}
                    target="_blank"
                    rel="noreferrer"
                    className="rw-accent-ink hover:underline"
                  >
                    {t(locale, "admin.text.badgeRepo")}
                  </a>
                  {s.demo_url && (
                    <a
                      href={s.demo_url}
                      target="_blank"
                      rel="noreferrer"
                      className="rw-accent-ink hover:underline"
                    >
                      {t(locale, "admin.text.badgeDemo")}
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
  const locale = useLocale();
  return (
    <CrudPage<Hackathon>
      title={t(locale, "admin.title.hackathons")}
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
