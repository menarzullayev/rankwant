"use client";

import { useState } from "react";
import { useLocale } from "@/i18n/LocaleProvider";

import { FormCheck } from "@/components/form/FormKit";
import { FM_INP } from "@/components/form/chrome";
import { CrudPage, type FieldDef } from "@/components/admin/CrudPage";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { t, errorText } from "@/i18n/messages";
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
    labelKey: "admin.label.text.slug",
    type: "slug",
    required: true,
    readonlyOnEdit: true,
  },
  { name: "title", labelKey: "admin.label.text.title", type: "text", required: true },
  { name: "locale", labelKey: "admin.label.text.language", type: "text", helpKey: "admin.help.languageCodes" },
  { name: "order", labelKey: "admin.label.text.order", type: "number", min: 0 },
  { name: "description", labelKey: "admin.label.text.description", type: "textarea", rows: 4 },
  { name: "is_published", labelKey: "admin.label.flag.published", type: "checkbox" },
];

const input = FM_INP;

/** Roadmap qadamlari — PATCH `steps` butun ro'yxatni almashtiradi.
 * Har qadamda maqola YOKI masala bo'lishi shart (server tekshiradi). */
function StepsEditor({
  roadmap,
  reload,
}: {
  roadmap: Roadmap;
  reload: () => void;
}) {
  const locale = useLocale();
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
      <p className="text-theme-xs font-medium rw-dim uppercase">{t(locale, "admin.label.misc.steps")}</p>
      {error && <p className="text-theme-xs rw-bad-ink">{error}</p>}
      {steps.map((s, i) => (
        <div key={i} className="flex flex-wrap items-center gap-2">
          <input
            value={s.order}
            type="number"
            min={0}
            onChange={(e) => patch(i, { order: Number(e.target.value) })}
            className={`${input} w-16`}
            title={t(locale, "admin.title.order")}
          />
          <input
            value={s.title}
            placeholder="sarlavha"
            onChange={(e) => patch(i, { title: e.target.value })}
            className={`${input} w-44`}
          />
          <input
            value={s.article ?? ""}
            placeholder={t(locale, "admin.placeholder.articleSlug")}
            onChange={(e) => patch(i, { article: e.target.value })}
            className={`${input} w-40 font-mono`}
          />
          <input
            value={s.problem ?? ""}
            placeholder={t(locale, "admin.placeholder.problemSlug")}
            onChange={(e) => patch(i, { problem: e.target.value })}
            className={`${input} w-40 font-mono`}
          />
          <FormCheck
            checked={s.is_optional}
            onChange={(e) => patch(i, { is_optional: e.target.checked })}
            label={t(locale, "admin.text.badgeOptional")}
          />
          <button
            type="button"
            onClick={() => {
              setSteps((prev) => prev.filter((_, j) => j !== i));
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
          {t(locale, "admin.text.addStep")}
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

export function RoadmapsAdmin() {
  const locale = useLocale();
  return (
    <CrudPage<Roadmap>
      title={t(locale, "admin.section.roadmaps")}
      path="/staff/roadmaps/"
      idField="slug"
      columns={[
        { key: "order", labelKey: "admin.label.text.num", align: "right" },
        {
          key: "slug",
          labelKey: "admin.label.text.slug",
          render: (r) => <span className="font-mono">{r.slug}</span>,
        },
        { key: "title", labelKey: "admin.label.text.title" },
        { key: "locale", labelKey: "admin.label.text.language" },
        { key: "step_count", labelKey: "admin.label.misc.steps", align: "right" },
        {
          key: "is_published",
          labelKey: "admin.label.text.status",
          render: (r) => (
            <Badge color={r.is_published ? "success" : "warning"}>
              {r.is_published ? t(locale, "admin.text.publish") : t(locale, "admin.label.status.draft")}
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
