import Link from "next/link";

import { Badge } from "@/components/ui/Badge";
import { ButtonLink } from "@/components/ui/Button";
import { Card, StatCard } from "@/components/ui/Card";
import { TBody, TD, TH, THead, TR, Table } from "@/components/ui/Table";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";
import { ContestIcon, LeaderboardIcon, ProblemsIcon, QvantIcon } from "@/icons";
import { api, ApiError, type Contest, type Post } from "@/lib/api";

export const dynamic = "force-dynamic";

/** Yaqin musobaqa = hozir ketayotgan yoki hali boshlanmagan, eng yaqini birinchi. */
function upcoming(contests: Contest[]): Contest[] {
  return contests
    .filter((c) => !c.is_finished)
    .sort((a, b) => +new Date(a.start_at) - +new Date(b.start_at))
    .slice(0, 4);
}

export default async function Home() {
  const locale = DEFAULT_LOCALE;

  // Barchasi mustaqil — ketma-ket kutish bosh sahifani sekinlashtirardi.
  const [stats, contests, users, articles, roadmaps] = await Promise.all([
    api.stats(),
    api.contests(),
    api.leaderboard(),
    api.articles(),
    api.roadmaps(),
  ]);

  // Blog bo'sh yoki o'chirilgan bo'lsa bosh sahifa baribir ochilishi kerak.
  let posts: Post[] = [];
  try {
    posts = (await api.posts()).results.slice(0, 3);
  } catch (error) {
    if (!(error instanceof ApiError)) throw error;
  }

  const soon = upcoming(contests.results);
  const top = users.results.slice(0, 5);

  return (
    <div className="space-y-6">
      <section
        className="rounded-2xl border border-gray-200 bg-white px-6 py-10 shadow-theme-xs
          dark:border-[#232936] dark:bg-[#141821]"
      >
        <h1 className="text-title-sm font-bold text-gray-800 dark:text-white/90">RankWant</h1>
        <p className="mt-3 max-w-2xl text-theme-sm text-gray-500 dark:text-gray-400">
          Reyting xohlaganlar uchun: masala yeching, musobaqada qatnashing, darajangizni
          ko&apos;ring.
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <ButtonLink href="/register">{t(locale, "home.start")}</ButtonLink>
          <ButtonLink href="/problems" variant="outline">
            {t(locale, "nav.problems")}
          </ButtonLink>
        </div>
        <p className="mt-4 text-theme-xs text-gray-400">{t(locale, "home.guestHint")}</p>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label={t(locale, "nav.problems")}
          value={stats.problems}
          icon={<ProblemsIcon />}
        />
        <StatCard
          label={t(locale, "nav.contests")}
          value={stats.contests}
          icon={<ContestIcon />}
        />
        <StatCard
          label={t(locale, "nav.leaderboard")}
          value={stats.users}
          icon={<LeaderboardIcon />}
        />
        <StatCard
          label={t(locale, "home.attempts")}
          value={stats.attempts}
          icon={<QvantIcon />}
        />
      </section>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card
          title={t(locale, "home.upcoming")}
          action={
            <Link href="/contests" className="text-theme-sm text-brand-500 hover:underline">
              {t(locale, "home.all")}
            </Link>
          }
          bodyClassName="p-0"
        >
          <ul className="divide-y divide-gray-100 dark:divide-[#232936]">
            {soon.map((c) => (
              <li key={c.slug}>
                <Link
                  href={`/contests/${c.slug}`}
                  className="flex items-center gap-3 px-5 py-4 transition
                    hover:bg-gray-50 dark:hover:bg-white/[0.03]"
                >
                  <span className="min-w-0 flex-1">
                    <span className="block truncate font-medium text-gray-800 dark:text-white/90">
                      {c.title}
                    </span>
                    <span className="mt-0.5 block text-theme-xs text-gray-400">
                      {new Date(c.start_at).toLocaleString(locale)}
                    </span>
                  </span>
                  <Badge color={c.is_running ? "success" : "info"}>
                    {t(locale, c.is_running ? "contests.running" : "contests.upcoming")}
                  </Badge>
                  {c.is_rated && <Badge color="brand">{t(locale, "contests.rated")}</Badge>}
                </Link>
              </li>
            ))}
            {soon.length === 0 && (
              <li className="px-5 py-8 text-center text-theme-sm text-gray-400">
                {t(locale, "empty")}
              </li>
            )}
          </ul>
        </Card>

        <Card
          title={t(locale, "home.topUsers")}
          action={
            <Link href="/leaderboard" className="text-theme-sm text-brand-500 hover:underline">
              {t(locale, "home.all")}
            </Link>
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
                  <TD className="text-gray-400">{i + 1}</TD>
                  <TD>
                    <Link
                      href={`/users/${u.username}`}
                      className="font-medium text-gray-800 hover:text-brand-500 dark:text-white/90"
                    >
                      {u.display_name || u.username}
                    </Link>
                  </TD>
                  <TD align="right" className="font-semibold text-gray-800 dark:text-white/90">
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
          <Link href="/learn" className="text-theme-sm text-brand-500 hover:underline">
            {t(locale, "home.all")}
          </Link>
        }
      >
        <div className="grid gap-4 md:grid-cols-3">
          {roadmaps.slice(0, 2).map((r) => (
            <div
              key={r.slug}
              className="rounded-xl border border-gray-200 p-4 dark:border-[#232936]"
            >
              <p className="font-medium text-gray-800 dark:text-white/90">{r.title}</p>
              <p className="mt-1 line-clamp-2 text-theme-sm text-gray-500 dark:text-gray-400">
                {r.description}
              </p>
              <div className="mt-3">
                <Badge color="brand">{r.step_count} qadam</Badge>
              </div>
            </div>
          ))}
          {articles.results.slice(0, 1).map((a) => (
            <Link
              key={a.slug}
              href={`/learn/${a.slug}`}
              className="rounded-xl border border-gray-200 p-4 transition hover:border-brand-400
                dark:border-[#232936]"
            >
              <p className="font-medium text-gray-800 dark:text-white/90">{a.title}</p>
              <p className="mt-1 line-clamp-2 text-theme-sm text-gray-500 dark:text-gray-400">
                {a.summary}
              </p>
              <div className="mt-3">
                <Badge>
                  {a.reading_minutes} {t(locale, "learn.minutes")}
                </Badge>
              </div>
            </Link>
          ))}
        </div>
      </Card>

      {/* Vision principle #2 — KEP dan asosiy farq, doim ko'rinib turadi. */}
      <Card title={t(locale, "home.openRating")}>
        <p className="text-theme-sm text-gray-500 dark:text-gray-400">
          Har bir reytingning formulasi ochiq va har o&apos;zgarishning sababi yozib boriladi.{" "}
          <Link href="/rating" className="font-medium text-brand-500 hover:underline">
            {t(locale, "nav.ratingInfo")}
          </Link>
        </p>
      </Card>

      {posts.length > 0 && (
        <Card
          title={t(locale, "home.announcements")}
          action={
            <Link href="/blog" className="text-theme-sm text-brand-500 hover:underline">
              {t(locale, "home.all")}
            </Link>
          }
          bodyClassName="p-0"
        >
          <ul className="divide-y divide-gray-100 dark:divide-[#232936]">
            {posts.map((post) => (
              <li key={post.slug}>
                <Link
                  href={`/blog/${post.slug}`}
                  className="block px-5 py-4 transition hover:bg-gray-50 dark:hover:bg-white/[0.03]"
                >
                  <span className="block font-medium text-gray-800 dark:text-white/90">
                    {post.title}
                  </span>
                  <span className="mt-0.5 block text-theme-xs text-gray-400">
                    {new Date(post.published_at).toLocaleDateString(locale)}
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </Card>
      )}
    </div>
  );
}
