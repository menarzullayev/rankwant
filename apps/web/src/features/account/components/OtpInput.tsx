"use client";

import { useRef, useState } from "react";

/** A six-cell one-time code field built on ONE real input.
 *
 *  Six separate inputs break the things people rely on: pasting the whole
 *  code, the phone's "from messages" suggestion (`one-time-code`), and a
 *  screen reader that should hear one field, not six. The input is laid over
 *  the cells (invisible, full size), so typing, paste and autofill all land in
 *  it, and the cells only draw what it holds. */
export function OtpInput({
  label,
  value,
  onChange,
  onComplete,
  length = 6,
  invalid = false,
  disabled = false,
}: {
  /** Accessible name of the field. */
  label: string;
  value: string;
  onChange: (value: string) => void;
  /** Called once when the last cell is filled. */
  onComplete?: (value: string) => void;
  length?: number;
  invalid?: boolean;
  disabled?: boolean;
}) {
  const [focused, setFocused] = useState(false);
  const input = useRef<HTMLInputElement>(null);

  return (
    <div className="relative mx-auto w-fit">
      <input
        ref={input}
        value={value}
        disabled={disabled}
        inputMode="numeric"
        autoComplete="one-time-code"
        pattern="[0-9]*"
        maxLength={length}
        aria-label={label}
        aria-invalid={invalid || undefined}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        onChange={(event) => {
          // Digits only: a pasted "123 456" or "123-456" still works.
          const digits = event.target.value.replace(/\D/g, "").slice(0, length);
          onChange(digits);
          if (digits.length === length) onComplete?.(digits);
        }}
        className="absolute inset-0 z-10 h-full w-full cursor-text opacity-0"
      />
      <div aria-hidden className="flex gap-2">
        {Array.from({ length }, (_, i) => {
          const active = focused && i === Math.min(value.length, length - 1);
          return (
            <span
              key={i}
              className={`grid h-14 w-11 place-items-center rw-radius-sm border text-xl font-semibold rw-strong rw-field-bg ${
                invalid ? "rw-bad-ink border-current" : active ? "border-[var(--rw-accent)] ring-1 ring-[var(--rw-accent)]" : "rw-line"
              }`}
            >
              {value[i] ?? ""}
            </span>
          );
        })}
      </div>
    </div>
  );
}
