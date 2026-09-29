import type { Route } from "next";
import Link from "next/link";

import { Badge, DifficultyBadge } from "@/components/ui/Badge";
import { Dropdown } from "@/components/ui/Dropdown";
import { Card } from "@/components/ui/Card";
import { ContentName } from "@/components/ui/UzFallbackBadge";
import { fill, t, type Locale } from "@/i18n/messages";
import { Icon } from "@/components/ui/Icon";
import type {
  Achievement,
  ActivityEvent,
  Paginated,
  Purchase,
  Follower,
} from "@/lib/api";
import { getWithSession } from "@/lib/api.server";
import { SLOT_OF } from "@/lib/cosmetics";
import { TimeStamp } from "@/components/kit/TimeStamp";
import { formatDate, formatShare } from "@rankwant/shared/format";
import { Avatar } from "@/components/ui/Identity";
import { UserName } from "@/components/ui/Identity";
import { EmptyRow, TBody, TD, TH, THead, TR, Table } from "@/components/ui/Table";
import { MedalDot, achievementLabel } from "./Medal";
import { PinButton } from "./PinButton";

const date = (value: string, locale: Locale) => formatDate(value, locale);

function Empty({ text }: { text: string }) {
  return (
    <Card>
      <p className="text-theme-sm rw-faint">{text}</p>
    </Card>
  );
}

/** Voqealar lentasi — musobaqa, bajarilgan vazifa va qiyin masala. */
export async function ActivityTab({
  username,
  before,
  locale,
}: {
  username: string;
  before?: string;
  locale: Locale;
}) {
  const query = before ? `?before=${encodeURIComponent(before)}` : "";
  const data = await getWithSession<{
    results: ActivityEvent[];
    next_before: string | null;
    hidden?: boolean;
  }>(`/users/${username}/activity/${query}`);
  if (data.hidden) return <Empty text={t(locale, "profile.activityHidden")} />;
  if (data.results.length === 0) return <Empty text={t(locale, "profile.activityEmpty")} />;

  return (
    <Card bodyClassName="p-0">
      <ol className="divide-y rw-divide">
        {data.results.map((event, i) => (
          <li
            key={`${event.type}-${event.at}-${i}`}
            className="flex flex-wrap items-center gap-x-3 gap-y-1 px-5 py-3"
          >
            <span className="min-w-0 flex-1 text-theme-sm">
              {event.type === "contest" && (
                <>
                  <span className="rw-dim">{t(locale, "profile.activityContest")}: </span>
                  <Link href={`/contests/${event.ref}`} className="rw-strong hover:underline">
                    {event.ref}
                  </Link>
                  {event.rank !== null && <span className="rw-dim"> · #{event.rank}</span>}
                </>
              )}
              {event.type === "quest" && (
                <>
                  <span className="rw-dim">{t(locale, "profile.activityQuest")}: </span>
                  <span className="rw-strong">
                    <ContentName
                      row={{
                        name_uz: event.title_uz,
                        name_ru: event.title_ru,
                        name_en: event.title_en,
                      }}
                      locale={locale}
                    />
                  </span>
                </>
              )}
              {event.type === "hard_solve" && (
                <>
                  <span className="rw-dim">{t(locale, "profile.activityHardSolve")}: </span>
                  <Link href={`/problems/${event.ref}`} className="rw-strong hover:underline">
                    {event.title}
                  </Link>
                </>
              )}
            </span>
            {event.type === "contest" && (
              <span
                className={`text-theme-sm font-semibold tabular-nums ${
                  event.delta >= 0 ? "rw-ok-ink" : "rw-bad-ink"
                }`}
              >
                {event.delta > 0 ? "+" : ""}
                {event.delta}
              </span>
            )}
            {event.type === "quest" && <Badge color="brand">+{event.awarded} Qvant</Badge>}
            {event.type === "hard_solve" && <DifficultyBadge value={event.difficulty} />}
            <TimeStamp value={event.at} locale={locale} tone="badge" />
          </li>
        ))}
      </ol>
      {data.next_before && (
        <div className="border-t rw-divider px-5 py-3">
          <Link
            href={
              `/users/${username}/activity?before=${encodeURIComponent(data.next_before)}` as Route
            }
            className="text-theme-sm rw-accent-ink hover:underline"
          >
            {t(locale, "profile.activityOlder")}
          </Link>
        </div>
      )}
    </Card>
  );
}

export async function AchievementsTab({
  username,
  locale,
  pinned,
}: {
  username: string;
  locale: Locale;
  /** Egasiga — tanlangan kodlar; mehmonga `null`. */
  pinned: string[] | null;
}) {
  const rows = await getWithSession<Achievement[]>(`/users/${username}/achievements/`);
  const done = rows.filter((row) => row.done).length;

  return (
    <section className="space-y-4">
      <p className="text-theme-sm rw-dim">
        {fill(t(locale, "profile.achDone"), { done, total: rows.length })}
      </p>
      {pinned && <p className="text-theme-xs rw-faint">{t(locale, "profile.pinHint")}</p>}
      <ul className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        {rows.map((row) => (
          <li key={row.code} className="flex flex-col gap-1 rw-radius border rw-line rw-surface p-4">
            <p className="flex items-center gap-2 text-theme-sm font-medium rw-strong">
              <MedalDot tier={row.tier} muted={!row.done} />
              <span className="min-w-0 flex-1">{achievementLabel(row, locale)}</span>
              {row.done && <Icon name="action.confirm" className="size-4 shrink-0 rw-ok-ink" />}
            </p>
            <p className="text-theme-xs rw-faint">
              {t(locale, `tier.${row.tier}`)} ·{" "}
              {fill(t(locale, "profile.rarity"), { pct: formatShare(row.rarity, locale) })}
            </p>
            {row.done ? (
              row.achieved_at && (
                <p className="text-theme-xs rw-faint">
                  {fill(t(locale, "profile.achievedOn"), {
                    date: formatDate(row.achieved_at, locale),
                  })}
                </p>
              )
            ) : (
              <>
                <div className="mt-2 h-1.5 overflow-hidden rounded-full rw-chip">
                  <div
                    className="h-full rounded-full"
                    style={{
                      width: `${Math.round((row.progress / row.target) * 100)}%`,
                      background: "var(--rw-accent)",
                    }}
                  />
                </div>
                <p className="text-theme-xs tabular-nums rw-faint">
                  {row.progress} / {row.target}
                </p>
              </>
            )}
            {pinned && row.done && (
              <div className="mt-2">
                <PinButton code={row.code} pinned={pinned} />
              </div>
            )}
          </li>
        ))}
      </ul>
    </section>
  );
}

export async function PurchasesTab({
  username,
  locale,
}: {
  username: string;
  locale: Locale;
}) {
  const rows = await getWithSession<Purchase[]>(`/users/${username}/purchases/`);
  if (rows.length === 0) return <Empty text={t(locale, "profile.purchasesEmpty")} />;

  return (
    <Card bodyClassName="p-0">
      <ul className="divide-y rw-divide">
        {rows.map((row, i) => {
          const slot = SLOT_OF[row.category];
          return (
            <li key={`${row.code}-${i}`} className="flex flex-wrap items-center gap-3 px-5 py-3">
              <span className="min-w-0 flex-1">
                <span className="block text-theme-sm font-medium rw-strong">
                  <ContentName
                    row={{
                      name_uz: row.title_uz,
                      name_ru: row.title_ru,
                      name_en: row.title_en,
                    }}
                    locale={locale}
                  />
                </span>
                <span className="text-theme-xs rw-faint">
                  {slot ? t(locale, `settings.slot.${slot}`) : t(locale, "profile.freeze")}
                </span>
              </span>
              {row.is_equipped && <Badge color="success">{t(locale, "profile.equipped")}</Badge>}
              <time dateTime={row.purchased_at} className="text-theme-xs rw-faint">
                {date(row.purchased_at, locale)}
              </time>
            </li>
          );
        })}
      </ul>
    </Card>
  );
}

export async function PeopleTab({
  username,
  direction,
  page,
  q,
  ordering,
  locale,
}: {
  username: string;
  direction: "followers" | "following";
  page: number;
  q: string;
  ordering: string;
  locale: Locale;
}) {
  const params = new URLSearchParams({ page: String(page) });
  if (q) params.set("q", q);
  if (ordering) params.set("ordering", ordering);
  const data = await getWithSession<Paginated<Follower>>(
    `/users/${username}/${direction}/?${params}`,
  );
  const title = t(locale, direction === "followers" ? "profile.followers" : "profile.followingTab");
  // `slug` is the URL segment, not a label: `/users/<name>/followers`.
  // The two values are the API's route names, identical in all ten
  // languages. Translating them would break the link.
  const slug = direction;
  const link = (to: number) => {
    const next = new URLSearchParams(params);
    next.set("page", String(to));
    return `/users/${username}/${slug}?${next}` as Route;
  };
  const field =
    "h-9 rw-radius-sm border rw-line px-3 text-theme-sm rw-strong rw-field-bg rw-focus-ring rw-fm-inp";
  const btn =
    "h-9 rw-radius-sm border rw-line px-3 text-theme-sm rw-strong rw-field-bg rw-focus-ring";

  return (
    <Card title={`${title} · ${data.count}`} bodyClassName="p-0">
      <form method="get" className="flex flex-wrap items-center gap-2 border-b rw-divider px-5 py-3">
        <input
          type="search"
          name="q"
          defaultValue={q}
          placeholder={t(locale, "profile.searchPeople")}
          aria-label={t(locale, "profile.searchPeople")}
          className={`min-w-0 flex-1 ${field}`}
        />
        <Dropdown
          size="sm"
          hideLabel
          label={t(locale, "profile.sortBy")}
          name="ordering"
          defaultValue={ordering || "recent"}
          options={[
            { value: "recent", label: t(locale, "profile.sortNewest") },
            { value: "rating", label: t(locale, "profile.sortRating") },
            { value: "name", label: t(locale, "profile.sortName") },
          ]}
          className="w-44"
        />
        <button type="submit" className={`font-medium rw-hover-bg ${btn}`}>
          {t(locale, "profile.search")}
        </button>
      </form>
      <Table>
        <THead>
          <TH>{t(locale, "standings.user")}</TH>
          <TH>{t(locale, "settings.school")}</TH>
          <TH align="right">{t(locale, "leaderboard.contest")}</TH>
          <TH align="right">{t(locale, "profile.lastActivityCol")}</TH>
        </THead>
        <TBody>
          {data.results.map((person) => (
            <TR key={person.username}>
              <TD>
                <span className="flex items-center gap-3">
                  <Avatar
                    url={person.avatar_url}
                    name={person.display_name || person.username}
                    className="size-8 text-theme-sm"
                  />
                  <UserName
                    username={person.username}
                    name={person.display_name}
                    title={person.title}
                    locale={locale}
                  />
                </span>
              </TD>
              <TD className="rw-dim">{person.school || "—"}</TD>
              <TD align="right" className="tabular-nums">
                {person.rating_contest}
              </TD>
              <TD align="right" className="rw-faint">
                {person.last_seen ? (
                  <TimeStamp value={person.last_seen} locale={locale} tone="relative" />
                ) : (
                  "—"
                )}
              </TD>
            </TR>
          ))}
          {data.results.length === 0 && <EmptyRow colSpan={4}>{t(locale, "common.empty")}</EmptyRow>}
        </TBody>
      </Table>
      {(data.previous || data.next) && (
        <div className="flex justify-between border-t rw-divider px-5 py-3 text-theme-sm">
          {data.previous ? (
            <Link href={link(page - 1)} className="rw-accent-ink hover:underline">
              ← {t(locale, "profile.prev")}
            </Link>
          ) : (
            <span />
          )}
          {data.next && (
            <Link href={link(page + 1)} className="rw-accent-ink hover:underline">
              {t(locale, "profile.next")} →
            </Link>
          )}
        </div>
      )}
    </Card>
  );
}
