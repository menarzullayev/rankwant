import type { Route } from "next";

import { Badge } from "@/components/ui/Badge";
import { ButtonLink } from "@/components/ui/Button";
import { IntentLink } from "@/components/ui/IntentLink";
import { Card, StatCard } from "@/components/ui/Card";
import { TBody, TD, TH, THead, TR, Table } from "@/components/ui/Table";
import { UpdateKindBadge } from "@/components/UpdateKindBadge";
import { getLocale } from "@/i18n/server";
import { date, dateTime, fill, t } from "@/i18n/messages";
import { Icon } from "@/components/ui/Icon";
import {
  api,
  ApiError,
  type Attempt,
  type Contest,
  type Paginated,
  type Post,
  type ProblemDetail,
  type Recommendation,
  type SystemUpdate,
  type UserPublic,
} from "@/lib/api";
import { getSessionUser, getWithSession } from "@/lib/api.server";

/** Kirgan foydalanuvchi uchun «qayerdan davom etaman» savoliga javob:
 * avval tugallanmagan urinish, bo'lmasa tavsiya. Mehmonga `null`. */
async function resumeTarget(
  me: UserPublic | null,
): Promise<{ slug: string; title: string } | null> {
  if (!me) return null;

  const attempts = await getWithSession<Paginated<Attempt>>(
    `/attempts/?username=${encodeURIComponent(me.username)}`,
  ).catch(() => null);

  const pending = attempts?.results.find((a) => a.verdict !== "AC");
  if (pending) {
    const problem = await api
      .problem(pending.problem)
      .catch((): ProblemDetail | null => null);
    if (problem) return { slug: problem.slug, title: problem.title };
  }

  const recommended = await getWithSession<Recommendation>(
    "/problems/recommendation/",
  ).catch(() => null);
  const first = recommended?.results[0];
  return first ? { slug: first.slug, title: first.title } : null;
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
    api.roadmaps(),
  ]);

  // Blog va o'zgarishlar — ikkalasi ham YORDAMCHI bo'lim: biri bo'sh yoki
  // o'chirilgan bo'lsa bosh sahifa baribir ochilishi kerak. Lekin ularni
  // ketma-ket kutish ortiqcha — shuning uchun bitta `Promise.all` ichida.
  const [posts, updates] = await Promise.all([
    api
      .posts()
      .then((page) => page.results.slice(0, 3))
      .catch(softFail<Post>),
    api
      .updates("?page_size=4")
      .then((page) => page.results)
      .catch(softFail<SystemUpdate>),
  ]);

  const me = await getSessionUser<UserPublic>();
  const resume = await resumeTarget(me);

  const soon = upcoming(contests.results);
  const top = users.results.slice(0, 5);

  return (
    <div className="space-y-6">
      <section className="rw-radius border rw-line rw-surface px-6 py-10 rw-shadow">
        <h1 className="text-title-sm font-bold rw-strong">
          {me
            ? fill(t(locale, "home.greeting"), {
                name: me.display_name || me.username,
              })
            : "RankWant"}
        </h1>
        <p className="mt-3 max-w-2xl text-theme-sm rw-dim">
          {me
            ? t(locale, "home.resumeHint")
            : t(locale, "home.ratingHint")}
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          {resume ? (
            <ButtonLink intent href={{ pathname: `/problems/${resume.slug}` }}>
              Davom etish · {resume.title}
            </ButtonLink>
          ) : (
            <ButtonLink
              intent
              href={me ? "/problems" : ("/login?tab=register" as Route)}
            >
              {me ? t(locale, "nav.problems") : t(locale, "home.start")}
            </ButtonLink>
          )}
          <ButtonLink
            intent
            href={resume ? "/problems" : "/contests"}
            variant="outline"
          >
            {resume ? t(locale, "nav.problems") : t(locale, "nav.contests")}
          </ButtonLink>
        </div>
        {!me && (
          <p className="mt-4 text-theme-xs rw-faint">
            {t(locale, "home.guestHint")}
          </p>
        )}
      </section>

      {/* lg da 4 ustun: 1024–1279 px da 2+2 qolsa, 4 karta ikki qatorni
          egallab, keyingi bo'limni pastga suradi (o'lchandi: 1024x768 da
          faqat 38 px ko'rinardi, 4 ustunda 216 px). 3 ustunli pog'ona
          qo'shilmadi — u vertikal yutuq bermaydi (4 karta baribir 2 qator)
          va 4-kartani yolg'iz qoldiradi. */}
      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label={t(locale, "nav.problems")}
          value={stats.problems}
          icon={<Icon name="nav.problems" />}
          valueClassName="lg:text-2xl xl:text-title-sm"
        />
        <StatCard
          label={t(locale, "nav.contests")}
          value={stats.contests}
          icon={<Icon name="ranking.trophy" />}
          valueClassName="lg:text-2xl xl:text-title-sm"
        />
        <StatCard
          label={t(locale, "nav.leaderboard")}
          value={stats.users}
          icon={<Icon name="nav.leaderboard" />}
          valueClassName="lg:text-2xl xl:text-title-sm"
        />
        <StatCard
          label={t(locale, "home.attempts")}
          value={stats.attempts}
          icon={<Icon name="shop.coin" />}
          valueClassName="lg:text-2xl xl:text-title-sm"
        />
      </section>

      <div className="grid gap-6 lg:grid-cols-2">
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
              <p className="font-medium rw-strong">{r.title}</p>
              <p className="mt-1 line-clamp-2 text-theme-sm rw-dim">
                {r.description}
              </p>
              <div className="mt-3">
                <Badge color="brand">{r.step_count} qadam</Badge>
              </div>
            </div>
          ))}
          {articles.results.slice(0, 1).map((a) => (
            <IntentLink
              key={a.slug}
              href={`/learn/${a.slug}`}
              className="rw-radius border rw-line p-4 transition rw-hover-line"
            >
              <p className="font-medium rw-strong">{a.title}</p>
              <p className="mt-1 line-clamp-2 text-theme-sm rw-dim">
                {a.summary}
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

      {/* Vision principle #2 — KEP dan asosiy farq, doim ko'rinib turadi. */}
      <Card title={t(locale, "home.openRating")}>
        <p className="text-theme-sm rw-dim">
          Har bir reytingning formulasi ochiq va har o&apos;zgarishning sababi
          yozib boriladi.{" "}
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
                        {post.title}
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
