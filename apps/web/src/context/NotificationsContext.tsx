"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  useSyncExternalStore,
} from "react";

import { useSession } from "@/context/SessionContext";
import { getJson, postJson } from "@/lib/api";
import {
  EMPTY_SUMMARY,
  POLL_MS,
  type NotificationSummary,
} from "@/lib/notifications/model";
import { EVENT_NOTIFICATION, EVENT_RESYNC, useEventStream } from "@/lib/useEventStream";

/** The bell's numbers and the signal that the lists should be re-read.
 *
 *  One provider because two surfaces read the same state — the bell in
 *  the header and the full page — and each asking on its own would show
 *  two different counts for a moment.
 *
 *  The live channel (ADR-0029) only says "something changed": the counts
 *  and the rows are always read again over REST. A missed event costs a
 *  late refresh, never a wrong number.
 */
type NotificationsState = {
  summary: NotificationSummary;
  /** The stream is connected; otherwise the counts refresh once a minute. */
  live: boolean;
  /** Bumps whenever open lists should read their first page again. */
  tick: number;
  refresh: () => Promise<void>;
  /** A local correction ahead of the server's answer (optimistic actions). */
  adjust: (change: (current: NotificationSummary) => NotificationSummary) => void;
  /** The bell or the page was opened: nothing is "new" any more. */
  markSeen: () => void;
};

const NotificationsContext = createContext<NotificationsState | undefined>(undefined);

export function useNotifications() {
  const context = useContext(NotificationsContext);
  if (!context) throw new Error("useNotifications must be used inside NotificationsProvider");
  return context;
}

function subscribeVisibility(notify: () => void) {
  document.addEventListener("visibilitychange", notify);
  return () => document.removeEventListener("visibilitychange", notify);
}

/** Whether this tab is on screen. A hidden tab holds no stream: the
 *  server allows five per user, and a row of background tabs would take
 *  them from the page that is waiting for a verdict. */
function useVisible(): boolean {
  return useSyncExternalStore(
    subscribeVisibility,
    () => document.visibilityState === "visible",
    () => true,
  );
}

export function NotificationsProvider({ children }: { children: React.ReactNode }) {
  const { user, ready } = useSession();
  const visible = useVisible();
  const [summary, setSummary] = useState<NotificationSummary>(EMPTY_SUMMARY);
  const [tick, setTick] = useState(0);
  const signedIn = ready && user !== null;

  const refresh = useCallback(async () => {
    const body = await getJson<NotificationSummary>("/notifications/summary/").catch(() => null);
    if (body) setSummary(body);
  }, []);

  const changed = useCallback(() => {
    void refresh();
    setTick((value) => value + 1);
  }, [refresh]);

  const onEvent = useCallback(
    (name: string) => {
      // The same stream carries verdict events for the problem page.
      if (name === EVENT_NOTIFICATION || name === EVENT_RESYNC) changed();
    },
    [changed],
  );
  const stream = useEventStream({ onEvent, enabled: signedIn && visible });
  const live = stream === "open";

  // On sign-in, and every time the tab comes back: whatever happened while
  // it was hidden arrived on no stream. A guest asks nothing — the
  // endpoint would answer 401 and the browser would log it.
  useEffect(() => {
    if (!signedIn || !visible) return;
    const handle = window.setTimeout(changed, 0);
    return () => window.clearTimeout(handle);
  }, [signedIn, visible, changed]);

  // No stream (unsupported, blocked, or given up after repeated drops).
  useEffect(() => {
    if (!signedIn || !visible || stream !== "fallback") return;
    const handle = window.setInterval(changed, POLL_MS);
    return () => window.clearInterval(handle);
  }, [signedIn, visible, stream, changed]);

  const adjust = useCallback<NotificationsState["adjust"]>((change) => {
    setSummary((current) => change(current));
  }, []);

  const markSeen = useCallback(() => {
    setSummary((current) => (current.unseen === 0 ? current : { ...current, unseen: 0 }));
    void postJson("/notifications/mark-seen/", {}).catch(() => undefined);
  }, []);

  return (
    <NotificationsContext.Provider
      value={{
        summary: signedIn ? summary : EMPTY_SUMMARY,
        live,
        tick,
        refresh,
        adjust,
        markSeen,
      }}
    >
      {children}
    </NotificationsContext.Provider>
  );
}
