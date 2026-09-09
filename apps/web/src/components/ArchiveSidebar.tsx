import Link from "next/link";

import { Card } from "@/components/ui/Card";
import { VerdictBadge } from "@/components/VerdictBadge";
import type {
  ArchiveProgress,
  Attempt,
  CalendarEvent,
  Problem,
  Roadmap,
  TopicSkill,
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

/** O'quv rejalari — KEP'ning «Study plans» bloki, progress bilan.
 * Progress alohida modeldan emas: traektoriya qadamining masalasi
 * yechilganmi, shundan hisoblanadi. */
function Roadmaps({ items }: { items: Roadmap[] }) {
  return (
    <Card
      title="O'quv rejalari"
      action={
        <Link
          href="/roadmaps"
          className="text-theme-sm rw-accent-ink hover:underline"
        >
          Hammasi
        </Link>
      }
      bodyClassName="space-y-3"
    >
      {items.slice(0, 3).map((roadmap) => {
        const percent = roadmap.step_count
          ? Math.round((roadmap.solved_steps / roadmap.step_count) * 100)
          : 0;
        return (
          <Link key={roadmap.slug} href="/roadmaps" className="block">
            <div className="flex items-baseline justify-between gap-3">
              <span className="text-theme-sm font-medium rw-strong">
                {roadmap.title}
              </span>
              <span className="shrink-0 text-theme-xs rw-faint tabular-nums">
                {roadmap.solved_steps} / {roadmap.step_count}
              </span>
            </div>
            <div
              className="mt-1 h-1.5 overflow-hidden rounded-full rw-chip"
              role="progressbar"
              aria-valuenow={roadmap.solved_steps}
              aria-valuemin={0}
              aria-valuemax={roadmap.step_count}
              aria-label={roadmap.title}
            >
              <div
                className="h-full rounded-full rw-accent-bg"
                style={{ width: `${percent}%` }}
              />
            </div>
          </Link>
        );
      })}
    </Card>
  );
}

/** «Oxirgi musobaqa / urinishlar / ko'p ko'rilgan» — KEP'ning uch tabli
 * bloki. Server komponenti bo'lib qolishi uchun tab o'rniga uchtasi
 * ketma-ket: mijoz holati kerak emas va SSR da hammasi ko'rinadi. */
function Digest({
  attempts,
  popular,
}: {
  attempts: Attempt[];
  popular: Problem[];
}) {
  if (attempts.length === 0 && popular.length === 0) return null;

  return (
    <Card title="Hamjamiyat" bodyClassName="space-y-4">
      {attempts.length > 0 && (
        <div>
          <p className="mb-1.5 text-theme-xs font-medium tracking-wider rw-faint uppercase">
            Oxirgi urinishlar
          </p>
          <ul className="space-y-1">
            {attempts.slice(0, 5).map((attempt) => (
              <li
                key={attempt.id}
                className="flex items-center gap-2 text-theme-xs"
              >
                <VerdictBadge verdict={attempt.verdict} />
                <Link
                  href={`/problems/${attempt.problem}`}
                  className="min-w-0 flex-1 truncate rw-dim-2 rw-link-hover"
                >
                  {attempt.problem}
                </Link>
                <span className="shrink-0 rw-faint">{attempt.username}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {popular.length > 0 && (
        <div>
          <p className="mb-1.5 text-theme-xs font-medium tracking-wider rw-faint uppercase">
            Ko&apos;p ko&apos;rilgan
          </p>
          <ul className="space-y-1">
            {popular.slice(0, 5).map((problem) => (
              <li
                key={problem.slug}
                className="flex items-baseline gap-2 text-theme-xs"
              >
                <Link
                  href={`/problems/${problem.slug}`}
                  className="min-w-0 flex-1 truncate rw-dim-2 rw-link-hover"
                >
                  {problem.title}
                </Link>
                <span className="shrink-0 rw-faint tabular-nums">
                  {problem.view_count}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </Card>
  );
}

/** Mavzu kesimidagi kuch.
 *
 * Umumiy Skills reytingi bitta raqam va u «keyin nima qilay?» degan
 * savolga javob bermaydi. Bu blok beradi: qaysi mavzuda kuchlisiz va
 * qayerda urinib, yecha olmagansiz. Ikkinchisi qimmatroq — taqalgan
 * joy o'rganish uchun eng foydali nuqta.
 *
 * Faqat kirgan foydalanuvchi uchun: mehmonda hamma qator nol bo'lardi. */
function TopicStrength({ topics }: { topics: TopicSkill[] }) {
  const strong = topics.filter((t) => t.solved > 0).slice(0, 5);
  const stuck = topics
    .filter((t) => t.solved === 0 && t.stuck > 0)
    .sort((a, b) => b.stuck - a.stuck)
    .slice(0, 3);

  if (strong.length === 0 && stuck.length === 0) return null;

  const peak = Math.max(...strong.map((t) => t.rating), 1);

  return (
    <Card title="Mavzu bo'yicha kuch" bodyClassName="space-y-3">
      {strong.map((topic) => (
        <div key={topic.slug}>
          <div className="flex items-baseline justify-between gap-2 text-theme-xs">
            <Link
              href={`/problems?topics=${topic.slug}`}
              className="font-medium rw-strong rw-link-hover"
            >
              {topic.label}
            </Link>
            <span className="rw-faint tabular-nums">
              {topic.solved} / {topic.total}
            </span>
          </div>
          <div className="mt-1 h-1.5 overflow-hidden rounded-full rw-chip">
            <div
              className="h-full rounded-full rw-accent-bg"
              style={{ width: `${Math.round((topic.rating / peak) * 100)}%` }}
            />
          </div>
        </div>
      ))}

      {stuck.length > 0 && (
        <p className="text-theme-xs rw-dim">
          Urinib, hali yecha olmaganingiz:{" "}
          {stuck.map((topic, index) => (
            <span key={topic.slug}>
              {index > 0 && ", "}
              <Link
                href={`/problems?topics=${topic.slug}&attempted=true&solved=false`}
                className="font-medium rw-accent-ink"
              >
                {topic.label}
              </Link>
            </span>
          ))}
        </p>
      )}
    </Card>
  );
}

export function ArchiveSidebar({
  progress,
  skills,
  resume,
  upcoming,
  roadmaps,
  attempts,
  popular,
}: {
  progress: ArchiveProgress;
  skills: TopicSkill[];
  resume: Problem | null;
  upcoming: CalendarEvent | null;
  roadmaps: Roadmap[];
  attempts: Attempt[];
  popular: Problem[];
}) {
  return (
    <aside className="space-y-4">
      {resume && <Continue problem={resume} />}
      <Progress data={progress} />
      <TopicStrength topics={skills} />
      {upcoming && <Upcoming event={upcoming} />}
      {roadmaps.length > 0 && <Roadmaps items={roadmaps} />}
      <Digest attempts={attempts} popular={popular} />
    </aside>
  );
}
