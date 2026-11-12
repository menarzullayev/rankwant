"use client";

import { numericDate } from "@rankwant/shared/format";
import Link from "next/link";
import { useCallback, useEffect, useId, useState } from "react";

import {
  CrudPage,
  type ColumnDef,
  type FieldDef,
} from "@/components/admin/CrudPage";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { Status } from "@/components/ui/Status";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t, type MessageKey } from "@/i18n/messages";
import type { components } from "@/lib/api/generated/schema";
import { staff } from "@/lib/staff";

type Budget = components["schemas"]["TutorBudget"];
type Report = components["schemas"]["StaffTutorReport"] & {
  [key: string]: unknown;
};

const REASON: Record<string, MessageKey> = {
  wrong: "tutor.report.wrong",
  solution: "tutor.report.solution",
  harmful: "tutor.report.harmful",
  other: "tutor.report.other",
};

const STATUS: Record<string, MessageKey> = {
  open: "admin.label.flag.open",
  accepted: "admin.label.status.accepted",
  rejected: "admin.label.status.rejectedShort",
};

/** Dollars at API prices: four decimals, since one reply is a fraction of a cent. */
function usd(value: string | number): string {
  return `$${Number(value).toFixed(4)}`;
}

/** This month's spend against the limit (decision ⑧). Every reply goes
 *  through `claude -p` today, so the number is what it would cost on the
 *  API — a measure, not a bill. */
function BudgetCard() {
  const locale = useLocale();
  const [data, setData] = useState<Budget | null>(null);
  const [limit, setLimit] = useState("");
  const [state, setState] = useState<"idle" | "saving" | "saved" | "failed">(
    "idle",
  );
  const inputId = useId();

  const load = useCallback(async () => {
    try {
      const next = await staff.get<Budget>("/staff/tutor/budget/");
      setData(next);
      setLimit(String(next.limit_usd));
    } catch {
      setState("failed");
    }
  }, []);

  useEffect(() => {
    let cancelled = false;
    staff.get<Budget>("/staff/tutor/budget/").then(
      (next) => {
        if (cancelled) return;
        setData(next);
        setLimit(String(next.limit_usd));
      },
      () => {
        if (!cancelled) setState("failed");
      },
    );
    return () => {
      cancelled = true;
    };
  }, []);

  async function save(event: React.FormEvent) {
    event.preventDefault();
    setState("saving");
    try {
      setData(
        await staff.update<Budget>("/staff/tutor/budget/", {
          limit_usd: limit,
        }),
      );
      setState("saved");
    } catch {
      setState("failed");
      await load();
    }
  }

  const share = data?.percent ?? null;
  return (
    <Card title={t(locale, "admin.tutor.budget")}>
      {!data ? (
        <p className="text-theme-sm rw-dim">
          {t(
            locale,
            state === "failed" ? "tutor.fail.other" : "tutor.thinking",
          )}
        </p>
      ) : (
        <div className="space-y-4">
          <dl className="grid grid-cols-2 gap-2 sm:grid-cols-4">
            {[
              [t(locale, "admin.tutor.month"), data.month],
              [t(locale, "admin.tutor.spent"), usd(data.spent_usd)],
              [t(locale, "admin.tutor.replies"), String(data.replies)],
              [
                t(locale, "admin.tutor.share"),
                share === null ? "—" : `${share.toFixed(1)}%`,
              ],
            ].map(([label, value]) => (
              <div key={label} className="rw-radius-sm rw-field-bg px-3 py-2">
                <dt className="text-theme-xs rw-faint">{label}</dt>
                <dd className="text-theme-sm font-medium rw-strong tabular-nums">
                  {value}
                </dd>
              </div>
            ))}
          </dl>
          {share !== null && (
            <div
              role="progressbar"
              aria-label={t(locale, "admin.tutor.share")}
              aria-valuemin={0}
              aria-valuemax={100}
              aria-valuenow={Math.min(100, Math.round(share))}
              className="h-2 overflow-hidden rw-radius-full rw-field-bg"
            >
              <div
                className={`h-full ${data.over ? "bg-[var(--rw-bad-ink)]" : data.warning ? "bg-[var(--rw-warn-ink)]" : "rw-accent-bg"}`}
                style={{ width: `${Math.min(100, share)}%` }}
              />
            </div>
          )}
          {data.over ? (
            <Status status="bad" label={t(locale, "admin.tutor.over")} />
          ) : data.warning ? (
            <Status status="warn" label={t(locale, "admin.tutor.warning")} />
          ) : null}
          <p className="text-theme-xs rw-faint">
            {t(locale, "admin.tutor.apiPrice")}
          </p>
          {data.by_model.length > 0 && (
            <ul className="space-y-1 text-theme-sm">
              {data.by_model.map((m) => (
                <li
                  key={m.model}
                  className="flex justify-between gap-3 tabular-nums"
                >
                  <span className="font-mono text-theme-xs rw-dim-2">
                    {m.model}
                  </span>
                  <span className="rw-strong">
                    {fill(t(locale, "admin.tutor.modelLine"), {
                      replies: m.replies,
                      spent: usd(m.spent_usd),
                    })}
                  </span>
                </li>
              ))}
            </ul>
          )}
          <form onSubmit={save} className="flex flex-wrap items-end gap-2">
            <div>
              <label htmlFor={inputId} className="block text-theme-xs rw-faint">
                {t(locale, "admin.tutor.limit")}
              </label>
              <input
                id={inputId}
                type="number"
                min={0}
                step={0.01}
                value={limit}
                onChange={(e) => setLimit(e.target.value)}
                className="min-h-11 w-40 rw-radius-sm border rw-line rw-field-bg px-3 text-theme-sm rw-strong tabular-nums rw-focus-ring"
              />
            </div>
            <button
              type="submit"
              disabled={state === "saving"}
              className="min-h-11 rw-radius-sm rw-accent-bg px-4 text-theme-sm font-semibold rw-btn-label rw-focus-ring disabled:opacity-50"
            >
              {t(locale, "admin.tutor.save")}
            </button>
            {state === "saved" && (
              <span role="status" className="text-theme-xs rw-ok-ink">
                {t(locale, "admin.tutor.saved")}
              </span>
            )}
          </form>
          <p className="text-theme-xs rw-faint">
            {t(locale, "admin.tutor.limitHint")}
          </p>
        </div>
      )}
    </Card>
  );
}

const columns: ColumnDef<Report>[] = [
  {
    key: "problem",
    labelKey: "admin.label.text.problem",
    render: (r) => (
      <Link
        href={`/problems/${r.problem}`}
        className="font-mono text-theme-xs rw-accent-ink hover:underline"
      >
        {r.problem}
      </Link>
    ),
  },
  {
    key: "reason",
    labelKey: "admin.label.text.reason",
    render: (r, _reload, locale) => (
      <Badge>{REASON[r.reason] ? t(locale, REASON[r.reason]) : r.reason}</Badge>
    ),
  },
  {
    key: "reply_text",
    labelKey: "admin.tutor.exchange",
    render: (r) => (
      <div className="max-w-xl space-y-1">
        {r.question_text && (
          <p className="line-clamp-2 rw-dim">{r.question_text}</p>
        )}
        <p
          title={r.reply_text}
          className="line-clamp-4 whitespace-pre-line rw-strong"
        >
          {r.reply_text}
        </p>
        {r.note && (
          <p className="line-clamp-2 text-theme-xs rw-faint">{r.note}</p>
        )}
      </div>
    ),
  },
  { key: "username", labelKey: "admin.label.text.who" },
  {
    key: "status",
    labelKey: "admin.label.text.status",
    render: (r, _reload, locale) => (
      <Badge
        color={
          r.status === "open"
            ? "warning"
            : r.status === "accepted"
              ? "success"
              : "neutral"
        }
      >
        {t(locale, STATUS[r.status ?? "open"] ?? "admin.label.flag.open")}
      </Badge>
    ),
  },
  {
    key: "created_at",
    labelKey: "admin.label.text.date",
    align: "right",
    render: (r) => (
      <span className="rw-faint tabular-nums">{numericDate(r.created_at)}</span>
    ),
  },
];

/** Only the status changes: the copied question and reply are the student's
 *  report (the API refuses to edit them). */
const fields: FieldDef[] = [
  {
    name: "status",
    labelKey: "admin.label.text.status",
    type: "select",
    required: true,
    options: (["open", "accepted", "rejected"] as const).map((value) => ({
      value,
      labelKey: STATUS[value],
    })),
  },
];

/** AI tutor (ADR-0065): the monthly budget and the reported replies — the
 *  only conversations staff see (decision ⑦). */
export function TutorAdmin() {
  const locale = useLocale();
  return (
    <div className="space-y-6">
      <BudgetCard />
      <CrudPage<Report>
        title={t(locale, "admin.tutor.reports")}
        path="/staff/tutor-reports/"
        columns={columns}
        fields={fields}
        canCreate={false}
        canDelete={false}
        fromItem={(r) => ({ status: r.status })}
      />
    </div>
  );
}
