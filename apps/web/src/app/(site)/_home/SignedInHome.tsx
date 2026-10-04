import type { Route } from "next";

import { Badge } from "@/components/ui/Badge";
import { ButtonLink } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { IntentLink } from "@/components/ui/IntentLink";
import { UpdateKindBadge } from "@/features/updates";
import { date, dateTime, fill, t, type Locale, type MessageKey } from "@/i18n/messages";
import {
  api,
  type Attempt,
  type Contest,
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

/** The four ratings, in the order the profile shows them. */
const RATINGS: { kind: RatingKind; label: MessageKey }[] = [
  { kind: "skills", label: "leaderboard.skills" },
  { kind: "contest", label: "leaderboard.contest" },
  { kind: "activity", label: "leaderboard.activity" },
  { kind: "challenges", label: "leaderboard.challenges" },
];

const ALL_LINK = "text-theme-sm rw-accent-ink hover:underline";

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

/** The signed-in home page (HITL 2026-10-05): what the visitor was doing
 *  and where they stand, before anything about the site.
 *
 *  It lives beside the page, not under `features/`: it composes several
 *  features (updates, profile, contests), and one feature importing
 *  another is what `tools/check_features.py` forbids.
 *
 *  Every block reads an endpoint that already exists. A block whose data is
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
  resume: { slug: string; title: string } | null;
  stats: PlatformStats;
  contests: Contest[];
  users: UserPublic[];
  roadmaps: Roadmap[];
  updates: SystemUpdate[];
  posts: Post[];
}) {
  // Independent reads; each one failing only removes its own block.
  const [profile, series, wallet, attempts, paths] = await Promise.all([
    api.user(me.username).catch(() => me),
    api.ratingSeries(me.username).catch(() => null),
    getWithSession<Wallet>("/qvant/wallet/").catch(() => null),
    getWithSession<Paginated<Attempt>>(
      `/attempts/?username=${encodeURIComponent(me.username)}&page_size=5`,
    ).catch(() => null),
    // With the session, so `solved_steps` is this user's progress.
    getWithSession<Roadmap[]>("/roadmaps/").catch(() => roadmaps),
  ]);

  const contest = featuredContest(contests);
  const recent = attempts?.results.slice(0, 5) ?? [];
  // The attempt carries the problem's slug; the timeline shows its title.
  // A title that cannot be read falls back to the slug.
  const slugs = [...new Set(recent.map((a) => a.problem))];
  const titles = new Map(
    await Promise.all(
      slugs.map(async (slug) => {
        const problem = await api.problem(slug).catch(() => null);
        return [slug, problem?.title ?? slug] as const;
      }),
    ),
  );
  const path = paths[0] ?? null;
  const podium = users.slice(0, 3);
  const [lead, ...otherPosts] = posts;

  return (
    <div className="space-y-6">
      <div>
        <p className="text-theme-sm rw-dim">{date(new Date().toISOString(), locale)}</p>
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
              <p className="text-theme-sm rw-dim">
                {dateTime(contest.start_at, locale)} — {dateTime(contest.end_at, locale)}
              </p>
              {contest.is_finished && (
                <p className="rw-radius-sm rw-accent-soft px-4 py-3 text-theme-sm">
                  {t(locale, "home.noUpcomingContest")}
                </p>
              )}
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
            return (
              <div key={kind} className="rw-radius border rw-line rw-surface p-5">
                <p className="text-theme-sm font-medium rw-strong">{t(locale, label)}</p>
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
          {recent.length > 0 ? (
            <ol className="ml-1 border-l rw-divider">
              {recent.map((a) => (
                <li key={a.id} className="pb-4 pl-5 last:pb-0">
                  <p className="text-theme-xs rw-faint">{dateTime(a.created_at, locale)}</p>
                  <p className="mt-1 flex flex-wrap items-center gap-2">
                    <IntentLink
                      href={`/problems/${a.problem}`}
                      className="font-medium rw-strong rw-link-hover"
                    >
                      {titles.get(a.problem) ?? a.problem}
                    </IntentLink>
                    <Badge color={a.verdict === "AC" ? "success" : "error"}>{a.verdict}</Badge>
                    <span className="text-theme-xs rw-dim">{a.language}</span>
                  </p>
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
            <progress
              className="mt-2 h-2 w-full"
              value={path.solved_steps}
              max={path.step_count || 1}
            />
          </Card>
        )}
      </div>

      {podium.length > 0 && (
        <Card
          title={t(locale, "home.topUsers")}
          action={
            <IntentLink href="/leaderboard" className={ALL_LINK}>
              {t(locale, "home.all")}
            </IntentLink>
          }
        >
          <ol className="grid gap-4 sm:grid-cols-3">
            {podium.map((u, i) => (
              <li key={u.username} className="rw-radius-sm border rw-line p-4">
                <p className="text-theme-xl font-bold rw-faint">{i + 1}</p>
                <IntentLink
                  href={`/users/${u.username}`}
                  className="mt-2 block truncate font-medium rw-strong rw-link-hover"
                >
                  {u.display_name || u.username}
                </IntentLink>
                <p className="mt-1 text-theme-sm rw-dim">
                  {t(locale, "leaderboard.skills")}{" "}
                  <span className="font-semibold rw-strong">{u.rating_skills}</span>
                </p>
              </li>
            ))}
          </ol>
        </Card>
      )}

      {(updates.length > 0 || posts.length > 0) && (
        <div className="grid gap-6 lg:grid-cols-12">
          {lead && (
            <Card
              title={t(locale, "home.announcements")}
              className="lg:col-span-7"
              action={
                <IntentLink href="/blog" className={ALL_LINK}>
                  {t(locale, "home.all")}
                </IntentLink>
              }
            >
              <IntentLink href={`/blog/${lead.slug}`} className="block">
                <p className="text-theme-xs rw-faint">{date(lead.published_at, locale)}</p>
                <p className="mt-1 text-theme-xl font-bold rw-strong">{lead.title}</p>
                <p className="mt-2 line-clamp-3 text-theme-sm rw-dim">{lead.summary}</p>
              </IntentLink>
              {otherPosts.length > 0 && (
                <ul className="mt-4 divide-y rw-divide border-t rw-divider">
                  {otherPosts.map((post) => (
                    <li key={post.slug}>
                      <IntentLink
                        href={`/blog/${post.slug}`}
                        className="flex flex-wrap items-baseline justify-between gap-2 py-3"
                      >
                        <span className="font-medium rw-strong">{post.title}</span>
                        <span className="text-theme-xs rw-faint">
                          {date(post.published_at, locale)}
                        </span>
                      </IntentLink>
                    </li>
                  ))}
                </ul>
              )}
            </Card>
          )}

          {updates.length > 0 && (
            <Card
              title={t(locale, "update.home")}
              className={lead ? "lg:col-span-5" : "lg:col-span-12"}
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
                          {date(u.released_at, locale)}
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

      <Card title={t(locale, "footer.platform")}>
        <dl className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
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
