"use client";

import type { MouseEvent } from "react";

import { useCustomizer } from "@/context/CustomizerContext";
import { useStyle } from "@/context/StyleContext";
import { useTheme } from "@/context/ThemeContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { isDual, type StyleId } from "@/layout/styles";
import { rememberPrefs } from "@/lib/prefs";
import {
  clampThemeToggle,
  themeToggleToEffect,
  type ThemeToggleId,
} from "@/lib/theme/toggle";

const SUN = (
  <svg viewBox="0 0 24 24" aria-hidden="true">
    <circle cx="12" cy="12" r="3.6" />
    <path d="M12 3.2v2.1M12 18.7v2.1M3.2 12h2.1M18.7 12h2.1M5.7 5.7l1.5 1.5M16.8 16.8l1.5 1.5M18.3 5.7l-1.5 1.5M7.2 16.8l-1.5 1.5" />
  </svg>
);
const MOON = (
  <svg viewBox="0 0 24 24" aria-hidden="true">
    <path d="M15.1 4.2a7.6 7.6 0 1 0 4.7 12.2 6.2 6.2 0 0 1-4.7-12.2z" />
  </svg>
);

function face(id: ThemeToggleId) {
  switch (id) {
    case "aylanma":
      return (
        <span className="tg-orb-inner">
          <span className="face sun">{SUN}</span>
          <span className="face moon">{MOON}</span>
        </span>
      );
    case "relss":
      return (
        <>
          <span className="sky" aria-hidden="true" />
          <span className="stars" aria-hidden="true" />
          <span className="thumb">
            <span className="ic sun">{SUN}</span>
            <span className="ic moon">{MOON}</span>
          </span>
        </>
      );
    case "ufq":
      return (
        <>
          <span className="wash" aria-hidden="true" />
          <span className="body-orb" aria-hidden="true" />
        </>
      );
    case "morph":
      return (
        <>
          <span className="core" aria-hidden="true" />
          <span className="cut" aria-hidden="true" />
          <span className="rays" aria-hidden="true">
            {Array.from({ length: 8 }, (_, i) => (
              <i key={i} style={{ ["--a" as string]: i }} />
            ))}
          </span>
        </>
      );
    case "osmon":
      return (
        <>
          <span className="field" aria-hidden="true" />
          <span className="dots" aria-hidden="true" />
          <span className="orb" aria-hidden="true" />
        </>
      );
    default:
      return (
        <span className="swap">
          {SUN}
          {MOON}
        </span>
      );
  }
}

function classFor(id: ThemeToggleId): string {
  if (id === "aylanma") return "tg tg-orb";
  if (id === "relss") return "tg tg-track";
  if (id === "ufq") return "tg tg-horizon";
  if (id === "morph") return "tg tg-morph";
  if (id === "osmon") return "tg tg-sky";
  return "tg tg-icon";
}

/** Header va sozlagichdagi yorug‘/qorong‘i tugma. Uslub — `appearance.themeToggle`. */
export function ThemeToggle({
  variant,
  className = "",
}: {
  /** Sozlagichda oldindan ko‘rish — shu uslubni tanlab keyin almashtiradi. */
  variant?: ThemeToggleId;
  className?: string;
}) {
  const locale = useLocale();
  const { theme, toggleTheme } = useTheme();
  const { style } = useStyle();
  const { appearance, setAppearance } = useCustomizer();
  const id = clampThemeToggle(variant ?? appearance.themeToggle);
  if (!variant && !isDual(style as StyleId)) return null;

  const next = theme === "dark" ? "light" : "dark";
  const label = t(locale, next === "dark" ? "theme.dark" : "theme.light");

  function onClick(event: MouseEvent<HTMLButtonElement>) {
    if (variant && variant !== appearance.themeToggle) {
      setAppearance({ themeToggle: variant });
      rememberPrefs({ effect: themeToggleToEffect(variant) });
    }
    // D6: bir muhitli uslubda mavzu majburiy — almashirish buzuq holat.
    if (!isDual(style as StyleId)) return;
    toggleTheme({ x: event.clientX, y: event.clientY });
  }

  return (
    <button
      type="button"
      className={`${classFor(id)} ${className}`.trim()}
      aria-label={label}
      aria-pressed={theme === "dark"}
      onClick={onClick}
    >
      {face(id)}
    </button>
  );
}
