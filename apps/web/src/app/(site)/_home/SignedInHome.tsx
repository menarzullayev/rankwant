import type { Route } from "next";

import { Countdown } from "@/components/kit/TimeStamp";
import { Badge } from "@/components/ui/Badge";
import { ButtonLink } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { IntentLink } from "@/components/ui/IntentLink";
import { UpdateKindBadge } from "@/features/updates";
import {
  date,
  dateTime,
  fill,
  t,
  time,
  type Locale,
  type MessageKey,
} from "@/i18n/messages";
import {
  api,
  type HomeEvent,
  type Attempt,
  type Contest,
  type DailyStats,
  type Paginated,
  type PlatformStats,
  type Post,
  type RatingKind,
  type RatingPoint,
  type Roadmap,
  type SystemUpdate,
  type UserPublic,
  type Wallet,
} from "@/lib/api";
import { getWithSession } from "@/lib/api.server";

import { NewsCarousel } from "./NewsCarousel";
import { Person, type PersonRow } from "./Person";
import { TopUsers, type TopTab } from "./TopUsers";

export type ResumeTarget = {
  slug: string;
  title: string;
  difficulty: number;
  attempted: boolean;
};

/** The four ratings, in the order the profile shows them. */
const RATINGS: { kind: RatingKind; label: MessageKey }[] = [
  { kind: "skills", label: "leaderboard.skills" },
  { kind: "contest", label: "leaderboard.contest" },
  { kind: "activity", label: "leaderboard.activity" },
  { kind: "challenges", label: "leaderboard.challenges" },
];
const RATING_LABEL = Object.fromEntries(
  RATINGS.map(({ kind, label }) => [kind, label]),
) as Record<string, MessageKey | undefined>;

/** The page renders on the server, whose clock is UTC. Read as UTC, a date
 *  is yesterday's until 05:00 in Tashkent (measured on the live page,
 *  2026-10-05) — so every date here names the site's own zone. */
const ZONE = "Asia/Tashkent";
const ALL_LINK = "text-theme-sm rw-accent-ink hover:underline";
const MS = "ms";
const ARROW = " → ";
/** Activity rows shown, attempts and events together. */
const FEED = 6;
/** A path with more steps than this is drawn as one bar, not as segments. */
const SEGMENTS_MAX = 12;

/** Rating over time as one line. Fewer than two points draw nothing: a
 *  single point has no direction, and a flat placeholder would read as
 *  "no change" when the truth is "no history". */
function Spark({ points }: { points: RatingPoint[] }) {
  if (points.length < 2) return <span className="block h-10" aria-hidden />;
  const values = points.map((p) => p.after);
  const low = Math.min(...values);
  const span = Math.max(...values) - low || 1;
  const step = 100 / (values.length - 1);
  const path = values
    .map((v, i) => `${(i * step).toFixed(1)},${(30 - ((v - low) / span) * 28).toFixed(1)}`)
    .join(" ");
  return (
    <svg
      viewBox="0 0 100 32"
      preserveAspectRatio="none"
      className="h-10 w-full rw-accent-ink"
      aria-hidden
    >
      <polyline
        points={path}
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        vectorEffect="non-scaling-stroke"
      />
    </svg>
  );
}

/** One series of the 14-day chart, on its own scale.
 *
 *  Three charts, not three lines on one axis: attempts run in the hundreds
 *  and new users in single digits, so a shared axis would flatten two of
 *  the three into the baseline. */
function DayBars({ label, values }: { label: string; values: number[] }) {
  const top = Math.max(...values, 1);
  const total = values.reduce((sum, v) => sum + v, 0);
  return (
    <div>
      <div className="flex items-baseline justify-between gap-3">
        <span className="text-theme-sm rw-dim">{label}</span>
        <span className="text-theme-sm font-semibold tabular-nums rw-strong">{total}</span>
      </div>
      <svg
        viewBox={`0 0 ${values.length * 10} 32`}
        preserveAspectRatio="none"
        className="mt-1 h-10 w-full rw-accent-ink"
        role="img"
        aria-label={`${label}: ${total}`}
      >
        {values.map((v, i) => {
          // A day with anything gets a visible bar, however small next to the peak.
          const h = v > 0 ? Math.max(2, (v / top) * 32) : 0.5;
          return (
            <rect key={i} x={i * 10 + 1} y={32 - h} width="8" height={h} fill="currentColor" />
          );
        })}
      </svg>
    </div>
  );
}

/** The contest worth showing: the nearest one not finished, otherwise the
 *  most recent finished one — an empty card says nothing. */
function featuredContest(contests: Contest[]): Contest | null {
  const open = contests
    .filter((c) => !c.is_finished)
    .sort((a, b) => +new Date(a.start_at) - +new Date(b.start_at));
  if (open[0]) return open[0];
  return (
    [...contests].sort((a, b) => +new Date(b.start_at) - +new Date(a.start_at))[0] ?? null
  );
}

function duration(contest: Contest, locale: Locale): string {
  const minutes = Math.round((+new Date(contest.end_at) - +new Date(contest.start_at)) / 60000);
  const parts = [
    minutes >= 60 ? fill(t(locale, "home.hours"), { n: String(Math.floor(minutes / 60)) }) : "",
    minutes % 60 ? fill(t(locale, "home.minutes"), { n: String(minutes % 60) }) : "",
  ];
  return parts.filter(Boolean).join(" ");
}

/** Attempts on the same problem in a row are one line of the feed: a
 *  hundred submissions to one problem are one thing that happened. */
function groupAttempts(attempts: Attempt[]): { latest: Attempt; count: number }[] {
  const groups: { latest: Attempt; count: number }[] = [];
  for (const attempt of attempts) {
    const last = groups[groups.length - 1];
    if (last && last.latest.problem === attempt.problem) last.count += 1;
    else groups.push({ latest: attempt, count: 1 });
  }
  return groups;
}

function person(user: UserPublic): PersonRow {
  return {
    username: user.username,
    name: user.display_name,
    avatar: user.avatar_url,
    title: user.title,
  };
}

function Meta({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <dt className="text-theme-xs rw-dim">{label}</dt>
      <dd className="text-theme-sm font-semibold rw-strong">{children}</dd>
    </div>
  );
}

/** The signed-in home page (HITL 2026-10-05): what the visitor was doing
 *  and where they stand, before anything about the site.
 *
 *  It lives beside the page, not under `features/`: it composes several
 *  features (updates, profile, contests), and one feature importing
 *  another is what `tools/check_features.py` forbids.
 *
 *  Every block reads an endpoint that exists. A block whose data is
 *  missing is left out — it never renders a placeholder or a zero that
 *  would read as a fact.
 */
export async function SignedInHome({
  locale,
  me,
  resume,
  stats,
  contests,
  users,
  roadmaps,
  updates,
  posts,
}: {
  locale: Locale;
  me: UserPublic;
  resume: ResumeTarget | null;
  stats: PlatformStats;
  contests: Contest[];
  users: UserPublic[];
  roadmaps: Roadmap[];
  updates: SystemUpdate[];
  posts: Post[];
}) {
  const top = (field: string) =>
    api
      .topUsers(field)
      .then((page) => page.results)
      .catch((): UserPublic[] => []);

  // Independent reads; each one failing only removes its own block.
  const [
    profile,
    series,
    wallet,
    attempts,
    events,
    paths,
    daily,
    presence,
    byContest,
    byActivity,
    byChallenges,
    byStreak,
    byQvant,
  ] = await Promise.all([
    api.user(me.username).catch(() => me),
    api.ratingSeries(me.username).catch(() => null),
    getWithSession<Wallet>("/qvant/wallet/").catch(() => null),
    getWithSession<Paginated<Attempt>>(
      `/attempts/?username=${encodeURIComponent(me.username)}&page_size=25`,
    ).catch(() => null),
    getWithSession<HomeEvent[]>("/me/activity/").catch((): HomeEvent[] => []),
    // With the session, so `solved_steps` and `next_step` are this user's.
    getWithSession<Roadmap[]>("/roadmaps/").catch(() => roadmaps),
    api.statsDaily().catch((): DailyStats[] => []),
    api.presence().catch(() => null),
    top("rating_contest"),
    top("rating_activity"),
    top("rating_challenges"),
    top("streak_count"),
    api.qvantTop().catch(() => []),
  ]);

  const contest = featuredContest(contests);
  const groups = groupAttempts(attempts?.results ?? []);
  // The attempt carries the problem's slug; the feed shows its title.
  // A title that cannot be read falls back to the slug.
  const slugs = [...new Set(groups.slice(0, FEED).map((g) => g.latest.problem))];
  const titles = new Map(
    await Promise.all(
      slugs.map(async (slug) => {
        const problem = await api.problem(slug).catch(() => null);
        return [slug, problem?.title ?? slug] as const;
      }),
    ),
  );
  const stamp = (value: string) => dateTime(value, locale, { timeZone: ZONE });

  const feed = [
    ...groups.map(({ latest, count }) => ({
      key: `a${latest.id}`,
      at: latest.created_at,
      body: (
        <>
          <IntentLink
            href={`/problems/${latest.problem}` as Route}
            className="font-medium rw-strong rw-link-hover"
          >
            {titles.get(latest.problem) ?? latest.problem}
          </IntentLink>
          <Badge color={latest.verdict === "AC" ? "success" : "error"}>{latest.verdict}</Badge>
          <span className="text-theme-xs rw-dim">
            {latest.language}
            {latest.time_ms > 0 && (
              <>
                {" · "}
                {latest.time_ms} {MS}
              </>
            )}
          </span>
          {count > 1 && (
            <span className="text-theme-xs rw-dim">
              {fill(t(locale, "home.attemptCount"), { count: String(count) })}
            </span>
          )}
        </>
      ),
    })),
    ...events
      // A solve already shows as its attempt line.
      .filter((e) => !(e.kind === "solved" && groups.some((g) => g.latest.problem === e.ref_id)))
      .map((e) => ({
        key: `e${e.id}`,
        at: e.created_at,
        body:
          e.kind === "solved" ? (
            <>
              <span className="rw-dim">{t(locale, "home.event.solved")}</span>
              <IntentLink
                href={`/problems/${e.ref_id}` as Route}
                className="font-medium rw-strong rw-link-hover"
              >
                {e.data.title ?? e.ref_id}
              </IntentLink>
            </>
          ) : e.kind === "rating" ? (
            <>
              <span className="font-medium rw-strong">
                {t(locale, RATING_LABEL[String(e.data.type)] ?? "leaderboard.title")}
                {": "}
                {e.data.before}
                {ARROW}
                {e.data.after}
              </span>
              <Badge color={Number(e.data.delta) >= 0 ? "success" : "error"}>
                {Number(e.data.delta) > 0 ? "+" : ""}
                {e.data.delta}
              </Badge>
            </>
          ) : e.kind === "qvant" ? (
            <span className="font-medium rw-strong">
              {t(locale, "nav.qvant")}
              {": "}
              {Number(e.data.amount) > 0 ? "+" : ""}
              {e.data.amount}
            </span>
          ) : (
            <>
              <span className="rw-dim">{t(locale, "home.event.contest")}</span>
              <IntentLink
                href={`/contests/${e.ref_id}` as Route}
                className="font-medium rw-strong rw-link-hover"
              >
                {e.data.title ?? e.ref_id}
              </IntentLink>
            </>
          ),
      })),
  ]
    .sort((a, b) => +new Date(b.at) - +new Date(a.at))
    .slice(0, FEED);

  const path = paths[0] ?? null;
  const next = path?.next_step ?? null;
  const nextHref = next?.problem
    ? `/problems/${next.problem}`
    : next?.article
      ? `/learn/${next.article}`
      : "/roadmaps";

  const ranked = (list: UserPublic[], value: (user: UserPublic) => number) =>
    list.slice(0, 3).map((user) => ({ ...person(user), value: value(user) }));
  const tabs: TopTab[] = [
    { key: "skills", label: t(locale, "leaderboard.skills"), rows: ranked(users, (u) => u.rating_skills) },
    { key: "contest", label: t(locale, "leaderboard.contest"), rows: ranked(byContest, (u) => u.rating_contest) },
    { key: "activity", label: t(locale, "leaderboard.activity"), rows: ranked(byActivity, (u) => u.rating_activity) },
    { key: "challenges", label: t(locale, "leaderboard.challenges"), rows: ranked(byChallenges, (u) => u.rating_challenges) },
    { key: "streak", label: t(locale, "leaderboard.streak"), rows: ranked(byStreak, (u) => u.streak_count) },
    {
      key: "qvant",
      label: t(locale, "nav.qvant"),
      rows: byQvant.slice(0, 3).map((row) => ({
        username: row.username,
        name: row.display_name,
        avatar: row.avatar_url,
        title: null,
        value: row.balance,
      })),
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <p className="text-theme-sm rw-dim">
          {date(new Date(), locale, {
            weekday: "long",
            day: "numeric",
            month: "long",
            year: "numeric",
            timeZone: ZONE,
          })}
        </p>
        <h1 className="mt-1 text-title-sm font-bold rw-strong">
          {fill(t(locale, "home.greeting"), { name: me.display_name || me.username })}
        </h1>
      </div>

      <div className="grid gap-6 lg:grid-cols-12">
        {/* The one raised block on the page: the next thing to do. */}
        <section className="rw-radius border rw-line rw-surface p-6 rw-shadow lg:col-span-7">
          <p className="text-theme-xs font-semibold uppercase rw-dim">
            {t(locale, "home.continue")}
          </p>
          <p className="mt-3 text-2xl font-bold rw-strong">
            {resume ? resume.title : t(locale, "nav.problems")}
          </p>
          {resume && (
            <p className="mt-1 text-theme-sm rw-dim">
              {t(locale, "problems.difficulty")} {resume.difficulty}
              {" · "}
              {t(locale, resume.attempted ? "home.attempted" : "home.notAttempted")}
            </p>
          )}
          <div className="mt-5 flex flex-wrap gap-3">
            <ButtonLink
              intent
              href={resume ? { pathname: `/problems/${resume.slug}` } : "/problems"}
            >
              {t(locale, resume ? "home.openProblem" : "nav.problems")}
            </ButtonLink>
            <ButtonLink intent href={resume ? "/problems" : "/contests"} variant="outline">
              {t(locale, resume ? "nav.problems" : "nav.contests")}
            </ButtonLink>
          </div>
          <dl className="mt-6 flex flex-wrap gap-x-8 gap-y-3 border-t rw-divider pt-4 text-theme-sm">
            <div>
              <dt className="rw-dim">{t(locale, "profile.solved")}</dt>
              <dd className="text-theme-xl font-bold rw-strong">{profile.solved_count}</dd>
            </div>
            <div>
              <dt className="rw-dim">{t(locale, "leaderboard.streak")}</dt>
              <dd className="text-theme-xl font-bold rw-strong">
                {profile.streak_count} {t(locale, "header.streak")}
              </dd>
            </div>
            {wallet && (
              <div>
                <dt className="rw-dim">{t(locale, "nav.qvant")}</dt>
                <dd className="text-theme-xl font-bold rw-strong">{wallet.balance}</dd>
              </div>
            )}
          </dl>
        </section>

        <Card
          title={t(locale, "home.contest")}
          className="lg:col-span-5"
          action={
            <IntentLink href="/contests" className={ALL_LINK}>
              {t(locale, "home.all")}
            </IntentLink>
          }
        >
          {contest ? (
            <div className="space-y-4">
              <div className="flex flex-wrap items-center gap-2">
                <Badge
                  color={contest.is_running ? "success" : contest.is_finished ? "neutral" : "info"}
                >
                  {t(
                    locale,
                    contest.is_running
                      ? "contests.running"
                      : contest.is_finished
                        ? "contests.finished"
                        : "contests.upcoming",
                  )}
                </Badge>
                {contest.is_rated && <Badge color="brand">{t(locale, "contests.rated")}</Badge>}
                <Badge>{contest.scoring_type}</Badge>
              </div>
              <IntentLink
                href={`/contests/${contest.slug}`}
                className="block text-theme-xl font-bold rw-strong rw-link-hover"
              >
                {contest.title}
              </IntentLink>
              <dl className="grid grid-cols-2 gap-3">
                <Meta label={t(locale, "home.starts")}>{stamp(contest.start_at)}</Meta>
                <Meta label={t(locale, "home.duration")}>{duration(contest, locale)}</Meta>
                <Meta label={t(locale, "profile.participants")}>{contest.participant_count}</Meta>
              </dl>
              {contest.is_finished ? (
                <p className="rw-radius-sm rw-accent-soft px-4 py-3 text-theme-sm">
                  {t(locale, "home.noUpcomingContest")}
                </p>
              ) : (
                <p className="rw-radius-sm rw-accent-soft px-4 py-3 text-theme-sm">
                  <Countdown
                    until={contest.is_running ? contest.end_at : contest.start_at}
                    locale={locale}
                  />
                </p>
              )}
              <div className="flex flex-wrap gap-3">
                <ButtonLink intent href={`/contests/${contest.slug}` as Route} variant="outline">
                  {t(locale, contest.is_finished ? "standings.title" : "home.openContest")}
                </ButtonLink>
                {contest.is_finished && (
                  <ButtonLink intent href="/problems" variant="outline">
                    {t(locale, "home.practiceArchive")}
                  </ButtonLink>
                )}
              </div>
            </div>
          ) : (
            <p className="text-theme-sm rw-dim">{t(locale, "home.noUpcomingContest")}</p>
          )}
        </Card>
      </div>

      <section aria-labelledby="home-ratings" className="space-y-3">
        <div className="flex items-baseline justify-between gap-3">
          <h2 id="home-ratings" className="text-theme-xl font-semibold rw-strong">
            {t(locale, "home.myRatings")}
          </h2>
          <IntentLink href="/rating" className={ALL_LINK}>
            {t(locale, "nav.ratingInfo")}
          </IntentLink>
        </div>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {RATINGS.map(({ kind, label }) => {
            const rank = profile.ranks?.[kind];
            const best = profile.max_ratings?.[kind];
            const name = t(locale, label);
            return (
              <div key={kind} className="rw-radius border rw-line rw-surface p-5">
                <div className="flex items-center justify-between gap-2">
                  <p className="text-theme-sm font-medium rw-strong">{name}</p>
                  <IntentLink
                    href="/rating"
                    aria-label={fill(t(locale, "home.howRated"), { name })}
                    className="flex size-7 items-center justify-center rounded-full border rw-line text-theme-xs font-bold rw-dim rw-hover-bg"
                  >
                    <span aria-hidden="true">i</span>
                  </IntentLink>
                </div>
                <p className="mt-2 flex flex-wrap items-baseline gap-x-3">
                  <span className="text-title-sm font-bold rw-strong lg:text-2xl xl:text-title-sm">
                    {profile[`rating_${kind}`]}
                  </span>
                  {rank ? (
                    <span className="text-theme-sm rw-dim">
                      {fill(t(locale, "home.rankPlace"), { rank: String(rank) })}
                    </span>
                  ) : null}
                </p>
                <div className="mt-3">
                  <Spark points={series?.series[kind] ?? []} />
                </div>
                {best ? (
                  <p className="mt-2 text-theme-xs rw-faint">
                    {fill(t(locale, "home.bestRating"), { value: String(best) })}
                  </p>
                ) : kind === "contest" && !profile.title ? (
                  <p className="mt-2 text-theme-xs rw-faint">{t(locale, "home.noTitle")}</p>
                ) : null}
              </div>
            );
          })}
        </div>
      </section>

      <div className="grid gap-6 lg:grid-cols-12">
        <Card
          title={t(locale, "home.activity")}
          className="lg:col-span-7"
          action={
            <IntentLink href="/attempts" className={ALL_LINK}>
              {t(locale, "home.all")}
            </IntentLink>
          }
        >
          {feed.length > 0 ? (
            <ol className="ml-1 border-l rw-divider">
              {feed.map((item) => (
                <li key={item.key} className="pb-4 pl-5 last:pb-0">
                  <p className="text-theme-xs rw-faint">{stamp(item.at)}</p>
                  <p className="mt-1 flex flex-wrap items-center gap-2">{item.body}</p>
                </li>
              ))}
            </ol>
          ) : (
            <p className="text-theme-sm rw-dim">{t(locale, "home.noActivity")}</p>
          )}
        </Card>

        {path && (
          <Card
            title={t(locale, "home.learningPath")}
            className="lg:col-span-5"
            action={
              <IntentLink href="/roadmaps" className={ALL_LINK}>
                {t(locale, "home.all")}
              </IntentLink>
            }
          >
            <p className="text-theme-xl font-bold rw-strong">{path.title}</p>
            <p className="mt-1 text-theme-sm rw-dim">{path.description}</p>
            <p className="mt-4 text-theme-sm rw-strong">
              {fill(t(locale, "home.stepsDone"), {
                done: String(path.solved_steps),
                total: String(path.step_count),
              })}
            </p>
            {path.step_count > 0 && path.step_count <= SEGMENTS_MAX ? (
              <div className="mt-2 flex gap-1.5" aria-hidden="true">
                {Array.from({ length: path.step_count }, (_, i) => (
                  <span
                    key={i}
                    className={`h-2 flex-1 rounded-full ${i < path.solved_steps ? "rw-accent-bg" : "rw-accent-soft"}`}
                  />
                ))}
              </div>
            ) : (
              <progress
                className="mt-2 h-2 w-full"
                value={path.solved_steps}
                max={path.step_count || 1}
              />
            )}
            {next ? (
              <div className="mt-4 flex flex-wrap items-center justify-between gap-3 rw-radius-sm border rw-line p-4">
                <div className="min-w-0">
                  <p className="text-theme-xs rw-dim">
                    {fill(t(locale, "home.nextStep"), { n: String(next.order) })}
                  </p>
                  <p className="truncate font-medium rw-strong">
                    {next.title || next.problem || next.article}
                  </p>
                </div>
                <ButtonLink intent href={nextHref as Route} variant="outline">
                  {t(locale, "home.startStep")}
                </ButtonLink>
              </div>
            ) : (
              path.step_count > 0 && (
                <p className="mt-4 text-theme-sm rw-dim">{t(locale, "home.pathDone")}</p>
              )
            )}
          </Card>
        )}
      </div>

      <Card
        title={t(locale, "home.topUsers")}
        action={
          <IntentLink href="/leaderboard" className={ALL_LINK}>
            {t(locale, "home.all")}
          </IntentLink>
        }
      >
        <TopUsers
          tabs={tabs}
          label={t(locale, "home.topBy")}
          empty={t(locale, "home.emptyTop")}
        />
      </Card>

      {(updates.length > 0 || posts.length > 0) && (
        <div className="grid gap-6 lg:grid-cols-12">
          {posts.length > 0 && (
            <Card
              title={t(locale, "home.announcements")}
              className="lg:col-span-7"
              action={
                <IntentLink href="/blog" className={ALL_LINK}>
                  {t(locale, "home.all")}
                </IntentLink>
              }
            >
              <NewsCarousel
                slides={posts.map((post) => ({
                  slug: post.slug,
                  title: post.title,
                  summary: post.summary,
                  date: date(post.published_at, locale, { timeZone: ZONE }),
                  cover: post.cover_url,
                }))}
                labels={{
                  read: t(locale, "home.readPost"),
                  previous: t(locale, "home.prevPost"),
                  next: t(locale, "home.nextPost"),
                }}
              />
            </Card>
          )}

          {updates.length > 0 && (
            <Card
              title={t(locale, "update.home")}
              className={posts.length > 0 ? "lg:col-span-5" : "lg:col-span-12"}
              action={
                <IntentLink href={"/updates" as Route} className={ALL_LINK}>
                  {t(locale, "home.all")}
                </IntentLink>
              }
            >
              <ol className="ml-1 border-l rw-divider">
                {updates.map((u) => (
                  <li key={u.id} className="pb-4 pl-5 last:pb-0">
                    <IntentLink href={`/updates/${u.id}`} className="block">
                      <span className="flex flex-wrap items-center gap-2">
                        <UpdateKindBadge kind={u.kind} locale={locale} />
                        <span className="text-theme-xs rw-faint">
                          {date(u.released_at, locale, { timeZone: ZONE })}
                        </span>
                      </span>
                      <span className="mt-1 block font-medium rw-strong">{u.title}</span>
                    </IntentLink>
                  </li>
                ))}
              </ol>
            </Card>
          )}
        </div>
      )}

      <Card title={t(locale, "home.platformActivity")}>
        <div className="grid gap-6 lg:grid-cols-2">
          {daily.length > 0 && (
            <div className="space-y-4">
              <p className="text-theme-sm font-semibold rw-strong">{t(locale, "home.last14")}</p>
              <DayBars label={t(locale, "home.newUsers")} values={daily.map((d) => d.new_users)} />
              <DayBars
                label={t(locale, "home.activeUsers")}
                values={daily.map((d) => d.active_users)}
              />
              <DayBars label={t(locale, "home.attempts")} values={daily.map((d) => d.attempts)} />
            </div>
          )}
          {presence && (
            <div className="space-y-3">
              <div className="flex flex-wrap items-baseline justify-between gap-3">
                <p className="text-theme-sm font-semibold rw-strong">
                  {t(locale, "home.activeToday")}
                </p>
                <span className="text-theme-sm rw-dim">
                  {fill(t(locale, "home.onlineNow"), { count: String(presence.online) })}
                </span>
              </div>
              {presence.results.length > 0 ? (
                <ul className="grid gap-3 sm:grid-cols-2">
                  {presence.results.map((row) => (
                    <li key={row.username}>
                      <Person
                        person={{
                          username: row.username,
                          name: row.display_name,
                          avatar: row.avatar_url,
                          title: row.title,
                        }}
                      >
                        {row.online ? (
                          <span className="block text-theme-xs rw-ok-ink">
                            {t(locale, "profile.online")}
                          </span>
                        ) : (
                          <span className="block text-theme-xs rw-dim">
                            {time(row.last_seen, locale, {
                              hour: "2-digit",
                              minute: "2-digit",
                              timeZone: ZONE,
                            })}
                          </span>
                        )}
                      </Person>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-theme-sm rw-dim">{t(locale, "home.nobodyToday")}</p>
              )}
            </div>
          )}
        </div>
        <dl className="mt-6 grid gap-4 border-t rw-divider pt-4 sm:grid-cols-2 lg:grid-cols-4">
          {(
            [
              ["nav.problems", stats.problems],
              ["nav.contests", stats.contests],
              ["home.attempts", stats.attempts],
              ["admin.section.users", stats.users],
            ] as const
          ).map(([label, value]) => (
            <div key={label}>
              <dd className="text-2xl font-bold rw-strong">{value}</dd>
              <dt className="text-theme-sm rw-dim">{t(locale, label)}</dt>
            </div>
          ))}
        </dl>
      </Card>
    </div>
  );
}
