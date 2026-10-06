"use client";

import { useMemo, useState } from "react";

import { localized, type TeamLocale, type TeamText } from "@/content/team";

import { PersonCard, SocialLinks, initialsOf } from "./Person";
import type { TeamDepartment, TeamMember, TeamRole } from "./types";

const ALL = -1;

/** Every role on the page is the same person, so the same photo is told
 *  apart by a ring in the role's hue and by a small mark. Without a photo
 *  the disc is the hue itself under the initials. */
function Avatar({
  member,
  hue,
  badge,
  alt,
}: {
  member: TeamMember;
  hue: number;
  badge: string;
  alt: string;
}) {
  const ring = `0 0 0 3px hsl(${hue} 62% 46%)`;
  return (
    <span className="relative shrink-0">
      {member.photo_url ? (
        // See `PersonCard`: the address is set in the admin panel.
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={member.photo_url}
          alt={alt}
          loading="lazy"
          decoding="async"
          style={{ boxShadow: ring }}
          className="size-16 rounded-full object-cover"
        />
      ) : (
        <span
          role="img"
          aria-label={alt}
          style={{ background: `hsl(${hue} 62% 42%)` }}
          className="grid size-16 place-items-center rounded-full text-theme-xl font-bold text-white"
        >
          {initialsOf(member.name)}
        </span>
      )}
      {badge ? (
        <span className="absolute -end-1 -bottom-1 grid h-6 min-w-6 place-items-center rounded-full border rw-line rw-surface px-1 font-mono text-theme-2xs font-semibold rw-strong">
          {badge}
        </span>
      ) : null}
    </span>
  );
}

const chip = (active: boolean) =>
  `inline-flex h-11 shrink-0 items-center gap-2 rounded-full border px-4 text-theme-sm whitespace-nowrap transition rw-focus-ring ${
    active ? "rw-accent-bg font-semibold" : "rw-divider rw-surface rw-dim-2 rw-hover-bg"
  }`;

export function TeamDirectory({
  text,
  locale,
  owner,
  departments,
  roles,
}: {
  text: TeamText;
  locale: TeamLocale;
  owner: TeamMember;
  departments: TeamDepartment[];
  roles: TeamRole[];
}) {
  const [dept, setDept] = useState(ALL);
  const [query, setQuery] = useState("");
  const [serious, setSerious] = useState(false);
  const [open, setOpen] = useState<number | null>(null);

  const names = useMemo(
    () => new Map(departments.map((item) => [item.id, localized(item, "name", locale)])),
    [departments, locale],
  );

  const needle = query.trim().toLowerCase();
  const shown = roles.filter((role) => {
    if (dept !== ALL && role.department !== dept) return false;
    if (!needle) return true;
    const haystack = `${localized(role, "title", locale)} ${localized(role, "about", locale)} ${
      names.get(role.department) ?? ""
    }`;
    return haystack.toLowerCase().includes(needle);
  });

  const alt = text.photoAlt.replace("{name}", owner.name);
  const count = serious
    ? text.soloCount
    : text.count
        .replace("{roles}", String(shown.length))
        .replace("{people}", shown.length ? "1" : "0");

  function pick(next: number) {
    setDept(next);
    setOpen(null);
    setSerious(false);
  }

  return (
    <div data-team-directory>
      {/* Sticky from `md` only: twelve wrapped chips are three or four rows on
          a phone, and a bar that tall would cover a third of the screen. */}
      <div className="z-10 -mx-1 flex flex-wrap items-center gap-3 px-1 py-3 rw-ground-bg md:sticky md:top-16">
        <div
          role="group"
          aria-label={text.filterLabel}
          className="flex min-w-0 flex-1 flex-wrap gap-2 py-1"
        >
          <button type="button" aria-pressed={dept === ALL} onClick={() => pick(ALL)} className={chip(dept === ALL)}>
            {text.all}
            <span className="font-mono text-theme-xs opacity-70">{roles.length}</span>
          </button>
          {departments.map((item) => (
            <button
              key={item.id}
              type="button"
              aria-pressed={dept === item.id}
              onClick={() => pick(item.id)}
              className={chip(dept === item.id)}
            >
              {names.get(item.id)}
              <span className="font-mono text-theme-xs opacity-70">
                {roles.filter((role) => role.department === item.id).length}
              </span>
            </button>
          ))}
        </div>
        <input
          type="search"
          value={query}
          disabled={serious}
          onChange={(event) => {
            setQuery(event.target.value);
            setOpen(null);
          }}
          placeholder={text.search}
          aria-label={text.search}
          className="h-11 w-full rounded-full border rw-divider rw-field-bg px-4 text-theme-sm rw-strong rw-fm-inp rw-focus-ring sm:w-56"
        />
        <label className="inline-flex h-11 cursor-pointer items-center gap-2 text-theme-sm rw-dim-2 select-none">
          <input
            type="checkbox"
            checked={serious}
            onChange={(event) => setSerious(event.target.checked)}
            className="size-4"
          />
          {text.serious}
        </label>
      </div>

      <p className="mt-1 mb-3 text-theme-xs rw-faint" aria-live="polite">
        {count}
      </p>

      {serious ? (
        <section className="grid items-center gap-6 rw-radius border rw-line rw-surface p-5 rw-shadow md:grid-cols-[minmax(0,18rem)_minmax(0,1fr)]">
          <PersonCard member={owner} locale={locale} alt={alt} website={text.website} large />
          <div className="min-w-0 space-y-3">
            <p className="font-mono text-theme-xs tracking-wide rw-accent-ink uppercase">{text.serious}</p>
            <h2 className="text-title-sm font-bold rw-strong">{owner.name}</h2>
            <p className="text-theme-sm font-medium rw-accent-ink">{localized(owner, "title", locale)}</p>
            {localized(owner, "context", locale) ? (
              <p className="text-theme-sm rw-strong">{localized(owner, "context", locale)}</p>
            ) : null}
            <p className="max-w-prose text-theme-sm rw-dim">{text.soloText}</p>
            <SocialLinks member={owner} website={text.website} />
          </div>
        </section>
      ) : shown.length === 0 ? (
        <p className="py-12 text-center text-theme-sm rw-dim">{text.empty}</p>
      ) : (
        <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4">
          {shown.map((role) => {
            const expanded = open === role.id;
            const panel = `rw-team-role-${role.id}`;
            const status = localized(role, "status", locale);
            const reports = localized(role, "reports_to", locale);
            const rows: (readonly [string, string])[] = [
              ...(reports ? [[text.reportsTo, reports] as const] : []),
              ...text.detail,
            ];
            return (
              <li
                key={role.id}
                className="flex min-w-0 flex-col gap-3 rw-radius border rw-line rw-surface p-5 rw-shadow"
              >
                <p className="font-mono text-theme-2xs tracking-wide rw-faint uppercase">
                  {names.get(role.department)}
                </p>
                <div className="flex items-center gap-3">
                  <Avatar member={owner} hue={role.hue} badge={role.badge} alt={alt} />
                  <div className="min-w-0">
                    <h2 className="text-theme-base leading-snug font-semibold rw-strong">{owner.name}</h2>
                    <p className="text-theme-sm font-medium rw-accent-ink">{localized(role, "title", locale)}</p>
                  </div>
                </div>
                <p className="text-theme-sm rw-dim">{localized(role, "about", locale)}</p>
                {status ? (
                  <p>
                    <span
                      className={`inline-flex rounded-full px-2.5 py-0.5 text-theme-xs ${
                        role.tone === "ok" ? "rw-ok-soft" : "rw-warn-soft"
                      }`}
                    >
                      {status}
                    </span>
                  </p>
                ) : null}
                <SocialLinks member={owner} website={text.website} />
                <button
                  type="button"
                  aria-expanded={expanded}
                  aria-controls={panel}
                  onClick={() => setOpen(expanded ? null : role.id)}
                  className="mt-auto h-11 text-start text-theme-sm font-semibold rw-accent-ink rw-focus-ring"
                >
                  {expanded ? text.less : text.more}
                </button>
                {expanded ? (
                  <dl id={panel} className="space-y-1.5 border-t border-dashed rw-divider pt-3 text-theme-sm">
                    {rows.map(([label, value]) => (
                      <div key={label} className="flex justify-between gap-3">
                        <dt className="rw-dim">{label}</dt>
                        <dd className="text-end font-medium rw-strong">{value}</dd>
                      </div>
                    ))}
                  </dl>
                ) : null}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
