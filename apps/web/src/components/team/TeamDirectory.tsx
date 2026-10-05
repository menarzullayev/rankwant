"use client";

import { useMemo, useState } from "react";

import type { TeamRole, TeamText } from "@/content/team";

type Member = {
  name: string;
  initials: string;
  links: readonly { label: string; href: string }[];
};

const ALL = -1;

/** Every role on the page is the same person, so the avatars differ by hue
 *  and by a small mark. The colour is fixed-lightness HSL under white text,
 *  the same recipe the accent swatches use. */
function Avatar({
  member,
  hue,
  badge,
  alt,
  large = false,
}: {
  member: Member;
  hue: number;
  badge?: string;
  alt: string;
  large?: boolean;
}) {
  return (
    <span
      role="img"
      aria-label={alt}
      style={{ background: `hsl(${hue} 62% 42%)` }}
      className={`relative grid shrink-0 place-items-center rounded-full font-bold text-white ${
        large ? "size-28 text-title-sm" : "size-16 text-theme-xl"
      }`}
    >
      {member.initials}
      {badge ? (
        <span className="absolute -end-1 -bottom-1 grid h-6 min-w-6 place-items-center rounded-full border rw-line rw-surface px-1 font-mono text-theme-2xs font-semibold rw-strong">
          {badge}
        </span>
      ) : null}
    </span>
  );
}

function Links({ member }: { member: Member }) {
  return (
    <ul className="flex flex-wrap gap-2">
      {member.links.map((link) => (
        <li key={link.href}>
          <a
            href={link.href}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex h-11 items-center rw-radius-sm border rw-divider px-3 text-theme-sm font-medium rw-dim-2 transition rw-hover-bg rw-focus-ring"
          >
            {link.label}
          </a>
        </li>
      ))}
    </ul>
  );
}

const chip = (active: boolean) =>
  `inline-flex h-11 shrink-0 items-center gap-2 rounded-full border px-4 text-theme-sm whitespace-nowrap transition rw-focus-ring ${
    active ? "rw-accent-bg font-semibold" : "rw-divider rw-surface rw-dim-2 rw-hover-bg"
  }`;

export function TeamDirectory({
  text,
  roles,
  member,
}: {
  text: TeamText;
  roles: TeamRole[];
  member: Member;
}) {
  const [dept, setDept] = useState(ALL);
  const [query, setQuery] = useState("");
  const [serious, setSerious] = useState(false);
  const [open, setOpen] = useState<number | null>(null);

  const perDept = useMemo(
    () => text.depts.map((_, index) => roles.filter((role) => role.dept === index).length),
    [roles, text.depts],
  );

  const needle = query.trim().toLowerCase();
  const shown = roles
    .map((role, index) => ({ role, index, words: text.roles[index] }))
    .filter(
      ({ role, words }) =>
        (dept === ALL || role.dept === dept) &&
        (!needle ||
          `${words[0]} ${words[1]} ${text.depts[role.dept]}`.toLowerCase().includes(needle)),
    );

  const alt = text.photoAlt.replace("{name}", member.name);
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
      <div className="sticky top-16 z-10 -mx-1 flex flex-wrap items-center gap-3 px-1 py-3 rw-ground-bg">
        <div
          role="group"
          aria-label={text.filterLabel}
          className="flex min-w-0 flex-1 gap-2 overflow-x-auto py-1"
        >
          <button type="button" aria-pressed={dept === ALL} onClick={() => pick(ALL)} className={chip(dept === ALL)}>
            {text.all}
            <span className="font-mono text-theme-xs opacity-70">{roles.length}</span>
          </button>
          {text.depts.map((name, index) => (
            <button
              key={name}
              type="button"
              aria-pressed={dept === index}
              onClick={() => pick(index)}
              className={chip(dept === index)}
            >
              {name}
              <span className="font-mono text-theme-xs opacity-70">{perDept[index]}</span>
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
        <section className="grid items-center gap-6 rw-radius border rw-line rw-surface p-6 rw-shadow md:grid-cols-[auto_minmax(0,1fr)]">
          <Avatar member={member} hue={262} alt={alt} large />
          <div className="min-w-0 space-y-3">
            <p className="font-mono text-theme-xs tracking-wide rw-accent-ink uppercase">{text.serious}</p>
            <h2 className="text-title-sm font-bold rw-strong">{member.name}</h2>
            <p className="text-theme-sm font-medium rw-accent-ink">{text.soloRole}</p>
            <p className="max-w-prose text-theme-sm rw-dim">{text.soloText}</p>
            <Links member={member} />
          </div>
        </section>
      ) : shown.length === 0 ? (
        <p className="py-12 text-center text-theme-sm rw-dim">{text.empty}</p>
      ) : (
        <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4">
          {shown.map(({ role, index, words }) => {
            const expanded = open === index;
            const panel = `rw-team-role-${index}`;
            return (
              <li
                key={index}
                className="flex min-w-0 flex-col gap-3 rw-radius border rw-line rw-surface p-5 rw-shadow"
              >
                <p className="font-mono text-theme-2xs tracking-wide rw-faint uppercase">
                  {text.depts[role.dept]}
                </p>
                <div className="flex items-center gap-3">
                  <Avatar member={member} hue={role.hue} badge={role.badge} alt={alt} />
                  <div className="min-w-0">
                    <h2 className="text-theme-base leading-snug font-semibold rw-strong">{member.name}</h2>
                    <p className="text-theme-sm font-medium rw-accent-ink">{words[0]}</p>
                  </div>
                </div>
                <p className="text-theme-sm rw-dim">{words[1]}</p>
                <p>
                  <span
                    className={`inline-flex rounded-full px-2.5 py-0.5 text-theme-xs ${
                      role.tone === "ok" ? "rw-ok-soft" : "rw-warn-soft"
                    }`}
                  >
                    {words[3]}
                  </span>
                </p>
                <Links member={member} />
                <button
                  type="button"
                  aria-expanded={expanded}
                  aria-controls={panel}
                  onClick={() => setOpen(expanded ? null : index)}
                  className="mt-auto h-11 text-start text-theme-sm font-semibold rw-accent-ink rw-focus-ring"
                >
                  {expanded ? text.less : text.more}
                </button>
                {expanded ? (
                  <dl id={panel} className="space-y-1.5 border-t border-dashed rw-divider pt-3 text-theme-sm">
                    {[[text.reportsTo, words[2]] as const, ...text.detail].map(([label, value]) => (
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
