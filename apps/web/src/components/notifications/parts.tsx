"use client";

import type { Route } from "next";
import Link from "next/link";

import { Icon } from "@/components/ui/Icon";
import { t, type Locale } from "@/i18n/messages";
import type { StreamState } from "@/lib/useEventStream";
import {
  notificationHref,
  notificationIcon,
  notificationText,
  timeLabel,
  type Notification,
} from "@/lib/notifications/model";

const ICON_BUTTON =
  "flex size-11 shrink-0 items-center justify-center rw-radius-sm rw-dim-2 transition rw-hover-bg rw-focus-ring";
/** The title's hit area covers the row up to the action buttons. */
const STRETCH = "after:absolute after:inset-y-0 after:left-0 after:content-['']";
const TEXT_LINK =
  "inline-flex min-h-11 items-center rw-radius-sm px-2 text-theme-sm font-semibold rw-accent-ink transition rw-hover-bg rw-focus-ring disabled:cursor-default disabled:opacity-50 disabled:hover:bg-transparent";

/** One notification. The title is the way in: it opens the page the
 *  notification is about and marks it read. A row with nowhere to go is
 *  still a button, so "read" is one press either way. */
export function NotificationRow({
  row,
  locale,
  compact,
  fresh,
  onOpen,
  onToggle,
  onRemove,
}: {
  row: Notification;
  locale: Locale;
  /** The bell panel: no delete button, body kept to two lines. */
  compact: boolean;
  fresh: boolean;
  onOpen: (row: Notification) => void;
  onToggle: (row: Notification) => void;
  onRemove?: (row: Notification) => void;
}) {
  const text = notificationText(row, locale);
  const href = notificationHref(row);
  const reach = compact ? "after:right-11" : "after:right-22";
  const title = `block text-left text-theme-sm break-words rw-strong rw-focus-ring ${STRETCH} ${reach} ${
    row.is_read ? "font-medium" : "font-bold"
  }`;
  const toggleLabel = t(locale, row.is_read ? "notif.markUnread" : "notif.markRead");

  return (
    <li
      data-notification={row.id}
      data-unread={!row.is_read}
      className={`relative flex items-start gap-3 py-2.5 pr-1 pl-4 ${
        row.is_read ? "" : "bg-[color-mix(in_srgb,var(--rw-accent)_7%,transparent)]"
      } ${fresh ? "rw-notif-new" : ""}`}
    >
      <span className="mt-0.5 flex size-9 shrink-0 items-center justify-center rw-radius-sm border rw-divider rw-dim-2">
        <Icon name={notificationIcon(row.kind)} className="size-4" />
      </span>
      <div className="min-w-0 flex-1 py-0.5">
        {href ? (
          <Link href={href as Route} onClick={() => onOpen(row)} className={title}>
            {text.title}
          </Link>
        ) : (
          <button type="button" onClick={() => onOpen(row)} className={title}>
            {text.title}
          </button>
        )}
        {text.body && (
          <p className={`mt-0.5 text-theme-xs break-words rw-dim ${compact ? "line-clamp-2" : ""}`}>
            {text.body}
          </p>
        )}
        <p className="mt-1 flex flex-wrap items-center gap-x-1.5 text-theme-xs rw-faint">
          {!row.is_read && (
            <span aria-hidden="true" className="size-2 rounded-full rw-accent-bg" />
          )}
          <span>{t(locale, `settings.kind.${row.kind}`)}</span>
          <span aria-hidden="true">·</span>
          <time dateTime={row.created_at}>{timeLabel(row.created_at, locale)}</time>
        </p>
      </div>
      <div className="relative z-10 flex shrink-0">
        <button
          type="button"
          onClick={() => onToggle(row)}
          aria-label={toggleLabel}
          title={toggleLabel}
          className={ICON_BUTTON}
        >
          <Icon name={row.is_read ? "notification.badgeNew" : "notification.bellRead"} className="size-4" />
        </button>
        {onRemove && (
          <button
            type="button"
            onClick={() => onRemove(row)}
            aria-label={t(locale, "notif.delete")}
            title={t(locale, "notif.delete")}
            className={ICON_BUTTON}
          >
            <Icon name="action.delete" className="size-4" />
          </button>
        )}
      </div>
    </li>
  );
}

/** A centred message: nothing here, nothing left, it broke, sign in. */
export function StateBox({
  icon,
  title,
  body,
  children,
}: {
  icon: string;
  title: string;
  body: string;
  children?: React.ReactNode;
}) {
  return (
    <div className="px-5 py-12 text-center">
      <span className="mx-auto mb-3 flex size-14 items-center justify-center rounded-full rw-accent-soft">
        <Icon name={icon} className="size-6" />
      </span>
      <p className="text-theme-base font-semibold rw-strong">{title}</p>
      <p className="mx-auto mt-1 max-w-sm text-theme-sm rw-dim">{body}</p>
      {children && <div className="mt-4 flex justify-center">{children}</div>}
    </div>
  );
}

const BAR = "block rounded bg-[color-mix(in_srgb,var(--rw-text)_12%,transparent)]";

export function ListSkeleton({ rows, label }: { rows: number; label: string }) {
  return (
    <div role="status" aria-label={label} className="animate-pulse motion-reduce:animate-none">
      {Array.from({ length: rows }, (_, index) => (
        <div key={index} className="flex gap-3 py-3 pr-4 pl-4">
          <span className={`${BAR} size-9 shrink-0`} />
          <span className="flex-1 space-y-2 py-1">
            <span className={`${BAR} h-3 ${index % 2 ? "w-2/3" : "w-5/6"}`} />
            <span className={`${BAR} h-2.5 w-1/3`} />
          </span>
        </div>
      ))}
    </div>
  );
}

/** Whether the list updates by itself, and how. While the channel is
 *  still connecting nothing is shown — "refreshes every minute" for the
 *  first moment of every page would be a false alarm. */
export function LiveMark({ channel, locale }: { channel: StreamState; locale: Locale }) {
  if (channel === "connecting") return null;
  const live = channel === "open";
  return (
    <span className="inline-flex items-center gap-1.5 text-theme-xs whitespace-nowrap rw-dim">
      <span
        aria-hidden="true"
        className={`size-2 rounded-full ${live ? "bg-[var(--rw-ok-ink,currentColor)]" : "bg-[var(--rw-warn-ink)]"}`}
      />
      {t(locale, live ? "notif.live" : "notif.polling")}
    </span>
  );
}

/** "Deleted — Undo", for as long as the deletion has not been sent. */
export function UndoBar({
  what,
  locale,
  onUndo,
}: {
  what: "one" | "read" | null;
  locale: Locale;
  onUndo: () => void;
}) {
  if (!what) return null;
  return (
    <div
      role="status"
      className="flex items-center justify-between gap-3 border-t rw-divider rw-surface py-1 pr-2 pl-4 text-theme-sm rw-strong"
    >
      {t(locale, what === "one" ? "notif.deleted" : "notif.cleared")}
      <button type="button" onClick={onUndo} className={TEXT_LINK}>
        {t(locale, "notif.undo")}
      </button>
    </div>
  );
}

export function Tabs({
  unread,
  total,
  unreadCount,
  locale,
  onChange,
}: {
  unread: boolean;
  total: number;
  unreadCount: number;
  locale: Locale;
  onChange: (unread: boolean) => void;
}) {
  const tab = (active: boolean) =>
    `inline-flex min-h-11 items-center gap-1.5 border-b-2 px-2 text-theme-sm whitespace-nowrap transition rw-focus-ring ${
      active ? "border-current font-semibold rw-accent-ink" : "border-transparent rw-dim-2"
    }`;
  return (
    <div role="tablist" aria-label={t(locale, "notif.title")} className="flex gap-2">
      <button type="button" role="tab" aria-selected={!unread} onClick={() => onChange(false)} className={tab(!unread)}>
        {t(locale, "notif.all")}
        <span className="font-mono text-theme-xs opacity-70">{total}</span>
      </button>
      <button type="button" role="tab" aria-selected={unread} onClick={() => onChange(true)} className={tab(unread)}>
        {t(locale, "notif.unread")}
        <span className="font-mono text-theme-xs opacity-70">{unreadCount}</span>
      </button>
    </div>
  );
}

export { TEXT_LINK, ICON_BUTTON };
