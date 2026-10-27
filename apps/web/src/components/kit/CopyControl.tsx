"use client";

import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";

import { Icon } from "@/components/ui/Icon";
import { useOverlay } from "@/components/overlay/OverlayHost";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import type { CopyShape, TipKind } from "@/lib/theme/kit";

/** The one copy control (HITL 2026-10-27, look C of the prototype).
 *
 *  Every place that copies text goes through `write()` and the same four
 *  states: idle, busy (text fetched from the server), done, fail. The answer
 *  is on the button itself — the icon turns into a check and the label says
 *  «copied» for 1.5 s. A toast appears only when copying failed, because then
 *  there is nothing on the button the person can act on.
 *
 *  Three shapes plus a cell: `icon` (no text; code corners, table rows),
 *  `label` (icon and text; toolbars), `field` (the value with the button
 *  attached; links and codes), `cell` (the value itself is the button; admin
 *  tables). The button is always visible: a hover-only icon cannot be found
 *  on a phone. */

const BALLOON_TIP: TipKind = "balloon";
const DONE_MS = 1500;
const FAIL_MS = 2200;

export type CopyState = "idle" | "busy" | "done" | "fail";

/** Text, or a function that fetches it (the attempts table asks the server
 *  for the source only when the button is pressed). */
export type CopySource = string | (() => Promise<string>);

async function write(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    return false;
  }
}

/** The only place that writes to the clipboard. Returns the visible state and
 *  `run`; the failure toast is raised here so no caller can forget it. */
export function useCopy(): {
  state: CopyState;
  run: (source: CopySource) => Promise<boolean>;
} {
  const locale = useLocale();
  const overlay = useOverlay();
  const [state, setState] = useState<CopyState>("idle");
  const timer = useRef(0);
  const busy = useRef(false);

  useEffect(() => () => window.clearTimeout(timer.current), []);

  const settle = useCallback((next: CopyState, ms: number) => {
    setState(next);
    window.clearTimeout(timer.current);
    timer.current = window.setTimeout(() => setState("idle"), ms);
  }, []);

  const run = useCallback(
    async (source: CopySource) => {
      if (busy.current) return false;
      busy.current = true;
      try {
        if (typeof source !== "string") setState("busy");
        const text = typeof source === "string" ? source : await source();
        if (!text || !(await write(text))) {
          overlay.toast(t(locale, "problem.copyFailed"));
          settle("fail", FAIL_MS);
          return false;
        }
        settle("done", DONE_MS);
        return true;
      } catch {
        overlay.toast(t(locale, "problem.copyFailed"));
        settle("fail", FAIL_MS);
        return false;
      } finally {
        busy.current = false;
      }
    },
    [locale, overlay, settle],
  );

  return { state, run };
}

export function CopyButton({
  text,
  shape = "icon",
  label,
  copiedLabel,
  icon = "action.copy",
  size = "md",
  display,
  shareTitle,
  className = "",
  stopPropagation = false,
}: {
  text: CopySource;
  shape?: Exclude<CopyShape, "cell">;
  /** Visible text for `label` and `field`, and the accessible name for `icon`. */
  label?: string;
  copiedLabel?: string;
  /** Icon key before copying (`action.share` for the share button). */
  icon?: string;
  size?: "md" | "sm";
  /** `field` only: what to show instead of the raw text. */
  display?: string;
  /** Where the system share sheet exists, open it instead of copying. */
  shareTitle?: string;
  className?: string;
  /** For a button inside a clickable row. */
  stopPropagation?: boolean;
}) {
  const locale = useLocale();
  const { state, run } = useCopy();
  const copyLabel = label ?? t(locale, "problem.copy");
  const doneLabel = copiedLabel ?? t(locale, "problem.copied");
  const failLabel = t(locale, "problem.copyFailed");

  let lab = copyLabel;
  let glyph = icon;
  if (state === "done") {
    lab = doneLabel;
    glyph = "status.ok";
  } else if (state === "fail") {
    lab = failLabel;
    glyph = "status.bad";
  }

  async function press(event: React.MouseEvent) {
    if (stopPropagation) event.stopPropagation();
    if (shareTitle && typeof navigator.share === "function") {
      try {
        const url = typeof text === "string" ? text : await text();
        await navigator.share({ title: shareTitle, url });
      } catch {
        // The person closed the sheet: not an error.
      }
      return;
    }
    await run(text);
  }

  const button = (
    <button
      type="button"
      data-copy-shape={shape}
      data-size={size}
      data-state={state === "idle" ? undefined : state}
      className={`rw-copy rw-focus-ring ${shape === "field" ? "" : className}`}
      onClick={(event) => void press(event)}
      disabled={state === "busy"}
      aria-label={shape === "icon" ? lab : undefined}
      data-tip={shape === "icon" ? lab : undefined}
      data-tip-kind={shape === "icon" ? BALLOON_TIP : undefined}
    >
      <Icon name={glyph} className="size-4" />
      {shape !== "icon" && <span className="rw-copy-lab">{lab}</span>}
    </button>
  );

  // The change of text is announced; the button's own name would not be.
  const live = (
    <span className="sr-only" role="status">
      {state === "done" ? doneLabel : state === "fail" ? failLabel : ""}
    </span>
  );

  if (shape === "field") {
    return (
      <div className={`rw-copy-field rw-field-bg ${className}`}>
        <span className="rw-copy-val">{display ?? (typeof text === "string" ? text : "")}</span>
        {button}
        {live}
      </div>
    );
  }
  return (
    <>
      {button}
      {live}
    </>
  );
}

/** A table cell whose value is the button (admin id/slug columns). */
export function CopyCell({ text }: { text: string }) {
  const locale = useLocale();
  const { state, run } = useCopy();
  const name = state === "done" ? t(locale, "problem.copied") : t(locale, "problem.copy");
  return (
    <button
      type="button"
      data-copy-shape="cell"
      data-state={state === "idle" ? undefined : state}
      className="rw-copy-cell rw-focus-ring"
      onClick={() => void run(text)}
      aria-label={`${name}: ${text}`}
    >
      <span className="truncate">{text}</span>
      <Icon name={state === "done" ? "status.ok" : "action.copy"} className="size-3.5" />
    </button>
  );
}

/** A code block with its name and the copy button in the bar. */
export function CodeCopy({
  text,
  filename,
  children,
}: {
  text: string;
  filename?: string;
  children: ReactNode;
}) {
  const locale = useLocale();
  return (
    <div className="rw-kit-code">
      <div className="rw-kit-code-bar">
        <span className="rw-faint">{filename ?? t(locale, "attempt.source")}</span>
        <CopyButton text={text} shape="label" size="sm" />
      </div>
      {children}
    </div>
  );
}
