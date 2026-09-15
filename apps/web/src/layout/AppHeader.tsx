"use client";

import { usePathname } from "next/navigation";

import { useSidebar } from "@/context/SidebarContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { Icon } from "@/components/ui/Icon";
import { NAV } from "./nav";
import HeaderStatus from "./HeaderStatus";
import SearchBox from "./SearchBox";
import { LocaleSwitch } from "./LocaleSwitch";
import UpdatesBell from "@/components/UpdatesBell";
import { CustomizerTrigger } from "@/components/customizer/CustomizerTrigger";
import { CUSTOMIZER_ENABLED } from "@/lib/theme/flag";
import UserMenu from "./UserMenu";

export default function AppHeader() {
  const { toggleMobileSidebar } = useSidebar();
  const pathname = usePathname();
  const locale = useLocale();
  const current = NAV.find(
    (n) => pathname === n.href || pathname.startsWith(`${n.href}/`),
  );
  // Kirish/ro'yxat sahifalarida header soddalashadi: qidiruv ham, uslub
  // tanlash ham kirmagan odamga kerak emas — qidiradigan narsasi ham,
  // saqlaydigan sozlamasi ham yo'q. Til va mavzu qoladi, chunki ular
  // sahifani o'qish uchun kerak bo'lishi mumkin.
  //
  // Uch bo'lim (kirish/ro'yxat/tiklash) bitta manzilda (1-qaror), ya'ni
  // tekshiruv ham bitta: `usePathname()` `?tab=` ni ko'rsatmaydi va
  // ko'rsatishi ham shart emas — qidiruv baribir barcha bo'limlarda
  // keraksiz.
  const auth = pathname === "/login";

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-3 border-b rw-divider rw-chrome px-4 md:px-6">
      {/* 40x40 — header'dagi boshqa tugmalar bilan bir o'lchamda.
          Ilgari bosiladigan maydon faqat ikonka kattaligida edi: 20x20,
          ya'ni WCAG 2.5.8 (AA) talab qilgan 24x24 dan ham kichik.
          `-ml-2.5` ikonkani eski joyida qoldiradi — faqat nishon
          kattalashadi, ko'rinish o'zgarmaydi. */}
      <button
        type="button"
        onClick={toggleMobileSidebar}
        aria-label={t(locale, "nav.menu")}
        className="-ml-2.5 flex size-10 items-center justify-center rw-radius-sm rw-dim-2 transition rw-hover-bg lg:hidden"
      >
        <Icon name="nav.menu" />
      </button>

      <span className="hidden text-theme-sm font-medium rw-strong sm:inline">
        {current ? t(locale, current.key) : "RankWant"}
      </span>

      {/* `min-w-0` SHART: usiz flex bolalari o'z eng kichik kengligidan
          pastga tushmaydi va guruh sarlavhadan chiqib ketadi. O'lchandi —
          1280px da hujjat 1339px bo'lib, butun saytda gorizontal siljish
          paydo bo'lardi. */}
      <div className="ml-auto flex min-w-0 items-center gap-2">
        {!auth && <SearchBox />}
        <HeaderStatus />
        {/* O'zgarishlar belgisi — bildirishnomalar qo'ng'irog'idan keyin,
            lekin alohida ikonka bilan: ikkalasi bir xil ko'rinishda
            bo'lsa qaysi biri nima ekanini ajratib bo'lmasdi. */}
        <UpdatesBell />
        {/* Ko'rinish sozlagichi — mavzu va uslub tugmalari o'rniga
            (D3). Ikkitasi ham bitta panelga yig'ildi, chunki bir xil
            sozlamani ikki joydan boshqarish chalkashlik tug'diradi.
            Bu ikonka telefonda ham kerak: u yerda suzuvchi tugma yo'q
            (D32), ya'ni bu — asosiy kirish nuqtasi. */}
        {!auth && CUSTOMIZER_ENABLED && <CustomizerTrigger />}
        <LocaleSwitch />
        <UserMenu />
      </div>
    </header>
  );
}
