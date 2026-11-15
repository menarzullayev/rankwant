import { inReaderAlphabet } from "@/i18n/alphabet";
import type { Route } from "next";

import { Badge } from "@/components/ui/Badge";
import { IntentLink } from "@/components/ui/IntentLink";
import { Card } from "@/components/ui/Card";
import { TBody, TD, TH, THead, TR, Table } from "@/components/ui/Table";
import { UpdateKindBadge } from "@/features/updates";
import { getLocale } from "@/i18n/server";
import { LOCALES, date, dateTime, fill, t } from "@/i18n/messages";
import {
  api,
  ApiError,
  type Attempt,
  type Contest,
  type Paginated,
  type Post,
  type Problem,
  type ProblemDetail,
  type Recommendation,
  type SystemUpdate,
  type UserPublic,
} from "@/lib/api";
import { getSessionUser, getWithSession } from "@/lib/api.server";
import {
  AlgorithmLibrary,
  PopularProblems,
  RecentContests,
  libraryArticles,
  popularProblems,
  recentContests,
} from "./_home/GuestContent";
import { GuestHero } from "./_home/GuestHero";
import { pickHeroProblem } from "./_home/hero-model";
import { RegionMap } from "./_home/RegionMap";
import { SignedInHome, type ResumeTarget } from "./_home/SignedInHome";

/** Kirgan foydalanuvchi uchun «qayerdan davom etaman» savoliga javob:
 * avval tugallanmagan urinish, bo'lmasa tavsiya. Mehmonga `null`.
 * `attempted` separates the two: a pending attempt has been tried, a
 * recommendation has not. */
async function resumeTarget(
  me: UserPublic | null,
): Promise<ResumeTarget | null> {
  if (!me) return null;

  const attempts = await getWithSession<Paginated<Attempt>>(
    `/attempts/?username=${encodeURIComponent(me.username)}`,
  ).catch(() => null);

  const pending = attempts?.results.find((a) => a.verdict !== "AC");
  if (pending) {
    const problem = await api
      .problem(pending.problem)
      .catch((): ProblemDetail | null => null);
    if (problem) {
      return {
        slug: problem.slug,
        title: problem.title,
        difficulty: problem.difficulty,
        attempted: true,
      };
    }
  }

  const recommended = await getWithSession<Recommendation>(
    "/problems/recommendation/",
  ).catch(() => null);
  const first = recommended?.results[0];
  return first
    ? {
        slug: first.slug,
        title: first.title,
        difficulty: first.difficulty,
        attempted: false,
      }
    : null;
}

/** Yordamchi bo'lim yiqilsa — bo'sh ro'yxat, lekin sahifa ochiladi.
 *
 *  Faqat API xatosi yutiladi: boshqa xato (masalan `fetch` yiqilishi)
 *  yashirilmaydi, aks holda nosozlik jimgina "bo'lim yo'q"ga aylanardi.
 */
function softFail<T>(error: unknown): T[] {
  if (!(error instanceof ApiError)) throw error;
  return [];
}

// Layout cookie o'qiydi, shuning uchun Next sahifani dinamik chizadi.
// Mehmon GET `/` Cache-Control ni `home-cache.ts` + proxy/instrumentation
// origin'da qo'yadi; Cloudflare origin header'ga rioya qiladi.
export const dynamic = "force-dynamic";

/** Yaqin musobaqa = hozir ketayotgan yoki hali boshlanmagan, eng yaqini birinchi. */
function upcoming(contests: Contest[]): Contest[] {
  return contests
    .filter((c) => !c.is_finished)
    .sort((a, b) => +new Date(a.start_at) - +new Date(b.start_at))
    .slice(0, 4);
}

export default async function Home() {
  const locale = await getLocale();

  // Barchasi mustaqil — ketma-ket kutish bosh sahifani sekinlashtirardi.
  const [stats, contests, users, articles, roadmaps] = await Promise.all([
    api.stats(),
    api.contests(),
    api.leaderboard(),
    api.articles(),
    api.roadmaps(locale),
  ]);

  // Blog va o'zgarishlar — ikkalasi ham YORDAMCHI bo'lim: biri bo'sh yoki
  // o'chirilgan bo'lsa bosh sahifa baribir ochilishi kerak. Lekin ularni
  // ketma-ket kutish ortiqcha — shuning uchun bitta `Promise.all` ichida.
  const [posts, updates, popular, activeMembers] = await Promise.all([
    api
      .posts()
      .then((page) => page.results.slice(0, 3))
      .catch(softFail<Post>),
    api
      .updates("?page_size=4")
      .then((page) => page.results)
      .catch(softFail<SystemUpdate>),
    // Public content for visitors who arrive from a search engine (decision 2026-11-15).
    api
      .popularProblems()
      .then((page) => page.results)
      .catch(softFail<Problem>),
    // The map is shown only when somebody was active: a tile map of zeros says nothing.
    api
      .regionActivity()
      .then((activity) => activity.total)
      .catch(() => 0),
  ]);

  const me = await getSessionUser<UserPublic>();
  const resume = await resumeTarget(me);

  // A signed-in visitor gets the personal dashboard (HITL 2026-10-05).
  // The markup below stays the guest page: it is what the CDN caches and
  // what the homepage decisions in `check_decisions.py` guard.
  if (me) {
    return (
      <SignedInHome
        locale={locale}
        me={me}
        resume={resume}
        stats={stats}
        contests={contests.results}
        users={users.results}
        roadmaps={roadmaps}
        updates={updates}
        posts={posts}
      />
    );
  }

  // The numbers of the first block describe what the platform can do; they are read
  // from the database, and none of them is the user count (decision 2026-11-15).
  const [languageCount, problemCount, heroProblem] = await Promise.all([
    api
      .languages()
      .then((page) => page.count)
      .catch(() => 0),
    api
      .problemTotal()
      .then((page) => page.count)
      .catch(() => 0),
    (async () => {
      const pick = pickHeroProblem(popular);
      return pick ? api.heroProblem(pick.slug).catch(() => null) : null;
    })(),
  ]);

  const soon = upcoming(contests.results);
  const last = recentContests(contests.results);
  const top = users.results.slice(0, 5);
  const library = libraryArticles(articles.results);
  const popularList = popularProblems(popular);

  return (
    <div className="space-y-6">
      <GuestHero
        locale={locale}
        numbers={{
          languages: languageCount,
          problems: problemCount,
          articles: articles.count,
          interfaces: LOCALES.length,
        }}
        problem={heroProblem}
      />

      <div className="grid gap-6 lg:grid-cols-2">
        {soon.length === 0 && last.length > 0 ? (
          <RecentContests contests={last} locale={locale} />
        ) : (
        <Card
          title={t(locale, "home.upcoming")}
          action={
            <IntentLink
              href="/contests"
              className="text-theme-sm rw-accent-ink hover:underline"
            >
              {t(locale, "home.all")}
            </IntentLink>
          }
          bodyClassName="p-0"
        >
          <ul className="divide-y rw-divide">
            {soon.map((c) => (
              <li key={c.slug}>
                <IntentLink
                  href={`/contests/${c.slug}`}
                  className="flex items-center gap-3 px-5 py-4 transition rw-hover-bg"
                >
                  <span className="min-w-0 flex-1">
                    <span className="block truncate font-medium rw-strong">
                      {c.title}
                    </span>
                    <span className="mt-0.5 block text-theme-xs rw-faint">
                      {dateTime(c.start_at, locale)}
                    </span>
                  </span>
                  <Badge color={c.is_running ? "success" : "info"}>
                    {t(
                      locale,
                      c.is_running ? "contests.running" : "contests.upcoming",
                    )}
                  </Badge>
                  {c.is_rated && (
                    <Badge color="brand">{t(locale, "contests.rated")}</Badge>
                  )}
                </IntentLink>
              </li>
            ))}
            {soon.length === 0 && (
              <li className="px-5 py-8 text-center text-theme-sm rw-faint">
                {t(locale, "common.empty")}
              </li>
            )}
          </ul>
        </Card>
        )}

        <Card
          title={t(locale, "home.topUsers")}
          action={
            <IntentLink
              href="/leaderboard"
              className="text-theme-sm rw-accent-ink hover:underline"
            >
              {t(locale, "home.all")}
            </IntentLink>
          }
          bodyClassName="p-0"
        >
          <Table>
            <THead>
              <TH>#</TH>
              <TH>{t(locale, "standings.user")}</TH>
              <TH align="right">{t(locale, "leaderboard.skills")}</TH>
            </THead>
            <TBody>
              {top.map((u, i) => (
                <TR key={u.username}>
                  <TD className="rw-faint">{i + 1}</TD>
                  <TD>
                    <IntentLink
                      href={`/users/${u.username}`}
                      className="font-medium rw-strong rw-link-hover"
                    >
                      {u.display_name || u.username}
                    </IntentLink>
                  </TD>
                  <TD align="right" className="font-semibold rw-strong">
                    {u.rating_skills}
                  </TD>
                </TR>
              ))}
            </TBody>
          </Table>
        </Card>
      </div>

      <Card
        title={t(locale, "home.whereToStart")}
        action={
          <IntentLink
            href="/learn"
            className="text-theme-sm rw-accent-ink hover:underline"
          >
            {t(locale, "home.all")}
          </IntentLink>
        }
      >
        <div className="grid gap-4 md:grid-cols-3">
          {roadmaps.slice(0, 2).map((r) => (
            <div key={r.slug} className="rw-radius border rw-line p-4">
              <p className="font-medium rw-strong">
                {inReaderAlphabet(r.title, r.locale)}
              </p>
              <p className="mt-1 line-clamp-2 text-theme-sm rw-dim">
                {inReaderAlphabet(r.description, r.locale)}
              </p>
              <div className="mt-3">
                <Badge color="brand">
                  {fill(t(locale, "learn.stepCount"), { count: r.step_count })}
                </Badge>
              </div>
            </div>
          ))}
          {articles.results.slice(0, 1).map((a) => (
            <IntentLink
              key={a.slug}
              href={`/learn/${a.slug}`}
              className="rw-radius border rw-line p-4 transition rw-hover-line"
            >
              <p className="font-medium rw-strong">
                {inReaderAlphabet(a.title, a.locale)}
              </p>
              <p className="mt-1 line-clamp-2 text-theme-sm rw-dim">
                {inReaderAlphabet(a.summary, a.locale)}
              </p>
              <div className="mt-3">
                <Badge>
                  {a.reading_minutes} {t(locale, "learn.minutes")}
                </Badge>
              </div>
            </IntentLink>
          ))}
        </div>
      </Card>

      {/* Public content for visitors from a search engine (decision 2026-11-15):
          plain server-rendered links, so the cached page carries them as HTML. */}
      {(popularList.length > 0 || library.length > 0) && (
        <div className="grid gap-6 lg:grid-cols-2">
          <PopularProblems problems={popularList} locale={locale} />
          <AlgorithmLibrary articles={library} locale={locale} />
        </div>
      )}

      {/* Active members by region (decision 2026-11-11 ④); the numbers load in the
          browser. The block is shown only when somebody was active in the last 30
          days — the server asks once, cached — because a map of zeros says nothing. */}
      {activeMembers > 0 && <RegionMap />}

      {/* Vision principle #2 — KEP dan asosiy farq, doim ko'rinib turadi. */}
      <Card title={t(locale, "home.openRating")}>
        <p className="text-theme-sm rw-dim">
          {t(locale, "home.openRatingBody")}{" "}
          <IntentLink
            href="/rating"
            className="font-medium rw-accent-ink hover:underline"
          >
            {t(locale, "nav.ratingInfo")}
          </IntentLink>
        </p>
      </Card>

      {/* Qaror 5: o'zgarishlar bosh sahifada ham, arxivda ham ko'rinadi.
          E'lonlar bilan yonma-yon — ikkalasi ham "platformadan xabar". */}
      {(updates.length > 0 || posts.length > 0) && (
        <div className="grid gap-6 lg:grid-cols-2">
          {updates.length > 0 && (
            <Card
              className={posts.length === 0 ? "lg:col-span-2" : ""}
              title={t(locale, "update.home")}
              action={
                <IntentLink
                  href={"/updates" as Route}
                  className="text-theme-sm rw-accent-ink hover:underline"
                >
                  {t(locale, "home.all")}
                </IntentLink>
              }
              bodyClassName="p-0"
            >
              <ul className="divide-y rw-divide">
                {updates.map((u) => (
                  <li key={u.id}>
                    <IntentLink
                      href={`/updates/${u.id}`}
                      className="block px-5 py-4 transition rw-hover-bg"
                    >
                      <span className="flex flex-wrap items-center gap-2">
                        <UpdateKindBadge kind={u.kind} locale={locale} />
                        <span className="text-theme-xs rw-faint">
                          {date(u.released_at, locale)}
                        </span>
                      </span>
                      <span className="mt-2 block font-medium rw-strong">
                        {u.title}
                      </span>
                    </IntentLink>
                  </li>
                ))}
              </ul>
            </Card>
          )}

          {posts.length > 0 && (
            <Card
              className={updates.length === 0 ? "lg:col-span-2" : ""}
              title={t(locale, "home.announcements")}
              action={
                <IntentLink
                  href="/blog"
                  className="text-theme-sm rw-accent-ink hover:underline"
                >
                  {t(locale, "home.all")}
                </IntentLink>
              }
              bodyClassName="p-0"
            >
              <ul className="divide-y rw-divide">
                {posts.map((post) => (
                  <li key={post.slug}>
                    <IntentLink
                      href={`/blog/${post.slug}`}
                      className="block px-5 py-4 transition rw-hover-bg"
                    >
                      <span className="block font-medium rw-strong">
                        {inReaderAlphabet(post.title, post.locale)}
                      </span>
                      <span className="mt-0.5 block text-theme-xs rw-faint">
                        {date(post.published_at, locale)}
                      </span>
                    </IntentLink>
                  </li>
                ))}
              </ul>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}
