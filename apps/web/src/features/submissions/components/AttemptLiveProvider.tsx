"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { useRouter } from "next/navigation";

import {
  type AttemptLiveEventPayload,
  type AttemptLivePatch,
} from "@/features/submissions/attemptLiveOverlay";
import {
  type AttemptLiveState,
  emptyLiveState,
  reduceLiveState,
} from "@/features/submissions/attemptLiveState";
import {
  EVENT_ATTEMPT_PROGRESS,
  EVENT_ATTEMPT_QUEUED,
  EVENT_ATTEMPT_FINISHED,
  EVENT_COMPILATION_FINISHED,
  EVENT_COMPILATION_STARTED,
  EVENT_RESYNC,
  EVENT_TEST_FINISHED,
  EVENT_TEST_STARTED,
  EVENT_VERDICT,
  useEventStream,
} from "@/lib/useEventStream";
import { isPendingVerdict } from "@/lib/theme/verdict";
import { runningTargetFrom } from "@/features/submissions/runningTestStepper";

const REFRESH_DEBOUNCE_MS = 400;
const POLL_MS = 12_000;

type PatchServerHint = {
  verdict: string;
  running_test_index: number | null;
};

type Ctx = {
  getPatch: (attemptId: number, server?: PatchServerHint) => AttemptLivePatch | undefined;
  getLiveState: (attemptId: number) => AttemptLiveState | undefined;
};

const AttemptLiveContext = createContext<Ctx | null>(null);

export function useAttemptLive(): Ctx {
  const ctx = useContext(AttemptLiveContext);
  if (!ctx) {
    throw new Error("useAttemptLive must be used within AttemptLiveProvider");
  }
  return ctx;
}

export function useAttemptLiveOptional(): Ctx | null {
  return useContext(AttemptLiveContext);
}

/** Masala urinishlari — SSE + jonli testlar ro'yxati (haqiqiy judge hodisalari). */
export function AttemptLiveProvider({
  problem,
  children,
}: {
  problem: string;
  children: ReactNode;
}) {
  const router = useRouter();
  const [patches, setPatches] = useState<Record<number, AttemptLivePatch>>({});
  const [liveById, setLiveById] = useState<Record<number, AttemptLiveState>>({});
  const seenEventIds = useRef(new Set<string>());
  const refreshTimer = useRef<number | null>(null);

  const scheduleRefresh = useCallback(
    (delayMs: number) => {
      if (refreshTimer.current !== null) return;
      refreshTimer.current = window.setTimeout(() => {
        refreshTimer.current = null;
        router.refresh();
      }, delayMs);
    },
    [router],
  );

  useEffect(
    () => () => {
      if (refreshTimer.current !== null) window.clearTimeout(refreshTimer.current);
    },
    [],
  );

  useEffect(() => {
    const poll = window.setInterval(() => scheduleRefresh(REFRESH_DEBOUNCE_MS), POLL_MS);
    return () => window.clearInterval(poll);
  }, [scheduleRefresh]);

  const ingest = useCallback(
    (name: string, data: AttemptLiveEventPayload | null, eventId?: string) => {
      if (eventId) {
        if (seenEventIds.current.has(eventId)) return;
        seenEventIds.current.add(eventId);
        if (seenEventIds.current.size > 4096) {
          seenEventIds.current.clear();
        }
      }
      const raw = data?.attempt_id;
      const id = typeof raw === "number" ? raw : raw != null ? Number(raw) : NaN;
      if (!Number.isFinite(id)) return;

      setLiveById((prev) => ({
        ...prev,
        [id]: reduceLiveState(prev[id] ?? emptyLiveState(), name, data as Record<string, unknown>),
      }));

      setPatches((prev) => {
        const merged: AttemptLivePatch = {
          ...prev[id],
          ...(data?.verdict !== undefined ? { verdict: data.verdict } : {}),
          ...(data?.running_test_index !== undefined
            ? { running_test_index: data.running_test_index }
            : {}),
        };
        const same =
          prev[id]?.verdict === merged.verdict &&
          prev[id]?.running_test_index === merged.running_test_index;
        if (same) return prev;
        return { ...prev, [id]: merged };
      });
    },
    [],
  );

  const matchesProblem = useCallback(
    (data: unknown) => {
      const payload = data as AttemptLiveEventPayload | null;
      return !payload?.problem || payload.problem === problem;
    },
    [problem],
  );

  useEventStream({
    problem,
    onEvent: (name, data, meta) => {
      if (name === EVENT_RESYNC) {
        scheduleRefresh(REFRESH_DEBOUNCE_MS);
        return;
      }
      const liveEvents = [
        EVENT_VERDICT,
        EVENT_ATTEMPT_FINISHED,
        EVENT_ATTEMPT_QUEUED,
        EVENT_ATTEMPT_PROGRESS,
        EVENT_TEST_STARTED,
        EVENT_COMPILATION_STARTED,
        EVENT_COMPILATION_FINISHED,
        EVENT_TEST_FINISHED,
      ];
      if (!liveEvents.includes(name)) return;
      if (!matchesProblem(data)) return;
      ingest(name, data as AttemptLiveEventPayload, meta?.eventId);
      if (name === EVENT_VERDICT || name === EVENT_ATTEMPT_FINISHED) {
        scheduleRefresh(REFRESH_DEBOUNCE_MS);
      }
    },
  });

  const getPatch = useCallback(
    (attemptId: number, server?: PatchServerHint): AttemptLivePatch | undefined => {
      const patch = patches[attemptId];
      const live = liveById[attemptId];
      const verdict = patch?.verdict ?? live?.verdict ?? server?.verdict;
      const target = runningTargetFrom(
        patch,
        server?.verdict ?? "PENDING",
        server?.running_test_index ?? null,
      );
      const runningIndex =
        live?.runningIndex ??
        (target != null && isPendingVerdict(verdict ?? "PENDING") ? target : patch?.running_test_index);

      if (!patch && runningIndex === undefined) return undefined;

      return {
        ...patch,
        ...(verdict !== undefined ? { verdict } : {}),
        ...(runningIndex !== undefined ? { running_test_index: runningIndex } : {}),
      };
    },
    [liveById, patches],
  );

  const getLiveState = useCallback(
    (attemptId: number) => liveById[attemptId],
    [liveById],
  );

  const value = useMemo<Ctx>(() => ({ getPatch, getLiveState }), [getPatch, getLiveState]);

  return (
    <AttemptLiveContext.Provider value={value}>{children}</AttemptLiveContext.Provider>
  );
}

/** @deprecated AttemptLiveProvider ichida ishlatiladi. */
export function AttemptLive({ problem }: { problem: string }) {
  return <AttemptLiveProvider problem={problem}>{null}</AttemptLiveProvider>;
}
