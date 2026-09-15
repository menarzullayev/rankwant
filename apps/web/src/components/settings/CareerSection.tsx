"use client";

import { useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Field } from "@/components/ui/Field";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { Icon } from "@/components/ui/Icon";
import { putJson, type Education, type WorkRow } from "@/lib/api";
import { Loading, Status, useAction, useLoad } from "./kit";

type Value = string | number | null;
type Column = { key: string; label: string; year?: boolean; hint?: string };

/** Ta'lim va ish joyi — bir xil «qatorlar ro'yxati»: qo'shish, o'chirish
 *  va hammasini birga saqlash (API ham butun ro'yxatni almashtiradi). */
function RowsCard<T extends Record<string, Value>>({
  title,
  path,
  columns,
  empty,
  addLabel,
}: {
  title: string;
  path: string;
  columns: Column[];
  empty: T;
  addLabel: string;
}) {
  const locale = useLocale();
  const loaded = useLoad<T[]>(path);
  const action = useAction();
  const [edited, setEdited] = useState<T[] | null>(null);
  const rows = edited ?? loaded.data ?? [];
  const first = columns[0].key;
  const latest = new Date().getFullYear() + 10;

  function change(i: number, column: Column, raw: string) {
    const value: Value = column.year ? (raw ? Number(raw) : null) : raw;
    setEdited(rows.map((row, j) => (j === i ? { ...row, [column.key]: value } : row)));
  }

  async function save() {
    // Nomi bo'sh qator — qo'shilib to'ldirilmay qolgani, uni yubormaymiz.
    const filled = rows.filter((row) => String(row[first] ?? "").trim());
    await action.run(async () => {
      loaded.setData(await putJson<T[]>(path, filled));
      setEdited(null);
    });
  }

  return (
    <Card title={title}>
      {!loaded.data && !loaded.error ? (
        <Loading />
      ) : (
        <>
          <ul className="space-y-4">
            {rows.map((row, i) => (
              <li key={i} className="relative rw-radius border rw-line p-4 pr-12">
                <button
                  type="button"
                  onClick={() => setEdited(rows.filter((_, j) => j !== i))}
                  aria-label={`${t(locale, "settings.remove")}: ${String(row[first] ?? "")}`}
                  className="absolute right-2 top-2 flex size-8 items-center justify-center rw-radius-sm rw-dim transition rw-hover-bg rw-focus-ring"
                >
                  <Icon name="nav.close" className="size-4" />
                </button>
                <div className="grid gap-3 sm:grid-cols-2">
                  {columns.map((column) => (
                    <Field
                      key={column.key}
                      label={column.label}
                      name={`${path}-${i}-${column.key}`}
                      value={row[column.key] === null ? "" : String(row[column.key])}
                      onChange={(event) => change(i, column, event.target.value)}
                      hint={column.hint}
                      required={column.key === first}
                      {...(column.year
                        ? { type: "number", min: 1950, max: latest, inputMode: "numeric" as const }
                        : { maxLength: 150 })}
                    />
                  ))}
                </div>
              </li>
            ))}
          </ul>
          <div className="mt-4 flex flex-wrap items-center gap-3">
            {rows.length < 20 && (
              <Button variant="outline" onClick={() => setEdited([...rows, { ...empty }])}>
                {addLabel}
              </Button>
            )}
            <Button busy={action.busy} disabled={edited === null} onClick={save}>
              {t(locale, "settings.save")}
            </Button>
            <Status error={action.error || loaded.error} done={action.done} />
          </div>
        </>
      )}
    </Card>
  );
}

export function CareerSection() {
  const locale = useLocale();
  const years: Column[] = [
    { key: "start_year", label: t(locale, "settings.startYear"), year: true },
    {
      key: "end_year",
      label: t(locale, "settings.endYear"),
      year: true,
      hint: t(locale, "settings.endYearHint"),
    },
  ];
  return (
    <>
      <RowsCard<Education>
        title={t(locale, "settings.education")}
        path="/me/educations/"
        addLabel={t(locale, "settings.addEducation")}
        empty={{ organization: "", degree: "", start_year: null, end_year: null }}
        columns={[
          { key: "organization", label: t(locale, "settings.organization") },
          { key: "degree", label: t(locale, "settings.degree") },
          ...years,
        ]}
      />
      <RowsCard<WorkRow>
        title={t(locale, "settings.work")}
        path="/me/work/"
        addLabel={t(locale, "settings.addWork")}
        empty={{ company: "", title: "", start_year: null, end_year: null }}
        columns={[
          { key: "company", label: t(locale, "settings.company") },
          { key: "title", label: t(locale, "settings.position") },
          ...years,
        ]}
      />
    </>
  );
}
