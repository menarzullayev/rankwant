"use client";

import { IntentLink } from "@/components/ui/IntentLink";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import { useSidebar } from "@/context/SidebarContext";
import { useUpdates } from "@/context/UpdatesContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { Icon } from "@/components/ui/Icon";
import HeaderStatus from "./HeaderStatus";
import SearchBox from "./SearchBox";
import { LocaleSwitch } from "./LocaleSwitch";
import UpdatesBell from "@/components/UpdatesBell";
import { CustomizerTrigger } from "@/components/customizer/CustomizerTrigger";
import { CUSTOMIZER_ENABLED } from "@/lib/theme/flag";
import UserMenu from "./UserMenu";
import { NAV_GROUPS } from "./nav";
import BrandMark from "./BrandMark";
import { topnavShapeClass, type NavShape } from "./nav-config";

/** Yuqori navigatsiya — `navMode: "topnav"` tanlanganda ishlaydi (D46).
 *
 *  Farqi sidenav'dan: bandlar bitta qatorga sig'maydi (21 ta), shuning
 *  uchun ular GURUH bo'yicha yig'iladi va har guruh ochiladigan ro'yxat
 *  (dropdown) beradi. kep.uz da ham shunday: 5 ta asosiy band + 7 ta
 *  `aria-haspopup` trigger.
 *
 *  Shakl (`default | slim | stacked`) balandlik VA burchakni belgilaydi —
 *  `nav-config.ts` dagi `topnavShapeClass` orqali, ya'ni qoida bitta joyda.
 *
 *  Mobil (`lg` dan kichik): burger tugmasi. U mavjud `SidebarContext`
 *  ning `isMobileOpen` ini ishlatadi — ya'ni ekran ostidagi qoraytma va
 *  `Esc` bilan yopish allaqachon ishlaydi, yangi holat kiritilmaydi.
 */
export default function AppTopNav({
  shape = "default",
}: {
  shape?: NavShape;
}) {
  const { isMobileOpen, openMobileSidebar, closeMobileSidebar } = useSidebar();
  const { count } = useUpdates();
  const pathname = usePathname();
  const locale = useLocale();
  // Faqat bitta guruh ochiq tursin — aks holda ikkinchisini ochganda
  // birinchisi ochiq qolib, ekran band bo'ladi.
  const [openGroup, setOpenGroup] = useState<string | null>(null);
  const barRef = useRef<HTMLDivElement>(null);
  // Kirish sahifasida qidiruv va sozlagich keraksiz — `AppHeader` dagi
  // sabab bilan bir xil.
  const auth = pathname === "/login";
  // Klaviatura navigatsiyasi uchun guruh tugmalari. `menubar` naqshida
  // strelkalar fokusni qo'lda ko'chiradi, ya'ni har tugma qaysi
  // yo'nalishda turganini bilish kerak.
  const groupRefs = useRef<(HTMLButtonElement | null)[]>([]);

  /** Guruhlar orasida fokusni ko'chiradi (`Home`/`End` bilan chetga). */
  const focusGroup = (index: number) => {
    const total = NAV_GROUPS.length;
    const next = ((index % total) + total) % total;
    groupRefs.current[next]?.focus();
    return next;
  };

  /** Guruh tugmasidagi strelkalar — ARIA `menubar` naqshи. */
  const onGroupKey = (event: React.KeyboardEvent, index: number) => {
    switch (event.key) {
      case "ArrowRight":
        event.preventDefault();
        focusGroup(index + 1);
        break;
      case "ArrowLeft":
        event.preventDefault();
        focusGroup(index - 1);
        break;
      case "Home":
        event.preventDefault();
        focusGroup(0);
        break;
      case "End":
        event.preventDefault();
        focusGroup(NAV_GROUPS.length - 1);
        break;
      case "ArrowDown":
      case "Enter":
      case " ":
        // Ochib, birinchi bandga fokus beradi — aks holda odam yana
        // `Tab` bosishi kerak bo'lardi.
        event.preventDefault();
        setOpenGroup(NAV_GROUPS[index].key);
        requestAnimationFrame(() => {
          // ⚠️ `getElementById` SHART, `querySelector` emas: guruh kaliti
          // `navGroup.lab` ko'rinishida, ya'ni ichida NUQTA bor — u CSS
          // selektorda klass belgisi bo'lib, element topilmay qolardi
          // (o'lchandi: menyu ochilardi, lekin fokus ichiga o'tmasdi).
          const menu = document.getElementById(
            `rw-topnav-menu-${NAV_GROUPS[index].key}`,
          );
          menu?.querySelector<HTMLAnchorElement>("a")?.focus();
        });
        break;
      case "Escape":
        setOpenGroup(null);
        break;
      default:
        break;
    }
  };

  /** Ochiq ro'yxat ichidagi strelkalar. */
  const onMenuKey = (event: React.KeyboardEvent, groupIndex: number) => {
    const items = [
      ...(event.currentTarget as HTMLElement).querySelectorAll<HTMLAnchorElement>("a"),
    ];
    const current = items.indexOf(document.activeElement as HTMLAnchorElement);
    switch (event.key) {
      case "ArrowDown":
        event.preventDefault();
        items[(current + 1) % items.length]?.focus();
        break;
      case "ArrowUp":
        event.preventDefault();
        items[(current - 1 + items.length) % items.length]?.focus();
        break;
      case "Home":
        event.preventDefault();
        items[0]?.focus();
        break;
      case "End":
        event.preventDefault();
        items[items.length - 1]?.focus();
        break;
      case "ArrowRight":
      case "ArrowLeft": {
        // `menubar` naqshi: qo'shni guruhga o'tib, uning ro'yxatini ochadi.
        event.preventDefault();
        const dir = event.key === "ArrowRight" ? 1 : -1;
        const next =
          (((groupIndex + dir) % NAV_GROUPS.length) + NAV_GROUPS.length) %
          NAV_GROUPS.length;
        setOpenGroup(NAV_GROUPS[next].key);
        // Fokus ham darhol yangi menyu ichiga o'tadi — `menubar` naqshida
        // strelka "keyingi menyu" degani, "keyingi tugma" emas.
        requestAnimationFrame(() => {
          const menu = document.getElementById(
            `rw-topnav-menu-${NAV_GROUPS[next].key}`,
          );
          const first = menu?.querySelector<HTMLAnchorElement>("a");
          if (first) first.focus();
          else groupRefs.current[next]?.focus();
        });
        break;
      }
      case "Escape":
        // Fokus guruh tugmasiga qaytadi — ARIA talabi. `stopPropagation`
        // sababi yuqoridagi `onKey` bilan bir xil: `Customizer` panelni
        // yopib qo'ymasin.
        event.preventDefault();
        event.stopPropagation();
        setOpenGroup(null);
        groupRefs.current[groupIndex]?.focus();
        break;
      default:
        break;
    }
  };

  // Sahifa almashganda ochiq ro'yxat yopilsin. Effekt EMAS — loyihada
  // effekt ichida `setState` taqiqlangan (kaskad render). React'ning
  // rasmiy usuli: render vaqtida oldingi qiymat bilan solishtirish.
  const [lastPath, setLastPath] = useState(pathname);
  if (pathname !== lastPath) {
    setLastPath(pathname);
    setOpenGroup(null);
  }

  // Tashqariga bosilganda yopish. `pointerdown` — `click` dan oldin keladi,
  // shuning uchun link bosilishi bilan ro'yxat yopilishi to'qnashmaydi.
  useEffect(() => {
    if (!openGroup) return;
    const onDown = (event: PointerEvent) => {
      if (!barRef.current?.contains(event.target as Node)) setOpenGroup(null);
    };
    const onKey = (event: KeyboardEvent) => {
      if (event.key !== "Escape") return;
      // ⚠️ `stopPropagation` SHART: `Customizer` ham `Escape` ni global
      // tinglaydi va panelni yopadi. O'lchandi — menyuni yopish niyatida
      // bosilgan `Escape` butun sozlagichni ham yopib qo'yardi.
      // `document` darajasida to'xtatilsa, hodisa `window` ga yetmaydi.
      event.stopPropagation();
      setOpenGroup(null);
    };
    document.addEventListener("pointerdown", onDown);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("pointerdown", onDown);
      document.removeEventListener("keydown", onKey);
    };
  }, [openGroup]);

  return (
    <header
      ref={barRef}
      className={`sticky top-0 z-40 w-full border-b rw-divider rw-chrome ${topnavShapeClass(shape)}`}
    >
      <div className="rw-content mx-auto flex h-full w-full items-center gap-3 px-4">
        {/* Burger — faqat tor ekranda. `lg:hidden` bilan emas, shart bilan:
            topnav rejimida sidenav umuman chizilmaydi, demak uning
            burgeri ham yo'q — bu tugma yagona kirish nuqtasi. */}
        <button
          type="button"
          onClick={isMobileOpen ? closeMobileSidebar : openMobileSidebar}
          aria-expanded={isMobileOpen}
          aria-controls="rw-topnav-drawer"
          aria-label={t(locale, "nav.menu")}
          className="flex size-9 shrink-0 items-center justify-center rw-radius-sm rw-dim-2 transition rw-hover-bg lg:hidden"
        >
          {isMobileOpen ? <Icon name="nav.close" /> : <Icon name="nav.menu" />}
        </button>

        {/* Brend — bitta manba (qaror 22): AppSidebar'dagi kabi bu
            yerda ham `BrandMark`; wordmark nusxasi olib tashlandi. */}
        <BrandMark variant="full" />

        {/* Guruhlar — faqat keng ekranda. */}
        <nav
          role="menubar"
          aria-label={t(locale, "nav.main")}
          className="hidden min-w-0 flex-1 items-center gap-1 lg:flex"
        >
          {NAV_GROUPS.map((group, groupIndex) => {
            const open = openGroup === group.key;
            // Guruh ichida joriy sahifa bo'lsa, guruh sarlavhasi ham
            // faol ko'rinadi — aks holda odam qayerdaligini ko'rmaydi.
            const hasActive = group.items.some(
              (item) =>
                pathname === item.href || pathname.startsWith(`${item.href}/`),
            );
            return (
              <div key={group.key} className="relative">
                <button
                  ref={(el) => {
                    groupRefs.current[groupIndex] = el;
                  }}
                  type="button"
                  role="menuitem"
                  onClick={() => setOpenGroup(open ? null : group.key)}
                  onKeyDown={(event) => onGroupKey(event, groupIndex)}
                  aria-expanded={open}
                  aria-haspopup="true"
                  className={`menu-item ${hasActive ? "menu-item-active" : "menu-item-inactive"}`}
                >
                  <span className="truncate">{t(locale, group.key)}</span>
                  <Icon name="nav.expandDown" className={`size-4 shrink-0 transition-transform ${open ? "rotate-180" : ""}`} />
                </button>

                {open && (
                  <ul
                    id={`rw-topnav-menu-${group.key}`}
                    onKeyDown={(event) => onMenuKey(event, groupIndex)}
                    className="absolute start-0 top-full z-50 mt-1 min-w-[220px] rw-radius rw-surface rw-shadow rw-line overflow-hidden border p-1"
                    role="menu"
                  >
                    {group.items.map(({ href, key, iconKey }) => {
                      const active =
                        pathname === href || pathname.startsWith(`${href}/`);
                      const unread = href === "/updates" ? count : 0;
                      return (
                        <li key={href} role="none">
                          <IntentLink
                            href={href}
                            role="menuitem"
                            aria-current={active ? "page" : undefined}
                            onClick={() => setOpenGroup(null)}
                            className={`menu-item ${active ? "menu-item-active" : "menu-item-inactive"}`}
                          >
                            <Icon
                              name={iconKey}
                              className={`size-5 shrink-0 ${active ? "menu-item-icon-active" : "menu-item-icon-inactive"}`}
                            />
                            <span className="truncate">{t(locale, key)}</span>
                            {unread > 0 && (
                              <span className="ml-auto flex h-5 min-w-5 items-center justify-center rounded-full px-1.5 text-[10px] font-semibold rw-accent-bg">
                                {unread > 99 ? "99+" : unread}
                              </span>
                            )}
                          </IntentLink>
                        </li>
                      );
                    })}
                  </ul>
                )}
              </div>
            );
          })}
        </nav>

        {/* O'ng guruh — `AppHeader` dagi tartib bilan bir xil.
            Topnav AppHeader O'RNINI oladi (ikkita header bo'lmasin),
            shu sababli qidiruv, qo'ng'iroq, til va hisob shu yerda. */}
        <div className="ml-auto flex min-w-0 items-center gap-2">
          {!auth && <SearchBox />}
          <HeaderStatus />
          <UpdatesBell />
          {!auth && CUSTOMIZER_ENABLED && <CustomizerTrigger />}
          <LocaleSwitch />
          <UserMenu />
        </div>
      </div>

      {/* Mobil ro'yxat — tor ekranda burger bilan ochiladi.
          Sidenav'ning drawer'i emas: u butunlay alohida, chunki topnav
          rejimida sidenav umuman chizilmaydi. */}
      {isMobileOpen && (
        <div
          id="rw-topnav-drawer"
          className="max-h-[70vh] overflow-y-auto border-t rw-divider rw-surface px-4 py-3 lg:hidden"
        >
          {NAV_GROUPS.map((group) => (
            <div key={group.key} className="mb-3">
              <p className="mb-1 px-3 text-theme-xs font-medium tracking-wider rw-dim-2 uppercase">
                {t(locale, group.key)}
              </p>
              <ul className="flex flex-col gap-1">
                {group.items.map(({ href, key, iconKey }) => {
                  const active =
                    pathname === href || pathname.startsWith(`${href}/`);
                  return (
                    <li key={href}>
                      <IntentLink
                        href={href}
                        aria-current={active ? "page" : undefined}
                        onClick={closeMobileSidebar}
                        className={`menu-item ${active ? "menu-item-active" : "menu-item-inactive"}`}
                      >
                        <Icon
                          name={iconKey}
                          className={`size-5 shrink-0 ${active ? "menu-item-icon-active" : "menu-item-icon-inactive"}`}
                        />
                        <span className="truncate">{t(locale, key)}</span>
                      </IntentLink>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </div>
      )}
    </header>
  );
}
