"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useRef,
  useState,
  useSyncExternalStore,
} from "react";

import type { AttemptDetail } from "@/lib/api";

import type { runSampleCallback } from "./problem-solve-types";

export type SampleInlineState =
  | { status: "idle" }
  | { status: "running" }
  | { status: "done"; ok: boolean; message: string };

export type VerdictLayoutMode = "tab" | "column" | "toast" | "modal";

const VERDICT_LAYOUT_KEY = "rw:verdict-layout";
const LAYOUTS: VerdictLayoutMode[] = ["tab", "column", "toast", "modal"];

const layoutListeners = new Set<() => void>();

function readLayout(): VerdictLayoutMode {
  try {
    const raw = localStorage.getItem(VERDICT_LAYOUT_KEY);
    if (raw && LAYOUTS.includes(raw as VerdictLayoutMode))
      return raw as VerdictLayoutMode;
  } catch {
    // private mode
  }
  return "tab";
}

function writeLayout(mode: VerdictLayoutMode) {
  try {
    localStorage.setItem(VERDICT_LAYOUT_KEY, mode);
  } catch {
    // ignore
  }
  layoutListeners.forEach((l) => l());
}

function subscribeLayout(cb: () => void) {
  layoutListeners.add(cb);
  return () => layoutListeners.delete(cb);
}

export function useVerdictLayoutMode(): [
  VerdictLayoutMode,
  (mode: VerdictLayoutMode) => void,
] {
  const mode = useSyncExternalStore(
    subscribeLayout,
    readLayout,
    () => "tab" as VerdictLayoutMode,
  );
  return [mode, writeLayout];
}

type ProblemSolveContextValue = {
  inlineSamples: Record<number, SampleInlineState>;
  setInlineSample: (order: number, state: SampleInlineState) => void;
  runSample: (order: number) => void;
  registerRunSample: (fn: runSampleCallback | null) => void;
  attempt: AttemptDetail | null;
  setAttempt: (a: AttemptDetail | null) => void;
  submitBusy: boolean;
  setSubmitBusy: (v: boolean) => void;
  modalOpen: boolean;
  setModalOpen: (v: boolean) => void;
};

const ProblemSolveContext = createContext<ProblemSolveContextValue | null>(
  null,
);

export function ProblemSolveProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [inlineSamples, setInlineSamples] = useState<
    Record<number, SampleInlineState>
  >({});
  const [attempt, setAttempt] = useState<AttemptDetail | null>(null);
  const [submitBusy, setSubmitBusy] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const runSampleRef = useRef<runSampleCallback | null>(null);

  const setInlineSample = useCallback(
    (order: number, state: SampleInlineState) => {
      setInlineSamples((prev) => ({ ...prev, [order]: state }));
    },
    [],
  );

  const registerRunSample = useCallback((fn: runSampleCallback | null) => {
    runSampleRef.current = fn;
  }, []);

  const runSample = useCallback((order: number) => {
    void runSampleRef.current?.(order);
  }, []);

  const value = useMemo(
    () => ({
      inlineSamples,
      setInlineSample,
      runSample,
      registerRunSample,
      attempt,
      setAttempt,
      submitBusy,
      setSubmitBusy,
      modalOpen,
      setModalOpen,
    }),
    [
      inlineSamples,
      setInlineSample,
      runSample,
      registerRunSample,
      attempt,
      submitBusy,
      modalOpen,
    ],
  );

  return (
    <ProblemSolveContext.Provider value={value}>
      {children}
    </ProblemSolveContext.Provider>
  );
}

export function useProblemSolve() {
  return useContext(ProblemSolveContext);
}
