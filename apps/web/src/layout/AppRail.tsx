"use client";

import { useEffect, useRef, useState } from "react";
import { usePathname } from "next/navigation";

import { Icon } from "@/components/ui/Icon";
import { IntentLink } from "@/components/ui/IntentLink";
import { useNavBadges } from "@/context/NavBadgesContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t, type MessageKey } from "@/i18n/messages";
import { badgeText, groupBadge } from "@/lib/nav-badges";
import { NAV_GROUPS } from "./nav";

/** The sentence behind each kind of badge (`{count}` is filled in). */
const BADGE_SAYS = {
  todo: "nav.badge.todo",
  unread: "nav.badge.unread",
  new: "nav.badge.new",
  live: "nav.badge.live",
} as const;

const PANEL_ID = "rw-rail-panel";

/** `nav.problems` → `nav.hint.problems`: the one-line hint under an entry. */
const hintKey = (key: string) => key.replace(/^nav\./, "nav.hint.") as MessageKey;

/** The `newNav` shell (2026-11-10, owner's choice "A · Rail + panel").
 *
 *  From `lg` up the 260 px side menu becomes a 72 px rail of the five
 *  groups; a click opens the group's panel with its entries and a one-line
 *  hint each. The content gains 188 px (1106 → 1294 px at 1366). Below
 *  `lg` nothing changes: the drawer stays (`AppSidebar`, owner's choice).
 *
 *  Still 21 entries in 5 groups (`nav.ts`), still prefetched only on
 *  intent (`IntentLink`); a group carries its strongest badge as a dot. */
export default function AppRail() {
  const pathname = usePathname();
  const locale = useLocale();
  const badges = useNavBadges();
  const [open, setOpen] = useState<string | null>(null);
  const railRef = useRef<HTMLElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);
  const buttons = useRef(new Map<string, HTMLButtonElement>());
  // Opened from the keyboard: focus moves into the panel. The panel comes
  // after all five buttons in the DOM, so Tab alone would walk the rest of
  // the rail first (measured: Enter on "Musobaqa", Tab → "Kampus").
  const focusPanel = useRef(false);

  // Any route change closes the panel, not only a click on its own links:
  // Back/Forward, a link in the page or the search palette would leave it
  // covering the new page. Derived during render, React's pattern for
  // resetting state on a prop change.
  const [seenPath, setSeenPath] = useState(pathname);
  if (seenPath !== pathname) {
    setSeenPath(pathname);
    setOpen(null);
  }

  const group = NAV_GROUPS.find((g) => g.key === open) ?? null;

  // Esc closes and returns focus to the group's button; a click outside
  // the rail and the panel closes it.
  useEffect(() => {
    if (!open) return;
    if (focusPanel.current) {
      focusPanel.current = false;
      panelRef.current?.querySelector<HTMLElement>("a")?.focus();
    }
    const onKey = (event: KeyboardEvent) => {
      if (event.key !== "Escape") return;
      setOpen(null);
      buttons.current.get(open)?.focus();
    };
    const onPointer = (event: PointerEvent) => {
      const target = event.target as Node;
      if (railRef.current?.contains(target) || panelRef.current?.contains(target)) return;
      setOpen(null);
    };
    // Below `lg` the rail is hidden: an open panel must not come back when
    // the window widens again.
    const wide = window.matchMedia("(min-width: 1024px)");
    const onNarrow = () => {
      if (!wide.matches) setOpen(null);
    };
    document.addEventListener("keydown", onKey);
    document.addEventListener("pointerdown", onPointer);
    wide.addEventListener("change", onNarrow);
    return () => {
      document.removeEventListener("keydown", onKey);
      document.removeEventListener("pointerdown", onPointer);
      wide.removeEventListener("change", onNarrow);
    };
  }, [open]);

  const isActive = (href: string) => pathname === href || pathname.startsWith(`${href}/`);

  return (
    <>
      <nav
        ref={railRef}
        id="rw-rail"
        aria-label={t(locale, "nav.main")}
        className="fixed top-0 left-0 z-50 hidden h-screen w-[72px] flex-col border-r rw-divider rw-chrome lg:flex"
      >
        {/* The header's row: the rail starts below it, like the menu did. */}
        <div className="h-16 shrink-0" />
        <ul className="flex flex-col gap-1 px-1">
          {NAV_GROUPS.map((g) => {
            const current = g.items.some((item) => isActive(item.href));
            const badge = groupBadge(
              g.items.map((item) => item.href),
              badges,
            );
            const said = badge
              ? fill(t(locale, BADGE_SAYS[badge.kind]), { count: badge.count })
              : null;
            const label = t(locale, g.key);
            return (
              <li key={g.key}>
                <button
                  type="button"
                  ref={(el) => {
                    if (el) buttons.current.set(g.key, el);
                    else buttons.current.delete(g.key);
                  }}
                  onClick={(event) => {
                    // `detail` is 0 for a click made with Enter or Space.
                    focusPanel.current = event.detail === 0 && open !== g.key;
                    setOpen((now) => (now === g.key ? null : g.key));
                  }}
                  aria-expanded={open === g.key}
                  aria-controls={PANEL_ID}
                  title={said ? `${label} — ${said}` : label}
                  data-current={current || undefined}
                  className="rw-rail-btn rw-focus-ring"
                >
                  <Icon name={g.items[0].iconKey} className="size-5 shrink-0" />
                  <span className="w-full truncate text-center">{label}</span>
                  {badge && (
                    <span
                      className="rw-nav-badge"
                      data-kind={badge.kind}
                      data-rail=""
                      aria-hidden="true"
                    />
                  )}
                  {said && <span className="sr-only">{said}</span>}
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      {group && (
        <div
          ref={panelRef}
          id={PANEL_ID}
          role="region"
          aria-label={t(locale, group.key)}
          className="fixed top-0 bottom-0 left-[72px] z-40 hidden w-[260px] flex-col border-r rw-divider rw-chrome rw-shadow lg:flex"
        >
          <div className="flex h-16 shrink-0 items-center px-4">
            <h2 className="text-theme-sm font-semibold tracking-wider uppercase rw-dim-2">
              {t(locale, group.key)}
            </h2>
          </div>
          <ul className="flex flex-col gap-1 px-3 pb-6 rw-scroll-y rw-scroll-trap">
            {group.items.map(({ href, key, iconKey }) => {
              const active = isActive(href);
              const badge = badges[href];
              const said = badge
                ? fill(t(locale, BADGE_SAYS[badge.kind]), { count: badge.count })
                : null;
              return (
                <li key={href}>
                  <IntentLink
                    href={href}
                    onClick={() => setOpen(null)}
                    aria-current={active ? "page" : undefined}
                    className={`menu-item min-h-11 ${active ? "menu-item-active" : "menu-item-inactive"}`}
                  >
                    <Icon
                      name={iconKey}
                      className={`size-5 shrink-0 ${
                        active ? "menu-item-icon-active" : "menu-item-icon-inactive"
                      }`}
                    />
                    <span className="flex min-w-0 flex-col">
                      <span className="truncate">{t(locale, key)}</span>
                      <span className="truncate text-theme-xs font-normal rw-faint">
                        {t(locale, hintKey(key))}
                      </span>
                    </span>
                    {badge && (
                      <span className="rw-nav-badge" data-kind={badge.kind} aria-hidden="true">
                        {badge.kind === "live"
                          ? t(locale, "nav.badge.liveShort")
                          : badgeText(badge.count)}
                      </span>
                    )}
                    {said && <span className="sr-only">{said}</span>}
                  </IntentLink>
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </>
  );
}
