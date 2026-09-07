"use client";

import { useState } from "react";

import { CrudPage, type ColumnDef } from "@/components/admin/CrudPage";
import { Badge, type BadgeColor } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { DEFAULT_LOCALE } from "@/i18n/messages";
import { ApiError } from "@/lib/api";
import { staff } from "@/lib/staff";

type DuelStatus = "open" | "accepted" | "finished" | "cancelled";

type Duel = {
  id: number;
  slug: string;
  title: string;
  status: DuelStatus;
  challenger: string;
  opponent: string | null;
  problem_count: number;
  difficulty: number;
  duration_minutes: number;
  start_at: string;
  end_at: string;
  is_due: boolean;
  problems: string[];
  winner: string | null;
  challenger_solved: number;
  opponent_solved: number;
  is_draw: boolean;
  ratings_applied_at: string | null;
  created_at: string;
};

const STATUS: Record<DuelStatus, { label: string; color: BadgeColor }> = {
  open: { label: "Ochiq", color: "info" },
  accepted: { label: "Qabul qilindi", color: "brand" },
  finished: { label: "Tugadi", color: "success" },
  cancelled: { label: "Bekor qilindi", color: "neutral" },
};

function result(d: Duel): string {
  if (d.status !== "finished") return "—";
  const score = `${d.challenger_solved} : ${d.opponent_solved}`;
  return d.is_draw ? `Durang (${score})` : `${d.winner ?? "?"} (${score})`;
}

const COLUMNS: ColumnDef<Duel>[] = [
  { key: "title", label: "Nomi" },
  { key: "challenger", label: "Chaqiruvchi" },
  { key: "opponent", label: "Raqib", render: (d) => d.opponent ?? "—" },
  {
    key: "status",
    label: "Holat",
    render: (d) => (
      <Badge color={STATUS[d.status].color}>{STATUS[d.status].label}</Badge>
    ),
  },
  {
    key: "start_at",
    label: "Boshlanish",
    render: (d) => new Date(d.start_at).toLocaleString(DEFAULT_LOCALE),
  },
  { key: "result", label: "Natija", render: result },
];

/** Bekor qilish / yakunlash — ikkalasi ham tasdiq bilan. Muddati o'tmagan duel
 *  avval `not_due` bilan rad etiladi; keyin majburiy yakunlash alohida tasdiqlanadi. */
function DuelActions({ duel, reload }: { duel: Duel; reload: () => void }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function run(fn: () => Promise<unknown>) {
    setBusy(true);
    setError("");
    try {
      await fn();
      reload();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  function cancel() {
    if (
      !window.confirm(
        `«${duel.title}» bekor qilinsinmi? Ishtirokchilarga xabar boradi.`,
      )
    )
      return;
    void run(() => staff.action(`/staff/duels/${duel.slug}/cancel/`));
  }

  function finalize() {
    if (
      !window.confirm(
        `«${duel.title}» yakunlansinmi? Natija va reyting hisoblanadi.`,
      )
    )
      return;
    void run(async () => {
      try {
        await staff.action(`/staff/duels/${duel.slug}/finalize/`);
      } catch (e) {
        if (!(e instanceof ApiError && e.code === "not_due")) throw e;
        if (!window.confirm("Duel hali tugamagan. Majburan yakunlansinmi?"))
          return;
        await staff.action(`/staff/duels/${duel.slug}/finalize/`, {
          force: true,
        });
      }
    });
  }

  const canCancel = duel.status === "open" || duel.status === "accepted";
  const canFinalize = duel.status === "accepted";

  return (
    <div className="space-y-3 text-theme-sm">
      <dl className="grid gap-x-6 gap-y-1 text-gray-600 sm:grid-cols-2 lg:grid-cols-4 dark:text-gray-300">
        <div>
          <dt className="text-theme-xs text-gray-400">Slug</dt>
          <dd className="font-mono">{duel.slug}</dd>
        </div>
        <div>
          <dt className="text-theme-xs text-gray-400">Masalalar</dt>
          <dd>
            {duel.problems.length ? duel.problems.join(", ") : "—"} (
            {duel.problem_count} ta, ~{duel.difficulty})
          </dd>
        </div>
        <div>
          <dt className="text-theme-xs text-gray-400">Tugash</dt>
          <dd>
            {new Date(duel.end_at).toLocaleString(DEFAULT_LOCALE)} ·{" "}
            {duel.duration_minutes} daq
          </dd>
        </div>
        <div>
          <dt className="text-theme-xs text-gray-400">Reyting</dt>
          <dd>
            {duel.ratings_applied_at
              ? new Date(duel.ratings_applied_at).toLocaleString(DEFAULT_LOCALE)
              : "—"}
          </dd>
        </div>
      </dl>
      {(canCancel || canFinalize) && (
        <div className="flex flex-wrap gap-2">
          {canFinalize && (
            <Button className="h-9" disabled={busy} onClick={finalize}>
              {duel.is_due ? "Yakunlash" : "Majburan yakunlash"}
            </Button>
          )}
          {canCancel && (
            <Button
              className="h-9"
              variant="outline"
              disabled={busy}
              onClick={cancel}
            >
              Bekor qilish
            </Button>
          )}
        </div>
      )}
      {error && <p className="text-error-500">{error}</p>}
    </div>
  );
}

export function DuelsAdmin() {
  return (
    <CrudPage<Duel>
      title="Duellar"
      path="/staff/duels/"
      idField="slug"
      columns={COLUMNS}
      fields={[]}
      ordering="-created_at"
      readOnly
      canDelete={false}
      rowExtra={(duel, reload) => <DuelActions duel={duel} reload={reload} />}
    />
  );
}
