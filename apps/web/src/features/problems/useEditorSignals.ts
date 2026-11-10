"use client";

import { useCallback, useEffect, useRef } from "react";

/** What the editor tells the jury about a contest solution (ADR-0055, part 4).
 *
 *  Pastes into the editor (Monaco's hidden textarea raises a native `paste`
 *  that bubbles to the wrapper), times the page lost focus, and how long it
 *  has been open. Nothing about the content of other tabs or the clipboard
 *  beyond the pasted length. Off outside a contest.
 */
export type EditorSignals = {
  pasted_chars: number;
  largest_paste: number;
  paste_count: number;
  blur_count: number;
  active_ms: number;
};

export function useEditorSignals(enabled: boolean) {
  const stats = useRef({ pasted: 0, largest: 0, count: 0, blurs: 0 });
  const opened = useRef(0);

  useEffect(() => {
    if (!enabled) return;
    opened.current = Date.now();
    const away = () => {
      stats.current.blurs += 1;
    };
    const hidden = () => {
      if (document.visibilityState === "hidden") away();
    };
    window.addEventListener("blur", away);
    document.addEventListener("visibilitychange", hidden);
    return () => {
      window.removeEventListener("blur", away);
      document.removeEventListener("visibilitychange", hidden);
    };
  }, [enabled]);

  const onPaste = useCallback(
    (event: React.ClipboardEvent) => {
      if (!enabled) return;
      const size = event.clipboardData?.getData("text")?.length ?? 0;
      stats.current.pasted += size;
      stats.current.largest = Math.max(stats.current.largest, size);
      stats.current.count += 1;
    },
    [enabled],
  );

  const snapshot = useCallback((): EditorSignals | undefined => {
    if (!enabled) return undefined;
    const s = stats.current;
    return {
      pasted_chars: s.pasted,
      largest_paste: s.largest,
      paste_count: s.count,
      blur_count: s.blurs,
      active_ms: Math.max(0, Date.now() - opened.current),
    };
  }, [enabled]);

  return { onPaste, snapshot };
}
