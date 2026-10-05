"use client";

import type { Route } from "next";
import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";

import { Icon } from "@/components/ui/Icon";
import { useNotifications } from "@/context/NotificationsContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";
import { PANEL_SIZE, type Notification } from "@/lib/notifications/model";

import { Feed } from "./Feed";
import { ICON_BUTTON, LiveMark, Tabs, TEXT_LINK, UndoBar } from "./parts";
import { useNotificationList } from "./useNotificationList";

/** Where the panel hangs: under the bell from `sm` up, the whole screen below. */
type Anchor = { top: number; right: number } | null;

const DESKTOP = "(min-width: 640px)";

/** The header bell: a count of what is new, and a panel with the latest.
 *
 *  Opening the panel marks everything *seen* — the badge clears — but not
 *  *read*: a row stays marked until it is opened or "Mark all read" is
 *  pressed, so a glance does not bury something that still needs a reply.
 */
export function NotificationBell() {
  const locale = useLocale();
  const { summary, markSeen } = useNotifications();
  const [open, setOpen] = useState(false);
  const [anchor, setAnchor] = useState<Anchor>(null);
  const bell = useRef<HTMLButtonElement>(null);

  const close = useCallback((returnFocus: boolean) => {
    setOpen(false);
    if (returnFocus) requestAnimationFrame(() => bell.current?.focus());
  }, []);

  function toggle() {
    if (open) {
      close(false);
      return;
    }
    const box = bell.current?.getBoundingClientRect();
    setAnchor(
      box && window.matchMedia(DESKTOP).matches
        ? { top: Math.round(box.bottom + 8), right: Math.round(window.innerWidth - box.right) }
        : null,
    );
    setOpen(true);
    if (summary.unseen > 0) markSeen();
  }

  const unseen = summary.unseen;
  const label =
    unseen > 0
      ? `${t(locale, "notif.title")} — ${fill(t(locale, "notif.unreadCount"), { n: unseen })}`
      : t(locale, "notif.title");

  return (
    <>
      <button
        ref={bell}
        type="button"
        onClick={toggle}
        aria-haspopup="dialog"
        aria-expanded={open}
        aria-label={label}
        data-tip={open ? undefined : t(locale, "notif.title")}
        data-tip-kind="flip"
        className="relative flex size-10 items-center justify-center rw-radius-sm border rw-line rw-dim-2 transition rw-hover-bg rw-focus-ring"
      >
        <Icon name="notification.bell" />
        {unseen > 0 && (
          <span
            aria-hidden="true"
            className="absolute -top-1 -right-1 flex h-4 min-w-4 items-center justify-center rounded-full rw-accent-bg px-1 text-theme-2xs font-semibold"
          >
            {unseen > 99 ? "99+" : unseen}
          </span>
        )}
      </button>
      {open && <Panel anchor={anchor} bell={bell} onClose={close} />}
    </>
  );
}

function Panel({
  anchor,
  bell,
  onClose,
}: {
  anchor: Anchor;
  bell: React.RefObject<HTMLButtonElement | null>;
  onClose: (returnFocus: boolean) => void;
}) {
  const locale = useLocale();
  const { summary, channel } = useNotifications();
  const [unread, setUnread] = useState(false);
  const panel = useRef<HTMLDivElement>(null);
  const list = useNotificationList({ unread, kind: null, size: PANEL_SIZE, active: true });

  useEffect(() => {
    panel.current?.focus();
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose(true);
    };
    const onPointer = (event: MouseEvent) => {
      const target = event.target as Node;
      if (panel.current?.contains(target) || bell.current?.contains(target)) return;
      onClose(false);
    };
    // The panel is placed from the bell's position at the moment it
    // opened; a resized window would leave it hanging in the wrong place.
    const onResize = () => onClose(false);
    document.addEventListener("keydown", onKey);
    document.addEventListener("mousedown", onPointer);
    window.addEventListener("resize", onResize);
    return () => {
      document.removeEventListener("keydown", onKey);
      document.removeEventListener("mousedown", onPointer);
      window.removeEventListener("resize", onResize);
    };
  }, [bell, onClose]);

  // Full screen on a phone: the page behind must not scroll under it.
  useEffect(() => {
    if (anchor) return;
    const before = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = before;
    };
  }, [anchor]);

  function open(row: Notification) {
    list.setRead(row, true);
    onClose(false);
  }

  return createPortal(
    <div
      ref={panel}
      role="dialog"
      aria-label={t(locale, "notif.title")}
      tabIndex={-1}
      data-notification-panel=""
      style={anchor ? { top: anchor.top, right: anchor.right } : undefined}
      className={`fixed z-[85] flex flex-col overflow-hidden rw-surface outline-none ${
        anchor
          ? "max-h-[min(36rem,calc(100dvh-5rem))] w-[25rem] rounded-xl border rw-divider rw-shadow"
          : "inset-0"
      }`}
    >
      <div className="flex shrink-0 items-center gap-1 border-b rw-divider py-1 pr-1 pl-4">
        <h2 className="min-w-0 flex-1 truncate text-theme-base font-semibold rw-strong">
          {t(locale, "notif.title")}
        </h2>
        <button
          type="button"
          onClick={list.readAll}
          disabled={summary.unread === 0}
          className={TEXT_LINK}
        >
          {t(locale, "notif.markAll")}
        </button>
        <button
          type="button"
          onClick={() => onClose(true)}
          aria-label={t(locale, "nav.close")}
          className={ICON_BUTTON}
        >
          <Icon name="nav.close" className="size-5" />
        </button>
      </div>
      <div className="shrink-0 border-b rw-divider px-3">
        <Tabs
          unread={unread}
          total={summary.total}
          unreadCount={summary.unread}
          locale={locale}
          onChange={setUnread}
        />
      </div>
      <div className="min-h-0 flex-1 overflow-y-auto">
        <Feed
          status={list.status}
          items={list.items}
          total={summary.total}
          filtered={unread}
          fresh={list.fresh}
          locale={locale}
          compact
          grouped={false}
          onRetry={list.reload}
          onOpen={open}
          onToggle={(row) => list.setRead(row, !row.is_read)}
        />
      </div>
      {list.failed && (
        <p role="alert" className="shrink-0 border-t rw-divider px-4 py-2 text-theme-xs rw-dim">
          {t(locale, "notif.failed")}
        </p>
      )}
      <UndoBar what={list.undoable} locale={locale} onUndo={list.undo} />
      <div className="flex shrink-0 items-center justify-between gap-2 border-t rw-divider py-1 pr-2 pl-4">
        <LiveMark channel={channel} locale={locale} />
        <Link
          href={"/notifications" as Route}
          onClick={() => onClose(false)}
          className={TEXT_LINK}
        >
          {t(locale, "notif.seeAll")}
        </Link>
      </div>
    </div>,
    document.body,
  );
}
