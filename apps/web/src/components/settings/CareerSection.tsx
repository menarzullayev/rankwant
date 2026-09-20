"use client";

import { useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Field } from "@/components/ui/Field";
import { useLocale } from "@/i18n/LocaleProvider";
import { t, type Locale } from "@/i18n/messages";
import { Icon } from "@/components/ui/Icon";
import { putJson, type Education, type WorkRow } from "@/lib/api";
import { Check, Loading, Select, Status, useAction, useLoad } from "./kit";

type CareerRow = Education | WorkRow;
type Column = { key: "organization" | "degree" | "company" | "title"; label: string };

function monthLabel(n: number, locale: Locale) {
  return new Intl.DateTimeFormat([locale, "uz"], { month: "long" }).format(
    new Date(Date.UTC(2020, n - 1, 1)),
  );
}

function RowsCard<T extends CareerRow>({
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
  const cell = (row: T, key: string) =>
    String((row as unknown as Record<string, unknown>)[key] ?? "");

  function patch(i: number, part: Partial<T>) {
    setEdited(rows.map((row, j) => (j === i ? { ...row, ...part } : row)));
  }

  async function save() {
    const filled = rows.filter((row) => cell(row, first).trim());
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
                  aria-label={`${t(locale, "settings.remove")}: ${cell(row, first)}`}
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
                      value={cell(row, column.key)}
                      onChange={(event) =>
                        patch(i, { [column.key]: event.target.value } as Partial<T>)
                      }
                      required={column.key === first}
                      maxLength={150}
                    />
                  ))}
                  <Field
                    label={t(locale, "settings.startYear")}
                    name={`${path}-${i}-start_year`}
                    type="number"
                    min={1950}
                    max={latest}
                    inputMode="numeric"
                    value={row.start_year ?? ""}
                    onChange={(event) =>
                      patch(i, {
                        start_year: event.target.value ? Number(event.target.value) : null,
                      } as Partial<T>)
                    }
                  />
                  <Select
                    label={t(locale, "settings.startMonth")}
                    name={`${path}-${i}-start_month`}
                    value={row.start_month ? String(row.start_month) : ""}
                    onChange={(next) =>
                      patch(i, {
                        start_month: next ? Number(next) : null,
                      } as Partial<T>)
                    }
                    options={[
                      { value: "", label: t(locale, "settings.notChosen") },
                      ...Array.from({ length: 12 }, (_, month) => ({
                        value: String(month + 1),
                        label: monthLabel(month + 1, locale),
                      })),
                    ]}
                  />
                  <Field
                    label={t(locale, "settings.endYear")}
                    name={`${path}-${i}-end_year`}
                    type="number"
                    min={1950}
                    max={latest}
                    inputMode="numeric"
                    value={row.current ? "" : (row.end_year ?? "")}
                    disabled={row.current}
                    onChange={(event) =>
                      patch(i, {
                        end_year: event.target.value ? Number(event.target.value) : null,
                      } as Partial<T>)
                    }
                  />
                  <Select
                    label={t(locale, "settings.endMonth")}
                    name={`${path}-${i}-end_month`}
                    value={row.current ? "" : row.end_month ? String(row.end_month) : ""}
                    disabled={row.current}
                    onChange={(next) =>
                      patch(i, {
                        end_month: next ? Number(next) : null,
                      } as Partial<T>)
                    }
                    options={[
                      { value: "", label: t(locale, "settings.notChosen") },
                      ...Array.from({ length: 12 }, (_, month) => ({
                        value: String(month + 1),
                        label: monthLabel(month + 1, locale),
                      })),
                    ]}
                  />
                  <div className="sm:col-span-2">
                    <Check
                      label={t(locale, "settings.toPresent")}
                      checked={row.current}
                      onChange={(event) =>
                        patch(i, {
                          current: event.target.checked,
                          ...(event.target.checked
                            ? { end_year: null, end_month: null }
                            : {}),
                        } as Partial<T>)
                      }
                    />
                  </div>
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
  return (
    <>
      <RowsCard<Education>
        title={t(locale, "settings.education")}
        path="/me/educations/"
        addLabel={t(locale, "settings.addEducation")}
        empty={{
          organization: "",
          degree: "",
          start_year: null,
          start_month: null,
          end_year: null,
          end_month: null,
          current: false,
        }}
        columns={[
          { key: "organization", label: t(locale, "settings.organization") },
          { key: "degree", label: t(locale, "settings.degree") },
        ]}
      />
      <RowsCard<WorkRow>
        title={t(locale, "settings.work")}
        path="/me/work/"
        addLabel={t(locale, "settings.addWork")}
        empty={{
          company: "",
          title: "",
          start_year: null,
          start_month: null,
          end_year: null,
          end_month: null,
          current: false,
        }}
        columns={[
          { key: "company", label: t(locale, "settings.company") },
          { key: "title", label: t(locale, "settings.position") },
        ]}
      />
    </>
  );
}
