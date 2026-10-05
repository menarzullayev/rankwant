"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { useNotifications } from "@/context/NotificationsContext";
import { deleteJson, getJson, postJson, type Paginated } from "@/lib/api";
import {
  cursorOf,
  listQuery,
  UNDO_MS,
  type Notification,
  type NotificationSummary,
} from "@/lib/notifications/model";

export type ListStatus = "loading" | "ready" | "error";

type Loaded = {
  /** The request this answer belongs to; a stale one is not shown. */
  key: string;
  items: Notification[];
  cursor: string | null;
  failed: boolean;
};

/** What a pending deletion needs in order to be taken back or carried out. */
type Pending = {
  /** Which sentence the undo bar shows. */
  what: "one" | "read";
  items: Notification[];
  summary: NotificationSummary;
  commit: () => Promise<unknown>;
};

const NOTHING: Loaded = { key: "", items: [], cursor: null, failed: false };

/** One list of notifications and everything that can be done to it.
 *
 *  Actions are optimistic: the row changes at once and the request
 *  follows. A deletion is not sent for `UNDO_MS` — "Undo" simply never
 *  sends it — and is carried out early when another one starts, when the
 *  list goes away, or when the page is being left.
 */
export function useNotificationList({
  unread,
  kind,
  size,
  active,
}: {
  unread: boolean;
  kind: string | null;
  size: number;
  /** A closed panel or a guest asks nothing. */
  active: boolean;
}) {
  const { summary, tick, refresh, adjust } = useNotifications();
  const [loaded, setLoaded] = useState<Loaded>(NOTHING);
  const [retry, setRetry] = useState(0);
  const [fresh, setFresh] = useState<ReadonlySet<number>>(new Set());
  const [undoable, setUndoable] = useState<Pending["what"] | null>(null);
  const [failed, setFailed] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const pending = useRef<{ entry: Pending; timer: number } | null>(null);
  const summaryNow = useRef(summary);
  const loadedNow = useRef(loaded);
  useEffect(() => {
    summaryNow.current = summary;
    loadedNow.current = loaded;
  }, [summary, loaded]);

  const key = active ? `${unread}|${kind ?? ""}|${size}|${retry}` : "";
  const current = loaded.key === key ? loaded : NOTHING;
  let status: ListStatus = "ready";
  if (active && loaded.key !== key) status = "loading";
  else if (current.failed) status = "error";

  // First page — whenever the filter changes or a retry is asked for.
  useEffect(() => {
    if (!key) return;
    const controller = new AbortController();
    getJson<Paginated<Notification>>(`/notifications/${listQuery({ unread, kind, size })}`, {
      signal: controller.signal,
    })
      .then((body) =>
        setLoaded({ key, items: body.results, cursor: cursorOf(body.next), failed: false }),
      )
      .catch(() => {
        if (!controller.signal.aborted) setLoaded({ key, items: [], cursor: null, failed: true });
      });
    return () => controller.abort();
  }, [key, unread, kind, size]);

  // Something arrived: read the first page again and put what is new on
  // top. Rows already on screen stay where they are, further pages too.
  const seenTick = useRef(tick);
  useEffect(() => {
    if (seenTick.current === tick) return;
    seenTick.current = tick;
    if (!key) return;
    getJson<Paginated<Notification>>(`/notifications/${listQuery({ unread, kind, size })}`)
      .then((body) => {
        const shownNow = loadedNow.current;
        if (shownNow.key !== key || shownNow.failed) return;
        const known = new Set(shownNow.items.map((row) => row.id));
        const arrived = body.results.filter((row) => !known.has(row.id));
        if (arrived.length === 0) return;
        setFresh(new Set(arrived.map((row) => row.id)));
        setLoaded((before) =>
          before.key === key ? { ...before, items: [...arrived, ...before.items] } : before,
        );
      })
      .catch(() => undefined);
  }, [tick, key, unread, kind, size]);

  const patch = useCallback(
    (change: (items: Notification[]) => Notification[]) =>
      setLoaded((before) => ({ ...before, items: change(before.items) })),
    [],
  );

  /** Sends a request; on failure says so and reads the truth back. */
  const send = useCallback(
    (request: Promise<unknown>) => {
      setFailed(false);
      request
        .then(() => refresh())
        .catch(() => {
          setFailed(true);
          setRetry((value) => value + 1);
          void refresh();
        });
    },
    [refresh],
  );

  const flush = useCallback(() => {
    const held = pending.current;
    if (!held) return;
    window.clearTimeout(held.timer);
    pending.current = null;
    setUndoable(null);
    send(held.entry.commit());
  }, [send]);

  const hold = useCallback(
    (entry: Pending) => {
      flush();
      const timer = window.setTimeout(flush, UNDO_MS);
      pending.current = { entry, timer };
      setUndoable(entry.what);
    },
    [flush],
  );

  // A deletion in waiting must not be lost with the component or the page.
  useEffect(() => {
    const leave = () => flush();
    window.addEventListener("pagehide", leave);
    return () => {
      window.removeEventListener("pagehide", leave);
      flush();
    };
  }, [flush]);

  const setRead = useCallback(
    (row: Notification, read: boolean) => {
      if (row.is_read === read) return;
      patch((items) => items.map((item) => (item.id === row.id ? { ...item, is_read: read } : item)));
      adjust((now) => ({ ...now, unread: Math.max(0, now.unread + (read ? -1 : 1)) }));
      const path = read ? "/notifications/mark-read/" : "/notifications/mark-unread/";
      send(postJson(path, { ids: [row.id] }));
    },
    [adjust, patch, send],
  );

  const readAll = useCallback(() => {
    patch((items) => items.map((item) => ({ ...item, is_read: true })));
    adjust((now) => ({ ...now, unread: 0, unseen: 0 }));
    send(postJson("/notifications/mark-read/", {}));
  }, [adjust, patch, send]);

  const remove = useCallback(
    (row: Notification) => {
      const before = { items: current.items, summary: summaryNow.current };
      hold({
        what: "one",
        ...before,
        commit: () => deleteJson(`/notifications/${row.id}/`),
      });
      patch((items) => items.filter((item) => item.id !== row.id));
      adjust((now) => ({
        ...now,
        total: Math.max(0, now.total - 1),
        unread: Math.max(0, now.unread - (row.is_read ? 0 : 1)),
      }));
    },
    [adjust, current.items, hold, patch],
  );

  const clearRead = useCallback(() => {
    const before = { items: current.items, summary: summaryNow.current };
    hold({ what: "read", ...before, commit: () => postJson("/notifications/clear-read/", {}) });
    patch((items) => items.filter((item) => !item.is_read));
    adjust((now) => ({ ...now, total: now.unread }));
  }, [adjust, current.items, hold, patch]);

  const undo = useCallback(() => {
    const held = pending.current;
    if (!held) return;
    window.clearTimeout(held.timer);
    pending.current = null;
    setUndoable(null);
    setLoaded((before) => ({ ...before, items: held.entry.items }));
    adjust(() => held.entry.summary);
  }, [adjust]);

  const loadMore = useCallback(() => {
    if (!current.cursor || loadingMore) return;
    setLoadingMore(true);
    getJson<Paginated<Notification>>(
      `/notifications/${listQuery({ unread, kind, size, cursor: current.cursor })}`,
    )
      .then((body) =>
        setLoaded((before) => {
          if (before.key !== key) return before;
          const known = new Set(before.items.map((row) => row.id));
          return {
            ...before,
            items: [...before.items, ...body.results.filter((row) => !known.has(row.id))],
            cursor: cursorOf(body.next),
          };
        }),
      )
      .catch(() => setFailed(true))
      .finally(() => setLoadingMore(false));
  }, [current.cursor, key, kind, loadingMore, size, unread]);

  return {
    items: current.items,
    status,
    hasMore: current.cursor !== null,
    loadingMore,
    fresh,
    /** Which deletion can still be taken back, if any. */
    undoable,
    /** The last action did not reach the server. */
    failed,
    reload: () => setRetry((value) => value + 1),
    loadMore,
    setRead,
    readAll,
    remove,
    clearRead,
    undo,
  };
}
