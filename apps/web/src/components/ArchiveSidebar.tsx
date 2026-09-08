import Link from "next/link";

import { Card } from "@/components/ui/Card";
import type {
  ArchiveProgress,
  CalendarEvent,
  Problem,
  Roadmap,
} from "@/lib/api";

/** Daraja bo'yicha progress — KEP'ning «Difficulty breakdown» bloki.
 *
 * Mehmonda ham chiziladi: o'shanda arxiv hajmini ko'rsatuvchi karta
 * bo'ladi va ro'yxatdan o'tishga sabab beradi. */
function Progress({ data }: { data: ArchiveProgress }) {
  const percent = data.total ? Math.round((data.solved / data.total) * 100) : 0;

  return (
    <Card title="Yechilganlar" bodyClassName="space-y-3">
      <p className="text-theme-sm rw-dim">
        <span className="text-title-sm font-bold rw-strong tabular-nums">
          {data.solved}
        </span>{" "}
        / {data.total} masala
        {data.solved > 0 && ` · ${percent}%`}
      </p>

      <div className="space-y-2">
        {data.levels
          .filter((level) => level.total > 0)
          .map((level) => (
            <div key={level.code}>
              <div className="flex items-baseline justify-between gap-2 text-theme-xs">
                <span className={`level-${level.code} font-medium`}>
                  {level.label}
                </span>
                <span className="rw-faint tabular-nums">
                  {level.solved} / {level.total}
                </span>
              </div>
              <div
                className="mt-1 h-1.5 overflow-hidden rounded-full rw-chip"
                role="progressbar"
                aria-valuenow={level.solved}
                aria-valuemin={0}
                aria-valuemax={level.total}
                aria-label={level.label}
              >
                <div
                  className={`level-${level.code} h-full rounded-full`}
                  style={{
                    width: `${Math.round((level.solved / level.total) * 100)}%`,
                    backgroundColor: "currentColor",
                  }}
                />
              </div>
            </div>
          ))}
      </div>
    </Card>
  );
}

/** Boshlangan, lekin yechilmagan masala — RoboContest'ning «Davom etish». */
function Continue({ problem }: { problem: Problem }) {
  return (
    <Card title="Davom ettirish" bodyClassName="space-y-2">
      <Link
        href={`/problems/${problem.slug}`}
        className="block font-medium rw-strong rw-link-hover"
      >
        {problem.code !== null && (
          <span className="mr-2 font-mono text-theme-xs rw-faint tabular-nums">
            #{String(problem.code).padStart(4, "0")}
          </span>
        )}
        {problem.title}
      </Link>
      <p className="text-theme-xs rw-faint">
        Oxirgi urinish: {problem.my_verdict}
      </p>
    </Card>
  );
}

function Upcoming({ event }: { event: CalendarEvent }) {
  return (
    <Card title="Yaqin musobaqa" bodyClassName="space-y-2">
      <Link
        href={`/contests/${event.slug}`}
        className="block font-medium rw-strong rw-link-hover"
      >
        {event.title}
      </Link>
      <p className="text-theme-xs rw-faint">
        <time dateTime={event.start_at}>
          {new Date(event.start_at).toLocaleString("uz")}
        </time>
      </p>
    </Card>
  );
}

function Roadmaps({ items }: { items: Roadmap[] }) {
  return (
    <Card
      title="Traektoriya"
      action={
        <Link
          href="/roadmaps"
          className="text-theme-sm rw-accent-ink hover:underline"
        >
          Hammasi
        </Link>
      }
      bodyClassName="rw-divide divide-y"
    >
      {items.slice(0, 3).map((roadmap) => (
        <Link
          key={roadmap.slug}
          href={`/roadmaps#${roadmap.slug}`}
          className="flex items-baseline justify-between gap-3 py-2 first:pt-0 last:pb-0"
        >
          <span className="text-theme-sm font-medium rw-strong">
            {roadmap.title}
          </span>
          <span className="shrink-0 text-theme-xs rw-faint">
            {roadmap.step_count} qadam
          </span>
        </Link>
      ))}
    </Card>
  );
}

export function ArchiveSidebar({
  progress,
  resume,
  upcoming,
  roadmaps,
}: {
  progress: ArchiveProgress;
  resume: Problem | null;
  upcoming: CalendarEvent | null;
  roadmaps: Roadmap[];
}) {
  return (
    <aside className="space-y-4">
      {resume && <Continue problem={resume} />}
      <Progress data={progress} />
      {upcoming && <Upcoming event={upcoming} />}
      {roadmaps.length > 0 && <Roadmaps items={roadmaps} />}
    </aside>
  );
}
