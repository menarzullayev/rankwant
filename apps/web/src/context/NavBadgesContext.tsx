"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { usePathname } from "next/navigation";

import { useSession } from "@/context/SessionContext";
import { useUpdates } from "@/context/UpdatesContext";
import { fetchNavBadges, markNavSeen, type NavBadge } from "@/lib/api";
import {
  SEEN_ON_VISIT,
  sectionOf,
  toBadgeMap,
  type NavBadgeMap,
} from "@/lib/nav-badges";

/** Side-menu badges: what waits for the user, what runs now, what is new.
 *
 *  One request for every section (`/me/nav-badges/`), read when the user
 *  is known, again when they move to another page (at most once in
 *  `REFRESH_MS`) and when the tab comes back to the front. A guest sends
 *  nothing: the endpoint needs a session and the guest pages are cached
 *  at the edge.
 *
 *  The changelog keeps its own, older count (`UpdatesContext`: a row per
 *  entry read); it is merged in here so the menu draws every badge the
 *  same way.
 */
const NavBadgesContext = createContext<NavBadgeMap>({});

/** The counts behind a badge change far less often than pages do. */
const REFRESH_MS = 30_000;

export function useNavBadges() {
  return useContext(NavBadgesContext);
}

export function NavBadgesProvider({ children }: { children: React.ReactNode }) {
  const { user, ready } = useSession();
  const { count: updates } = useUpdates();
  const pathname = usePathname();
  const [rows, setRows] = useState<NavBadge[]>([]);
  const readAt = useRef(0);
  const signedIn = ready && Boolean(user);

  const refresh = useCallback(async () => {
    readAt.current = Date.now();
    const body = await fetchNavBadges().catch(() => null);
    if (body) setRows(body.badges);
  }, []);

  // Opening a section is what clears its "unread" / "new" badge. The
  // answer carries the fresh list, so no second request follows.
  useEffect(() => {
    if (!signedIn) return;
    const section = sectionOf(pathname);
    let cancelled = false;
    void (async () => {
      if (section && SEEN_ON_VISIT.has(section)) {
        const body = await markNavSeen(section).catch(() => null);
        if (body) {
          readAt.current = Date.now();
          if (!cancelled) setRows(body.badges);
          return;
        }
        // The write failed: the badges are still owed a plain read.
      }
      if (Date.now() - readAt.current >= REFRESH_MS) await refresh();
    })();
    return () => {
      cancelled = true;
    };
  }, [signedIn, pathname, refresh]);

  useEffect(() => {
    if (!signedIn) return;
    const onShow = () => {
      if (document.visibilityState !== "visible") return;
      if (Date.now() - readAt.current >= REFRESH_MS) void refresh();
    };
    document.addEventListener("visibilitychange", onShow);
    return () => document.removeEventListener("visibilitychange", onShow);
  }, [signedIn, refresh]);

  const value = useMemo(
    () => (signedIn ? toBadgeMap(rows, updates) : {}),
    [signedIn, rows, updates],
  );

  return (
    <NavBadgesContext.Provider value={value}>
      {children}
    </NavBadgesContext.Provider>
  );
}
