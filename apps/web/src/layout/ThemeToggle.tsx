"use client";

import { useStyle } from "@/context/StyleContext";
import { useTheme } from "@/context/ThemeContext";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";
import { MoonIcon, SunIcon } from "@/icons";
import { isDual } from "./styles";

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();
  const { style } = useStyle();

  // Terminal, gil, aurora kabi uslublar bitta muhitga chizilgan —
  // ularda tugma hech nimani o'zgartirmasdi.
  if (!isDual(style)) return null;

  return (
    <button
      type="button"
      onClick={toggleTheme}
      aria-label={t(
        DEFAULT_LOCALE,
        theme === "dark" ? "theme.light" : "theme.dark",
      )}
      className="flex size-10 items-center justify-center rw-radius-sm border rw-line rw-dim-2 transition rw-hover-bg"
    >
      {theme === "dark" ? <SunIcon /> : <MoonIcon />}
    </button>
  );
}
