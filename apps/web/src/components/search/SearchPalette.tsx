"use client";

import type { Route } from "next";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useRef, useState, type KeyboardEvent } from "react";
import { createPortal } from "react-dom";

import { useOverlay } from "@/components/overlay/OverlayHost";
import { Icon } from "@/components/ui/Icon";
import { useCustomizer } from "@/context/CustomizerContext";
import { useSession } from "@/context/SessionContext";
import { useStyle } from "@/context/StyleContext";
import { useTheme } from "@/context/ThemeContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";
import { NAV } from "@/layout/nav";
import { isDual, type StyleId } from "@/layout/styles";
import { API_BASE } from "@/lib/api";
import {
  SEARCH_TYPES,
  filterLocal,
  foldText,
  hitHref,
  hitIcon,
  isServerType,
  MIN_QUERY,
  parseQuery,
  prefixOf,
  searchHref,
  type SearchResponse,
  type SearchType,
} from "@/lib/search/model";
import { clearRecent, readRecent, rememberRecent } from "@/lib/search/recent";
import { CUSTOMIZER_ENABLED } from "@/lib/theme/flag";

import { describeHit } from "./describe";
import { Highlight } from "./Highlight";

/** How many of each type the mixed list shows, and a single type's list. */
const MIXED = 4;
const SINGLE = 8;
/** Wait for the typing to pause before asking the server. */
const DEBOUNCE_MS = 180;

type Option = {
  id: string;
  icon: string;
  title: string;
  subtitle: string;
  meta: string;
  /** Mark the matched part of the title. */
  marked: boolean;
  run: () => void;
};

type Section = {
  key: string;
  label: string;
  more?: { label: string; run: () => void };
  options: Option[];
};

type LocalItem = { id: string; label: string; icon: string; hint: string; run: () => void };

type Answer = { key: string; type: SearchType; data: SearchResponse | null };

const CHIP =
  "inline-flex h-9 shrink-0 items-center gap-1.5 rounded-full border px-3 text-theme-sm whitespace-nowrap transition rw-focus-ring [@media(pointer:coarse)]:h-11";
/** Key caps — names of keys, the same in every language. */
const KEY = { esc: "Esc", enter: "Enter", tab: "Tab", up: "↑", down: "↓" } as const;
const KBD = "rw-radius-sm border rw-line px-1.5 py-0.5 font-mono text-theme-xs rw-faint";

/** The one search surface: results, pages and commands in a single list.
 *
 *  Focus never leaves the input. The list is driven from there
 *  (`aria-activedescendant`): arrows move, Enter opens, Tab steps through
 *  the types, Escape closes. That also makes the dialog its own focus trap.
 */
export function SearchPalette({ onClose }: { onClose: () => void }) {
  const locale = useLocale();
  const router = useRouter();
  const overlay = useOverlay();
  const { user } = useSession();
  const { style } = useStyle();
  const { theme, toggleTheme } = useTheme();
  const { setOpen: setCustomizerOpen } = useCustomizer();

  const [raw, setRaw] = useState("");
  const [chip, setChip] = useState<SearchType>("all");
  const [selected, setSelected] = useState(0);
  const [recent, setRecent] = useState<string[]>(readRecent);
  const [answer, setAnswer] = useState<Answer>({ key: "", type: "all", data: null });
  const input = useRef<HTMLInputElement>(null);

  const { query, type, prefixed } = parseQuery(raw, chip);
  const remote = type === "all" || isServerType(type);
  const askable = foldText(query).length >= MIN_QUERY;
  const requestKey = remote && askable ? `${type}|${query}` : "";

  useEffect(() => {
    if (!requestKey) return;
    const controller = new AbortController();
    const handle = setTimeout(() => {
      const params = new URLSearchParams({ q: query });
      if (type !== "all") {
        params.set("type", type);
        params.set("limit", String(SINGLE));
      }
      fetch(`${API_BASE}/search/?${params.toString()}`, { signal: controller.signal })
        .then((response) =>
          response.ok ? response.json() : Promise.reject(new Error(String(response.status))),
        )
        .then((data: SearchResponse) => setAnswer({ key: requestKey, type, data }))
        .catch(() => {
          if (!controller.signal.aborted) setAnswer({ key: requestKey, type, data: null });
        });
    }, DEBOUNCE_MS);
    return () => {
      clearTimeout(handle);
      controller.abort();
    };
  }, [requestKey, query, type]);

  // The page behind must not scroll under the dialog.
  useEffect(() => {
    const before = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = before;
    };
  }, []);

  const settled = answer.key === requestKey;
  const pending = requestKey !== "" && !settled;
  const failed = requestKey !== "" && settled && answer.data === null;
  // While the next answer is on its way the last one of the same type
  // stays: an empty list between two keystrokes reads as "nothing found".
  const data = requestKey !== "" && answer.type === type ? answer.data : null;

  const sections = useMemo<Section[]>(() => {
    const go = (href: string, remember = true) => () => {
      if (remember && askable) rememberRecent(query);
      onClose();
      router.push(href as Route);
    };

    const pages: LocalItem[] = NAV.map((item) => ({
      id: `page-${item.href}`,
      label: t(locale, item.key),
      icon: item.iconKey,
      hint: item.href,
      run: go(item.href, false),
    }));
    if (user) {
      pages.push({
        id: "page-settings",
        label: t(locale, "settings.title"),
        icon: "system.settings",
        hint: "/settings",
        run: go("/settings", false),
      });
    }
    if (user?.is_staff) {
      pages.push({
        id: "page-admin",
        label: t(locale, "admin.title"),
        icon: "system.settings",
        hint: "/admin",
        run: go("/admin", false),
      });
    }

    const commands: LocalItem[] = [];
    if (isDual(style as StyleId)) {
      commands.push({
        id: "cmd-theme",
        label: t(locale, theme === "dark" ? "theme.light" : "theme.dark"),
        icon: theme === "dark" ? "system.light" : "system.dark",
        hint: "",
        run: () => {
          onClose();
          toggleTheme();
        },
      });
    }
    if (CUSTOMIZER_ENABLED) {
      commands.push({
        id: "cmd-appearance",
        label: t(locale, "settings.openCustomizer"),
        icon: "system.palette",
        hint: "",
        run: () => {
          onClose();
          setCustomizerOpen(true);
        },
      });
    }
    commands.push({
      id: "cmd-copy",
      label: t(locale, "kit.paletteCopyUrl"),
      icon: "action.copy",
      hint: "",
      run: () => {
        onClose();
        void navigator.clipboard
          .writeText(window.location.href)
          .then(() => overlay.toast(t(locale, "problem.copied")))
          .catch(() => overlay.toast(t(locale, "problem.copyFailed")));
      },
    });

    const local = (key: SearchType, items: LocalItem[], cap: number): Section | null => {
      const found = filterLocal(items, query);
      if (found.length === 0) return null;
      return {
        key,
        label: t(locale, `search.type.${key}`),
        more:
          type === "all" && found.length > cap
            ? { label: t(locale, "search.type.all"), run: () => pick(key) }
            : undefined,
        options: found.slice(0, cap).map((item) => ({
          id: item.id,
          icon: item.icon,
          title: item.label,
          subtitle: item.hint,
          meta: "",
          marked: true,
          run: item.run,
        })),
      };
    };

    const out: Section[] = [];

    if (!query && type === "all") {
      if (recent.length > 0) {
        out.push({
          key: "recent",
          label: t(locale, "search.recent"),
          more: {
            label: t(locale, "common.clear"),
            run: () => {
              clearRecent();
              setRecent([]);
            },
          },
          options: recent.map((item, index) => ({
            id: `recent-${index}`,
            icon: "action.search",
            title: item,
            subtitle: "",
            meta: "",
            marked: false,
            run: () => {
              setRaw(item);
              setSelected(0);
            },
          })),
        });
      }
      out.push({
        key: "quick",
        label: t(locale, "search.quick"),
        options: [...pages.slice(0, 5), ...commands].map((item) => ({
          id: item.id,
          icon: item.icon,
          title: item.label,
          subtitle: item.hint,
          meta: "",
          marked: false,
          run: item.run,
        })),
      });
      return out;
    }

    if (remote && data) {
      for (const group of data.groups) {
        const label = t(locale, `search.type.${group.type}`);
        const counted = `${label} · ${group.count}`;
        out.push({
          key: group.type,
          label: group.fuzzy ? fill(t(locale, "search.fuzzy"), { label }) : counted,
          more:
            type === "all" && group.count > group.results.length
              ? { label: t(locale, "search.type.all"), run: () => pick(group.type) }
              : undefined,
          options: group.results.map((hit) => {
            const text = describeHit(hit, locale);
            return {
              id: `hit-${hit.type}-${hit.kind}-${hit.key}`,
              icon: hitIcon(hit),
              title: text.title,
              subtitle: text.subtitle,
              meta: text.meta,
              marked: !group.fuzzy,
              run: go(hitHref(hit)),
            };
          }),
        });
      }
    }
    if (type === "all" || type === "page") {
      const section = local("page", pages, type === "all" ? MIXED : pages.length);
      if (section) out.push(section);
    }
    if (type === "all" || type === "cmd") {
      const section = local("cmd", commands, commands.length);
      if (section) out.push(section);
    }
    if (remote && data && data.total > 0) {
      out.push({
        key: "all-results",
        label: "",
        options: [
          {
            id: "see-all",
            icon: "action.search",
            title: fill(t(locale, "search.seeAll"), { q: query }),
            subtitle: fill(t(locale, "search.count"), { n: data.total }),
            meta: "",
            marked: false,
            run: go(searchHref(query, type)),
          },
        ],
      });
    }
    return out;

    function pick(next: SearchType) {
      setRaw(query);
      setChip(next);
      setSelected(0);
    }
  }, [
    askable,
    data,
    locale,
    onClose,
    overlay,
    query,
    recent,
    remote,
    router,
    setCustomizerOpen,
    style,
    theme,
    toggleTheme,
    type,
    user,
  ]);

  const options = sections.flatMap((section) => section.options);
  const index = Math.min(selected, Math.max(0, options.length - 1));
  const current = options[index];

  useEffect(() => {
    if (current) document.getElementById(current.id)?.scrollIntoView({ block: "nearest" });
  }, [current]);

  function choose(next: SearchType) {
    // A typed prefix would win over the chip that was just pressed.
    setRaw(query);
    setChip(next);
    setSelected(0);
    input.current?.focus();
  }

  function onKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    switch (event.key) {
      case "ArrowDown":
        event.preventDefault();
        setSelected(Math.min(options.length - 1, index + 1));
        break;
      case "ArrowUp":
        event.preventDefault();
        setSelected(Math.max(0, index - 1));
        break;
      case "Home":
        if (options.length > 0 && event.ctrlKey) {
          event.preventDefault();
          setSelected(0);
        }
        break;
      case "End":
        if (options.length > 0 && event.ctrlKey) {
          event.preventDefault();
          setSelected(options.length - 1);
        }
        break;
      case "Enter":
        event.preventDefault();
        if (current) current.run();
        else if (remote && askable) {
          rememberRecent(query);
          onClose();
          router.push(searchHref(query, type) as Route);
        }
        break;
      case "Tab": {
        event.preventDefault();
        const at = SEARCH_TYPES.indexOf(type);
        const step = event.shiftKey ? SEARCH_TYPES.length - 1 : 1;
        choose(SEARCH_TYPES[(at + step) % SEARCH_TYPES.length]);
        break;
      }
      case "Escape":
        event.preventDefault();
        onClose();
        break;
    }
  }

  const typeLabel = t(locale, `search.type.${type}`);
  const empty = options.length === 0;
  const needMore = remote && type !== "all" && !askable;
  let status = "";
  if (pending) status = t(locale, "search.loading");
  else if (failed) status = t(locale, "search.failed");
  else if (needMore) status = t(locale, "search.minChars");
  else if (empty) status = fill(t(locale, "search.empty"), { q: query });
  else if (data) status = fill(t(locale, "search.count"), { n: data.total });

  return createPortal(
    <div
      className="fixed inset-0 z-[90] flex items-start justify-center bg-[color-mix(in_srgb,var(--rw-text)_32%,transparent)] sm:px-4 sm:pt-[10vh]"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-label={t(locale, "search.title")}
        data-search-palette=""
        className="flex h-dvh w-full flex-col overflow-hidden rw-surface rw-shadow sm:h-auto sm:max-h-[min(40rem,80vh)] sm:max-w-2xl sm:rounded-xl sm:border rw-line"
      >
        <div className="flex shrink-0 items-center gap-2 border-b rw-line pr-1 pl-3">
          <Icon name="action.search" className="pointer-events-none size-5 shrink-0 rw-faint" />
          {prefixed && (
            <span className="shrink-0 rounded-md rw-accent-soft px-2 py-0.5 text-theme-xs font-semibold whitespace-nowrap">
              {typeLabel}
            </span>
          )}
          <input
            ref={input}
            autoFocus
            type="text"
            role="combobox"
            aria-expanded="true"
            aria-controls="rw-search-list"
            aria-autocomplete="list"
            aria-activedescendant={current?.id}
            aria-label={t(locale, "search.title")}
            autoComplete="off"
            autoCapitalize="none"
            spellCheck={false}
            enterKeyHint="search"
            value={raw}
            placeholder={t(locale, "search.placeholder")}
            onChange={(event) => {
              setRaw(event.target.value);
              setSelected(0);
            }}
            onKeyDown={onKeyDown}
            className="h-14 min-w-0 flex-1 bg-transparent text-theme-base rw-strong outline-none"
          />
          <button
            type="button"
            tabIndex={-1}
            onClick={onClose}
            aria-label={t(locale, "nav.close")}
            className="flex size-11 shrink-0 items-center justify-center rw-radius-sm rw-dim-2 rw-hover-bg rw-focus-ring"
          >
            <kbd className={`hidden sm:block ${KBD}`}>{KEY.esc}</kbd>
            <Icon name="nav.close" className="size-5 sm:hidden" />
          </button>
        </div>

        <div
          role="group"
          aria-label={t(locale, "search.typeLabel")}
          className="flex shrink-0 gap-2 overflow-x-auto border-b rw-line px-3 py-2"
        >
          {SEARCH_TYPES.map((item) => (
            <button
              key={item}
              type="button"
              tabIndex={-1}
              aria-pressed={item === type}
              onClick={() => choose(item)}
              className={`${CHIP} ${
                item === type ? "rw-accent-bg font-semibold" : "rw-divider rw-dim-2 rw-hover-bg"
              }`}
            >
              {t(locale, `search.type.${item}`)}
              {prefixOf(item) && (
                <span aria-hidden="true" className="font-mono text-theme-xs opacity-70">
                  {prefixOf(item)}
                </span>
              )}
            </button>
          ))}
        </div>

        <div
          id="rw-search-list"
          role="listbox"
          aria-label={t(locale, "search.results")}
          aria-busy={pending}
          className="min-h-0 flex-1 overflow-y-auto p-2"
        >
          {sections.map((section) => (
            <ul key={section.key} role="group" aria-label={section.label || undefined}>
              {section.label && (
                <li role="presentation" className="flex min-h-9 items-center justify-between gap-3 px-2 pt-2">
                  <span className="text-theme-xs font-semibold tracking-wide rw-faint uppercase">
                    {section.label}
                  </span>
                  {section.more && (
                    <button
                      type="button"
                      tabIndex={-1}
                      onClick={section.more.run}
                      className="rw-radius-sm px-2 py-1 text-theme-xs font-semibold rw-accent-ink rw-hover-bg"
                    >
                      {section.more.label}
                    </button>
                  )}
                </li>
              )}
              {section.options.map((option) => {
                const active = option === current;
                return (
                  // Keyboard users reach an option through the input
                  // (`aria-activedescendant`); the click is the pointer's path.
                  <li
                    key={option.id}
                    id={option.id}
                    role="option"
                    aria-selected={active}
                    tabIndex={-1}
                    // Focus stays in the input when the pointer is used.
                    onMouseDown={(event) => event.preventDefault()}
                    onClick={option.run}
                    onKeyDown={(event) => {
                      // Reached only when assistive technology moves real
                      // focus onto the option instead of following the input.
                      if (event.key === "Enter" || event.key === " ") {
                        event.preventDefault();
                        option.run();
                      }
                    }}
                    onMouseMove={() => {
                      if (!active) setSelected(options.indexOf(option));
                    }}
                    className={`flex min-h-11 cursor-pointer items-center gap-3 rw-radius-sm px-2 py-1.5 ${
                      active ? "bg-[color-mix(in_srgb,var(--rw-accent)_14%,transparent)]" : ""
                    }`}
                  >
                    <span className="flex size-8 shrink-0 items-center justify-center rw-radius-sm border rw-line rw-dim-2">
                      <Icon name={option.icon} className="size-4" />
                    </span>
                    <span className="min-w-0 flex-1">
                      <span className="block truncate text-theme-sm rw-strong">
                        {option.marked ? (
                          <Highlight text={option.title} query={query} />
                        ) : (
                          option.title
                        )}
                      </span>
                      {option.subtitle && (
                        <span className="block truncate text-theme-xs rw-dim">
                          {option.subtitle}
                        </span>
                      )}
                    </span>
                    {option.meta && (
                      <span className="shrink-0 font-mono text-theme-xs rw-dim">{option.meta}</span>
                    )}
                    {active && (
                      <kbd aria-hidden="true" className={`hidden shrink-0 sm:block ${KBD}`}>
                        {KEY.enter}
                      </kbd>
                    )}
                  </li>
                );
              })}
            </ul>
          ))}
          {empty && (
            <div className="px-4 py-10 text-center">
              <p className="text-theme-sm rw-strong">{status}</p>
              {!pending && !failed && !needMore && (
                <p className="mt-1 text-theme-xs rw-dim">{t(locale, "search.emptyHint")}</p>
              )}
            </div>
          )}
        </div>

        <div className="flex shrink-0 items-center gap-4 border-t rw-line px-3 py-2 text-theme-xs rw-dim">
          <span className="hidden items-center gap-1.5 sm:flex">
            <kbd className={KBD}>{KEY.up}</kbd>
            <kbd className={KBD}>{KEY.down}</kbd>
            {t(locale, "search.hintMove")}
          </span>
          <span className="hidden items-center gap-1.5 sm:flex">
            <kbd className={KBD}>{KEY.enter}</kbd>
            {t(locale, "search.hintOpen")}
          </span>
          <span className="hidden items-center gap-1.5 sm:flex">
            <kbd className={KBD}>{KEY.tab}</kbd>
            {t(locale, "search.hintType")}
          </span>
          <p role="status" aria-live="polite" className="ml-auto truncate">
            {empty ? "" : status}
          </p>
        </div>
      </div>
    </div>,
    document.body,
  );
}
