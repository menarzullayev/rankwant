"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { useSession } from "@/context/SessionContext";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";
import { BellIcon, FlameIcon, QvantIcon } from "@/icons";
import { API_BASE } from "@/lib/api";

/** Qo'ng'iroq + Qvant balansi + streak — RoboContest/KEP header naqshi.
 * Sessiya bo'lmasa hech narsa ko'rsatilmaydi. */
export default function HeaderStatus() {
  const { user, ready } = useSession();
  const [unread, setUnread] = useState(0);
  const [balance, setBalance] = useState<number | null>(null);

  useEffect(() => {
    if (!user) return;
    const opts = {
      credentials: "include" as const,
      headers: { Accept: "application/json" },
    };
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
    "flex h-10 items-center gap-1.5 rw-radius-sm border rw-line px-3 text-theme-sm " +
    "font-medium rw-strong transition rw-hover-bg " +
    " ";

  return (
    <div className="flex items-center gap-2">
      <Link href="/qvant" className={`${pill} hidden sm:flex`} title="Qvant">
        <QvantIcon className="size-4 rw-accent-ink" />
        {balance ?? "…"}
      </Link>
      <span
        className={`${pill} hidden sm:flex`}
        title={`${user.streak_count} ${t(DEFAULT_LOCALE, "header.streak")}`}
      >
        <FlameIcon className="size-4 rw-warn-ink" />
        {user.streak_count}
      </span>
      <Link
        href="/notifications"
        className="relative flex size-10 items-center justify-center rw-radius-sm border rw-line rw-dim-2 transition rw-hover-bg"
        title={unread ? `${unread}` : t(DEFAULT_LOCALE, "header.noUnread")}
      >
        <BellIcon />
        {unread > 0 && (
          <span className="absolute -top-1 -right-1 flex h-4 min-w-4 items-center justify-center rounded-full rw-accent-bg px-1 text-[10px] font-semibold text-white">
            {unread > 99 ? "99+" : unread}
          </span>
        )}
      </Link>
    </div>
  );
}
