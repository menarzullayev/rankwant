"use client";

import { useState } from "react";

import { CrudPage, type FieldDef } from "@/components/admin/CrudPage";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";
import { ApiError } from "@/lib/api";
import { staff } from "@/lib/staff";

type Step = {
  order: number;
  title: string;
  article: string | null;
  problem: string | null;
  is_optional: boolean;
};

type Roadmap = {
  slug: string;
  title: string;
  description: string;
  locale: string;
  is_published: boolean;
  order: number;
  steps: Step[];
  step_count: number;
  [key: string]: unknown;
};

const FIELDS: FieldDef[] = [
  {
    name: "slug",
    label: "Slug",
    type: "slug",
    required: true,
    readonlyOnEdit: true,
  },
  { name: "title", label: "Sarlavha", type: "text", required: true },
  { name: "locale", label: "Til", type: "text", help: "uz / ru / en" },
  { name: "order", label: "Tartib", type: "number", min: 0 },
  { name: "description", label: "Tavsif", type: "textarea", rows: 4 },
  { name: "is_published", label: "Nashr qilingan", type: "checkbox" },
];

const input =
  "h-9 rw-radius-sm border rw-line rw-surface px-2 text-theme-sm outline-none " +
  "rw-focus-line rw-field-bg ";

/** Roadmap qadamlari — PATCH `steps` butun ro'yxatni almashtiradi.
 * Har qadamda maqola YOKI masala bo'lishi shart (server tekshiradi). */
function StepsEditor({
  roadmap,
  reload,
}: {
  roadmap: Roadmap;
  reload: () => void;
}) {
  const [steps, setSteps] = useState<Step[]>(roadmap.steps ?? []);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);
  const [busy, setBusy] = useState(false);

  function patch(i: number, change: Partial<Step>) {
    setSteps((prev) => prev.map((s, j) => (j === i ? { ...s, ...change } : s)));
    setSaved(false);
  }

  async function save() {
    setBusy(true);
    setError("");
    try {
      const payload = steps.map((s) => ({
        ...s,
        article: s.article?.trim() || null,
        problem: s.problem?.trim() || null,
      }));
      const data = await staff.update<Roadmap>(
        `/staff/roadmaps/${roadmap.slug}/`,
        { steps: payload },
      );
      setSteps(data.steps);
      setSaved(true);
      reload();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-2">
      <p className="text-theme-xs font-medium rw-dim uppercase">Qadamlar</p>
      {error && <p className="text-theme-xs rw-bad-ink">{error}</p>}
      {steps.map((s, i) => (
        <div key={i} className="flex flex-wrap items-center gap-2">
          <input
            value={s.order}
            type="number"
            min={0}
            onChange={(e) => patch(i, { order: Number(e.target.value) })}
            className={`${input} w-16`}
            title="Tartib"
          />
          <input
            value={s.title}
            placeholder="sarlavha"
            onChange={(e) => patch(i, { title: e.target.value })}
            className={`${input} w-44`}
          />
          <input
            value={s.article ?? ""}
            placeholder="maqola slugi"
            onChange={(e) => patch(i, { article: e.target.value })}
            className={`${input} w-40 font-mono`}
          />
          <input
            value={s.problem ?? ""}
            placeholder="masala slugi"
            onChange={(e) => patch(i, { problem: e.target.value })}
            className={`${input} w-40 font-mono`}
          />
          <label className="flex items-center gap-1 text-theme-xs rw-dim">
            <input
              type="checkbox"
              checked={s.is_optional}
              onChange={(e) => patch(i, { is_optional: e.target.checked })}
              className="size-4"
            />
            ixtiyoriy
          </label>
          <button
            type="button"
            onClick={() => {
              setSteps((prev) => prev.filter((_, j) => j !== i));
              setSaved(false);
            }}
            className="text-theme-xs rw-bad-ink hover:underline"
          >
            {t(DEFAULT_LOCALE, "admin.delete")}
          </button>
        </div>
      ))}
      <div className="flex items-center gap-2">
        <Button
          type="button"
          variant="outline"
          className="h-9"
          onClick={() => {
            setSteps((prev) => [
              ...prev,
              {
                order: prev.reduce((m, s) => Math.max(m, s.order), 0) + 1,
                title: "",
                article: null,
                problem: null,
                is_optional: false,
              },
            ]);
            setSaved(false);
          }}
        >
          + Qadam
        </Button>
        <Button type="button" className="h-9" disabled={busy} onClick={save}>
          {t(DEFAULT_LOCALE, "admin.save")}
        </Button>
        {saved && (
          <span className="text-theme-xs rw-ok-ink">
            {t(DEFAULT_LOCALE, "admin.saved")}
          </span>
        )}
      </div>
    </div>
  );
}

export function RoadmapsAdmin() {
  return (
    <CrudPage<Roadmap>
      title="Traektoriya"
      path="/staff/roadmaps/"
      idField="slug"
      columns={[
        { key: "order", label: "#", align: "right" },
        {
          key: "slug",
          label: "Slug",
          render: (r) => <span className="font-mono">{r.slug}</span>,
        },
        { key: "title", label: "Sarlavha" },
        { key: "locale", label: "Til" },
        { key: "step_count", label: "Qadamlar", align: "right" },
        {
          key: "is_published",
          label: "Holat",
          render: (r) => (
            <Badge color={r.is_published ? "success" : "warning"}>
              {r.is_published ? "Nashr" : "Qoralama"}
            </Badge>
          ),
        },
      ]}
      fields={FIELDS}
      toPayload={(values) => ({
        ...values,
        order: values.order ?? 0,
        locale: values.locale || "uz",
      })}
      rowExtra={(item, reload) => (
        <StepsEditor key={item.slug} roadmap={item} reload={reload} />
      )}
    />
  );
}
