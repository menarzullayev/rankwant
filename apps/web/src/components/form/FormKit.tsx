"use client";

import {
  useEffect,
  useId,
  useRef,
  useState,
  type InputHTMLAttributes,
  type ReactNode,
} from "react";

import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { currentFormVariant } from "@/lib/theme/form";
import type { CheckShape } from "@/lib/theme/kit";
import { FM_BOX, FM_CTL, FM_INP, FM_LAB, FM_RADIO } from "./chrome";

/** Sozlamalar qatori (`label`) yoki shartlar matni (`children`). */
export function FormCheck({
  label,
  hint,
  children,
  className,
  shape = "square",
  ...props
}: InputHTMLAttributes<HTMLInputElement> & {
  label?: string;
  hint?: string;
  children?: ReactNode;
  shape?: Extract<CheckShape, "square" | "pill" | "card" | "switch">;
}) {
  const copy = children ?? (
    <>
      {label}
      {hint ? <span className="mt-0.5 block text-theme-xs rw-dim">{hint}</span> : null}
    </>
  );
  const kit = shape === "square" ? undefined : shape;
  return (
    <label
      className={`${FM_CTL} rw-fm-check cursor-pointer ${className ?? ""}`}
      data-kit-check={kit}
    >
      <span className={`${FM_LAB} min-w-0`}>{copy}</span>
      <input type="checkbox" className={FM_BOX} {...props} />
    </label>
  );
}

/** Jadval katagi — yorliq yo'q, faqat belgi. */
export function FormBox({
  shape,
  ...props
}: InputHTMLAttributes<HTMLInputElement> & {
  shape?: Extract<CheckShape, "square" | "pill" | "switch">;
}) {
  const kit = shape && shape !== "square" ? shape : undefined;
  return (
    <input type="checkbox" className={FM_BOX} data-kit-check={kit} {...props} />
  );
}

export function FormRadios({
  name,
  label,
  value,
  defaultValue,
  options,
  onChange,
  tone,
}: {
  name: string;
  label: string;
  value?: string;
  defaultValue?: string;
  options: readonly { value: string; label: string }[];
  onChange?: (value: string) => void;
  tone?: "plain" | "card";
}) {
  const group = useId();
  return (
    <fieldset className={FM_CTL}>
      <legend className={FM_LAB}>{label}</legend>
      <div
        className={tone === "card" ? "rw-kit-radio-cards" : "rw-fm-hits"}
        role="radiogroup"
        data-kit-check={tone === "card" ? "radio-card" : undefined}
      >
        {options.map((opt) => (
          <label key={opt.value} className="rw-fm-hit">
            <input
              type="radio"
              className={FM_RADIO}
              name={name || group}
              value={opt.value}
              checked={value !== undefined ? value === opt.value : undefined}
              defaultChecked={
                value === undefined ? defaultValue === opt.value : undefined
              }
              onChange={() => onChange?.(opt.value)}
            />
            {opt.label}
          </label>
        ))}
      </div>
    </fieldset>
  );
}

export function FormFile({
  label,
  accept,
  disabled,
  onFile,
}: {
  label?: string;
  accept?: string;
  disabled?: boolean;
  onFile?: (file: File) => void;
}) {
  const locale = useLocale();
  const input = useRef<HTMLInputElement>(null);
  const [name, setName] = useState("");
  const [over, setOver] = useState(false);

  function take(file: File | undefined) {
    if (!file || disabled) return;
    setName(file.name);
    onFile?.(file);
    if (input.current) input.current.value = "";
  }

  const ui = (
    <span className={`rw-fm-drop${name ? " has-file" : ""}${over ? " is-over" : ""}`}>
      <input
        ref={input}
        type="file"
        accept={accept}
        disabled={disabled}
        className="sr-only"
        tabIndex={-1}
        onChange={(event) => take(event.target.files?.[0])}
      />
      <span
        className="rw-fm-drop-ui"
        onClick={() => input.current?.click()}
        onKeyDown={(event) => {
          if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            input.current?.click();
          }
        }}
        onDragOver={(event) => {
          event.preventDefault();
          setOver(true);
        }}
        onDragLeave={() => setOver(false)}
        onDrop={(event) => {
          event.preventDefault();
          setOver(false);
          take(event.dataTransfer.files[0]);
        }}
        role="button"
        tabIndex={disabled ? -1 : 0}
      >
        <b>{t(locale, "form.file.choose")}</b>
        <i>{name || t(locale, "form.file.empty")}</i>
      </span>
    </span>
  );

  if (!label) return ui;
  return (
    <div className={`${FM_CTL} rw-fm-file`}>
      <span className={FM_LAB}>{label}</span>
      {ui}
    </div>
  );
}

function toIso(y: number, m: number, d: number): string {
  return `${y}-${String(m + 1).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
}

function parseIso(iso: string): { y: number; m: number; d: number } | null {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso);
  if (!match) return null;
  const y = Number(match[1]);
  const m = Number(match[2]) - 1;
  const d = Number(match[3]);
  if (m < 0 || 11 < m || d < 1 || 31 < d) return null;
  return { y, m, d };
}

function todayParts(): { y: number; m: number; d: number } {
  const now = new Date();
  return { y: now.getFullYear(), m: now.getMonth(), d: now.getDate() };
}

function clampDay(iso: string, min?: string, max?: string): boolean {
  if (min && iso < min) return false;
  if (max && iso > max) return false;
  return true;
}

function intlLocale(locale: string): string {
  return locale === "kaa" ? "uz" : locale;
}

function weekdays(locale: string): string[] {
  const fmt = new Intl.DateTimeFormat(intlLocale(locale), { weekday: "short" });
  const monday = new Date(Date.UTC(2023, 0, 2));
  return Array.from({ length: 7 }, (_, i) => {
    const day = new Date(monday);
    day.setUTCDate(monday.getUTCDate() + i);
    return fmt.format(day);
  });
}

function formatDay(iso: string, locale: string, tabular: boolean): string {
  if (tabular) return iso;
  const parts = parseIso(iso);
  if (!parts) return iso;
  return new Intl.DateTimeFormat(intlLocale(locale), {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(new Date(parts.y, parts.m, parts.d));
}

export function FormDate({
  label,
  hint,
  name,
  id,
  value,
  defaultValue,
  min,
  max,
  required,
  disabled,
  onChange,
}: {
  label: string;
  hint?: string;
  name?: string;
  id?: string;
  value?: string;
  defaultValue?: string;
  min?: string;
  max?: string;
  required?: boolean;
  disabled?: boolean;
  onChange?: (iso: string) => void;
}) {
  const locale = useLocale();
  const [draft, setDraft] = useState(defaultValue ?? "");
  const [open, setOpen] = useState(false);
  const iso = value !== undefined ? value : draft;
  const seed = parseIso(iso) ?? todayParts();
  const [cursor, setCursor] = useState({ y: seed.y, m: seed.m });
  const wrap = useRef<HTMLDivElement>(null);
  const tabular = currentFormVariant() === "jadval";

  useEffect(() => {
    if (!open) return;
    function onPtr(event: PointerEvent) {
      if (wrap.current && !wrap.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("pointerdown", onPtr);
    return () => document.removeEventListener("pointerdown", onPtr);
  }, [open]);
  const days = daysInMonth(cursor.y, cursor.m);
  const lead = mondayOffset(cursor.y, cursor.m);
  const monthLabel = new Intl.DateTimeFormat(intlLocale(locale), {
    month: "long",
    year: "numeric",
  }).format(new Date(cursor.y, cursor.m, 1));

  function choose(day: number) {
    const next = toIso(cursor.y, cursor.m, day);
    if (!clampDay(next, min, max)) return;
    if (value === undefined) setDraft(next);
    onChange?.(next);
    setOpen(false);
  }

  function shift(delta: number) {
    const date = new Date(cursor.y, cursor.m + delta, 1);
    setCursor({ y: date.getFullYear(), m: date.getMonth() });
  }

  function toggle() {
    if (disabled) return;
    const parts = parseIso(iso) ?? todayParts();
    setCursor({ y: parts.y, m: parts.m });
    setOpen((was) => !was);
  }

  return (
    <div className={`${FM_CTL} rw-fm-date`}>
      <label className={FM_LAB} htmlFor={id ?? name}>
        {label}
      </label>
      <div
        ref={wrap}
        className={`rw-fm-date-wrap${open ? " is-open" : ""}`}
      >
        <input
          type="hidden"
          name={name}
          id={id ?? name}
          value={iso}
          required={required}
          disabled={disabled}
        />
        <button
          type="button"
          className={`${FM_INP} rw-fm-date-btn`}
          disabled={disabled}
          aria-expanded={open}
          aria-haspopup="dialog"
          onClick={toggle}
        >
          {iso ? formatDay(iso, locale, tabular) : t(locale, "form.sample.date")}
        </button>
        <div className="rw-fm-cal" role="dialog" aria-label={label}>
          <div className="rw-fm-cal-bar">
            <button
              type="button"
              aria-label={t(locale, "form.cal.prev")}
              onClick={() => shift(-1)}
            >
              ‹
            </button>
            <strong>{monthLabel}</strong>
            <button
              type="button"
              aria-label={t(locale, "form.cal.next")}
              onClick={() => shift(1)}
            >
              ›
            </button>
          </div>
          <div className="rw-fm-cal-grid">
            {weekdays(locale).map((wd) => (
              <span key={wd} className="rw-fm-cal-wd">
                {wd}
              </span>
            ))}
            {Array.from({ length: lead }, (_, i) => (
              <span key={`e${i}`} />
            ))}
            {Array.from({ length: days }, (_, i) => {
              const day = i + 1;
              const stamp = toIso(cursor.y, cursor.m, day);
              const on = stamp === iso;
              const blocked = !clampDay(stamp, min, max);
              return (
                <button
                  key={stamp}
                  type="button"
                  disabled={blocked}
                  className={on ? "is-on" : undefined}
                  onClick={() => choose(day)}
                >
                  {day}
                </button>
              );
            })}
          </div>
        </div>
      </div>
      {hint ? <span className="mt-1.5 block text-theme-xs rw-dim">{hint}</span> : null}
    </div>
  );
}

function daysInMonth(y: number, m: number): number {
  return new Date(y, m + 1, 0).getDate();
}

function mondayOffset(y: number, m: number): number {
  const sun = new Date(y, m, 1).getDay();
  return sun === 0 ? 6 : sun - 1;
}
