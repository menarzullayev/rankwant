"use client";

import { useEffect, useRef } from "react";

import { IntentLink } from "@/components/ui/IntentLink";
import { usePathname } from "next/navigation";

import { useSidebar } from "@/context/SidebarContext";
import { useUpdates } from "@/context/UpdatesContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { Icon } from "@/components/ui/Icon";
import { NAV_GROUPS } from "./nav";

export default function AppSidebar() {
  const {
    isExpanded,
    isMobileOpen,
    isHovered,
    setIsHovered,
    closeMobileSidebar,
    toggleSidebar,
  } = useSidebar();
  const { count } = useUpdates();
  const pathname = usePathname();
  const locale = useLocale();

  // Yig'ilgan sidebar sichqoncha ustiga kelganda vaqtincha ochiladi —
  // shunda ikonka-rejimda ham band nomini o'qish mumkin.
  const wide = isExpanded || isHovered || isMobileOpen;

  // Fokus boshqaruvi — overlay panel ochilganda fokus ICHKARIGA kiradi,
  // yopilganda esa uni ochgan tugmaga qaytadi.
  //
  // O'lchandi (2026-09-18, jonli brauzer, 390x844x2): panel ochilganda
  // ham, yopilganda ham `document.activeElement` — `body` edi. Ya'ni
  // klaviatura foydalanuvchisi uchun panel ochilganini bildiruvchi hech
  // narsa yo'q edi va Tab bosganda fokus sahifa boshidan boshlanardi.
  //
  // Diqqat: ish stolida `isMobileOpen` doim `false` (resize effekti
  // majburan yopadi), ya'ni bu effekt u yerda hech narsa qilmaydi.
  const closeButtonRef = useRef<HTMLButtonElement>(null);
  const openerRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (isMobileOpen) {
      openerRef.current =
        document.activeElement instanceof HTMLElement
          ? document.activeElement
          : null;
      closeButtonRef.current?.focus();
      return;
    }
    const opener = openerRef.current;
    openerRef.current = null;
    // Sahifa almashgan bo'lsa tugma DOM'dan chiqqan bo'lishi mumkin —
    // u holda fokusni majburlamaymiz.
    if (opener?.isConnected) opener.focus();
  }, [isMobileOpen]);

  return (
    <aside
      id="rw-sidenav-drawer"
      // Tor ekranda panel — overlay: orqasida qoraytma bor, sahifa
      // siljimaydi, fokus ichkarida qoladi. Ya'ni u modal dialog.
      // Keng ekranda esa u oddiy yon panel, dialog emas — shuning uchun
      // rol SHARTGA bog'langan.
      role={isMobileOpen ? "dialog" : undefined}
      aria-modal={isMobileOpen || undefined}
      aria-label={t(locale, "nav.main")}
      onMouseEnter={() => !isExpanded && setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={`fixed top-0 left-0 z-50 flex h-screen flex-col border-r rw-divider rw-chrome
 transition-all duration-300
 ${wide ? "w-[260px] px-4" : "w-[86px] px-2"}
 ${isMobileOpen ? "translate-x-0" : "-translate-x-full"} lg:translate-x-0`}
    >
      {/* Brend endi header'da (qaror 22) — panel tepasida faqat
          yopish/yig'ish tugmalari qoladi, nav bir qatorga ko'tariladi. */}
      <div className="flex h-16 items-center justify-end gap-1">
        <button
          type="button"
          ref={closeButtonRef}
          onClick={closeMobileSidebar}
          aria-label={t(locale, "nav.close")}
          className="flex size-10 items-center justify-center rw-radius-sm rw-dim-2 transition rw-hover-bg lg:hidden"
        >
          <Icon name="nav.close" />
        </button>
        <button
          type="button"
          onClick={() => {
            if (isExpanded) setIsHovered(false);
            toggleSidebar();
          }}
          aria-expanded={isExpanded}
          aria-controls="rw-sidenav"
          aria-label={t(
            locale,
            isExpanded ? "nav.collapseSidebar" : "nav.expandSidebar",
          )}
          className="hidden size-10 shrink-0 items-center justify-center rw-radius-sm rw-dim-2 transition rw-hover-bg lg:flex"
        >
          <Icon
            name="nav.collapse"
            className={`size-5 transition-transform ${isExpanded ? "" : "rotate-180"}`}
          />
        </button>
      </div>

      <nav
        id="rw-sidenav"
        className="no-scrollbar flex-1 overflow-y-auto pb-6"
      >
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
              <div className="mx-3 mb-2 border-t rw-divider" />
            )}
            <ul className="flex flex-col gap-1">
              {group.items.map(({ href, key, iconKey }) => {
                const active =
                  pathname === href || pathname.startsWith(`${href}/`);
                // O'qilmagan o'zgarishlar chipi (qaror 6). Son
                // `UpdatesProvider` dan keladi — header belgisi ham o'sha
                // holatni ko'rsatadi, ya'ni ikki joyda ikki xil raqam
                // chiqmaydi.
                const unread = href === "/updates" ? count : 0;
                return (
                  <li key={href}>
                    <IntentLink
                      href={href}
                      onClick={closeMobileSidebar}
                      aria-current={active ? "page" : undefined}
                      title={t(locale, key)}
                      className={`menu-item group relative ${
                        active ? "menu-item-active" : "menu-item-inactive"
                      } ${wide ? "" : "justify-center"}`}
                    >
                      <Icon
                        name={iconKey}
                        className={`size-5 shrink-0 ${
                          active
                            ? "menu-item-icon-active"
                            : "menu-item-icon-inactive"
                        }`}
                      />
                      {wide && (
                        <span className="truncate">{t(locale, key)}</span>
                      )}
                      {unread > 0 &&
                        (wide ? (
                          <span className="ml-auto flex h-5 min-w-5 items-center justify-center rounded-full px-1.5 text-theme-2xs font-semibold rw-accent-bg">
                            {unread > 99 ? "99+" : unread}
                          </span>
                        ) : (
                          // Yig'ilgan panelda matn yo'q — nuqta yetarli.
                          <span className="absolute top-1.5 right-1.5 size-2 rounded-full rw-accent-bg" />
                        ))}
                    </IntentLink>
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
