"use client";

import type { Route } from "next";
import Link from "next/link";
import { useEffect, useState } from "react";

import { Button, ButtonLink } from "@/components/ui/Button";
import { useNotifications } from "@/context/NotificationsContext";
import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { PAGE_SIZE } from "@/lib/notifications/model";

import { Feed } from "./Feed";
import { ListSkeleton, LiveMark, StateBox, Tabs, TEXT_LINK, UndoBar } from "./parts";
import { useNotificationList } from "./useNotificationList";

const CHIP =
  "inline-flex h-11 shrink-0 items-center rounded-full border px-4 text-theme-sm whitespace-nowrap transition rw-focus-ring";

/** The full notification page: every row, filters, and the bulk actions. */
export function NotificationCenter() {
  const locale = useLocale();
  const { user, ready } = useSession();
  const { summary, live, markSeen } = useNotifications();
  const [unread, setUnread] = useState(false);
  const [kind, setKind] = useState<string | null>(null);
  const signedIn = ready && user !== null;
  // A chip for a kind that no longer has rows is not offered — and must
  // not stay selected after its last row was deleted.
  const chosen = kind !== null && summary.kinds.includes(kind) ? kind : null;
  const list = useNotificationList({ unread, kind: chosen, size: PAGE_SIZE, active: signedIn });

  // Being on this page is having seen them.
  const unseen = summary.unseen;
  useEffect(() => {
    if (signedIn && unseen > 0) markSeen();
  }, [signedIn, unseen, markSeen]);

  const heading = (
    <h1 className="min-w-0 flex-1 text-title-sm font-bold rw-strong">{t(locale, "notif.title")}</h1>
  );

  if (!ready) {
    return (
      <div className="mx-auto w-full max-w-3xl space-y-4">
        {heading}
        <div className="overflow-hidden rw-radius border rw-divider rw-surface">
          <ListSkeleton rows={6} label={t(locale, "loading.label")} />
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="mx-auto w-full max-w-3xl space-y-4">
        {heading}
        <div className="rw-radius border rw-divider rw-surface">
          <StateBox
            icon="user.profile"
            title={t(locale, "notif.guestTitle")}
            body={t(locale, "notif.guestBody")}
          >
            <ButtonLink href={"/login?tab=login" as Route}>{t(locale, "notif.signIn")}</ButtonLink>
          </StateBox>
        </div>
      </div>
    );
  }

  const hasRead = summary.total > summary.unread;

  return (
    <div className="mx-auto w-full max-w-3xl space-y-4">
      <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
        {heading}
        <LiveMark live={live} locale={locale} />
      </div>

      <div className="flex flex-wrap items-center justify-between gap-x-3 border-b rw-divider">
        <Tabs
          unread={unread}
          total={summary.total}
          unreadCount={summary.unread}
          locale={locale}
          onChange={setUnread}
        />
        <div className="flex flex-wrap items-center">
          <button
            type="button"
            onClick={list.readAll}
            disabled={summary.unread === 0}
            className={TEXT_LINK}
          >
            {t(locale, "notif.markAll")}
          </button>
          <button type="button" onClick={list.clearRead} disabled={!hasRead} className={TEXT_LINK}>
            {t(locale, "notif.clearRead")}
          </button>
          <Link href={"/settings/bildirishnomalar" as Route} className={TEXT_LINK}>
            {t(locale, "notif.settings")}
          </Link>
        </div>
      </div>

      {summary.kinds.length > 1 && (
        <div
          role="group"
          aria-label={t(locale, "notif.filterLabel")}
          className="flex gap-2 overflow-x-auto py-1"
        >
          <button
            type="button"
            aria-pressed={chosen === null}
            onClick={() => setKind(null)}
            className={`${CHIP} ${chosen === null ? "rw-accent-bg font-semibold" : "rw-divider rw-surface rw-dim-2 rw-hover-bg"}`}
          >
            {t(locale, "notif.all")}
          </button>
          {summary.kinds.map((name) => (
            <button
              key={name}
              type="button"
              aria-pressed={chosen === name}
              onClick={() => setKind(name)}
              className={`${CHIP} ${chosen === name ? "rw-accent-bg font-semibold" : "rw-divider rw-surface rw-dim-2 rw-hover-bg"}`}
            >
              {t(locale, `settings.kind.${name}`)}
            </button>
          ))}
        </div>
      )}

      {list.failed && (
        <p role="alert" className="rw-radius border rw-divider px-4 py-3 text-theme-sm rw-strong">
          {t(locale, "notif.failed")}
        </p>
      )}

      <div className="overflow-hidden rw-radius border rw-divider rw-surface">
        <Feed
          status={list.status}
          items={list.items}
          total={summary.total}
          filtered={unread || chosen !== null}
          fresh={list.fresh}
          locale={locale}
          compact={false}
          grouped
          onRetry={list.reload}
          onOpen={(row) => list.setRead(row, true)}
          onToggle={(row) => list.setRead(row, !row.is_read)}
          onRemove={list.remove}
        />
        {list.status === "ready" && list.hasMore && (
          <div className="flex justify-center border-t rw-divider p-3">
            <Button variant="outline" onClick={list.loadMore} disabled={list.loadingMore}>
              {t(locale, "notif.more")}
            </Button>
          </div>
        )}
        <div className="sticky bottom-0">
          <UndoBar what={list.undoable} locale={locale} onUndo={list.undo} />
        </div>
      </div>
    </div>
  );
}
