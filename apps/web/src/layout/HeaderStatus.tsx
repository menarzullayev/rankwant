"use client";

import { IntentLink } from "@/components/ui/IntentLink";
import { useEffect, useState } from "react";

import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { NotificationBell } from "@/components/notifications/NotificationBell";
import { Icon } from "@/components/ui/Icon";
import { API_BASE } from "@/lib/api";

/** Qo'ng'iroq + Qvant balansi + streak — RoboContest/KEP header naqshi.
 * Sessiya bo'lmasa hech narsa ko'rsatilmaydi. Qo'ng'iroqning o'z soni va
 * paneli bor (`NotificationBell`); bu yerda faqat joyi. */
export default function HeaderStatus() {
  const locale = useLocale();
  const { user, ready } = useSession();
  const [balance, setBalance] = useState<number | null>(null);

  useEffect(() => {
    if (!user) return;
    const opts = {
      credentials: "include" as const,
      headers: { Accept: "application/json" },
    };
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
      <IntentLink href="/qvant" className={`${pill} hidden md:flex`} title="Qvant">
        <Icon name="shop.coin" className="size-4 rw-accent-ink" />
        {balance ?? "…"}
      </IntentLink>
      <span
        className={`${pill} hidden md:flex`}
        title={`${user.streak_count} ${t(locale, "header.streak")}`}
      >
        <Icon name="ranking.streak" className="size-4 rw-warn-ink" />
        {user.streak_count}
      </span>
      <NotificationBell />
    </div>
  );
}
