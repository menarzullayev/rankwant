"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { useSidebar } from "@/context/SidebarContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { CloseIcon } from "@/icons";
import { NAV_GROUPS } from "./nav";

export default function AppSidebar() {
  const {
    isExpanded,
    isMobileOpen,
    isHovered,
    setIsHovered,
    closeMobileSidebar,
  } = useSidebar();
  const pathname = usePathname();
  const locale = useLocale();

  // Yig'ilgan sidebar sichqoncha ustiga kelganda vaqtincha ochiladi —
  // shunda ikonka-rejimda ham band nomini o'qish mumkin.
  const wide = isExpanded || isHovered || isMobileOpen;

  return (
    <aside
      onMouseEnter={() => !isExpanded && setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={`fixed top-0 left-0 z-50 flex h-screen flex-col border-r rw-line rw-chrome
 px-4 transition-all duration-300
 ${wide ? "w-[260px]" : "w-[86px]"}
 ${isMobileOpen ? "translate-x-0" : "-translate-x-full"} lg:translate-x-0`}
    >
      <div className="flex h-16 items-center justify-between">
        <Link
          href="/"
          className="text-lg font-bold"
          onClick={closeMobileSidebar}
        >
          {wide ? (
            <>
              Rank<span className="rw-accent-ink">Want</span>
            </>
          ) : (
            <span className="rw-accent-ink">R</span>
          )}
        </Link>
        <button
          type="button"
          onClick={closeMobileSidebar}
          aria-label={t(locale, "nav.close")}
          className="rw-dim lg:hidden"
        >
          <CloseIcon />
        </button>
      </div>

      <nav className="no-scrollbar flex-1 overflow-y-auto pb-6">
        {NAV_GROUPS.map((group) => (
          <div key={group.key} className="mb-5">
            {/* Yorliq rangi `rw-dim-2`, `rw-faint` EMAS: bular navigatsiya
                tuzilmasi va o'qilishi shart. O'lchandi (haqiqiy piksellar,
                12 uslub × 2 tema): `rw-faint` bilan kontrast 1.59–4.43 va
                24 tadan BIRORTASI ham WCAG AA (4.5:1) dan o'tmagan;
                `rw-dim-2` bilan 3.40–9.50 va 21 tasi o'tadi. */}
            {wide ? (
              <p className="mb-2 px-3 text-theme-xs font-medium tracking-wider rw-dim-2 uppercase">
                {t(locale, group.key)}
              </p>
            ) : (
              <div className="mx-3 mb-2 border-t rw-line" />
            )}
            <ul className="flex flex-col gap-1">
              {group.items.map(({ href, key, Icon }) => {
                const active =
                  pathname === href || pathname.startsWith(`${href}/`);
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
                          active
                            ? "menu-item-icon-active"
                            : "menu-item-icon-inactive"
                        }`}
                      />
                      {wide && (
                        <span className="truncate">{t(locale, key)}</span>
                      )}
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
