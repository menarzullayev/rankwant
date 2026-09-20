"use client";

import { useEffect, useRef, useState, useSyncExternalStore } from "react";
import { flushSync } from "react-dom";

import { useCustomizer, useCustomizerShortcut } from "@/context/CustomizerContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { Icon } from "@/components/ui/Icon";

import { A11yTab } from "./A11yTab";
import { AppearanceTab } from "./AppearanceTab";
import { ResetRow } from "./ResetRow";

const HIDDEN_KEY = "rw:customizer-hidden";

const hiddenListeners = new Set<() => void>();

function subscribeHidden(onChange: () => void) {
  hiddenListeners.add(onChange);
  return () => {
    hiddenListeners.delete(onChange);
  };
}

function readHidden() {
  try {
    return localStorage.getItem(HIDDEN_KEY) === "1";
  } catch {
    return false;
  }
}

function writeHidden(value: boolean) {
  try {
    localStorage.setItem(HIDDEN_KEY, value ? "1" : "0");
  } catch {
    // Private mode — session only.
  }
  for (const listener of hiddenListeners) listener();
}

/** Panel and floating trigger.
 *
 *  Not a modal (D29): no dim, no focus trap — the point is to SEE the page.
 *  Tabs are a real tablist. Appearance is four accordion groups so only one
 *  cluster sits in the tab order at a time.
 */
export function Customizer() {
  const { open, setOpen, toggle } = useCustomizer();
  const locale = useLocale();
  const [tab, setTab] = useState<"appearance" | "a11y">("appearance");
  const panel = useRef<HTMLDivElement>(null);
  const hidden = useSyncExternalStore(subscribeHidden, readHidden, () => false);
  const shortcut = useCustomizerShortcut();

  function hideFloating() {
    flushSync(() => {
      writeHidden(true);
      setOpen(false);
    });
    document.getElementById("rw-customizer-open")?.focus();
  }

  useEffect(() => {
    if (!open) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setOpen(false);
        document.getElementById("rw-customizer-open")?.focus();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, setOpen]);

  if (hidden && !open) {
    return (
      <button
        id="rw-customizer-open"
        type="button"
        onClick={() => writeHidden(false)}
        aria-label={t(locale, "customizer.show")}
        title={t(locale, "customizer.show")}
        className="fixed end-0 top-1/3 z-40 hidden size-10 items-center justify-center rw-radius-sm border rw-line rw-surface rw-dim-2 shadow-lg transition rw-hover-bg lg:flex"
      >
        <Icon name="system.palette" className="size-4" />
      </button>
    );
  }

  return (
    <>
      {!open && (
        <button
          id="rw-customizer-open"
          type="button"
          onClick={toggle}
          aria-expanded={false}
          aria-label={t(locale, "customizer.title")}
          data-tip={t(locale, "customizer.title")}
          data-tip-kind="kbd"
          data-tip-kbd={shortcut}
          className="fixed end-0 top-1/3 z-40 hidden flex-col items-center gap-1 rw-radius-sm border rw-line rw-surface px-1.5 py-3 text-theme-xs rw-dim-2 shadow-lg transition rw-hover-bg lg:flex"
        >
          <Icon name="system.palette" className="size-4" />
          <span className="[writing-mode:vertical-rl]">
            {t(locale, "customizer.short")}
          </span>
        </button>
      )}

      {open && (
        <div
          ref={panel}
          role="region"
          aria-label={t(locale, "customizer.title")}
          className="fixed inset-x-0 bottom-0 z-50 flex max-h-[55dvh] flex-col rounded-t-2xl border rw-line rw-surface shadow-2xl lg:inset-y-0 lg:end-0 lg:start-auto lg:max-h-none lg:w-[22rem] lg:rounded-none"
        >
          <header className="flex items-center justify-between gap-2 border-b rw-divide px-4 py-3">
            <h2 className="text-theme-lg font-semibold rw-strong" id="rw-cz-title">
              {t(locale, "customizer.title")}
            </h2>
            <div className="flex items-center gap-1">
              {!hidden && (
                <button
                  type="button"
                  onClick={hideFloating}
                  aria-label={t(locale, "customizer.hide")}
                  title={t(locale, "customizer.hide")}
                  className="hidden size-9 items-center justify-center rw-radius-sm rw-dim-2 transition rw-hover-bg lg:flex"
                >
                  <Icon name="action.eyeOff" className="size-4" />
                </button>
              )}
              <button
                type="button"
                onClick={() => setOpen(false)}
                aria-label={t(locale, "customizer.close")}
                className="flex size-9 items-center justify-center rw-radius-sm rw-dim-2 transition rw-hover-bg"
              >
                <Icon name="nav.close" className="size-4" />
              </button>
            </div>
          </header>

          <div
            role="tablist"
            aria-labelledby="rw-cz-title"
            className="flex gap-2 border-b rw-divide px-4 py-2"
          >
            {(["appearance", "a11y"] as const).map((value) => (
              <button
                key={value}
                type="button"
                role="tab"
                id={`rw-cz-tab-${value}`}
                aria-selected={tab === value}
                aria-controls={`rw-cz-panel-${value}`}
                tabIndex={tab === value ? 0 : -1}
                onClick={() => setTab(value)}
                className={`rw-radius-sm px-3 py-1.5 text-theme-sm font-medium transition ${
                  tab === value ? "rw-accent-soft" : "rw-dim-2 rw-hover-bg"
                }`}
              >
                {t(locale, `customizer.tab.${value}`)}
              </button>
            ))}
          </div>

          <div
            id={`rw-cz-panel-${tab}`}
            role="tabpanel"
            aria-labelledby={`rw-cz-tab-${tab}`}
            className="min-h-0 flex-1 space-y-6 overflow-y-auto px-4 py-4"
          >
            {tab === "appearance" ? <AppearanceTab /> : <A11yTab />}
          </div>

          <footer className="border-t rw-divide px-4 py-3">
            <ResetRow />
          </footer>
        </div>
      )}
    </>
  );
}
