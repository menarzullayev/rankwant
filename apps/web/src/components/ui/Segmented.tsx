"use client";

import Link from "next/link";
import type { Route } from "next";
import { useRef } from "react";

/** Guruh tugmalar — bir necha ko'rinishdan bittasini tanlash (D61 ⑧).
 *
 *  Ikki rejim, chunki ikkalasi ham haqiqiy:
 *
 *  1. **Holat** (`onChange`) — tanlov React holatida qoladi.
 *     ARIA: `role="radiogroup"` + `role="radio"`.
 *  2. **Navigatsiya** (`href`) — tanlov URL'da qoladi, ya'ni sahifani
 *     ulashsa ham o'sha ko'rinish ochiladi. ARIA: `role="group"` +
 *     havolalar (`aria-current`). `role="radio"` havolaga qo'yilmaydi —
 *     u tugma roli, havola esa navigatsiya.
 *
 *  ⚠️ Ilgari `SolvedTab` da `role="tablist"`/`role="tab"` ishlatilgan edi,
 *  lekin `role="tabpanel"` yo'q edi. Bu noto'g'ri ARIA: ekran o'quvchi
 *  «tab» deb e'lon qiladi, keyin tegishli panelni topa olmaydi.
 *
 *  ⚠️ Klaviatura (faqat holat rejimida): radiogroup'da strelkalar ishlashi
 *  shart, Tab esa guruhdan bir marta o'tadi (roving tabindex).
 */
type Option<T extends string> = {
  value: T;
  label: string;
  icon?: React.ReactNode;
  /** Berilsa — havola rejimi (navigatsiya). */
  href?: Route;
};

export function Segmented<T extends string>({
  value,
  onChange,
  options,
  label,
  className = "",
}: {
  value: T;
  /** Faqat holat rejimida kerak. */
  onChange?: (next: T) => void;
  options: Option<T>[];
  /** Guruh nomi — ekran o'quvchi nima tanlanayotganini eshitadi. */
  label: string;
  className?: string;
}) {
  const refs = useRef<(HTMLElement | null)[]>([]);
  const nav = options.some((o) => o.href);

  const move = (from: number, delta: number) => {
    const n = options.length;
    const next = (from + delta + n) % n;
    onChange?.(options[next].value);
    refs.current[next]?.focus();
  };

  const onKey = (e: React.KeyboardEvent, i: number) => {
    if (e.key === "ArrowRight" || e.key === "ArrowDown") {
      e.preventDefault();
      move(i, 1);
    } else if (e.key === "ArrowLeft" || e.key === "ArrowUp") {
      e.preventDefault();
      move(i, -1);
    } else if (e.key === "Home") {
      e.preventDefault();
      move(0, 0);
    } else if (e.key === "End") {
      e.preventDefault();
      move(options.length - 1, 0);
    }
  };

  const box = `inline-flex overflow-hidden rw-radius-sm border rw-divider ${className}`;

  if (nav) {
    return (
      <div role="group" aria-label={label} className={box}>
        {options.map((o) => {
          const on = o.value === value;
          return (
            <Link
              key={o.value}
              href={(o.href ?? "#") as Route}
              aria-current={on ? "page" : undefined}
              className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-theme-sm font-medium rw-focus-ring ${
                on ? "rw-accent-soft rw-accent-ink" : "rw-dim rw-hover-bg"
              }`}
            >
              {o.icon}
              <span>{o.label}</span>
            </Link>
          );
        })}
      </div>
    );
  }

  return (
    <div role="radiogroup" aria-label={label} className={box}>
      {options.map((o, i) => {
        const on = o.value === value;
        return (
          <button
            key={o.value}
            ref={(n) => {
              refs.current[i] = n;
            }}
            type="button"
            role="radio"
            aria-checked={on}
            tabIndex={on ? 0 : -1}
            onClick={() => onChange?.(o.value)}
            onKeyDown={(e) => onKey(e, i)}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-theme-sm font-medium rw-focus-ring ${
              on ? "rw-accent-soft rw-accent-ink" : "rw-dim rw-hover-bg"
            }`}
          >
            {o.icon}
            <span>{o.label}</span>
          </button>
        );
      })}
    </div>
  );
}
