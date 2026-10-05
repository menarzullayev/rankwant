import { Icon } from "@/components/ui/Icon";
import { localized, type TeamLocale } from "@/content/team";

import type { TeamMember } from "./types";

/** GitHub and Telegram are the marks the sign-in buttons use; the other two
 *  are drawn from plain shapes. All take `currentColor`. */
function Mark({ kind }: { kind: "telegram" | "github" | "linkedin" | "instagram" }) {
  if (kind === "github") {
    return (
      <svg viewBox="0 0 24 24" className="size-5" aria-hidden="true">
        <path
          fill="currentColor"
          d="M12 .5A11.5 11.5 0 0 0 .5 12a11.5 11.5 0 0 0 7.86 10.92c.58.1.79-.25.79-.56v-2c-3.2.7-3.88-1.37-3.88-1.37-.53-1.34-1.29-1.7-1.29-1.7-1.05-.72.08-.7.08-.7 1.16.08 1.77 1.2 1.77 1.2 1.03 1.77 2.7 1.26 3.36.96.1-.75.4-1.26.73-1.55-2.55-.29-5.24-1.28-5.24-5.7 0-1.26.45-2.29 1.19-3.1-.12-.29-.52-1.46.11-3.05 0 0 .97-.31 3.18 1.18a11 11 0 0 1 5.8 0c2.2-1.5 3.17-1.18 3.17-1.18.63 1.59.23 2.76.12 3.05.74.81 1.18 1.84 1.18 3.1 0 4.43-2.69 5.4-5.25 5.69.41.36.78 1.06.78 2.14v3.17c0 .31.2.67.8.56A11.5 11.5 0 0 0 23.5 12 11.5 11.5 0 0 0 12 .5Z"
        />
      </svg>
    );
  }
  if (kind === "telegram") {
    return (
      <svg viewBox="0 0 24 24" className="size-5" aria-hidden="true">
        <path
          fill="currentColor"
          d="M12 0C5.37 0 0 5.37 0 12s5.37 12 12 12 12-5.37 12-12S18.63 0 12 0Zm5.9 8.14-1.98 9.35c-.15.66-.54.82-1.1.51l-3.03-2.24-1.47 1.41c-.16.16-.3.3-.61.3l.22-3.1 5.65-5.1c.25-.22-.05-.34-.38-.13l-6.98 4.4-3.01-.94c-.65-.2-.67-.65.14-.97L17.1 7.2c.54-.2 1.01.13.8.94Z"
        />
      </svg>
    );
  }
  if (kind === "instagram") {
    return (
      <svg viewBox="0 0 24 24" className="size-5" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
        <rect x="3" y="3" width="18" height="18" rx="5" />
        <circle cx="12" cy="12" r="4" />
        <circle cx="17.2" cy="6.8" r="1" fill="currentColor" stroke="none" />
      </svg>
    );
  }
  return (
    <svg viewBox="0 0 24 24" className="size-5" aria-hidden="true">
      <rect x="3" y="3" width="18" height="18" rx="3" fill="none" stroke="currentColor" strokeWidth="2" />
      <rect x="7" y="10" width="2.2" height="7" fill="currentColor" />
      <circle cx="8.1" cy="7.4" r="1.3" fill="currentColor" />
      <path
        d="M12.4 17v-7M12.4 13.2a2.3 2.3 0 0 1 4.6 0V17"
        fill="none"
        stroke="currentColor"
        strokeWidth="2.2"
      />
    </svg>
  );
}

const LINKS = [
  ["telegram", "Telegram", "telegram_url"],
  ["github", "GitHub", "github_url"],
  ["linkedin", "LinkedIn", "linkedin_url"],
  ["instagram", "Instagram", "instagram_url"],
] as const;

/** A member's links as icons. `overlay` sits on a photo: dark discs, white
 *  marks, whatever the page's style. Every link is a 44 px target and is
 *  named for a screen reader as "Telegram: <person>". */
export function SocialLinks({
  member,
  website,
  overlay = false,
}: {
  member: TeamMember;
  website: string;
  overlay?: boolean;
}) {
  const shape = overlay
    ? "grid size-11 place-items-center rounded-full bg-black/55 text-white backdrop-blur-sm transition hover:bg-black/75 rw-focus-ring"
    : "grid size-11 place-items-center rw-radius-sm border rw-divider rw-dim-2 transition rw-hover-bg rw-focus-ring";
  const items = LINKS.filter(([, , field]) => member[field]);
  if (items.length === 0 && !member.website_url) return null;
  return (
    <ul className={overlay ? "flex flex-col gap-2" : "flex flex-wrap gap-2"}>
      {items.map(([kind, label, field]) => (
        <li key={kind}>
          <a
            href={member[field]}
            target="_blank"
            rel="noopener noreferrer"
            aria-label={`${label}: ${member.name}`}
            title={label}
            className={shape}
          >
            <Mark kind={kind} />
          </a>
        </li>
      ))}
      {member.website_url ? (
        <li>
          <a
            href={member.website_url}
            target="_blank"
            rel="noopener noreferrer"
            aria-label={`${website}: ${member.name}`}
            title={website}
            className={shape}
          >
            <Icon name="nav.external" className="size-5" />
          </a>
        </li>
      ) : null}
    </ul>
  );
}

export function initialsOf(name: string): string {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? "")
    .join("");
}

/** A person as a portrait: the photo fills the card, the name and title sit
 *  on a dark fade at the bottom, the links in the top corner. Without a
 *  photo the card shows the initials on the accent colour. */
export function PersonCard({
  member,
  locale,
  alt,
  website,
  large = false,
}: {
  member: TeamMember;
  locale: TeamLocale;
  alt: string;
  website: string;
  large?: boolean;
}) {
  const title = localized(member, "title", locale);
  const context = localized(member, "context", locale);
  return (
    <article
      data-team-person
      className="relative isolate flex aspect-[3/4] w-full flex-col justify-end overflow-hidden rw-radius rw-accent-bg rw-shadow"
    >
      {member.photo_url ? (
        // A plain <img>: the photo's address comes from the admin panel and may
        // be on any https host; `next/image` would need each host allow-listed.
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={member.photo_url}
          alt={alt}
          loading="lazy"
          decoding="async"
          className="absolute inset-0 -z-10 size-full object-cover"
        />
      ) : (
        <span
          aria-hidden="true"
          className="absolute inset-0 -z-10 grid place-items-center text-title-md font-bold opacity-80"
        >
          {initialsOf(member.name)}
        </span>
      )}
      <div className="absolute end-3 top-3">
        <SocialLinks member={member} website={website} overlay />
      </div>
      <div className="bg-gradient-to-t from-black/85 via-black/55 to-transparent px-4 pt-16 pb-4 text-white">
        <h3 className={`leading-tight font-bold ${large ? "text-title-sm" : "text-theme-xl"}`}>
          {member.name}
        </h3>
        <p className="mt-1 text-theme-sm font-medium opacity-95">{title}</p>
        {context ? <p className="mt-1 text-theme-xs opacity-85">{context}</p> : null}
      </div>
    </article>
  );
}
