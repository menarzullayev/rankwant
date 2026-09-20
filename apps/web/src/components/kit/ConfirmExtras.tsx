"use client";

import { useState } from "react";

import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";

export function InlineConfirm({
  label,
  prompt,
  confirmLabel,
  danger,
  disabled,
  onConfirm,
}: {
  label: string;
  prompt?: string;
  confirmLabel?: string;
  danger?: boolean;
  disabled?: boolean;
  onConfirm: () => void;
}) {
  const locale = useLocale();
  const [open, setOpen] = useState(false);
  const go = confirmLabel ?? t(locale, "common.yes");

  if (!open) {
    return (
      <button
        type="button"
        disabled={disabled}
        className={`text-theme-xs ${danger ? "rw-bad-ink" : "rw-accent-ink"} hover:underline disabled:opacity-40`}
        onClick={() => setOpen(true)}
      >
        {label}
      </button>
    );
  }

  return (
    <span className="rw-kit-inline" data-kit-confirm="inline">
      <span className="warn">{prompt ?? t(locale, "kit.sure")}</span>
      <button
        type="button"
        className={`text-theme-xs font-medium ${danger ? "rw-bad-ink" : "rw-accent-ink"} hover:underline`}
        onClick={() => {
          setOpen(false);
          onConfirm();
        }}
      >
        {go}
      </button>
      <button
        type="button"
        className="text-theme-xs rw-dim hover:underline"
        onClick={() => setOpen(false)}
      >
        {t(locale, "admin.cancel")}
      </button>
    </span>
  );
}

export function HoldButton({
  label,
  danger,
  disabled,
  holdMs = 900,
  onConfirm,
}: {
  label: string;
  danger?: boolean;
  disabled?: boolean;
  holdMs?: number;
  onConfirm: () => void;
}) {
  const locale = useLocale();
  const [pct, setPct] = useState(0);

  return (
    <button
      type="button"
      disabled={disabled}
      className={`rw-kit-hold${danger ? " is-danger" : ""}`}
      data-tip={t(locale, "kit.holdHint")}
      data-tip-kind="soft"
      onPointerDown={(event) => {
        if (disabled || event.button !== 0) return;
        const node = event.currentTarget;
        const start = performance.now();
        const frame = { current: 0 };
        let done = false;
        const finish = (ok: boolean) => {
          if (done) return;
          done = true;
          window.cancelAnimationFrame(frame.current);
          setPct(0);
          try {
            if (node.hasPointerCapture(event.pointerId)) {
              node.releasePointerCapture(event.pointerId);
            }
          } catch {
            /* capture already gone */
          }
          node.removeEventListener("pointerup", onUp);
          node.removeEventListener("pointerleave", onUp);
          if (ok) onConfirm();
        };
        const onUp = () => finish(false);
        const tick = (now: number) => {
          const next = Math.min(100, ((now - start) / holdMs) * 100);
          setPct(next);
          if (next >= 100) {
            finish(true);
            return;
          }
          frame.current = window.requestAnimationFrame(tick);
        };
        frame.current = window.requestAnimationFrame(tick);
        try {
          node.setPointerCapture(event.pointerId);
        } catch {
          /* some browsers refuse capture */
        }
        node.addEventListener("pointerup", onUp);
        node.addEventListener("pointerleave", onUp);
      }}
    >
      <span className="rw-kit-hold-bar" style={{ width: `${pct}%` }} />
      <span className="rw-kit-hold-lab">{label}</span>
    </button>
  );
}
