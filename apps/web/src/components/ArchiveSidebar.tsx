import Link from "next/link";

import { Card } from "@/components/ui/Card";
import { ContentName } from "@/components/ui/UzFallbackBadge";
import { Verdict } from "@/components/ui/Verdict";
import { dateTime, t, type Locale } from "@/i18n/messages";
import { Badge } from "@/components/ui/Badge";
import type {
  ArchiveProgress,
  Attempt,
  CalendarEvent,
  Problem,
  Recommendation,
  Roadmap,
  Topic,
  TopicSkill,
} from "@/lib/api";

/** Daraja bo'yicha progress — KEP'ning «Difficulty breakdown» bloki.
 *
 * Mehmonda ham chiziladi: o'shanda arxiv hajmini ko'rsatuvchi karta
 * bo'ladi va ro'yxatdan o'tishga sabab beradi. */
function Progress({ data, locale }: { data: ArchiveProgress; locale: Locale }) {
  const percent = data.total ? Math.round((data.solved / data.total) * 100) : 0;

  return (
    <Card title={t(locale, "profile.tab.solved")} bodyClassName="space-y-3">
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
function Continue({ problem, locale }: { problem: Problem; locale: Locale }) {
  return (
    <Card title={t(locale, "archive.continue")} bodyClassName="space-y-2">
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

function Upcoming({ event, locale }: { event: CalendarEvent; locale: Locale }) {
  return (
    <Card title={t(locale, "archive.upcoming")} bodyClassName="space-y-2">
      <Link
        href={`/contests/${event.slug}`}
        className="block font-medium rw-strong rw-link-hover"
      >
        {event.title}
      </Link>
      <p className="text-theme-xs rw-faint">
        <time dateTime={event.start_at}>
          {dateTime(event.start_at, locale)}
        </time>
      </p>
    </Card>
  );
}

/** O'quv rejalari — KEP'ning «Study plans» bloki, progress bilan.
 * Progress alohida modeldan emas: traektoriya qadamining masalasi
 * yechilganmi, shundan hisoblanadi. */
function Roadmaps({ items, locale }: { items: Roadmap[]; locale: Locale }) {
  return (
    <Card
      title={t(locale, "archive.roadmaps")}
      action={
        <Link
          href="/roadmaps"
          className="text-theme-sm rw-accent-ink hover:underline"
        >
          {t(locale, "filter.all")}
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
  locale,
  attempts,
  popular,
  liked,
}: {
  locale: Locale;
  attempts: Attempt[];
  popular: Problem[];
  liked: Problem[];
}) {
  if (attempts.length === 0 && popular.length === 0 && liked.length === 0)
    return null;

  return (
    <Card title={t(locale, "archive.community")} bodyClassName="space-y-4">
      {attempts.length > 0 && (
        <div>
          <p className="mb-1.5 text-theme-xs font-medium tracking-wider rw-faint uppercase">
            {t(locale, "archive.recentAttempts")}
          </p>
          <ul className="space-y-1">
            {attempts.slice(0, 5).map((attempt) => (
              <li
                key={attempt.id}
                className="flex items-center gap-2 text-theme-xs"
              >
                <Verdict verdict={attempt.verdict} />
                <Link
                  href={`/problems/${attempt.problem}`}
                  // `min-h-6` = 24px — WCAG 2.5.8 (Target Size). Matn
                  // 18px, ya'ni havolaning o'zi juda past edi (O'LCHANDI:
                  // h=18, qo'shni satr bilan oraliq 4px). Lighthouse
                  // `target-size` ni tutdi. `flex items-center` matnni
                  // vertikal markazda saqlaydi, ya'ni ko'rinish o'zgarmaydi.
                  className="flex min-h-6 min-w-0 flex-1 items-center truncate rw-dim-2 rw-link-hover"
                >
                  {attempt.problem}
                </Link>
                <span className="shrink-0 rw-faint">{attempt.username}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {liked.length > 0 && (
        <div>
          <p className="mb-1.5 text-theme-xs font-medium tracking-wider rw-faint uppercase">
            {t(locale, "archive.mostLiked")}
          </p>
          <ul className="space-y-1">
            {liked.slice(0, 5).map((problem) => (
              <li
                key={problem.slug}
                className="flex items-center gap-2 text-theme-xs"
              >
                <Link
                  href={`/problems/${problem.slug}`}
                  className="flex min-h-6 min-w-0 flex-1 items-center truncate rw-dim-2 rw-link-hover"
                >
                  {problem.title}
                </Link>
                <span className="shrink-0 rw-faint tabular-nums">
                  +{problem.likes_count}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {popular.length > 0 && (
        <div>
          <p className="mb-1.5 text-theme-xs font-medium tracking-wider rw-faint uppercase">
            {t(locale, "archive.mostViewed")}
          </p>
          <ul className="space-y-1">
            {popular.slice(0, 5).map((problem) => (
              <li
                key={problem.slug}
                className="flex items-center gap-2 text-theme-xs"
              >
                <Link
                  href={`/problems/${problem.slug}`}
                  // Yuqoridagi bilan bir xil sabab: WCAG 2.5.8.
                  // `items-baseline` → `items-center`: 24px qator
                  // ichida matn bazaviy chiziq bo'ylab emas, markazda
                  // turishi kerak.
                  className="flex min-h-6 min-w-0 flex-1 items-center truncate rw-dim-2 rw-link-hover"
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
function TopicStrength({ topics, locale }: { topics: TopicSkill[]; locale: Locale }) {
  const strong = topics.filter((t) => t.solved > 0).slice(0, 5);
  const stuck = topics
    .filter((t) => t.solved === 0 && t.stuck > 0)
    .sort((a, b) => b.stuck - a.stuck)
    .slice(0, 3);

  if (strong.length === 0 && stuck.length === 0) return null;

  const peak = Math.max(...strong.map((t) => t.rating), 1);

  return (
    <Card title={t(locale, "archive.topicStrength")} bodyClassName="space-y-3">
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

/** Tavsiya — jadval ustida emas, yon panelda.
 *
 * O'lchandi: jadval ustida u 171 px olardi va 873 px ekranda 25
 * qatordan atigi 7 tasi ko'rinardi. Arxivga kelgan odam avval arxivni
 * ko'rishi kerak; tavsiya esa filtrdagi «Menga tavsiya» rejimi bilan
 * ham ochiladi, ya'ni bu yerda u eslatma vazifasini bajaradi. */
function Recommended({ data, locale }: { data: Recommendation; locale: Locale }) {
  return (
    <Card
      title={t(locale, "recommend.title")}
      action={<Badge color="brand">{data.target_difficulty}</Badge>}
      bodyClassName="space-y-1"
    >
      {data.results.slice(0, 5).map((problem) => (
        <Link
          key={problem.slug}
          href={`/problems/${problem.slug}`}
          className="block truncate rw-radius-sm px-2 py-1 text-theme-sm rw-strong transition rw-hover-bg"
        >
          <span className={`level-${problem.level} mr-2 text-theme-xs`}>
            {problem.difficulty}
          </span>
          {problem.title}
        </Link>
      ))}
    </Card>
  );
}

function TagCloud({ topics, locale }: { topics: Topic[]; locale: Locale }) {
  const ranked = [...topics]
    .filter((topic) => topic.problem_count > 0)
    .sort((a, b) => b.problem_count - a.problem_count)
    .slice(0, 24);
  if (ranked.length === 0) return null;

  return (
    <Card title={t(locale, "archive.tagCloud")} bodyClassName="flex flex-wrap gap-1.5">
      {ranked.map((topic) => (
        <Link
          key={topic.slug}
          href={`/problems?topics=${topic.slug}`}
          className="rw-radius-sm border rw-line px-2 py-1 text-theme-xs rw-dim-2 rw-hover-bg"
        >
          <ContentName row={topic} locale={locale} />
          <span className="ml-1 tabular-nums rw-faint">{topic.problem_count}</span>
        </Link>
      ))}
    </Card>
  );
}

export function ArchiveSidebar({
  locale,
  progress,
  skills,
  recommended,
  resume,
  upcoming,
  roadmaps,
  attempts,
  popular,
  liked,
  tagCloud,
}: {
  locale: Locale;
  progress: ArchiveProgress;
  skills: TopicSkill[];
  recommended: Recommendation | null;
  resume: Problem | null;
  upcoming: CalendarEvent | null;
  roadmaps: Roadmap[];
  attempts: Attempt[];
  popular: Problem[];
  liked: Problem[];
  tagCloud: Topic[];
}) {
  return (
    <aside className="min-w-0 space-y-4">
      {resume && <Continue problem={resume} locale={locale} />}
      {recommended && recommended.results.length > 0 && (
        <Recommended data={recommended} locale={locale} />
      )}
      <Progress data={progress} locale={locale} />
      <TopicStrength topics={skills} locale={locale} />
      <TagCloud topics={tagCloud} locale={locale} />
      {upcoming && <Upcoming event={upcoming} locale={locale} />}
      {roadmaps.length > 0 && <Roadmaps items={roadmaps} locale={locale} />}
      <Digest
        locale={locale}
        attempts={attempts}
        popular={popular}
        liked={liked}
      />
    </aside>
  );
}
