"use client";

import { useEffect, useId, useRef, useState } from "react";

import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";

import { SignInLinks, gateTitle, useReturnTo, type GateReason } from "./SignInGate";

/** The props that make a control the dialog's button. A `trigger` must
 *  spread them onto a real `<button>`. */
export type TriggerProps = {
  type: "button";
  onClick: () => void;
  "aria-haspopup": "dialog";
  "aria-expanded": boolean;
  "aria-controls": string;
};

/** A small action (follow, vote, favourite, report, comment) for a guest.
 *
 *  The control stays where it is — a guest sees what the page can do — and
 *  pressing it opens a small dialog instead of leaving the page (ADR-0054,
 *  decision 6). Render this in the guest branch of the action:
 *
 *  ```tsx
 *  if (!user)
 *    return (
 *      <GuestPrompt
 *        reason="follow"
 *        trigger={(props) => <Button {...props}>Follow</Button>}
 *      />
 *    );
 *  ```
 *
 *  Escape and a press outside close it; Escape returns focus to the control.
 */
export function GuestPrompt({
  reason,
  trigger,
  align = "start",
}: {
  reason: GateReason;
  trigger: (props: TriggerProps) => React.ReactNode;
  /** Which edge of the control the dialog lines up with. */
  align?: "start" | "end";
}) {
  const locale = useLocale();
  const next = useReturnTo();
  const [open, setOpen] = useState(false);
  const host = useRef<HTMLSpanElement>(null);
  const id = useId();

  useEffect(() => {
    if (!open) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key !== "Escape") return;
      setOpen(false);
      host.current?.querySelector<HTMLElement>("button")?.focus();
    };
    const onPointer = (event: PointerEvent) => {
      if (!host.current?.contains(event.target as Node)) setOpen(false);
    };
    document.addEventListener("keydown", onKey);
    document.addEventListener("pointerdown", onPointer);
    return () => {
      document.removeEventListener("keydown", onKey);
      document.removeEventListener("pointerdown", onPointer);
    };
  }, [open]);

  return (
    <span ref={host} className="relative inline-block" data-guest-prompt={reason}>
      {trigger({
        type: "button",
        onClick: () => setOpen((value) => !value),
        "aria-haspopup": "dialog",
        "aria-expanded": open,
        "aria-controls": id,
      })}
      {open && (
        <div
          id={id}
          role="dialog"
          aria-label={t(locale, gateTitle(reason))}
          className={`absolute top-full z-30 mt-2 w-64 max-w-[calc(100vw-2rem)] space-y-3 border p-4 text-left rw-radius rw-surface rw-shadow rw-line ${
            align === "end" ? "right-0" : "left-0"
          }`}
        >
          <p className="text-theme-sm font-semibold rw-strong">{t(locale, gateTitle(reason))}</p>
          <SignInLinks next={next} />
        </div>
      )}
    </span>
  );
}
