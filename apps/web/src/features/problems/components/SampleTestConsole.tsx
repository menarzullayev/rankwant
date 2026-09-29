"use client";

import { useEffect, useId, useRef, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Loading } from "@/components/ui/Loading";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";
import type { Sample } from "@/lib/api";

export type SampleConsoleState = {
  status: "idle" | "running" | "ok" | "bad";
  log: string;
  got: string;
  outputStatus: "idle" | "ok" | "bad";
};

export function sampleConsoleIdleState(
  locale: Parameters<typeof t>[0],
): SampleConsoleState {
  return {
    status: "idle",
    log: t(locale, "submit.sampleConsoleIdle"),
    got: "—",
    outputStatus: "idle",
  };
}

/** Namuna sinov konsoli — prototip `sample-console-gallery` #3.
 *
 * Jadval faqat o'qish; bitta tanlangan namuna shu yerda ishga tushadi.
 */
export function SampleTestConsole({
  samples,
  selectedOrder,
  onSelect,
  onRun,
  busy,
  disabled,
  state,
}: {
  samples: Sample[];
  selectedOrder: number;
  onSelect: (order: number) => void;
  onRun: () => void;
  busy: boolean;
  disabled: boolean;
  state: SampleConsoleState;
}) {
  const locale = useLocale();
  const listId = useId();
  const [open, setOpen] = useState(false);
  const wrapRef = useRef<HTMLDivElement>(null);
  const selected =
    samples.find((s) => s.order === selectedOrder) ?? samples[0] ?? null;

  useEffect(() => {
    function close(e: MouseEvent) {
      if (!wrapRef.current?.contains(e.target as Node)) setOpen(false);
    }
    if (open) document.addEventListener("mousedown", close);
    return () => document.removeEventListener("mousedown", close);
  }, [open]);

  if (samples.length === 0) return null;

  return (
    <section
      className="border-t rw-divider rw-panel-2 text-theme-xs"
      aria-label={t(locale, "submit.sampleConsoleLabel")}
    >
      <div className="flex flex-wrap items-center gap-2 border-b rw-divider px-3 py-2">
        <div className="relative" ref={wrapRef}>
          <button
            type="button"
            id={`${listId}-btn`}
            aria-haspopup="listbox"
            aria-expanded={open}
            aria-controls={`${listId}-list`}
            onClick={() => setOpen((v) => !v)}
            className="inline-flex min-h-8 items-center gap-1 rw-radius-sm border rw-line rw-field-bg px-2 py-1 font-medium rw-strong rw-focus-ring"
          >
            {fill(t(locale, "submit.samplePick"), {
              order: selected?.order ?? 1,
            })}
            <span aria-hidden>▾</span>
          </button>
          {open && (
            <ul
              id={`${listId}-list`}
              role="listbox"
              aria-labelledby={`${listId}-btn`}
              className="absolute left-0 top-full z-20 mt-1 min-w-[10rem] rw-radius-sm border rw-line rw-panel-bg py-1 shadow-md"
            >
              {samples.map((sample) => (
                <li key={sample.order}>
                  <button
                    type="button"
                    role="option"
                    aria-selected={sample.order === selected?.order}
                    className={`block w-full px-3 py-1.5 text-left rw-hover-bg ${
                      sample.order === selected?.order ? "rw-accent-soft rw-accent-ink" : ""
                    }`}
                    onClick={() => {
                      onSelect(sample.order);
                      setOpen(false);
                    }}
                  >
                    {fill(t(locale, "submit.samplePick"), { order: sample.order })}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
        <Button
          variant="outline"
          onClick={onRun}
          disabled={disabled || busy}
        >
          {t(locale, "submit.testOnSamples")}
        </Button>
        <span className="text-theme-xs font-medium rw-faint">
          {t(locale, "submit.sampleResultsTitle")}
        </span>
        <span className="ml-auto tabular-nums rw-faint">
          {busy ? (
            <Loading variant="dotsFade" label={t(locale, "submit.sampleConsoleRunning")} />
          ) : state.status === "ok" ? (
            t(locale, "submit.matches")
          ) : state.status === "bad" ? (
            t(locale, "submit.outputMismatch")
          ) : (
            t(locale, "submit.sampleConsoleReady")
          )}
        </span>
      </div>

      <p
        className="border-b rw-divider px-3 py-2 font-mono text-theme-xs rw-dim"
        role="status"
      >
        {state.log}
      </p>

      {selected && (
        <div className="grid gap-0 sm:grid-cols-3">
          <SampleField
            label={t(locale, "problem.sampleInput")}
            text={selected.input}
          />
          <SampleField
            label={t(locale, "problem.sampleOutput")}
            text={state.got}
            highlight={
              state.outputStatus === "ok"
                ? "ok"
                : state.outputStatus === "bad"
                  ? "bad"
                  : undefined
            }
          />
          <SampleField
            label={t(locale, "problem.sampleAnswer")}
            text={selected.expected}
          />
        </div>
      )}
    </section>
  );
}

function SampleField({
  label,
  text,
  highlight,
}: {
  label: string;
  text: string;
  highlight?: "ok" | "bad";
}) {
  const ring =
    highlight === "ok"
      ? "ring-1 ring-[var(--rw-ok)]"
      : highlight === "bad"
        ? "ring-1 ring-[var(--rw-bad)]"
        : "";
  return (
    <div className={`border-t sm:border-t-0 sm:border-l rw-divider p-2 ${ring}`}>
      <p className="mb-1 text-theme-2xs font-semibold uppercase tracking-wide rw-faint">
        {label}
      </p>
      <pre className="max-h-40 overflow-auto rw-radius-sm rw-field-bg p-2 font-mono text-theme-xs rw-strong whitespace-pre-wrap break-words">
        {text || "—"}
      </pre>
    </div>
  );
}
