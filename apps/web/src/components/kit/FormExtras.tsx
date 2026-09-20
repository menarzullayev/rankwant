"use client";

import { useLayoutEffect, useRef, type ReactNode } from "react";

import { Icon } from "@/components/ui/Icon";
import { FM_BOX } from "@/components/form/chrome";
import type { TipKind } from "@/lib/theme/kit";

const INFO_TIP: TipKind = "info";
const RICH_TIP: TipKind = "rich";

export function FormIconSwitch({
  checked,
  onChange,
  onLabel,
  offLabel,
}: {
  checked: boolean;
  onChange: (on: boolean) => void;
  onLabel: string;
  offLabel: string;
}) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      className="rw-kit-icon-sw"
      data-kit-check="icon"
      aria-label={checked ? onLabel : offLabel}
      onClick={() => onChange(!checked)}
    >
      <span className="is-off">
        <Icon name="system.dark" size="sm" />
      </span>
      <span className="is-on">
        <Icon name="system.light" size="sm" />
      </span>
    </button>
  );
}

export function FormSeg3<T extends string>({
  value,
  options,
  label,
  onChange,
}: {
  value: T;
  options: readonly { value: T; label: string }[];
  label: string;
  onChange: (next: T) => void;
}) {
  return (
    <div className="rw-kit-seg3" role="radiogroup" aria-label={label} data-kit-check="seg3">
      {options.map((opt) => (
        <button
          key={opt.value}
          type="button"
          role="radio"
          aria-checked={opt.value === value}
          onClick={() => onChange(opt.value)}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}

export function FormStepper({
  value,
  options,
  label,
  onChange,
}: {
  value: number;
  options: readonly string[];
  label: string;
  onChange: (next: number) => void;
}) {
  const last = options.length - 1;
  return (
    <div className="rw-kit-stepper" data-kit-check="stepper" aria-label={label}>
      <button
        type="button"
        aria-label="-"
        disabled={value <= 0}
        onClick={() => onChange(Math.max(0, value - 1))}
      >
        −
      </button>
      <output>{options[value] ?? options[0]}</output>
      <button
        type="button"
        aria-label="+"
        disabled={value >= last}
        onClick={() => onChange(Math.min(last, value + 1))}
      >
        +
      </button>
    </div>
  );
}

export function FormTreeItem({
  label,
  checked,
  indeterminate,
  nested,
  onChange,
  extra,
}: {
  label: string;
  checked: boolean;
  indeterminate?: boolean;
  nested?: boolean;
  onChange: () => void;
  extra?: ReactNode;
}) {
  const ref = useRef<HTMLInputElement>(null);
  useLayoutEffect(() => {
    if (ref.current) ref.current.indeterminate = Boolean(indeterminate);
  }, [indeterminate]);
  return (
    <label className="rw-kit-tree-item" data-nested={nested || undefined} data-kit-check="tree">
      <input
        ref={ref}
        type="checkbox"
        className={FM_BOX}
        checked={checked}
        onChange={onChange}
      />
      <span>{label}</span>
      {extra}
    </label>
  );
}

export function InfoMark({ text, title }: { text: string; title?: string }) {
  let kind: TipKind = INFO_TIP;
  if (title) kind = RICH_TIP;
  return (
    <span
      className="rw-kit-info"
      data-tip={text}
      data-tip-kind={kind}
      data-tip-title={title}
      tabIndex={0}
    >
      i
    </span>
  );
}
