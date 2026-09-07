"use client";

import { useCallback, useEffect, useState } from "react";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyRow, TBody, TD, TH, THead, TR, Table } from "@/components/ui/Table";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";
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
  label: string;
  type?: FieldType;
  required?: boolean;
  help?: string;
  options?: { value: string; label: string }[];
  /** Tahrirda o'zgartirib bo'lmaydi (masalan slug) */
  readonlyOnEdit?: boolean;
  rows?: number;
  step?: number;
  min?: number;
  max?: number;
};

export type ColumnDef<T> = {
  key: string;
  label: string;
  align?: "left" | "right";
  render?: (item: T) => React.ReactNode;
};

type Row = Record<string, unknown>;

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
};

function toLocalInput(iso: unknown): string {
  if (!iso || typeof iso !== "string") return "";
  const d = new Date(iso);
  return new Date(d.getTime() - d.getTimezoneOffset() * 60_000).toISOString().slice(0, 16);
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
}: CrudPageProps<T>) {
  const locale = DEFAULT_LOCALE;
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
      setError(e instanceof ApiError ? e.message : String(e));
    }
  }, [path, page, q, ordering]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void load();
  }, [load]);

  function idOf(item: T): string {
    return String(item[idField]);
  }

  function initialValues(item: T | null): Row {
    if (!item) return Object.fromEntries(fields.map((f) => [f.name, f.type === "checkbox" ? false : ""]));
    if (fromItem) return fromItem(item);
    const v: Row = {};
    for (const f of fields) {
      const raw = item[f.name];
      if (f.type === "datetime") v[f.name] = toLocalInput(raw);
      else if (f.type === "list") v[f.name] = Array.isArray(raw) ? raw.join(", ") : "";
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
      setError(err instanceof ApiError ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  async function remove(item: T) {
    if (!window.confirm(t(locale, "admin.confirmDelete"))) return;
    try {
      await staff.remove(`${path}${idOf(item)}/`);
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : String(err));
    }
  }

  const values = initialValues(editing);
  const input =
    "h-10 w-full rounded-lg border border-gray-200 bg-white px-3 text-theme-sm outline-none " +
    "focus:border-brand-400 dark:border-[#232936] dark:bg-[#0b0d12] dark:text-white/90";

  return (
    <div className="space-y-4">
      {error && (
        <p className="rounded-lg bg-error-50 px-3 py-2 text-theme-sm text-error-600 dark:bg-error-500/12 dark:text-error-400">
          {error}
        </p>
      )}

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
            {!readOnly && (
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
            className="grid gap-3 border-b border-gray-100 p-5 md:grid-cols-2 dark:border-[#232936]"
          >
            {fields.map((f) => {
              const v = values[f.name];
              const disabled = !!editing && !!f.readonlyOnEdit;
              const wide = f.type === "textarea";
              return (
                <label key={f.name} className={`block ${wide ? "md:col-span-2" : ""}`}>
                  <span className="mb-1 block text-theme-xs font-medium text-gray-600 dark:text-gray-300">
                    {f.label}
                    {f.required && " *"}
                  </span>
                  {f.type === "textarea" ? (
                    <textarea name={f.name} defaultValue={String(v ?? "")} rows={f.rows ?? 6} required={f.required} disabled={disabled} className={`${input} h-auto py-2 font-mono`} />
                  ) : f.type === "checkbox" ? (
                    <input name={f.name} type="checkbox" defaultChecked={Boolean(v)} disabled={disabled} className="mt-2 size-4" />
                  ) : f.type === "select" ? (
                    <select name={f.name} defaultValue={String(v ?? "")} required={f.required} disabled={disabled} className={input}>
                      {!f.required && <option value="">—</option>}
                      {(f.options ?? []).map((o) => (
                        <option key={o.value} value={o.value}>{o.label}</option>
                      ))}
                    </select>
                  ) : (
                    <input
                      name={f.name}
                      type={f.type === "number" ? "number" : f.type === "datetime" ? "datetime-local" : "text"}
                      defaultValue={String(v ?? "")}
                      required={f.required}
                      disabled={disabled}
                      step={f.step}
                      min={f.min}
                      max={f.max}
                      pattern={f.type === "slug" ? "[a-z0-9-]+" : undefined}
                      className={input}
                    />
                  )}
                  {f.help && <span className="mt-1 block text-theme-xs text-gray-400">{f.help}</span>}
                </label>
              );
            })}
            <div className="flex gap-2 md:col-span-2">
              <Button type="submit" disabled={busy}>{t(locale, "admin.save")}</Button>
              <Button type="button" variant="outline" onClick={() => { setShowForm(false); setEditing(null); }}>
                {t(locale, "admin.cancel")}
              </Button>
            </div>
          </form>
        )}

        <Table>
          <THead>
            {columns.map((c) => (
              <TH key={c.key} align={c.align}>{c.label}</TH>
            ))}
            <TH align="right">{t(locale, "admin.actions")}</TH>
          </THead>
          <TBody>
            {rows.map((item) => (
              <>
                <TR key={idOf(item)}>
                  {columns.map((c) => (
                    <TD key={c.key} align={c.align}>
                      {c.render ? c.render(item) : String(item[c.key] ?? "")}
                    </TD>
                  ))}
                  <TD align="right">
                    <div className="flex justify-end gap-2">
                      {rowExtra && (
                        <button type="button" onClick={() => setExpanded(expanded === idOf(item) ? null : idOf(item))} className="text-theme-xs text-brand-500 hover:underline">
                          {expanded === idOf(item) ? "▲" : "▼"}
                        </button>
                      )}
                      {!readOnly && (
                        <button type="button" onClick={() => { setEditing(item); setShowForm(true); }} className="text-theme-xs text-brand-500 hover:underline">
                          {t(locale, "admin.edit")}
                        </button>
                      )}
                      {canDelete && !readOnly && (
                        <button type="button" onClick={() => remove(item)} className="text-theme-xs text-error-500 hover:underline">
                          {t(locale, "admin.delete")}
                        </button>
                      )}
                    </div>
                  </TD>
                </TR>
                {rowExtra && expanded === idOf(item) && (
                  <tr key={`${idOf(item)}-extra`} className="bg-gray-50 dark:bg-white/[0.02]">
                    <td colSpan={columns.length + 1} className="px-4 py-4">
                      {rowExtra(item, load)}
                    </td>
                  </tr>
                )}
              </>
            ))}
            {rows.length === 0 && <EmptyRow colSpan={columns.length + 1}>{t(locale, "admin.noRows")}</EmptyRow>}
          </TBody>
        </Table>
        {count > rows.length && (
          <div className="flex items-center justify-end gap-2 border-t border-gray-100 px-4 py-2 text-theme-xs dark:border-[#232936]">
            <button type="button" disabled={page <= 1} onClick={() => setPage((p) => p - 1)} className="disabled:opacity-40">←</button>
            <span>{page}</span>
            <button type="button" disabled={page * rows.length >= count} onClick={() => setPage((p) => p + 1)} className="disabled:opacity-40">→</button>
          </div>
        )}
      </Card>
    </div>
  );
}
