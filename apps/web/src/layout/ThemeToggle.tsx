"use client";

import { useTheme } from "@/context/ThemeContext";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";
import { MoonIcon, SunIcon } from "@/icons";

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();
  return (
    <button
      type="button"
      onClick={toggleTheme}
      aria-label={t(DEFAULT_LOCALE, theme === "dark" ? "theme.light" : "theme.dark")}
      className="flex size-10 items-center justify-center rounded-lg border border-gray-200
        text-gray-600 transition hover:bg-gray-100
        dark:border-[#232936] dark:text-gray-300 dark:hover:bg-white/5"
    >
      {theme === "dark" ? <SunIcon /> : <MoonIcon />}
    </button>
  );
}
