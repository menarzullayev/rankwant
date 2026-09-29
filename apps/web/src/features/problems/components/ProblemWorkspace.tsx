"use client";

import {
  useCallback,
  useEffect,
  useRef,
  useState,
  useSyncExternalStore,
} from "react";

import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";

const XL_QUERY = "(min-width: 1280px)";

function subscribeWide(callback: () => void) {
  const mq = window.matchMedia(XL_QUERY);
  mq.addEventListener("change", callback);
  return () => mq.removeEventListener("change", callback);
}

function readWide() {
  return window.matchMedia(XL_QUERY).matches;
}

const SPLIT_KEY = "rw:problem-split-pct";
const DEFAULT_SPLIT = 58;
const MIN_SPLIT = 34;
const MAX_SPLIT = 80;

function readSplit(): number {
  try {
    const n = Number(localStorage.getItem(SPLIT_KEY));
    if (Number.isFinite(n) && n >= MIN_SPLIT && n <= MAX_SPLIT) return n;
  } catch {
    // private mode
  }
  return DEFAULT_SPLIT;
}

function writeSplit(n: number) {
  try {
    localStorage.setItem(SPLIT_KEY, String(n));
  } catch {
    // ignore
  }
}

/** Masala yechish maydoni — prototipdagi split + mobil pastdan varaq.
 *
 * Production AppShell sidebar saqlanadi; bu faqat matn ↔ muharrir
 * bo'linishi. `xl` dan yuqorida sudraladigan vertikal tutqich;
 * pastda matn to'liq kenglik, muharrir «Kod» FAB orqali ochiladi.
 */
/** `render*` — har chaqiruv alohida daraxt; bitta React node ikki joyga
 *  qo'yilsa ikkala shox ham DOM'da qoladi (2× Monaco, 2× sarlavha). */
export function ProblemWorkspace({
  renderStatement,
  renderEditor,
}: {
  renderStatement: () => React.ReactNode;
  renderEditor: () => React.ReactNode;
}) {
  const locale = useLocale();
  const wide = useSyncExternalStore(subscribeWide, readWide, () => false);
  const [splitPct, setSplitPct] = useState(readSplit);
  const [sheetOpen, setSheetOpen] = useState(false);
  const dragging = useRef(false);
  const hostRef = useRef<HTMLDivElement>(null);

  const onPointerMove = useCallback((clientX: number) => {
    const host = hostRef.current;
    if (!host) return;
    const rect = host.getBoundingClientRect();
    const pct = ((clientX - rect.left) / rect.width) * 100;
    const next = Math.min(MAX_SPLIT, Math.max(MIN_SPLIT, pct));
    setSplitPct(next);
    writeSplit(next);
  }, []);

  useEffect(() => {
    function onMove(e: PointerEvent) {
      if (!dragging.current) return;
      onPointerMove(e.clientX);
    }
    function onUp() {
      dragging.current = false;
    }
    window.addEventListener("pointermove", onMove);
    window.addEventListener("pointerup", onUp);
    return () => {
      window.removeEventListener("pointermove", onMove);
      window.removeEventListener("pointerup", onUp);
    };
  }, [onPointerMove]);

  if (wide) {
    return (
      <div ref={hostRef} className="flex min-w-0 items-start gap-0">
        <div
          className="min-w-0 shrink-0 space-y-6"
          style={{ width: `${splitPct}%` }}
        >
          {renderStatement()}
        </div>
        <div
          role="separator"
          aria-orientation="vertical"
          aria-valuemin={MIN_SPLIT}
          aria-valuemax={MAX_SPLIT}
          aria-valuenow={Math.round(splitPct)}
          aria-label={t(locale, "problem.splitResize")}
          tabIndex={0}
          className="group relative z-10 w-2 shrink-0 cursor-col-resize self-stretch"
          onPointerDown={(e) => {
            dragging.current = true;
            e.currentTarget.setPointerCapture(e.pointerId);
          }}
          onKeyDown={(e) => {
            if (e.key === "ArrowLeft")
              setSplitPct((p) => {
                const n = Math.max(MIN_SPLIT, p - 2);
                writeSplit(n);
                return n;
              });
            if (e.key === "ArrowRight")
              setSplitPct((p) => {
                const n = Math.min(MAX_SPLIT, p + 2);
                writeSplit(n);
                return n;
              });
          }}
        >
          <span className="absolute inset-y-0 left-1/2 w-px -translate-x-1/2 bg-[var(--rw-line)] group-hover:bg-[var(--rw-accent)] group-focus-visible:bg-[var(--rw-accent)]" />
        </div>
        <div className="min-w-0 flex-1">{renderEditor()}</div>
      </div>
    );
  }

  return (
    <>
      <div className="min-w-0 space-y-6">{renderStatement()}</div>

      <div
        className={`fixed inset-x-0 bottom-0 z-40 max-h-[min(92vh,720px)] transform border-t rw-divider rw-panel-bg shadow-[0_-8px_32px_rgba(0,0,0,.12)] transition-transform duration-200 ${
          sheetOpen ? "translate-y-0" : "translate-y-full"
        }`}
        aria-hidden={!sheetOpen}
      >
        <div className="flex items-center justify-between border-b rw-divider px-4 py-2">
          <span className="text-theme-sm font-semibold rw-strong">
            {t(locale, "submit.solution")}
          </span>
          <button
            type="button"
            onClick={() => setSheetOpen(false)}
            className="rw-radius-sm px-2 py-1 text-theme-sm rw-dim rw-hover-bg rw-focus-ring"
          >
            {t(locale, "problem.closeEditor")}
          </button>
        </div>
        <div className="max-h-[calc(min(92vh,720px)-3rem)] overflow-y-auto p-4">
          {renderEditor()}
        </div>
      </div>

      {sheetOpen && (
        <button
          type="button"
          aria-label={t(locale, "problem.closeEditor")}
          className="fixed inset-0 z-30 bg-black/40"
          onClick={() => setSheetOpen(false)}
        />
      )}

      <button
        type="button"
        aria-expanded={sheetOpen}
        onClick={() => setSheetOpen((o) => !o)}
        className="fixed bottom-20 right-4 z-30 inline-flex items-center gap-2 rw-radius-full rw-accent-bg px-4 py-2.5 text-theme-sm font-semibold rw-btn-label shadow-lg rw-focus-ring"
      >
        <span className="font-mono text-theme-base">&lt;/&gt;</span>
        {t(locale, "problem.openEditor")}
      </button>
    </>
  );
}
