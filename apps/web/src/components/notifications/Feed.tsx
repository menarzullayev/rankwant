"use client";

import { Button } from "@/components/ui/Button";
import { t, type Locale } from "@/i18n/messages";
import { dayGroup, type DayGroup, type Notification } from "@/lib/notifications/model";

import { ListSkeleton, NotificationRow, StateBox } from "./parts";
import type { ListStatus } from "./useNotificationList";

const GROUP_KEYS: Record<DayGroup, string> = {
  today: "notif.today",
  yesterday: "notif.yesterday",
  earlier: "notif.earlier",
};

/** The body of a notification list in every state it can be in.
 *
 *  Loading, failed, empty, "all caught up" and the rows themselves — the
 *  bell panel and the full page draw the same thing, so a state cannot be
 *  handled in one and forgotten in the other.
 */
export function Feed({
  status,
  items,
  total,
  filtered,
  fresh,
  locale,
  compact,
  grouped,
  onRetry,
  onOpen,
  onToggle,
  onRemove,
}: {
  status: ListStatus;
  items: Notification[];
  /** Everything this user has, whatever the filter. */
  total: number;
  /** The list is narrowed (unread only, or one kind). */
  filtered: boolean;
  fresh: ReadonlySet<number>;
  locale: Locale;
  compact: boolean;
  /** Headings by day: today, yesterday, earlier. */
  grouped: boolean;
  onRetry: () => void;
  onOpen: (row: Notification) => void;
  onToggle: (row: Notification) => void;
  onRemove?: (row: Notification) => void;
}) {
  if (status === "loading") {
    return <ListSkeleton rows={compact ? 4 : 6} label={t(locale, "loading.label")} />;
  }
  if (status === "error") {
    return (
      <StateBox icon="status.warning" title={t(locale, "notif.errorTitle")} body={t(locale, "notif.errorBody")}>
        <Button onClick={onRetry}>{t(locale, "notif.retry")}</Button>
      </StateBox>
    );
  }
  if (items.length === 0) {
    // Nothing at all, or nothing left under this filter — two different
    // things to tell someone.
    return total === 0 || !filtered ? (
      <StateBox icon="notification.bell" title={t(locale, "notif.emptyTitle")} body={t(locale, "notif.emptyBody")} />
    ) : (
      <StateBox icon="action.confirm" title={t(locale, "notif.caughtUpTitle")} body={t(locale, "notif.caughtUpBody")} />
    );
  }

  const row = (item: Notification) => (
    <NotificationRow
      key={item.id}
      row={item}
      locale={locale}
      compact={compact}
      fresh={fresh.has(item.id)}
      onOpen={onOpen}
      onToggle={onToggle}
      onRemove={onRemove}
    />
  );

  if (!grouped) return <ul className="divide-y rw-divide">{items.map(row)}</ul>;

  const now = new Date();
  const groups: { name: DayGroup; rows: Notification[] }[] = [];
  for (const item of items) {
    const name = dayGroup(item.created_at, now);
    const last = groups[groups.length - 1];
    if (last && last.name === name) last.rows.push(item);
    else groups.push({ name, rows: [item] });
  }
  return (
    <>
      {groups.map((group) => (
        <section key={group.name} aria-label={t(locale, GROUP_KEYS[group.name])}>
          <h2 className="px-4 pt-4 pb-1 text-theme-xs font-semibold tracking-wide rw-faint uppercase">
            {t(locale, GROUP_KEYS[group.name])}
          </h2>
          <ul className="divide-y rw-divide">{group.rows.map(row)}</ul>
        </section>
      ))}
    </>
  );
}
