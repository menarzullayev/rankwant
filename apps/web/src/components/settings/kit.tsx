"use client";

import { useCallback, useEffect, useState } from "react";

import { useLocale } from "@/i18n/LocaleProvider";
import { errorText, t, type Locale } from "@/i18n/messages";
import { ApiError, getJson } from "@/lib/api";

/** Sozlamalar bo'limlari uchun umumiy bo'laklar. */

/** Maydon xatosi bo'lsa — serverning aniq sababi («Bu username band»),
 *  aks holda xato kodi tarjimasi. Umumiy «ma'lumot noto'g'ri» odamga
 *  qaysi maydonni tuzatishni aytmasdi. */
export function describeError(locale: Locale, err: unknown): string {
  if (err instanceof ApiError) {
    return err.code === "invalid"
      ? err.text
      : errorText(locale, err.code, err.text);
  }
  return t(locale, "error.error");
}

/** Bitta amalning holati: kutish, xato va «saqlandi». */
export function useAction() {
  const locale = useLocale();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [done, setDone] = useState(false);

  const run = useCallback(
    async (action: () => Promise<unknown>) => {
      setBusy(true);
      setError("");
      setDone(false);
      try {
        await action();
        setDone(true);
        return true;
      } catch (err) {
        setError(describeError(locale, err));
        return false;
      } finally {
        setBusy(false);
      }
    },
    [locale],
  );

  return { busy, error, done, run, setError };
}

/** Sahifa ochilganda bir marta GET. `path` o'zgarsa qayta so'raydi. */
export function useLoad<T>(path: string) {
  const locale = useLocale();
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState("");
  const [version, setVersion] = useState(0);

  useEffect(() => {
    let alive = true;
    getJson<T>(path)
      .then((value) => {
        if (!alive) return;
        setData(value);
        setError("");
      })
      .catch((err: unknown) => {
        if (alive) setError(describeError(locale, err));
      });
    return () => {
      alive = false;
    };
  }, [path, version, locale]);

  const reload = useCallback(() => setVersion((v) => v + 1), []);
  return { data, setData, error, reload };
}

export function Status({
  error,
  done,
  text,
}: {
  error?: string;
  done?: boolean;
  text?: string;
}) {
  const locale = useLocale();
  if (error) {
    return (
      <p
        role="alert"
        className="rw-radius-sm rw-bad-soft px-3 py-2 text-theme-sm rw-bad-ink"
      >
        {error}
      </p>
    );
  }
  if (done) {
    return (
      <p role="status" className="text-theme-sm rw-ok-ink">
        ✓ {text ?? t(locale, "settings.saved")}
      </p>
    );
  }
  return null;
}

export function Hint({ children }: { children: React.ReactNode }) {
  return <p className="text-theme-sm rw-dim">{children}</p>;
}

export function Loading() {
  const locale = useLocale();
  return (
    <p role="status" className="text-theme-sm rw-faint">
      {t(locale, "settings.loading")}
    </p>
  );
}

const CONTROL =
  "w-full rw-radius-sm border rw-line text-theme-sm rw-strong outline-none transition rw-focus-line rw-focus-ring rw-field-bg";

export function TextArea({
  label,
  hint,
  ...props
}: React.TextareaHTMLAttributes<HTMLTextAreaElement> & {
  label: string;
  hint?: string;
}) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-theme-sm font-medium rw-strong">
        {label}
      </span>
      <textarea className={`${CONTROL} min-h-24 px-4 py-3`} {...props} />
      {hint && <span className="mt-1.5 block text-theme-xs rw-dim">{hint}</span>}
    </label>
  );
}

export function Select({
  label,
  hint,
  leading,
  children,
  ...props
}: React.SelectHTMLAttributes<HTMLSelectElement> & {
  label: string;
  hint?: string;
  /** Maydon CHAPIDAGI element — mamlakat bayrog'i uchun (native
   *  `<select>` ichida SVG ko'rinmaydi, shuning uchun yonida turadi). */
  leading?: React.ReactNode;
}) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-theme-sm font-medium rw-strong">
        {label}
      </span>
      <span className="flex items-center gap-2">
        {leading}
        <select className={`${CONTROL} h-11 min-w-0 flex-1 px-3`} {...props}>
          {children}
        </select>
      </span>
      {hint && <span className="mt-1.5 block text-theme-xs rw-dim">{hint}</span>}
    </label>
  );
}

export function Check({
  label,
  hint,
  ...props
}: React.InputHTMLAttributes<HTMLInputElement> & {
  label: string;
  hint?: string;
}) {
  return (
    <label className="flex items-start gap-2.5 text-theme-sm rw-strong">
      <input
        type="checkbox"
        className="rw-accent-control mt-0.5 size-4 shrink-0"
        {...props}
      />
      <span>
        {label}
        {hint && <span className="mt-0.5 block text-theme-xs rw-dim">{hint}</span>}
      </span>
    </label>
  );
}
