"use client";

import {
  useCallback,
  useRef,
  useState,
  type ReactNode,
} from "react";

import { Icon } from "@/components/ui/Icon";
import { useOverlay } from "@/components/overlay/OverlayHost";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import type { CopyTone, TipKind } from "@/lib/theme/kit";

const KBD_TIP: TipKind = "kbd";
const BALLOON_TIP: TipKind = "balloon";
const COPY_SHORTCUT = "Ctrl+C";

async function write(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    return false;
  }
}

export function CopyButton({
  text,
  tone = "text",
  label,
  copiedLabel,
  kbd,
  className = "",
}: {
  text: string;
  tone?: Exclude<CopyTone, "all">;
  label?: string;
  copiedLabel?: string;
  kbd?: string;
  className?: string;
}) {
  const locale = useLocale();
  const overlay = useOverlay();
  const [done, setDone] = useState(false);
  const copyLabel = label ?? t(locale, "problem.copy");
  const doneLabel = copiedLabel ?? t(locale, "problem.copied");

  async function copy() {
    if (!(await write(text))) {
      overlay.toast(t(locale, "problem.copyFailed"));
      return;
    }
    setDone(true);
    overlay.toast(doneLabel);
    window.setTimeout(() => setDone(false), 1500);
  }

  const lab = done ? doneLabel : copyLabel;
  let tipKind: TipKind = BALLOON_TIP;
  let kbdHint: string | undefined;
  if (tone === "kbd") {
    tipKind = KBD_TIP;
    kbdHint = kbd ?? COPY_SHORTCUT;
  }

  return (
    <button
      type="button"
      data-kit-copy={tone}
      className={`rw-kit-copy ${className}`}
      onClick={() => void copy()}
      aria-label={lab}
      data-tip={lab}
      data-tip-kind={tipKind}
      data-tip-kbd={kbdHint}
    >
      {tone === "ghost" || tone === "hover" ? (
        <Icon name="action.copy" className="size-3.5" />
      ) : tone === "cell" ? (
        <span className="rw-kit-copy-lab">{text}</span>
      ) : (
        <>
          {tone !== "text" ? (
            <Icon name="action.copy" className="size-3.5" />
          ) : null}
          <span className="rw-kit-copy-lab">{tone === "chip" ? text : lab}</span>
          {tone === "kbd" && kbd ? <kbd className="rw-kit-kbd">{kbd}</kbd> : null}
        </>
      )}
    </button>
  );
}

export function CopyAllBar({
  text,
  label,
}: {
  text: string;
  label?: string;
}) {
  return (
    <div className="rw-kit-copy-all" data-kit-copy="all">
      <CopyButton text={text} tone="text" label={label} />
    </div>
  );
}

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
        <CopyButton text={text} tone="code" />
      </div>
      {children}
    </div>
  );
}

export function CopyCell({ text }: { text: string }) {
  return <CopyButton text={text} tone="cell" label={text} />;
}

export function useCopiedFlash(): {
  done: boolean;
  run: (text: string) => Promise<void>;
} {
  const overlay = useOverlay();
  const locale = useLocale();
  const [done, setDone] = useState(false);
  const timer = useRef(0);
  const run = useCallback(
    async (text: string) => {
      if (!(await write(text))) {
        overlay.toast(t(locale, "problem.copyFailed"));
        return;
      }
      setDone(true);
      overlay.toast(t(locale, "problem.copied"));
      window.clearTimeout(timer.current);
      timer.current = window.setTimeout(() => setDone(false), 1500);
    },
    [locale, overlay],
  );
  return { done, run };
}
