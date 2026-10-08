import type { Metadata } from "next";

import { PersonCard } from "@/components/team/Person";
import { TeamDirectory } from "@/components/team/TeamDirectory";
import { TeamHeader } from "@/components/team/TeamHeader";
import { readTeamView } from "@/components/team/state";
import type { TeamMember, TeamPayload } from "@/components/team/types";
import { TEAM_TEXT, pickTeam, type TeamLocale, type TeamText } from "@/content/team";
import { localeAlternatesFor } from "@/i18n/locale-alternates.server";
import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";
import { api } from "@/lib/api";

type Props = { searchParams: Promise<Record<string, string | string[] | undefined>> };

/** The page says who it is about when it is shared: its own title, a
 *  sentence counted from the list, and the founder's photo. It used to
 *  go out under the site's name and description, pointing at the home page
 *  (measured 2026-10-06: `og:url` was `https://rankwant.uz`). */
export async function generateMetadata(): Promise<Metadata> {
  const locale = await getLocale();
  const text = TEAM_TEXT[pickTeam(locale)];
  const team = await api.team().catch(() => null);
  const owner = team?.members.find((member) => member.holds_all_roles);
  const alternates = await localeAlternatesFor("/team");
  if (!team || !owner) return { title: t(locale, "team.title"), alternates };
  const roles = String(team.roles.length);
  const title = text.metaTitle.replace("{roles}", roles);
  const description = text.metaDescription
    .replace("{roles}", roles)
    .replace("{departments}", String(team.departments.length));
  return {
    title,
    description,
    alternates,
    openGraph: {
      title,
      description,
      url: alternates.canonical,
      type: "website",
      // A page's `openGraph` replaces the layout's, it is not merged.
      siteName: "RankWant",
      ...(owner.photo_url ? { images: [{ url: owner.photo_url, alt: owner.name }] } : {}),
    },
  };
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
export default async function TeamPage({ searchParams }: Props) {
  const locale = pickTeam(await getLocale());
  const text = TEAM_TEXT[locale];
  // The page must not turn into an error screen because one request failed.
  const team: TeamPayload | null = await api.team().catch(() => null);

  const owner = team?.members.find((member) => member.holds_all_roles) ?? null;
  const core = team?.members.filter((m) => m.section === "core" && !m.holds_all_roles) ?? [];
  const contributors = team?.members.filter((m) => m.section === "contributor") ?? [];
  const roles = owner ? (team?.roles ?? []) : [];
  const stats = [roles.length, team?.departments.length ?? 0, owner ? 1 : 0, 0];
  const initial = readTeamView(
    await searchParams,
    (team?.departments ?? []).map((item) => item.id),
  );

  return (
    // The sentences are Uzbek, Russian or English whatever the site's
    // language is; saying so keeps a Turkish page from upper-casing an
    // Uzbek "i" as "İ" (measured 2026-10-06: «RAHBARİYAT»).
    <div lang={locale} className="mx-auto max-w-6xl space-y-8">
      {owner && team ? (
        <TeamDirectory
          text={text}
          locale={locale}
          owner={owner}
          departments={team.departments}
          roles={roles}
          stats={stats}
          initial={initial}
        />
      ) : (
        <TeamHeader text={text} heading={text.heading} lede={text.lede} stats={null} />
      )}

      {team === null ? (
        <p role="status" className="rw-radius border rw-line rw-surface p-5 text-theme-sm rw-dim">
          {text.unavailable}
        </p>
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
