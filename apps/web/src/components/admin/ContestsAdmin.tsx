"use client";

import { useState } from "react";

import {
  type ColumnDef,
  CrudPage,
  type FieldDef,
} from "@/components/admin/CrudPage";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";
import { ApiError } from "@/lib/api";
import { staff, staffFetch } from "@/lib/staff";

type ContestProblemRow = {
  problem: string;
  index_letter: string;
  points: number;
  title?: string;
};

type ContestRow = {
  slug: string;
  title: string;
  description: string;
  start_at: string;
  end_at: string;
  freeze_minutes: number;
  scoring_type: "acm" | "ioi";
  is_rated: boolean;
  is_virtual: boolean;
  is_public: boolean;
  mirror_of: string | null;
  ratings_applied_at: string | null;
  problems: ContestProblemRow[];
  is_running: boolean;
  is_finished: boolean;
  [key: string]: unknown;
};

const PATH = "/staff/contests/";

const FIELDS: FieldDef[] = [
  {
    name: "slug",
    label: "Slug",
    type: "slug",
    required: true,
    readonlyOnEdit: true,
  },
  { name: "title", label: "Sarlavha", required: true },
  { name: "start_at", label: "Boshlanish", type: "datetime", required: true },
  { name: "end_at", label: "Tugash", type: "datetime", required: true },
  {
    name: "freeze_minutes",
    label: "Muzlatish (daqiqa)",
    type: "number",
    min: 0,
    help: "Oxirgi N daqiqada standings yangilanmaydi",
  },
  {
    name: "scoring_type",
    label: "Hisoblash",
    type: "select",
    required: true,
    options: [
      { value: "acm", label: "ACM/ICPC" },
      { value: "ioi", label: "IOI" },
    ],
  },
  { name: "mirror_of", label: "Ko'zgu (asl musobaqa slug'i)", type: "slug" },
  { name: "is_rated", label: "Reytingli", type: "checkbox" },
  { name: "is_virtual", label: "Virtual", type: "checkbox" },
  { name: "is_public", label: "Ommaviy", type: "checkbox" },
  {
    name: "description",
    label: "Tavsif (Markdown)",
    type: "textarea",
    rows: 6,
  },
];

function fmt(iso: string): string {
  return new Date(iso).toLocaleString();
}

const COLUMNS: ColumnDef<ContestRow>[] = [
  {
    key: "slug",
    label: "Slug",
    render: (c) => <span className="font-mono">{c.slug}</span>,
  },
  { key: "title", label: "Sarlavha" },
  { key: "start_at", label: "Boshlanish", render: (c) => fmt(c.start_at) },
  { key: "end_at", label: "Tugash", render: (c) => fmt(c.end_at) },
  {
    key: "scoring_type",
    label: "Hisob",
    render: (c) => <Badge color="info">{c.scoring_type.toUpperCase()}</Badge>,
  },
  {
    key: "state",
    label: "Holat",
    render: (c) => (
      <div className="flex flex-wrap gap-1">
        {c.is_running && <Badge color="success">jonli</Badge>}
        {c.is_finished && <Badge>tugagan</Badge>}
        {c.is_rated && <Badge color="brand">reytingli</Badge>}
        {!c.is_public && <Badge color="warning">yopiq</Badge>}
        {c.mirror_of && <Badge color="info">{`ko'zgu: ${c.mirror_of}`}</Badge>}
        {c.ratings_applied_at && <Badge color="success">yakunlangan</Badge>}
      </div>
    ),
  },
  {
    key: "problems",
    label: "Masalalar",
    align: "right",
    render: (c) => c.problems.length,
  },
];

const INPUT =
  "h-9 rw-radius-sm border rw-line rw-surface px-2 text-theme-sm outline-none " +
  "rw-focus-line rw-field-bg ";

/** Qator paneli: masalalar ro'yxati (to'liq almashtiriladi) + amallar. */
function ContestRowPanel({
  contest,
  reload,
}: {
  contest: ContestRow;
  reload: () => void;
}) {
  const locale = DEFAULT_LOCALE;
  const [rows, setRows] = useState<ContestProblemRow[]>(() =>
    contest.problems.map((p) => ({ ...p })),
  );
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);

  function update(i: number, patch: Partial<ContestProblemRow>) {
    setRows((prev) => prev.map((r, j) => (j === i ? { ...r, ...patch } : r)));
  }

  function nextLetter(): string {
    const used = new Set(rows.map((r) => r.index_letter));
    for (let code = 65; code <= 90; code += 1) {
      const letter = String.fromCharCode(code);
      if (!used.has(letter)) return letter;
    }
    return "";
  }

  async function run(label: string, fn: () => Promise<string>) {
    setBusy(true);
    setMsg(null);
    try {
      const text = await fn();
      setMsg({ ok: true, text: `${label}: ${text}` });
      reload();
    } catch (e) {
      setMsg({
        ok: false,
        text: e instanceof ApiError ? e.message : String(e),
      });
    } finally {
      setBusy(false);
    }
  }

  const saveProblems = () =>
    run(t(locale, "admin.saved"), async () => {
      const saved = await staffFetch<ContestProblemRow[]>(
        "PUT",
        `${PATH}${contest.slug}/problems/`,
        rows.map((r) => ({
          problem: r.problem.trim(),
          index_letter: r.index_letter.trim().toUpperCase(),
          points: r.points,
        })),
      );
      setRows(saved);
      return `${saved.length} ta masala`;
    });

  const rebuild = () =>
    run("Standings qayta qurildi", async () => {
      const res = await staff.action<{ rows: number }>(
        `${PATH}${contest.slug}/rebuild-standings/`,
      );
      return `${res.rows} ta qator`;
    });

  const finalize = () => {
    if (
      !window.confirm(
        "Musobaqa yakunlansinmi? Reyting qo'llanadi va qaytarib bo'lmaydi.",
      )
    ) {
      return;
    }
    return run("Yakunlandi", async () => {
      const res = await staff.action<{
        affected: number;
        ratings_applied_at: string | null;
      }>(`${PATH}${contest.slug}/finalize/`);
      if (!res.ratings_applied_at)
        return "musobaqa hali tugamagan — hech narsa qilinmadi";
      return `${res.affected} ta ishtirokchi reytingi yangilandi`;
    });
  };

  return (
    <div className="space-y-4">
      <div>
        <p className="mb-2 text-theme-xs font-medium rw-dim-2 uppercase">
          Masalalar
        </p>
        <div className="space-y-2">
          {rows.map((r, i) => (
            <div key={i} className="flex flex-wrap items-center gap-2">
              <input
                value={r.index_letter}
                onChange={(e) => update(i, { index_letter: e.target.value })}
                placeholder="A"
                maxLength={3}
                className={`${INPUT} w-16 font-mono uppercase`}
              />
              <input
                value={r.problem}
                onChange={(e) => update(i, { problem: e.target.value })}
                placeholder="masala slug'i"
                className={`${INPUT} w-64 font-mono`}
              />
              <input
                type="number"
                value={r.points}
                min={0}
                onChange={(e) => update(i, { points: Number(e.target.value) })}
                className={`${INPUT} w-24`}
                title="Ball"
              />
              {r.title && (
                <span className="text-theme-xs rw-faint">{r.title}</span>
              )}
              <button
                type="button"
                onClick={() =>
                  setRows((prev) => prev.filter((_, j) => j !== i))
                }
                className="text-theme-xs rw-bad-ink hover:underline"
              >
                {t(locale, "admin.delete")}
              </button>
            </div>
          ))}
          {rows.length === 0 && (
            <p className="text-theme-xs rw-faint">
              {t(locale, "admin.noRows")}
            </p>
          )}
        </div>
        <div className="mt-3 flex flex-wrap gap-2">
          <Button
            type="button"
            variant="outline"
            className="h-9"
            onClick={() =>
              setRows((prev) => [
                ...prev,
                { problem: "", index_letter: nextLetter(), points: 100 },
              ])
            }
          >
            + Masala
          </Button>
          <Button
            type="button"
            className="h-9"
            disabled={busy}
            onClick={saveProblems}
          >
            {t(locale, "admin.save")}
          </Button>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2 border-t rw-line pt-3">
        <Button
          type="button"
          variant="outline"
          className="h-9"
          disabled={busy}
          onClick={rebuild}
        >
          Standings qayta qurish
        </Button>
        <Button
          type="button"
          variant="outline"
          className="h-9"
          disabled={busy || !!contest.ratings_applied_at}
          onClick={finalize}
          title={
            contest.ratings_applied_at
              ? `Yakunlangan: ${fmt(contest.ratings_applied_at)}`
              : ""
          }
        >
          Yakunlash (reyting)
        </Button>
        {msg && (
          <span
            className={`text-theme-xs ${msg.ok ? "rw-ok-ink " : "rw-bad-ink "}`}
          >
            {msg.text}
          </span>
        )}
      </div>
    </div>
  );
}

export function ContestsAdmin() {
  return (
    <CrudPage<ContestRow>
      title="Musobaqalar"
      path={PATH}
      idField="slug"
      columns={COLUMNS}
      fields={FIELDS}
      ordering="-start_at"
      toPayload={(values) => ({
        ...values,
        mirror_of: values.mirror_of ? String(values.mirror_of).trim() : null,
        freeze_minutes: values.freeze_minutes ?? 0,
      })}
      rowExtra={(item, reload) => (
        <ContestRowPanel
          key={`${item.slug}-${item.problems.length}`}
          contest={item}
          reload={reload}
        />
      )}
    />
  );
}
