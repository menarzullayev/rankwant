"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  useSyncExternalStore,
} from "react";

import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";

import {
  ProblemWorkspaceProvider,
  type ProblemWorkspaceContextValue,
} from "./problem-workspace-context";
import { ProblemSolveProvider } from "./problem-solve-context";

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
const SHEET_H_KEY = "rw:sheet-h";
const COLLAPSE_KEY = "rw:editor-collapsed";
const DEFAULT_SPLIT = 58;
const MIN_SPLIT = 34;
const MAX_SPLIT = 80;
const MIN_SHEET = 40;
const MAX_SHEET = 96;
const DEFAULT_SHEET = 62;

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

function readSheetH(): number {
  try {
    const n = Number(localStorage.getItem(SHEET_H_KEY));
    if (Number.isFinite(n) && n >= MIN_SHEET && n <= MAX_SHEET) return n;
  } catch {
    // private mode
  }
  return DEFAULT_SHEET;
}

function writeSheetH(n: number) {
  try {
    localStorage.setItem(SHEET_H_KEY, String(n));
  } catch {
    // ignore
  }
}

function readCollapsed(): boolean {
  try {
    return localStorage.getItem(COLLAPSE_KEY) === "1";
  } catch {
    return false;
  }
}

function writeCollapsed(v: boolean) {
  try {
    localStorage.setItem(COLLAPSE_KEY, v ? "1" : "0");
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
/** Matn va muharrir alohida `ReactNode` — serverdan klientga uzatiladi.
 *  Har biri layoutda faqat bir marta mount qilinadi (mobil + desktop
 *  ikkalasi bir vaqtda emas). */
export function ProblemWorkspace({
  statement,
  editor,
}: {
  statement: React.ReactNode;
  editor: React.ReactNode;
}) {
  const locale = useLocale();
  const wide = useSyncExternalStore(subscribeWide, readWide, () => false);
  const [splitPct, setSplitPct] = useState(readSplit);
  const [sheetOpen, setSheetOpen] = useState(false);
  const [sheetHPct, setSheetHPct] = useState(readSheetH);
  const [editorCollapsed, setEditorCollapsedState] = useState(readCollapsed);
  const draggingSplit = useRef(false);
  const draggingSheet = useRef(false);
  const hostRef = useRef<HTMLDivElement>(null);
  const sheetRef = useRef<HTMLDivElement>(null);

  const setEditorCollapsed = useCallback((v: boolean) => {
    setEditorCollapsedState(v);
    writeCollapsed(v);
  }, []);

  const ctx = useMemo<ProblemWorkspaceContextValue>(
    () => ({
      wide,
      editorCollapsed,
      setEditorCollapsed,
    }),
    [wide, editorCollapsed, setEditorCollapsed],
  );

  const onPointerMoveSplit = useCallback((clientX: number) => {
    const host = hostRef.current;
    if (!host) return;
    const rect = host.getBoundingClientRect();
    const pct = ((clientX - rect.left) / rect.width) * 100;
    const next = Math.min(MAX_SPLIT, Math.max(MIN_SPLIT, pct));
    setSplitPct(next);
    writeSplit(next);
  }, []);

  const onPointerMoveSheet = useCallback((clientY: number) => {
    const sheet = sheetRef.current;
    if (!sheet) return;
    const rect = sheet.getBoundingClientRect();
    const pct = ((rect.bottom - clientY) / window.innerHeight) * 100;
    const next = Math.min(MAX_SHEET, Math.max(MIN_SHEET, pct));
    setSheetHPct(next);
    writeSheetH(next);
  }, []);

  useEffect(() => {
    function onMove(e: PointerEvent) {
      if (draggingSplit.current) onPointerMoveSplit(e.clientX);
      if (draggingSheet.current) onPointerMoveSheet(e.clientY);
    }
    function onUp() {
      draggingSplit.current = false;
      draggingSheet.current = false;
    }
    window.addEventListener("pointermove", onMove);
    window.addEventListener("pointerup", onUp);
    return () => {
      window.removeEventListener("pointermove", onMove);
      window.removeEventListener("pointerup", onUp);
    };
  }, [onPointerMoveSplit, onPointerMoveSheet]);

  const sheetStyle = {
    height: `${sheetHPct}vh`,
    maxHeight: "min(96vh, 720px)",
  };

  if (wide) {
    return (
      <ProblemSolveProvider>
        <ProblemWorkspaceProvider value={ctx}>
        <div ref={hostRef} className="flex min-w-0 items-start gap-0">
          <div
            className="min-w-0 shrink-0 space-y-6"
            style={{ width: editorCollapsed ? "100%" : `${splitPct}%` }}
          >
            {statement}
          </div>
          {!editorCollapsed && (
            <>
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
                  draggingSplit.current = true;
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
              <div className="min-w-0 flex-1">{editor}</div>
            </>
          )}
        </div>
        </ProblemWorkspaceProvider>
      </ProblemSolveProvider>
    );
  }

  return (
    <ProblemSolveProvider>
      <ProblemWorkspaceProvider value={ctx}>
      <div className="min-w-0 space-y-6">{statement}</div>

      {!editorCollapsed && (
        <>
          <div
            ref={sheetRef}
            style={sheetStyle}
            className={`fixed inset-x-0 bottom-0 z-40 transform border-t rw-divider rw-panel-bg shadow-[0_-8px_32px_rgba(0,0,0,.12)] transition-transform duration-200 ${
              sheetOpen ? "translate-y-0" : "translate-y-full"
            }`}
            aria-hidden={!sheetOpen}
          >
            <div
              role="separator"
              aria-orientation="horizontal"
              aria-valuemin={MIN_SHEET}
              aria-valuemax={MAX_SHEET}
              aria-valuenow={Math.round(sheetHPct)}
              aria-label={t(locale, "problem.sheetResize")}
              tabIndex={0}
              className="sticky top-0 z-10 flex h-5 cursor-row-resize items-center justify-center border-b rw-divider rw-panel-bg"
              onPointerDown={(e) => {
                draggingSheet.current = true;
                e.currentTarget.setPointerCapture(e.pointerId);
              }}
            >
              <span className="h-1 w-11 rw-radius-sm bg-[var(--rw-line)]" />
            </div>
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
            <div
              className="rw-scroll-y p-4"
              style={{ maxHeight: `calc(${sheetHPct}vh - 4.5rem)` }}
            >
              {editor}
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
            style={
              sheetOpen
                ? { bottom: `calc(${sheetHPct}vh + 10px)` }
                : undefined
            }
          >
            <span className="font-mono text-theme-base">&lt;/&gt;</span>
            {t(locale, "problem.openEditor")}
          </button>
        </>
      )}
    </ProblemWorkspaceProvider>
    </ProblemSolveProvider>
  );
}
