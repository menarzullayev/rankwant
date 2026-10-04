import type { Route } from "next";

import { MarkerText } from "@/components/ui/Identity";
import { Avatar } from "@/components/ui/Identity/Avatar";
import { rankClass } from "@/components/ui/Identity/UserName";
import { IntentLink } from "@/components/ui/IntentLink";
import type { UserTitle } from "@/lib/identity";

export type PersonRow = {
  username: string;
  name: string;
  avatar: string;
  title: UserTitle | null;
};

/** Avatar, name in the rank colour, handle underneath.
 *
 *  Not `UserName`: that one renders a plain `Link`, which prefetches as soon
 *  as it is on screen. The home page lists dozens of people, and its links
 *  prefetch on intent only (decision of 2026-09-18). */
export function Person({
  person,
  children,
}: {
  person: PersonRow;
  children?: React.ReactNode;
}) {
  const display = person.name || person.username;
  const { title } = person;
  return (
    <span className="flex min-w-0 items-center gap-3">
      <Avatar url={person.avatar} name={display} />
      <span className="min-w-0">
        <IntentLink
          href={`/users/${person.username}` as Route}
          className={`block truncate font-medium rw-link-hover ${rankClass(title)}`}
        >
          {title && title.marker > 0 ? (
            <MarkerText text={display} marker={title.marker} />
          ) : (
            display
          )}
        </IntentLink>
        {children}
      </span>
    </span>
  );
}
