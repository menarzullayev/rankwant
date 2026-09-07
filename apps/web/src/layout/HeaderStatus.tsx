"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { useSession } from "@/context/SessionContext";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";
import { BellIcon, FlameIcon, QvantIcon } from "@/icons";
import { API_BASE } from "@/lib/api";

/** Qo'ng'iroq + Qvant balansi + streak — RoboContest/KEP header naqshi.
 *  Sessiya bo'lmasa hech narsa ko'rsatilmaydi. */
export default function HeaderStatus() {
  const { user, ready } = useSession();
  const [unread, setUnread] = useState(0);
  const [balance, setBalance] = useState<number | null>(null);

  useEffect(() => {
    if (!user) return;
    const opts = { credentials: "include" as const, headers: { Accept: "application/json" } };
    fetch(`${API_BASE}/notifications/unread_count/`, opts)
      .then((r) => (r.ok ? r.json() : { count: 0 }))
      .then((d) => setUnread(d.count ?? d.unread ?? 0))
      .catch(() => {});
    fetch(`${API_BASE}/qvant/wallet/`, opts)
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => setBalance(d?.balance ?? null))
      .catch(() => {});
  }, [user]);

  if (!ready || !user) return null;

  const pill =
    "flex h-10 items-center gap-1.5 rounded-lg border border-gray-200 px-3 text-theme-sm " +
    "font-medium text-gray-700 transition hover:bg-gray-50 dark:border-[#232936] " +
    "dark:text-gray-200 dark:hover:bg-white/5";

  return (
    <div className="flex items-center gap-2">
      <Link href="/qvant" className={pill} title="Qvant">
        <QvantIcon className="size-4 text-brand-500" />
        {balance ?? "…"}
      </Link>
      <span className={pill} title={`${user.streak_count} ${t(DEFAULT_LOCALE, "header.streak")}`}>
        <FlameIcon className="size-4 text-warning-500" />
        {user.streak_count}
      </span>
      <Link
        href="/notifications"
        className="relative flex size-10 items-center justify-center rounded-lg border
          border-gray-200 text-gray-600 transition hover:bg-gray-50
          dark:border-[#232936] dark:text-gray-300 dark:hover:bg-white/5"
        title={unread ? `${unread}` : t(DEFAULT_LOCALE, "header.noUnread")}
      >
        <BellIcon />
        {unread > 0 && (
          <span
            className="absolute -top-1 -right-1 flex h-4 min-w-4 items-center justify-center
              rounded-full bg-brand-500 px-1 text-[10px] font-semibold text-white"
          >
            {unread > 99 ? "99+" : unread}
          </span>
        )}
      </Link>
    </div>
  );
}
