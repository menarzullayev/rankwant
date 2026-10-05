import type { Metadata } from "next";

import { PersonCard } from "@/components/team/Person";
import { TeamDirectory } from "@/components/team/TeamDirectory";
import type { TeamMember, TeamPayload } from "@/components/team/types";
import { TEAM_TEXT, pickTeam, type TeamLocale, type TeamText } from "@/content/team";
import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";
import { api } from "@/lib/api";

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "team.title") };
}

/** Where a visitor can write. The founder's own Telegram if there is one. */
const FALLBACK_CONTACT = "https://t.me/rankwant";

function People({
  title,
  lede,
  members,
  locale,
  text,
}: {
  title: string;
  lede?: string;
  members: TeamMember[];
  locale: TeamLocale;
  text: TeamText;
}) {
  if (members.length === 0) return null;
  return (
    <section className="space-y-4">
      <div>
        <h2 className="text-theme-xl font-semibold rw-strong">{title}</h2>
        {lede ? <p className="mt-1 text-theme-sm rw-dim">{lede}</p> : null}
      </div>
      <ul className="grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-4">
        {members.map((member) => (
          <li key={member.id}>
            <PersonCard
              member={member}
              locale={locale}
              alt={text.photoAlt.replace("{name}", member.name)}
              website={text.website}
            />
          </li>
        ))}
      </ul>
    </section>
  );
}

/** The team: many titles, one person — and, below the joke, the people who
 *  really helped.
 *
 *  People, departments and titles come from the API and are managed in
 *  `/admin/team`; the page's own sentences are content (`content/team.ts`).
 *  The numbers in the header are counted from what was loaded. */
export default async function TeamPage() {
  const locale = pickTeam(await getLocale());
  const text = TEAM_TEXT[locale];
  // The page must not turn into an error screen because one request failed.
  const team: TeamPayload | null = await api.team().catch(() => null);

  const owner = team?.members.find((member) => member.holds_all_roles) ?? null;
  const core = team?.members.filter((m) => m.section === "core" && !m.holds_all_roles) ?? [];
  const contributors = team?.members.filter((m) => m.section === "contributor") ?? [];
  const roles = owner ? (team?.roles ?? []) : [];
  const stats = [roles.length, team?.departments.length ?? 0, owner ? 1 : 0, 0];

  return (
    <div className="mx-auto max-w-6xl space-y-8">
      <header className="space-y-4">
        <p className="font-mono text-theme-xs tracking-wide rw-accent-ink uppercase">{text.eyebrow}</p>
        <h1 className="max-w-[18ch] text-title-md leading-tight font-bold text-balance rw-strong">
          {text.heading}
        </h1>
        <p className="max-w-prose text-theme-base rw-dim">{text.lede}</p>
        {owner ? (
          <dl className="grid grid-cols-2 gap-3 md:grid-cols-4">
            {stats.map((value, index) => (
              <div key={text.stats[index]} className="rw-radius border rw-line rw-surface px-4 py-3">
                <dd className="text-title-sm leading-tight font-bold rw-strong tabular-nums">{value}</dd>
                <dt className="text-theme-xs rw-dim">{text.stats[index]}</dt>
              </div>
            ))}
          </dl>
        ) : null}
      </header>

      {team === null ? (
        <p role="status" className="rw-radius border rw-line rw-surface p-5 text-theme-sm rw-dim">
          {text.unavailable}
        </p>
      ) : null}

      {owner && team ? (
        <TeamDirectory
          text={text}
          locale={locale}
          owner={owner}
          departments={team.departments}
          roles={roles}
        />
      ) : null}

      <People title={text.coreTitle} members={core} locale={locale} text={text} />
      <People
        title={text.contributorsTitle}
        lede={text.contributorsLede}
        members={contributors}
        locale={locale}
        text={text}
      />

      <section className="flex flex-wrap items-center justify-between gap-4 rw-radius border border-dashed rw-divider p-5">
        <div className="min-w-0">
          <h2 className="text-theme-lg font-semibold rw-strong">{text.hireTitle}</h2>
          <p className="mt-1 max-w-prose text-theme-sm rw-dim">{text.hireText}</p>
        </div>
        <a
          href={owner?.telegram_url || FALLBACK_CONTACT}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex h-11 items-center rw-radius-sm rw-accent-bg px-5 text-theme-sm font-semibold rw-focus-ring"
        >
          {text.hireCta}
        </a>
      </section>
    </div>
  );
}
