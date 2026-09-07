"use client";

import { useState } from "react";

import {
  CrudPage,
  type ColumnDef,
  type FieldDef,
} from "@/components/admin/CrudPage";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";
import { ApiError } from "@/lib/api";
import { staff } from "@/lib/staff";

type Stage = {
  order: number;
  title: string;
  contest: string;
  contest_title?: string;
  weight: number;
};

type Tournament = {
  slug: string;
  title: string;
  description: string;
  start_at: string;
  end_at: string;
  is_public: boolean;
  created_at: string;
  stages: Stage[];
  stage_count: number;
  [key: string]: unknown;
};

const PATH = "/staff/tournaments/";

const INPUT =
  "h-9 w-full rw-radius-sm border rw-line rw-surface px-2 text-theme-sm outline-none " +
  "rw-focus-line rw-field-bg ";

function fmt(iso: string): string {
  return new Date(iso).toLocaleString("uz-UZ", {
    dateStyle: "short",
    timeStyle: "short",
  });
}

const COLUMNS: ColumnDef<Tournament>[] = [
  {
    key: "slug",
    label: "Slug",
    render: (x) => <span className="font-mono">{x.slug}</span>,
  },
  { key: "title", label: "Nomi" },
  { key: "start_at", label: "Boshlanish", render: (x) => fmt(x.start_at) },
  { key: "end_at", label: "Tugash", render: (x) => fmt(x.end_at) },
  { key: "stage_count", label: "Bosqichlar", align: "right" },
  {
    key: "is_public",
    label: "Ochiq",
    render: (x) => (
      <Badge color={x.is_public ? "success" : "neutral"}>
        {x.is_public ? "ha" : "yo'q"}
      </Badge>
    ),
  },
];

const FIELDS: FieldDef[] = [
  {
    name: "slug",
    label: "Slug",
    type: "slug",
    required: true,
    readonlyOnEdit: true,
  },
  { name: "title", label: "Nomi", required: true },
  { name: "start_at", label: "Boshlanish", type: "datetime", required: true },
  { name: "end_at", label: "Tugash", type: "datetime", required: true },
  { name: "is_public", label: "Ochiq", type: "checkbox" },
  {
    name: "description",
    label: "Tavsif (Markdown)",
    type: "textarea",
    rows: 6,
  },
];

/** Bosqich muharriri — `stages` massivi PATCH bilan to'liq almashtiriladi. */
function StageEditor({
  item,
  reload,
}: {
  item: Tournament;
  reload: () => void;
}) {
  const locale = DEFAULT_LOCALE;
  const [stages, setStages] = useState<Stage[]>(() =>
    item.stages.map((s) => ({ ...s })),
  );
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<{ kind: "ok" | "err"; text: string } | null>(
    null,
  );

  function patch(i: number, changes: Partial<Stage>) {
    setStages((prev) =>
      prev.map((s, j) => (j === i ? { ...s, ...changes } : s)),
    );
  }

  function add() {
    const next = stages.reduce((m, s) => Math.max(m, s.order), 0) + 1;
    setStages((prev) => [
      ...prev,
      { order: next, title: "", contest: "", weight: 1 },
    ]);
  }

  async function save() {
    setBusy(true);
    setMsg(null);
    try {
      const payload = stages.map(({ order, title, contest, weight }) => ({
        order,
        title,
        contest: contest.trim(),
        weight,
      }));
      await staff.update(`${PATH}${item.slug}/`, { stages: payload });
      setMsg({ kind: "ok", text: t(locale, "admin.saved") });
      reload();
    } catch (e) {
      setMsg({
        kind: "err",
        text: e instanceof ApiError ? e.message : String(e),
      });
    } finally {
      setBusy(false);
    }
  }

  async function rebuild() {
    setBusy(true);
    setMsg(null);
    try {
      const r = await staff.action<{ participants: number }>(
        `${PATH}${item.slug}/rebuild/`,
      );
      setMsg({
        kind: "ok",
        text: `Jadval qayta hisoblandi — ishtirokchilar: ${r.participants}`,
      });
    } catch (e) {
      setMsg({
        kind: "err",
        text: e instanceof ApiError ? e.message : String(e),
      });
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-3">
      {msg && (
        <p
          className={`rw-radius-sm px-3 py-2 text-theme-sm ${
            msg.kind === "ok"
              ? "rw-ok-soft rw-ok-ink "
              : "rw-bad-soft rw-bad-ink "
          }`}
        >
          {msg.text}
        </p>
      )}

      <div className="grid grid-cols-[4rem_1fr_1fr_5rem_auto] gap-2 text-theme-xs font-medium rw-dim">
        <span>Tartib</span>
        <span>Nomi</span>
        <span>Contest slug</span>
        <span>Vazn</span>
        <span />
      </div>
      {stages.map((s, i) => (
        <div
          key={i}
          className="grid grid-cols-[4rem_1fr_1fr_5rem_auto] items-center gap-2"
        >
          <input
            type="number"
            min={1}
            value={s.order}
            onChange={(e) => patch(i, { order: Number(e.target.value) })}
            className={INPUT}
          />
          <input
            value={s.title}
            onChange={(e) => patch(i, { title: e.target.value })}
            placeholder="1-bosqich"
            className={INPUT}
          />
          <div>
            <input
              value={s.contest}
              onChange={(e) => patch(i, { contest: e.target.value })}
              placeholder="round-1"
              className={`${INPUT} font-mono`}
            />
            {s.contest_title && (
              <span className="mt-0.5 block text-theme-xs rw-faint">
                {s.contest_title}
              </span>
            )}
          </div>
          <input
            type="number"
            min={1}
            value={s.weight}
            onChange={(e) => patch(i, { weight: Number(e.target.value) })}
            className={INPUT}
          />
          <button
            type="button"
            onClick={() => setStages((prev) => prev.filter((_, j) => j !== i))}
            className="text-theme-xs rw-bad-ink hover:underline"
          >
            {t(locale, "admin.delete")}
          </button>
        </div>
      ))}
      {stages.length === 0 && (
        <p className="text-theme-xs rw-faint">
          {"Bosqichlar yo'q — contest qo'shing."}
        </p>
      )}

      <div className="flex flex-wrap gap-2">
        <Button
          type="button"
          variant="outline"
          className="h-9"
          onClick={add}
          disabled={busy}
        >
          + Bosqich
        </Button>
        <Button type="button" className="h-9" onClick={save} disabled={busy}>
          {t(locale, "admin.save")}
        </Button>
        <Button
          type="button"
          variant="outline"
          className="h-9"
          onClick={rebuild}
          disabled={busy}
        >
          Jadvalni qayta hisoblash
        </Button>
      </div>
    </div>
  );
}

export function TournamentsAdmin() {
  return (
    <CrudPage<Tournament>
      title="Chempionatlar"
      path={PATH}
      idField="slug"
      columns={COLUMNS}
      fields={FIELDS}
      ordering="-start_at"
      rowExtra={(item, reload) => (
        <StageEditor key={item.slug} item={item} reload={reload} />
      )}
    />
  );
}
