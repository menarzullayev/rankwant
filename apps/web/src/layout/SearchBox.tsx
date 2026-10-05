"use client";

import dynamic from "next/dynamic";
import { useCallback, useEffect, useRef, useState } from "react";

import { Icon } from "@/components/ui/Icon";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";

// The palette is only code until someone opens it — it stays out of the
// header's bundle, and it draws into `document.body`, which a server
// render does not have.
const SearchPalette = dynamic(
  () => import("@/components/search/SearchPalette").then((mod) => mod.SearchPalette),
  { ssr: false },
);

/** The header's door to the search palette.
 *
 *  It looks like a field from `md` up and is a magnifier button below
 *  that, but it is a button at every width: typing happens in the
 *  palette, which has room for results, types and recent searches. The
 *  header used to carry its own dropdown with four result types and no
 *  keyboard navigation; the palette replaced it (2026-10-05).
 */
export default function SearchBox() {
  const locale = useLocale();
  const [open, setOpen] = useState(false);
  const trigger = useRef<HTMLButtonElement>(null);

  // `Ctrl+K` / `Cmd+K` belongs to search alone (H2).
  //
  // ⚠️ `preventDefault()` is required: without it the browser opens its
  // own address-bar search. Plain combination only — `Ctrl+Shift+K` and
  // the like are left to the browser.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key.toLowerCase() !== "k" || e.shiftKey || e.altKey) return;
      if (!(e.metaKey || e.ctrlKey)) return;
      e.preventDefault();
      setOpen((was) => !was);
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, []);

  const close = useCallback(() => {
    setOpen(false);
    // Focus goes back to where it came from, as a dialog owes.
    requestAnimationFrame(() => trigger.current?.focus());
  }, []);

  return (
    <>
      <button
        ref={trigger}
        type="button"
        onClick={() => setOpen(true)}
        aria-haspopup="dialog"
        aria-expanded={open}
        aria-keyshortcuts="Control+K Meta+K"
        aria-label={t(locale, "header.search")}
        data-tip={t(locale, "header.search")}
        data-tip-kind="flip"
        className="flex size-10 shrink-0 items-center justify-center gap-2 rw-radius-sm rw-dim-2 transition rw-hover-bg rw-focus-ring md:h-10 md:w-36 md:min-w-0 md:shrink md:justify-start md:border md:px-3 rw-line lg:w-52 xl:w-80"
      >
        <Icon name="action.search" className="pointer-events-none size-5 shrink-0" />
        <span className="hidden min-w-0 flex-1 truncate text-left text-theme-sm rw-faint md:block">
          {t(locale, "header.search")}
        </span>
        <kbd
          aria-hidden="true"
          className="pointer-events-none hidden rw-radius-sm border rw-line px-1.5 py-0.5 text-theme-xs rw-faint lg:inline-block"
        >
          Ctrl K
        </kbd>
      </button>
      {open && <SearchPalette onClose={close} />}
    </>
  );
}
