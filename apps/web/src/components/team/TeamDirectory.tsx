"use client";

import { useEffect, useMemo, useRef, useState } from "react";

import { Dropdown } from "@/components/ui/Dropdown";
import { Icon } from "@/components/ui/Icon";
import { localized, type TeamLocale, type TeamText } from "@/content/team";
import { revealElement } from "@/lib/scroll";

import { PersonCard, SocialLinks, initialsOf } from "./Person";
import { TeamHeader } from "./TeamHeader";
import { ALL_DEPARTMENTS, teamHref, type TeamView } from "./state";
import type { TeamDepartment, TeamMember, TeamRole } from "./types";

/** How many roles the list opens with: a phone, and anything wider. The
 *  rest stay in the page (a search engine and "find in page" still read
 *  them) and are shown by one button. Measured 2026-10-06: the full list
 *  was twelve screens on a phone. */
const FIRST_PHONE = 8;
const FIRST_WIDE = 12;

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
  const ring = `0 0 0 2px hsl(${hue} 62% 46%)`;
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
          width={44}
          height={44}
          style={{ boxShadow: ring }}
          className="size-11 rounded-full object-cover"
        />
      ) : (
        <span
          role="img"
          aria-label={alt}
          style={{ background: `hsl(${hue} 62% 42%)` }}
          className="grid size-11 place-items-center rounded-full text-theme-sm font-bold text-white"
        >
          {initialsOf(member.name)}
        </span>
      )}
      {badge ? (
        <span
          aria-hidden="true"
          className="absolute -end-1.5 -bottom-1.5 grid h-5 min-w-5 place-items-center rounded-full border rw-line rw-surface px-1 font-mono text-theme-2xs font-semibold rw-strong"
        >
          {badge}
        </span>
      ) : null}
    </span>
  );
}

const chip = (active: boolean) =>
  `inline-flex h-9 shrink-0 items-center gap-2 rounded-full border px-3 text-theme-sm whitespace-nowrap transition rw-focus-ring ${
    active ? "rw-accent-bg font-semibold" : "rw-divider rw-surface rw-dim-2 rw-hover-bg"
  }`;

const viewButton = (active: boolean) =>
  `inline-flex h-10 items-center rounded-full px-4 text-theme-sm transition rw-focus-ring ${
    active ? "rw-accent-bg font-semibold" : "rw-dim-2 rw-hover-bg"
  }`;

/** The roles, the filter over them and the two ways to read the page.
 *
 *  The joke and the serious page are two views, not a checkbox over one:
 *  in the serious one the filter, the search and the joke numbers have
 *  nothing to act on, so they are not drawn. What is chosen is written to
 *  the address (`teamHref`), so a link opens the same view. */
export function TeamDirectory({
  text,
  locale,
  owner,
  departments,
  roles,
  stats,
  initial,
}: {
  text: TeamText;
  locale: TeamLocale;
  owner: TeamMember;
  departments: TeamDepartment[];
  roles: TeamRole[];
  stats: readonly number[];
  initial: TeamView;
}) {
  const [dept, setDept] = useState(initial.dept);
  const [query, setQuery] = useState(initial.query);
  const [serious, setSerious] = useState(initial.serious);
  const [all, setAll] = useState(false);
  const root = useRef<HTMLDivElement>(null);
  const list = useRef<HTMLUListElement>(null);

  const names = useMemo(
    () => new Map(departments.map((item) => [item.id, localized(item, "name", locale)])),
    [departments, locale],
  );

  // The address follows the view without a navigation: nothing is fetched
  // again, and Back still leaves the page.
  useEffect(() => {
    const href = teamHref({ dept, query, serious });
    if (href !== window.location.pathname + window.location.search) {
      window.history.replaceState(window.history.state, "", href);
    }
  }, [dept, query, serious]);

  const needle = query.trim().toLowerCase();
  const filtered = dept !== ALL_DEPARTMENTS || needle !== "";
  const shown = roles.filter((role) => {
    if (dept !== ALL_DEPARTMENTS && role.department !== dept) return false;
    if (!needle) return true;
    const haystack = `${localized(role, "title", locale)} ${localized(role, "about", locale)} ${
      names.get(role.department) ?? ""
    }`;
    return haystack.toLowerCase().includes(needle);
  });
  const whole = all || filtered;

  const alt = text.photoAlt.replace("{name}", owner.name);

  function pick(next: number) {
    setDept(next);
    setAll(false);
  }

  function showAll() {
    // The first role that was hidden takes the focus: the button is gone,
    // and a keyboard should land where the new rows begin.
    const first = window.matchMedia("(min-width: 640px)").matches ? FIRST_WIDE : FIRST_PHONE;
    setAll(true);
    requestAnimationFrame(() => {
      list.current?.querySelectorAll<HTMLElement>("summary")[first]?.focus();
    });
  }

  function toSerious() {
    setSerious(true);
    requestAnimationFrame(() => {
      revealElement(root.current, { block: "start" });
      root.current?.querySelector<HTMLElement>("h1")?.focus();
    });
  }

  const options = [
    { value: String(ALL_DEPARTMENTS), label: text.allDepartments },
    ...departments.map((item) => ({ value: String(item.id), label: names.get(item.id) ?? "" })),
  ];

  return (
    <div ref={root} data-team-directory className="space-y-5">
      <TeamHeader
        text={text}
        heading={serious ? text.seriousHeading : text.heading}
        lede={serious ? text.seriousLede : text.lede}
        stats={serious ? null : stats}
      />

      <div className="flex flex-wrap items-end gap-2 lg:items-center">
        <div
          role="group"
          aria-label={text.viewLabel}
          className="inline-flex shrink-0 rounded-full border rw-divider rw-surface p-0.5"
        >
          <button
            type="button"
            aria-pressed={!serious}
            onClick={() => setSerious(false)}
            className={viewButton(!serious)}
          >
            {text.viewFun}
          </button>
          <button
            type="button"
            aria-pressed={serious}
            onClick={() => setSerious(true)}
            className={viewButton(serious)}
          >
            {text.viewSerious}
          </button>
        </div>
        {serious ? null : (
          <>
            {/* A phone gets one list instead of thirteen chips: wrapped,
                they were six rows (312 px) before the first role. */}
            <div className="min-w-0 flex-1 basis-40 lg:hidden">
              <Dropdown
                label={text.filterLabel}
                options={options}
                value={String(dept)}
                onChange={(value) => pick(Number(value))}
              />
            </div>
            <input
              type="search"
              value={query}
              onChange={(event) => {
                setQuery(event.target.value);
                setAll(false);
              }}
              placeholder={text.search}
              aria-label={text.search}
              className="h-11 min-w-0 flex-1 basis-44 rounded-full border rw-divider rw-field-bg px-4 text-theme-sm rw-strong rw-fm-inp rw-focus-ring lg:ms-auto lg:max-w-60 lg:flex-none"
            />
            <div
              role="group"
              aria-label={text.filterLabel}
              className="hidden min-w-0 basis-full flex-wrap gap-2 lg:flex"
            >
              <button
                type="button"
                aria-pressed={dept === ALL_DEPARTMENTS}
                onClick={() => pick(ALL_DEPARTMENTS)}
                className={chip(dept === ALL_DEPARTMENTS)}
              >
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
          </>
        )}
      </div>

      {serious ? (
        <section className="grid items-center gap-6 rw-radius border rw-line rw-surface p-5 rw-shadow md:grid-cols-[minmax(0,16rem)_minmax(0,1fr)]">
          <PersonCard member={owner} locale={locale} alt={alt} website={text.website} plain />
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
      ) : (
        <>
          <p className="text-theme-xs rw-dim" role="status">
            {shown.length === 0
              ? text.empty
              : text.count.replace("{roles}", String(shown.length)).replace("{people}", "1")}
          </p>

          <ul ref={list} className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {shown.map((role, index) => {
              const status = localized(role, "status", locale);
              const reports = localized(role, "reports_to", locale);
              const about = localized(role, "about", locale);
              const rows: (readonly [string, string])[] = [
                ...(reports ? [[text.reportsTo, reports] as const] : []),
                ...text.detail,
              ];
              let fold = "";
              if (!whole && index >= FIRST_WIDE) fold = "hidden";
              else if (!whole && index >= FIRST_PHONE) fold = "hidden sm:block";
              return (
                <li key={role.id} className={`min-w-0 ${fold}`}>
                  {/* The title is the heading: the name is the same on every
                      card and told a screen reader's heading list nothing. */}
                  <details className="group h-full rw-radius border rw-line rw-surface rw-shadow">
                    <summary className="flex min-h-16 cursor-pointer list-none items-center gap-3 rw-radius px-3 py-2.5 rw-focus-ring [&::-webkit-details-marker]:hidden">
                      <Avatar member={owner} hue={role.hue} badge={role.badge} alt="" />
                      <div className="min-w-0 flex-1">
                        {/* The status sits on the title's line: beside the
                            whole text it squeezed the by-line into two rows. */}
                        <div className="flex items-start justify-between gap-2">
                          <h2 className="min-w-0 text-theme-sm leading-snug font-semibold rw-strong">
                            {localized(role, "title", locale)}
                          </h2>
                          {status ? (
                            <span
                              className={`shrink-0 rounded-full px-2.5 py-0.5 text-theme-xs max-[379px]:hidden ${
                                role.tone === "ok" ? "rw-ok-soft" : "rw-warn-soft"
                              }`}
                            >
                              {status}
                            </span>
                          ) : null}
                        </div>
                        <p className="text-theme-xs rw-dim">
                          {owner.name} · {names.get(role.department)}
                        </p>
                        <p className="mt-0.5 hidden text-theme-xs rw-dim-2 group-open:hidden sm:line-clamp-2">
                          {about}
                        </p>
                      </div>
                    </summary>
                    <div className="space-y-2 px-3 pb-3 text-theme-sm">
                      <p className="rw-dim">{about}</p>
                      <dl className="space-y-1.5 border-t border-dashed rw-divider pt-2">
                        {rows.map(([label, value]) => (
                          <div key={label} className="flex justify-between gap-3">
                            <dt className="rw-dim">{label}</dt>
                            <dd className="text-end font-medium rw-strong">{value}</dd>
                          </div>
                        ))}
                      </dl>
                    </div>
                  </details>
                </li>
              );
            })}
          </ul>

          {!whole && shown.length > FIRST_PHONE ? (
            <button
              type="button"
              onClick={showAll}
              className={`mx-auto flex h-11 items-center rw-radius-sm border rw-divider px-5 text-theme-sm font-medium rw-dim-2 rw-hover-bg rw-focus-ring ${
                shown.length > FIRST_WIDE ? "" : "sm:hidden"
              }`}
            >
              <span className="sm:hidden">
                {text.showMore.replace("{count}", String(shown.length - FIRST_PHONE))}
              </span>
              <span className="hidden sm:inline">
                {text.showMore.replace("{count}", String(shown.length - FIRST_WIDE))}
              </span>
            </button>
          ) : null}

          {/* The links were on every card — forty-eight of them to two
              addresses. They live in the serious view; this is the way in. */}
          <button
            type="button"
            onClick={toSerious}
            className="flex w-full items-center gap-3 rw-radius border rw-line rw-surface p-3 text-start rw-shadow rw-hover-bg rw-focus-ring"
          >
            <Avatar member={owner} hue={262} badge="" alt="" />
            <span className="min-w-0 flex-1">
              <span className="block text-theme-sm font-semibold rw-strong">
                {text.ownerCardTitle.replace("{name}", owner.name)}
              </span>
              <span className="block text-theme-xs rw-dim">{text.ownerCardText}</span>
            </span>
            <Icon name="nav.expandDown" className="size-5 shrink-0 -rotate-90 rw-dim" />
          </button>
        </>
      )}
    </div>
  );
}
