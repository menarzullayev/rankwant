"use client";

import { Fragment, useCallback, useEffect, useState } from "react";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Dropdown } from "@/components/ui/Dropdown";
import { Status } from "@/components/ui/Status";
import {
  EmptyRow,
  TBody,
  TD,
  TH,
  THead,
  TR,
  Table,
} from "@/components/ui/Table";
import { useConfirm } from "@/components/overlay/OverlayHost";
import { useLocale } from "@/i18n/LocaleProvider";
import { type Locale, type MessageKey } from "@/i18n/messages";
import { t, errorText } from "@/i18n/messages";
import { ApiError } from "@/lib/api";
import { staff } from "@/lib/staff";

export type FieldType =
  | "text"
  | "slug"
  | "textarea"
  | "number"
  | "checkbox"
  | "datetime"
  | "select"
  | "list"; // vergul bilan ajratilgan → string[]

export type FieldDef = {
  name: string;
  /** ⚠️ Kalit, matn emas. Maydonlar modul darajasidagi massivda turadi,
   *  ya'ni `t()` chaqira olmaydi — tarjima `CrudPage` ichida bo'ladi.
   *  Majburiy `MessageKey` bo'lgani uchun TypeScript o'tkazib yuborilgan
   *  satrni darhol tutadi. */
  labelKey: MessageKey;
  type?: FieldType;
  required?: boolean;
  helpKey?: MessageKey;
  options?: { value: string; labelKey: MessageKey }[];
  /** Tahrirda o'zgartirib bo'lmaydi (masalan slug) */
  readonlyOnEdit?: boolean;
  rows?: number;
  step?: number;
  min?: number;
  max?: number;
};

export type ColumnDef<T> = {
  key: string;
  /** Kalit, matn emas — yuqoridagi sabab bilan. */
  labelKey: MessageKey;
  align?: "left" | "right";
  /** `reload` — amal bajargan ustunlar jadvalni yangilay olishi uchun.
   *  `locale` — ustun modul darajasidagi massivda turadi, ya'ni hook
   *  chaqira olmaydi; sanani va matnni shu til bo'yicha chiqarish uchun
   *  kerak (avval `toLocaleDateString("uz")` qattiq yozilgan edi). */
  render?: (item: T, reload: () => void, locale: Locale) => React.ReactNode;
};

type Row = Record<string, unknown>;

/** Combobox o'z `label`ini chizadi — tashqi `<label>` ichiga tiqib
 *  bo'lmaydi. `check_hardcoded` ternary literalini matn deb o'qiydi. */
const FIELD_WRAP = { select: "div", field: "label" } as const;

/** `core.pagination.StandardPagination` bilan bir xil bo'lishi shart. */
const PAGE_SIZE = 25;

export type CrudPageProps<T extends Row> = {
  title: string;
  /** Staff API bazasi, masalan "/staff/problems/" */
  path: string;
  idField?: string;
  columns: ColumnDef<T>[];
  fields: FieldDef[];
  searchable?: boolean;
  ordering?: string;
  /** Har qatorda ko'rsatiladigan qo'shimcha amallar/panel (masalan testlar) */
  rowExtra?: (item: T, reload: () => void) => React.ReactNode;
  /** Payload'ni yuborishdan oldin o'zgartirish */
  toPayload?: (values: Row, editing: T | null) => Row;
  /** Elementdan forma qiymatlariga */
  fromItem?: (item: T) => Row;
  /** Yaratish/tahrirlash o'chirilgan bo'lsa (masalan duel nazorati) */
  readOnly?: boolean;
  canDelete?: boolean;
  /** Yozuv faqat tashqaridan tug'iladi (masalan foydalanuvchi xabari) —
   *  xodim uni tahrirlaydi, lekin yaratmaydi. */
  canCreate?: boolean;
};

function toLocalInput(iso: unknown): string {
  if (!iso || typeof iso !== "string") return "";
  const d = new Date(iso);
  return new Date(d.getTime() - d.getTimezoneOffset() * 60_000)
    .toISOString()
    .slice(0, 16);
}

export function CrudPage<T extends Row>({
  title,
  path,
  idField = "id",
  columns,
  fields,
  searchable = true,
  ordering,
  rowExtra,
  toPayload,
  fromItem,
  readOnly = false,
  canDelete = true,
  canCreate = true,
}: CrudPageProps<T>) {
  const locale = useLocale();
  const confirm = useConfirm();
  const [rows, setRows] = useState<T[]>([]);
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);
  const [q, setQ] = useState("");
  const [editing, setEditing] = useState<T | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [expanded, setExpanded] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const params: Record<string, string | number> = { page };
      if (q) params.search = q;
      if (ordering) params.ordering = ordering;
      const data = await staff.list<T>(path, params);
      setRows(data.results);
      setCount(data.count);
      setError("");
    } catch (e) {
      setError(
        e instanceof ApiError
          ? errorText(locale, e.code, e.message)
          : String(e),
      );
    }
  }, [path, page, q, ordering, locale]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void load();
  }, [load]);

  function idOf(item: T): string {
    return String(item[idField]);
  }

  function initialValues(item: T | null): Row {
    if (!item)
      return Object.fromEntries(
        fields.map((f) => [f.name, f.type === "checkbox" ? false : ""]),
      );
    if (fromItem) return fromItem(item);
    const v: Row = {};
    for (const f of fields) {
      const raw = item[f.name];
      if (f.type === "datetime") v[f.name] = toLocalInput(raw);
      else if (f.type === "list")
        v[f.name] = Array.isArray(raw) ? raw.join(", ") : "";
      else v[f.name] = raw ?? (f.type === "checkbox" ? false : "");
    }
    return v;
  }

  async function submit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setBusy(true);
    setError("");
    const form = new FormData(e.currentTarget);
    const values: Row = {};
    for (const f of fields) {
      if (editing && f.readonlyOnEdit) continue;
      const raw = form.get(f.name);
      switch (f.type) {
        case "checkbox":
          values[f.name] = form.get(f.name) === "on";
          break;
        case "number":
          values[f.name] = raw === "" || raw === null ? null : Number(raw);
          break;
        case "datetime":
          values[f.name] = raw ? new Date(String(raw)).toISOString() : null;
          break;
        case "list":
          values[f.name] = String(raw ?? "")
            .split(",")
            .map((s) => s.trim())
            .filter(Boolean);
          break;
        default:
          values[f.name] = raw ?? "";
      }
    }
    const payload = toPayload ? toPayload(values, editing) : values;
    try {
      if (editing) await staff.update(`${path}${idOf(editing)}/`, payload);
      else await staff.create(path, payload);
      setShowForm(false);
      setEditing(null);
      await load();
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

  async function remove(item: T) {
    if (!(await confirm(t(locale, "admin.confirmDelete"), { danger: true })))
      return;
    try {
      await staff.remove(`${path}${idOf(item)}/`);
      await load();
    } catch (err) {
      setError(
        err instanceof ApiError
          ? errorText(locale, err.code, err.message)
          : String(err),
      );
    }
  }

  const values = initialValues(editing);
  const input =
    "h-10 w-full rw-radius-sm border rw-line rw-surface px-3 text-theme-sm outline-none " +
    "rw-focus-line rw-field-bg ";

  return (
    <div className="space-y-4">
      {error && <Status status="bad" variant="alert" alert label={error} />}

      <Card
        title={title}
        action={
          <div className="flex items-center gap-2">
            {searchable && (
              <input
                value={q}
                onChange={(e) => {
                  setQ(e.target.value);
                  setPage(1);
                }}
                placeholder={t(locale, "admin.search")}
                className={`${input} w-48`}
              />
            )}
            <Badge>{count}</Badge>
            {!readOnly && canCreate && (
              <Button
                className="h-9"
                onClick={() => {
                  setEditing(null);
                  setShowForm(true);
                }}
              >
                {t(locale, "admin.create")}
              </Button>
            )}
          </div>
        }
        bodyClassName="p-0"
      >
        {showForm && (
          <form
            key={editing ? idOf(editing) : "new"}
            onSubmit={submit}
            className="grid gap-3 border-b rw-divider p-5 md:grid-cols-2"
          >
            {fields.map((f) => {
              const v = values[f.name];
              const disabled = !!editing && !!f.readonlyOnEdit;
              const wide = f.type === "textarea";
              const Tag = f.type === "select" ? FIELD_WRAP.select : FIELD_WRAP.field;
              return (
                <Tag
                  key={f.name}
                  className={`block ${wide ? "md:col-span-2" : ""}`}
                >
                  <span className="mb-1 block text-theme-xs font-medium rw-dim-2">
                    {t(locale, f.labelKey)}
                    {f.required && " *"}
                  </span>
                  {f.type === "textarea" ? (
                    <textarea
                      name={f.name}
                      defaultValue={String(v ?? "")}
                      rows={f.rows ?? 6}
                      required={f.required}
                      disabled={disabled}
                      className={`${input} h-auto py-2 font-mono`}
                    />
                  ) : f.type === "checkbox" ? (
                    <input
                      name={f.name}
                      type="checkbox"
                      defaultChecked={Boolean(v)}
                      disabled={disabled}
                      className="mt-2 size-4"
                    />
                  ) : f.type === "select" ? (
                    <Dropdown
                      hideLabel
                      label={`${t(locale, f.labelKey)}${f.required ? " *" : ""}`}
                      name={f.name}
                      defaultValue={String(v ?? "")}
                      disabled={disabled}
                      options={[
                        ...(!f.required
                          ? [{ value: "", label: t(locale, "settings.notChosen") }]
                          : []),
                        ...(f.options ?? []).map((o) => ({
                          value: o.value,
                          label: t(locale, o.labelKey),
                        })),
                      ]}
                    />
                  ) : (
                    <input
                      name={f.name}
                      type={
                        f.type === "number"
                          ? "number"
                          : f.type === "datetime"
                            ? "datetime-local"
                            : "text"
                      }
                      defaultValue={String(v ?? "")}
                      required={f.required}
                      disabled={disabled}
                      step={f.step}
                      min={f.min}
                      max={f.max}
                      // Quest va do'kon kodlari pastki chiziq ishlatadi
                      // (`weekly_marathon`), shuning uchun u ham ruxsat etiladi.
                      pattern={f.type === "slug" ? "[a-z0-9_-]+" : undefined}
                      className={input}
                    />
                  )}
                  {f.helpKey && (
                    <span className="mt-1 block text-theme-xs rw-faint">
                      {t(locale, f.helpKey)}
                    </span>
                  )}
                </Tag>
              );
            })}
            <div className="flex gap-2 md:col-span-2">
              <Button type="submit" disabled={busy}>
                {t(locale, "admin.save")}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setShowForm(false);
                  setEditing(null);
                }}
              >
                {t(locale, "admin.cancel")}
              </Button>
            </div>
          </form>
        )}

        <Table>
          <THead>
            {columns.map((c) => (
              <TH key={c.key} align={c.align}>
                {t(locale, c.labelKey)}
              </TH>
            ))}
            <TH align="right">{t(locale, "admin.actions")}</TH>
          </THead>
          <TBody>
            {rows.map((item) => (
              <Fragment key={idOf(item)}>
                <TR>
                  {columns.map((c) => (
                    <TD key={c.key} align={c.align}>
                      {c.render
                        ? c.render(item, load, locale)
                        : String(item[c.key] ?? "")}
                    </TD>
                  ))}
                  <TD align="right">
                    <div className="flex justify-end gap-2">
                      {rowExtra && (
                        <button
                          type="button"
                          onClick={() =>
                            setExpanded(
                              expanded === idOf(item) ? null : idOf(item),
                            )
                          }
                          className="text-theme-xs rw-accent-ink hover:underline"
                        >
                          {expanded === idOf(item) ? "▲" : "▼"}
                        </button>
                      )}
                      {!readOnly && (
                        <button
                          type="button"
                          onClick={() => {
                            setEditing(item);
                            setShowForm(true);
                          }}
                          className="text-theme-xs rw-accent-ink hover:underline"
                        >
                          {t(locale, "admin.edit")}
                        </button>
                      )}
                      {canDelete && !readOnly && (
                        <button
                          type="button"
                          onClick={() => remove(item)}
                          className="text-theme-xs rw-bad-ink hover:underline"
                        >
                          {t(locale, "admin.delete")}
                        </button>
                      )}
                    </div>
                  </TD>
                </TR>
                {rowExtra && expanded === idOf(item) && (
                  <tr className="rw-chip dark:bg-white/[0.02]">
                    <td colSpan={columns.length + 1} className="px-4 py-4">
                      {rowExtra(item, load)}
                    </td>
                  </tr>
                )}
              </Fragment>
            ))}
            {rows.length === 0 && (
              <EmptyRow colSpan={columns.length + 1}>
                {t(locale, "admin.noRows")}
              </EmptyRow>
            )}
          </TBody>
        </Table>
        {count > PAGE_SIZE && (
          <div className="flex items-center justify-end gap-2 border-t rw-divider px-4 py-2 text-theme-xs">
            <button
              type="button"
              disabled={page <= 1}
              onClick={() => setPage((p) => p - 1)}
              className="disabled:opacity-40"
            >
              ←
            </button>
            <span>{page}</span>
            <button
              type="button"
              // Oxirgi sahifa to'la bo'lmasa ham «keyingi» ochiq qolardi va
              // API «Invalid page» (404) qaytarardi.
              disabled={page >= Math.ceil(count / PAGE_SIZE)}
              onClick={() => setPage((p) => p + 1)}
              className="disabled:opacity-40"
            >
              →
            </button>
          </div>
        )}
      </Card>
    </div>
  );
}
