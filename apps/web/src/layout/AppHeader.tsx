"use client";

import { usePathname } from "next/navigation";

import { useSidebar } from "@/context/SidebarContext";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";
import { MenuIcon } from "@/icons";
import { NAV } from "./nav";
import ThemeToggle from "./ThemeToggle";
import UserMenu from "./UserMenu";

export default function AppHeader() {
  const { toggleMobileSidebar } = useSidebar();
  const pathname = usePathname();
  const locale = DEFAULT_LOCALE;
  const current = NAV.find((n) => pathname === n.href || pathname.startsWith(`${n.href}/`));

  return (
    <header
      className="sticky top-0 z-30 flex h-16 items-center gap-3 border-b border-gray-200
        bg-white/90 px-4 backdrop-blur md:px-6 dark:border-[#232936] dark:bg-[#141821]/90"
    >
      <button
        type="button"
        onClick={toggleMobileSidebar}
        aria-label={t(locale, "nav.menu")}
        className="text-gray-600 lg:hidden dark:text-gray-300"
      >
        <MenuIcon />
      </button>

      <span className="text-theme-sm font-medium text-gray-700 dark:text-gray-200">
        {current ? t(locale, current.key) : "RankWant"}
      </span>

      <div className="ml-auto flex items-center gap-2">
        <ThemeToggle />
        <UserMenu />
      </div>
    </header>
  );
}
