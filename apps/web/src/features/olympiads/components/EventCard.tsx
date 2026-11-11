import type { Route } from "next";
import Link from "next/link";

import { Badge } from "@/components/ui/Badge";
import { inReaderAlphabet } from "@/i18n/alphabet";
import { fill, t, type Locale } from "@/i18n/messages";
import type { OlympiadEventCard } from "@/lib/api";

import { KIND_LABEL, STATUS_LABEL, eventPath } from "../catalog";

/** One event of a season: when and where, its kind, and what the archive holds. */
export function EventCard({ event, locale }: { event: OlympiadEventCard; locale: Locale }) {
  const kind = KIND_LABEL[event.kind];
  const status = STATUS_LABEL[event.status];
  return (
    <Link
      href={eventPath(event.slug) as Route}
      className="flex h-full flex-col gap-2 rw-radius border rw-line rw-surface p-4 transition rw-hover-line rw-focus-ring"
    >
      <span className="font-semibold rw-strong">{inReaderAlphabet(event.title, "uz")}</span>
      <span className="text-theme-xs rw-dim">
        {[event.date_label, event.location].filter(Boolean).map((part) => inReaderAlphabet(part, "uz")).join(" · ")}
      </span>
      <span className="mt-auto flex flex-wrap items-center gap-2 text-theme-xs rw-faint">
        {kind && <Badge color="info">{t(locale, kind)}</Badge>}
        {status && event.status !== "completed" && <Badge color="neutral">{t(locale, status)}</Badge>}
        {event.task_count > 0 && <span>{fill(t(locale, "olympiads.taskCount"), { count: event.task_count })}</span>}
        {event.result_count > 0 && (
          <span>{fill(t(locale, "olympiads.resultCount"), { count: event.result_count })}</span>
        )}
      </span>
    </Link>
  );
}
