"use client";

import { useState } from "react";

import {
  CrudPage,
  type ColumnDef,
  type FieldDef,
} from "@/components/admin/CrudPage";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { useLocale } from "@/i18n/LocaleProvider";
import { t, errorText } from "@/i18n/messages";
import { ApiError } from "@/lib/api";
import { staff } from "@/lib/staff";

type ArenaRow = {
  slug: string;
  title: string;
  description: string;
  start_at: string;
  end_at: string;
  seconds_per_question: number;
  reward_qvant: number;
  is_public: boolean;
  questions: number[];
  question_count: number;
  participant_count: number;
  is_running: boolean;
  is_finished: boolean;
  rewards_applied_at: string | null;
  created_at: string;
};

const PATH = "/staff/arena/";

const INPUT =
  "h-9 rw-radius-sm border rw-line rw-surface px-3 text-theme-sm outline-none " +
  "rw-focus-line rw-field-bg ";

function toLocalInput(iso: string): string {
  const d = new Date(iso);
  return new Date(d.getTime() - d.getTimezoneOffset() * 60_000)
    .toISOString()
    .slice(0, 16);
}

function fmt(iso: string | null): string {
  return iso ? new Date(iso).toLocaleString() : "—";
}

function statusOf(item: ArenaRow): {
  label: string;
  color: "success" | "warning" | "neutral";
} {
  if (item.is_running) return { label: "Yurmoqda", color: "success" };
  if (item.is_finished) return { label: "Tugagan", color: "neutral" };
  return { label: "Kutilmoqda", color: "warning" };
}

const COLUMNS: ColumnDef<ArenaRow>[] = [
  { key: "slug", label: "Slug" },
  { key: "title", label: "Nomi" },
  { key: "start_at", label: "Boshlanish", render: (i) => fmt(i.start_at) },
  { key: "seconds_per_question", label: "s/savol", align: "right" },
  { key: "question_count", label: "Savollar", align: "right" },
  { key: "participant_count", label: "Ishtirokchi", align: "right" },
  {
    key: "status",
    label: "Holat",
    render: (i) => {
      const s = statusOf(i);
      return (
        <span className="flex flex-wrap gap-1">
          <Badge color={s.color}>{s.label}</Badge>
          {!i.is_public && <Badge>yashirin</Badge>}
          {i.rewards_applied_at && <Badge color="info">mukofotlangan</Badge>}
        </span>
      );
    },
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
  {
    name: "start_at",
    label: "Boshlanish vaqti",
    type: "datetime",
    required: true,
  },
  {
    name: "seconds_per_question",
    label: "Savol uchun soniya",
    type: "number",
    min: 5,
    required: true,
  },
  {
    name: "reward_qvant",
    label: "Mukofot (Qvant)",
    type: "number",
    min: 0,
    required: true,
  },
  { name: "is_public", label: "Ommaviy", type: "checkbox" },
  { name: "description", label: "Tavsif", type: "textarea", rows: 4 },
];

/** Har raund uchun panel: savollar tartibi, qayta rejalashtirish, reset, finalize. */
function ArenaRowPanel({
  item,
  reload,
}: {
  item: ArenaRow;
  reload: () => void;
}) {
  const locale = useLocale();
  const [ids, setIds] = useState<number[]>(item.questions);
  const [newId, setNewId] = useState("");
  const [startAt, setStartAt] = useState(toLocalInput(item.start_at));
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const dirty = ids.join(",") !== item.questions.join(",");
  const base = `${PATH}${item.slug}/`;

  async function run(label: string, fn: () => Promise<unknown>) {
    setBusy(true);
    setError("");
    setMsg("");
    try {
      await fn();
      setMsg(label);
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

  function addId() {
    const n = Number(newId);
    if (!Number.isInteger(n) || n < 1) return;
    if (!ids.includes(n)) setIds([...ids, n]);
    setNewId("");
  }

  function move(index: number, delta: number) {
    const to = index + delta;
    if (to < 0 || to >= ids.length) return;
    const next = [...ids];
    [next[index], next[to]] = [next[to], next[index]];
    setIds(next);
  }

  return (
    <div className="grid gap-4 text-theme-sm md:grid-cols-2">
      <div>
        <p className="mb-2 font-medium rw-strong">
          {"Savollar (tartib bo'yicha)"} <Badge>{ids.length}</Badge>
        </p>
        <ol className="mb-2 space-y-1">
          {ids.map((id, i) => (
            <li key={id} className="flex items-center gap-2">
              <span className="w-6 text-right rw-faint">{i + 1}.</span>
              <span className="font-mono">#{id}</span>
              <button
                type="button"
                onClick={() => move(i, -1)}
                disabled={i === 0}
                className="rw-accent-ink disabled:opacity-30"
              >
                ↑
              </button>
              <button
                type="button"
                onClick={() => move(i, 1)}
                disabled={i === ids.length - 1}
                className="rw-accent-ink disabled:opacity-30"
              >
                ↓
              </button>
              <button
                type="button"
                onClick={() => setIds(ids.filter((x) => x !== id))}
                className="rw-bad-ink"
              >
                ✕
              </button>
            </li>
          ))}
          {ids.length === 0 && (
            <li className="rw-faint">{t(locale, "admin.noRows")}</li>
          )}
        </ol>
        <div className="flex gap-2">
          <input
            type="number"
            min={1}
            value={newId}
            onChange={(e) => setNewId(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                addId();
              }
            }}
            placeholder="Savol ID"
            className={`${INPUT} w-32`}
          />
          <Button
            type="button"
            variant="outline"
            className="h-9"
            onClick={addId}
          >
            {"Qo'shish"}
          </Button>
          <Button
            type="button"
            className="h-9"
            disabled={busy || !dirty}
            onClick={() =>
              run(t(locale, "admin.saved"), () =>
                staff.update(base, { questions: ids }),
              )
            }
          >
            {t(locale, "admin.save")}
          </Button>
        </div>
      </div>

      <div className="space-y-3">
        <div>
          <p className="mb-2 font-medium rw-strong">Qayta rejalashtirish</p>
          <div className="flex gap-2">
            <input
              type="datetime-local"
              value={startAt}
              onChange={(e) => setStartAt(e.target.value)}
              className={INPUT}
            />
            <Button
              type="button"
              className="h-9"
              disabled={busy || !startAt}
              onClick={() =>
                run("Vaqt yangilandi", () =>
                  staff.action(`${base}reschedule/`, {
                    start_at: new Date(startAt).toISOString(),
                  }),
                )
              }
            >
              Saqlash
            </Button>
          </div>
          <p className="mt-1 text-theme-xs rw-faint">
            Tugash: {fmt(item.end_at)} · Ishtirokchi: {item.participant_count} ·
            Mukofot: {fmt(item.rewards_applied_at)}
          </p>
        </div>

        <div className="flex flex-wrap gap-2">
          <Button
            type="button"
            variant="outline"
            className="h-9"
            disabled={busy}
            onClick={() => {
              if (
                !window.confirm(
                  "Ishtirokchilar va javoblar o'chiriladi. Davom etilsinmi?",
                )
              )
                return;
              void run("Raund tozalandi", () => staff.action(`${base}reset/`));
            }}
          >
            Reset
          </Button>
          <Button
            type="button"
            className="h-9"
            disabled={busy || !item.is_finished || !!item.rewards_applied_at}
            onClick={() =>
              run("Mukofotlar berildi", () => staff.action(`${base}finalize/`))
            }
          >
            Finalize
          </Button>
        </div>

        {msg && <p className="rw-ok-ink">{msg}</p>}
        {error && <p className="rw-bad-ink">{error}</p>}
      </div>
    </div>
  );
}

export function ArenaAdmin() {
  return (
    <CrudPage<ArenaRow>
      title="Arena"
      path={PATH}
      idField="slug"
      columns={COLUMNS}
      fields={FIELDS}
      ordering="-start_at"
      rowExtra={(item, reload) => (
        // key: reload'dan keyin yangi savollar/vaqt bilan panel qayta boshlanadi
        <ArenaRowPanel
          key={`${item.slug}:${item.start_at}:${item.questions.join(",")}`}
          item={item}
          reload={reload}
        />
      )}
    />
  );
}
