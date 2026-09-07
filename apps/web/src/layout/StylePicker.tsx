"use client";

import { useState } from "react";

import { useStyle } from "@/context/StyleContext";
import { CheckIcon, PaletteIcon } from "@/icons";
import { STYLES } from "./styles";

/** Har qator o'z `data-style` ini oladi — CSS o'zgaruvchilari atribut
 * selektori bilan berilgani uchun namunalar haqiqiy uslub ranglarida
 * chiziladi, alohida preview ranglar ro'yxati kerak emas. */
export default function StylePicker() {
  const { style, setStyle } = useStyle();
  const [open, setOpen] = useState(false);
  const current = STYLES.find((s) => s.id === style);

  return (
    <>
      {open && (
        <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
      )}
      <div className="relative z-50">
        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          aria-label="Uslubni tanlash"
          aria-expanded={open}
          title={current?.label}
          className="flex size-10 items-center justify-center rw-radius-sm border rw-line rw-dim-2 transition rw-hover-bg"
        >
          <PaletteIcon />
        </button>

        {open && (
          <div className="absolute right-0 mt-2 max-h-[70vh] w-64 overflow-y-auto rw-radius border rw-line rw-surface p-1.5 rw-shadow">
            <p className="px-2.5 py-1.5 text-theme-xs rw-faint">
              Ko&apos;rinish
            </p>
            {STYLES.map((s) => (
              <button
                key={s.id}
                type="button"
                onClick={() => {
                  setStyle(s.id);
                  setOpen(false);
                }}
                className="flex w-full items-center gap-2.5 rw-radius-sm px-2.5 py-2 text-left transition rw-hover-bg"
              >
                <span
                  data-style={s.id}
                  aria-hidden
                  className="flex size-8 shrink-0 items-center justify-center gap-1 rw-radius-sm border rw-line rw-surface rw-shadow"
                >
                  <span className="size-2 rounded-full rw-accent-bg" />
                  <span className="h-2 w-1 rw-chip" />
                </span>
                <span className="min-w-0 flex-1">
                  <span className="block truncate text-theme-sm font-medium rw-strong">
                    {s.label}
                  </span>
                  <span className="block truncate text-theme-xs rw-faint">
                    {s.hint}
                  </span>
                </span>
                {s.id === style && (
                  <CheckIcon className="size-4 rw-accent-ink" />
                )}
              </button>
            ))}
          </div>
        )}
      </div>
    </>
  );
}
