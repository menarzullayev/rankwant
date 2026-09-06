"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { useSidebar } from "@/context/SidebarContext";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";
import { CloseIcon } from "@/icons";
import { NAV_GROUPS } from "./nav";

export default function AppSidebar() {
  const { isExpanded, isMobileOpen, isHovered, setIsHovered, closeMobileSidebar } = useSidebar();
  const pathname = usePathname();
  const locale = DEFAULT_LOCALE;

  // Yig'ilgan sidebar sichqoncha ustiga kelganda vaqtincha ochiladi —
  // shunda ikonka-rejimda ham band nomini o'qish mumkin.
  const wide = isExpanded || isHovered || isMobileOpen;

  return (
    <aside
      onMouseEnter={() => !isExpanded && setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={`fixed top-0 left-0 z-50 flex h-screen flex-col border-r border-gray-200 bg-white
        px-4 transition-all duration-300 dark:border-[#232936] dark:bg-[#141821]
        ${wide ? "w-[260px]" : "w-[86px]"}
        ${isMobileOpen ? "translate-x-0" : "-translate-x-full"} lg:translate-x-0`}
    >
      <div className="flex h-16 items-center justify-between">
        <Link href="/" className="text-lg font-bold" onClick={closeMobileSidebar}>
          {wide ? (
            <>
              Rank<span className="text-brand-500">Want</span>
            </>
          ) : (
            <span className="text-brand-500">R</span>
          )}
        </Link>
        <button
          type="button"
          onClick={closeMobileSidebar}
          aria-label={t(locale, "nav.close")}
          className="text-gray-500 lg:hidden dark:text-gray-400"
        >
          <CloseIcon />
        </button>
      </div>

      <nav className="no-scrollbar flex-1 overflow-y-auto pb-6">
        {NAV_GROUPS.map((group) => (
          <div key={group.key} className="mb-5">
            {wide ? (
              <p className="mb-2 px-3 text-theme-xs font-medium tracking-wider text-gray-400 uppercase">
                {t(locale, group.key)}
              </p>
            ) : (
              <div className="mx-3 mb-2 border-t border-gray-100 dark:border-[#232936]" />
            )}
            <ul className="flex flex-col gap-1">
              {group.items.map(({ href, key, Icon }) => {
                const active = pathname === href || pathname.startsWith(`${href}/`);
                return (
                  <li key={href}>
                    <Link
                      href={href}
                      onClick={closeMobileSidebar}
                      aria-current={active ? "page" : undefined}
                      title={t(locale, key)}
                      className={`menu-item group ${
                        active ? "menu-item-active" : "menu-item-inactive"
                      } ${wide ? "" : "justify-center"}`}
                    >
                      <Icon
                        className={`size-5 shrink-0 ${
                          active ? "menu-item-icon-active" : "menu-item-icon-inactive"
                        }`}
                      />
                      {wide && <span className="truncate">{t(locale, key)}</span>}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </nav>
    </aside>
  );
}
