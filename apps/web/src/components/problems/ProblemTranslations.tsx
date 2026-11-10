"use client";

/** A problem's text in other languages (ADR-0058) — one editor for the
 *  author's studio and the staff panel.
 *
 *  `base` is the problem's API path, ending in `/`: `/problems/mine/<slug>/`
 *  for the author, `/staff/problems/<slug>/` for staff. Who may write is the
 *  server's decision (a published problem answers 403 to its author); the
 *  caller passes `readOnly` so the buttons are not offered at all. */

import { useCallback, useEffect, useState } from "react";

import { FM_INP, FM_LAB } from "@/components/form/chrome";
import { useConfirm } from "@/components/overlay/OverlayHost";
import { Button } from "@/components/ui/Button";
import { useLocale } from "@/i18n/LocaleProvider";
import { errorText, fill, LOCALE_NAMES, LOCALES, t, type Locale } from "@/i18n/messages";
import { ApiError, deleteJson, getJson, putJson } from "@/lib/api/client";

type Fields = {
  title: string;
  statement: string;
  input_format: string;
  output_format: string;
  note: string;
  editorial: string;
};

type Row = Fields & { locale: string; updated_at: string };

const EMPTY: Fields = {
  title: "",
  statement: "",
  input_format: "",
  output_format: "",
  note: "",
  editorial: "",
};

function fieldsOf(row: Row | undefined): Fields {
  if (!row) return EMPTY;
  const { locale: _locale, updated_at: _updated, ...fields } = row;
  return fields;
}

const languageName = (code: string) => LOCALE_NAMES[code as Locale] ?? code;

function TextArea({
  label,
  value,
  onChange,
  rows,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  rows: number;
}) {
  return (
    <label className="block">
      <span className={FM_LAB}>{label}</span>
      <textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        rows={rows}
        spellCheck={false}
        className={`${FM_INP} font-mono`}
      />
    </label>
  );
}

export function ProblemTranslations({
  base,
  baseLocale,
  readOnly = false,
}: {
  base: string;
  /** The author's language: the problem's own text, never a translation. */
  baseLocale: string;
  readOnly?: boolean;
}) {
  const locale = useLocale();
  const confirm = useConfirm();
  const [rows, setRows] = useState<Row[] | null>(null);
  const [open, setOpen] = useState<string | null>(null);
  const [draft, setDraft] = useState<Fields>(EMPTY);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [status, setStatus] = useState("");

  const fail = useCallback(
    (e: unknown) =>
      setError(e instanceof ApiError ? errorText(locale, e.code, e.message) : String(e)),
    [locale],
  );

  const load = useCallback(async () => {
    try {
      setRows(await getJson<Row[]>(`${base}translations/`));
    } catch (e) {
      fail(e);
    }
  }, [base, fail]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void load();
  }, [load]);

  function set<K extends keyof Fields>(key: K, value: Fields[K]) {
    setDraft((prev) => ({ ...prev, [key]: value }));
  }

  function start(code: string) {
    setDraft(fieldsOf(rows?.find((row) => row.locale === code)));
    setOpen(open === code ? null : code);
    setError("");
    setStatus("");
  }

  async function save(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!open) return;
    setBusy(true);
    setError("");
    try {
      await putJson<Row>(`${base}translations/${open}/`, draft);
      setStatus(`${languageName(open)}: ${t(locale, "studio.saved")}`);
      setOpen(null);
      await load();
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  }

  async function remove(code: string) {
    const ok = await confirm(
      fill(t(locale, "translation.deleteConfirm"), { locale: languageName(code) }),
      { danger: true, confirmLabel: t(locale, "translation.delete") },
    );
    if (!ok) return;
    setError("");
    try {
      await deleteJson<void>(`${base}translations/${code}/`);
      if (open === code) setOpen(null);
      setStatus("");
      await load();
    } catch (err) {
      fail(err);
    }
  }

  const others = LOCALES.filter((code) => code !== baseLocale);
  return (
    <div className="space-y-3">
      <p className="text-theme-sm rw-dim">{t(locale, "translation.intro")}</p>
      <p className="text-theme-xs rw-faint">
        {fill(t(locale, "translation.base"), { locale: languageName(baseLocale) })}
      </p>
      {error && (
        <p role="alert" className="text-theme-sm rw-bad-ink">
          {error}
        </p>
      )}
      <p aria-live="polite" className="text-theme-xs rw-ok-ink">
        {status}
      </p>
      {rows === null ? (
        <p className="text-theme-sm rw-dim">{t(locale, "loading.label")}</p>
      ) : (
        <ul className="max-w-2xl divide-y rw-divide">
          {others.map((code) => {
            const row = rows.find((item) => item.locale === code);
            const formId = `translation-${code}`;
            return (
              <li key={code} className="py-2">
                <div className="flex flex-wrap items-center gap-x-3 gap-y-2 sm:grid sm:grid-cols-[8rem_minmax(0,18rem)_auto]">
                  <span className="w-32 shrink-0 text-theme-sm font-medium rw-strong sm:w-auto">
                    {languageName(code)}
                  </span>
                  <span className={`min-w-0 grow truncate text-theme-sm sm:grow-0 ${row ? "rw-dim" : "rw-faint"}`}>
                    {row ? row.title : t(locale, "translation.none")}
                  </span>
                  {!readOnly && (
                    <span className="flex gap-2">
                      <Button
                        type="button"
                        variant="outline"
                        aria-expanded={open === code}
                        aria-controls={formId}
                        onClick={() => start(code)}
                      >
                        {t(locale, row ? "translation.edit" : "translation.add")}
                      </Button>
                      {row && (
                        <Button type="button" variant="outline" onClick={() => remove(code)}>
                          {t(locale, "translation.delete")}
                        </Button>
                      )}
                    </span>
                  )}
                </div>
                {open === code && (
                  <form
                    id={formId}
                    onSubmit={save}
                    lang={code}
                    className="mt-3 max-w-2xl space-y-3 rw-radius-sm border rw-line p-3"
                  >
                    <label className="block">
                      <span className={FM_LAB}>{t(locale, "studio.field.title")}</span>
                      <input
                        value={draft.title}
                        onChange={(event) => set("title", event.target.value)}
                        required
                        maxLength={200}
                        className={FM_INP}
                      />
                    </label>
                    <TextArea
                      label={t(locale, "studio.tab.statement")}
                      value={draft.statement}
                      onChange={(value) => set("statement", value)}
                      rows={10}
                    />
                    <TextArea
                      label={t(locale, "problem.inputFormat")}
                      value={draft.input_format}
                      onChange={(value) => set("input_format", value)}
                      rows={3}
                    />
                    <TextArea
                      label={t(locale, "problem.outputFormat")}
                      value={draft.output_format}
                      onChange={(value) => set("output_format", value)}
                      rows={3}
                    />
                    <TextArea
                      label={t(locale, "problem.comments")}
                      value={draft.note}
                      onChange={(value) => set("note", value)}
                      rows={3}
                    />
                    <TextArea
                      label={t(locale, "studio.tab.editorial")}
                      value={draft.editorial}
                      onChange={(value) => set("editorial", value)}
                      rows={6}
                    />
                    <p className="text-theme-xs rw-faint">{t(locale, "studio.field.markdownHint")}</p>
                    <div className="flex flex-wrap justify-end gap-3">
                      <Button type="button" variant="outline" onClick={() => setOpen(null)}>
                        {t(locale, "studio.cancel")}
                      </Button>
                      <Button type="submit" busy={busy}>
                        {t(locale, "studio.save")}
                      </Button>
                    </div>
                  </form>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
