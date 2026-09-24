"use client";

import Link, { type LinkProps } from "next/link";
import type React from "react";
import { useState } from "react";

/** A `<Link>` that prefetches on intent (hover, keyboard focus or touch)
 *  instead of as soon as it is on screen.
 *
 *  The sidebar, the top bar and the header render ~23 links on every page.
 *  Prefetched on sight, each costs the server ~5.6 ms of CPU: ~130–150 ms
 *  per visit, about nine times the page render itself (measured
 *  2026-09-18, `docs/research/2026-09-18-homepage-profile`). On intent,
 *  only the link the visitor is about to open is fetched, still ahead of
 *  the click.
 *
 *  This is the pattern from the Next.js prefetching guide: `prefetch` stays
 *  `false` until the first intent event, then falls back to the default,
 *  which fetches the link because it is already in view.
 *
 *  Generic like `Link` itself: with `typedRoutes`, a plain
 *  `ComponentProps<typeof Link>` pins the route type to `unknown` and every
 *  literal `href` stops type-checking.
 *
 *  ⚠️ Next 16.3.5 changed `LinkProps` into a plain union that carries only
 *  the navigation props — the anchor attributes it used to inherit are no
 *  longer in it. `Link` still forwards them to the rendered `<a>`, so the
 *  type has to say so explicitly, otherwise every `role`, `aria-*`, `title`
 *  or `onFocus` handed to this component is rejected. Concretely, the old
 *  form failed with:
 *
 *      Property 'onFocus' does not exist on type 'LinkProps<RouteType>'.
 *
 *  Intersecting with the anchor props restores that surface and keeps the
 *  generic `href` inference intact. */
type AnchorProps = Omit<React.ComponentPropsWithoutRef<"a">, "href">;

export function IntentLink<RouteType>({
  onMouseEnter,
  onFocus,
  onTouchStart,
  ...props
}: LinkProps<RouteType> & AnchorProps) {
  const [intent, setIntent] = useState(false);
  return (
    <Link
      {...props}
      prefetch={intent ? null : false}
      onMouseEnter={(event) => {
        setIntent(true);
        onMouseEnter?.(event);
      }}
      onFocus={(event) => {
        setIntent(true);
        onFocus?.(event);
      }}
      onTouchStart={(event) => {
        setIntent(true);
        onTouchStart?.(event);
      }}
    />
  );
}
