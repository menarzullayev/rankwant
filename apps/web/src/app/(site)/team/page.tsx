import type { Metadata } from "next";

import { TeamDirectory } from "@/components/team/TeamDirectory";
import { TEAM_MEMBER, TEAM_ROLES, TEAM_TEXT, pickTeam } from "@/content/team";
import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "team.title") };
}

/** The team: twelve departments, twenty-four roles, one person.
 *
 *  The text is content (`content/team.ts`), picked on the server so the
 *  browser receives one language of it. The numbers in the header are
 *  counted from the data, not written beside it. */
export default async function TeamPage() {
  const locale = await getLocale();
  const text = TEAM_TEXT[pickTeam(locale)];
  const stats = [TEAM_ROLES.length, text.depts.length, 1, 0];
  const telegram = TEAM_MEMBER.links[0];

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <header className="space-y-4">
        <p className="font-mono text-theme-xs tracking-wide rw-accent-ink uppercase">{text.eyebrow}</p>
        <h1 className="max-w-[18ch] text-title-md leading-tight font-bold text-balance rw-strong">
          {text.heading}
        </h1>
        <p className="max-w-prose text-theme-base rw-dim">{text.lede}</p>
        <dl className="grid grid-cols-2 gap-3 md:grid-cols-4">
          {stats.map((value, index) => (
            <div key={text.stats[index]} className="rw-radius border rw-line rw-surface px-4 py-3">
              <dd className="text-title-sm leading-tight font-bold rw-strong tabular-nums">{value}</dd>
              <dt className="text-theme-xs rw-dim">{text.stats[index]}</dt>
            </div>
          ))}
        </dl>
      </header>

      <TeamDirectory text={text} roles={TEAM_ROLES} member={TEAM_MEMBER} />

      <section className="flex flex-wrap items-center justify-between gap-4 rw-radius border border-dashed rw-divider p-5">
        <div className="min-w-0">
          <h2 className="text-theme-lg font-semibold rw-strong">{text.hireTitle}</h2>
          <p className="mt-1 max-w-prose text-theme-sm rw-dim">{text.hireText}</p>
        </div>
        <a
          href={telegram.href}
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
