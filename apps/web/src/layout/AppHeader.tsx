"use client";

import { usePathname } from "next/navigation";

import { useSidebar } from "@/context/SidebarContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { MenuIcon } from "@/icons";
import { NAV } from "./nav";
import HeaderStatus from "./HeaderStatus";
import SearchBox from "./SearchBox";
import StylePicker from "./StylePicker";
import { LocaleSwitch } from "./LocaleSwitch";
import ThemeToggle from "./ThemeToggle";
import UserMenu from "./UserMenu";

export default function AppHeader() {
  const { toggleMobileSidebar } = useSidebar();
  const pathname = usePathname();
  const locale = useLocale();
  const current = NAV.find(
    (n) => pathname === n.href || pathname.startsWith(`${n.href}/`),
  );

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-3 border-b rw-line rw-chrome px-4 md:px-6">
      <button
        type="button"
        onClick={toggleMobileSidebar}
        aria-label={t(locale, "nav.menu")}
        className="rw-dim-2 lg:hidden"
      >
        <MenuIcon />
      </button>

      <span className="hidden text-theme-sm font-medium rw-strong sm:inline">
        {current ? t(locale, current.key) : "RankWant"}
      </span>

      {/* `min-w-0` SHART: usiz flex bolalari o'z eng kichik kengligidan
          pastga tushmaydi va guruh sarlavhadan chiqib ketadi. O'lchandi —
          1280px da hujjat 1339px bo'lib, butun saytda gorizontal siljish
          paydo bo'lardi. */}
      <div className="ml-auto flex min-w-0 items-center gap-2">
        <SearchBox />
        <HeaderStatus />
        <StylePicker />
        <LocaleSwitch />
        <ThemeToggle />
        <UserMenu />
      </div>
    </header>
  );
}
