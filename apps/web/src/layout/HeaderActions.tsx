"use client";

import { usePathname } from "next/navigation";

import { CustomizerTrigger } from "@/components/customizer/CustomizerTrigger";
import { useSession } from "@/context/SessionContext";
import { UpdatesBell } from "@/features/updates";
import { CUSTOMIZER_ENABLED } from "@/lib/theme/flag";

import { ThemeToggle } from "@/components/theme/ThemeToggle";

import HeaderStatus from "./HeaderStatus";
import { LocaleSwitch } from "./LocaleSwitch";
import SearchBox from "./SearchBox";
import UserMenu from "./UserMenu";

/** O'ng klaster — yagona manba (H1).
 *
 *  AppHeader (sidenav) va AppTopNav (D46) chap tomonda farq qiladi:
 *  sidenav — burger + brend + bo'lim nomi; topnav — burger + brend +
 *  guruh menubar. O'ngdagi qidiruv, holat, qo'ng'iroq, sozlagich, til
 *  va hisob IKKALA rejimda bir xil tartibda turishi shart. Ilgari bu
 *  ro'yxat ikki faylda nusxa edi va izoh «bir xil bo'lsin» deb
 *  yozilgan — tartib baribir ajralib ketardi.
 *
 *  Mavzu tugmasi H6 da qaytdi: uslubni sozlagich tanlaydi (standart
 *  doira). StylePicker yo'q (D3 qoladi).
 *  Kirish sahifasida qidiruv va sozlagich yo'q: qidiradigan narsa ham,
 *  saqlaydigan sozlama ham yo'q. Til va hisob qoladi.
 */
export default function HeaderActions() {
  const pathname = usePathname();
  const auth = pathname === "/login";
  const { user } = useSession();

  return (
    <div className="ml-auto flex min-w-0 items-center gap-1 min-[360px]:gap-1.5 sm:gap-2">
      {!auth && <SearchBox />}
      <div className="relative z-20 flex shrink-0 items-center gap-1 min-[360px]:gap-1.5 sm:gap-2">
        <HeaderStatus />
        {/* Signed in, the cluster also carries the notification bell and the
            account button, and it does not shrink. Measured at 390 px
            (2026-10-05): it needed 541 px — the search button sat on top of
            the bell and the account button was 73 px off screen. Below `xl`
            these three give way; each has another door (the sidebar's
            "Changes", the floating appearance tab, the customizer). A guest's
            header is shorter and keeps them at every width. */}
        <div className={`items-center gap-1 min-[360px]:gap-1.5 sm:gap-2 ${user ? "hidden xl:flex" : "flex"}`}>
          <UpdatesBell />
          {/* A guest's header has to fit 320 px (owner decision). Measured
              2026-10-05 at 375 px it was 377 px wide in Uzbek and 385 px in
              English: the theme switch arrived after that decision was
              measured. The switch now starts at `md` — the mode is the first
              control of the appearance panel — and the panel button at
              390 px (with it the English header was 368 px at 360 px and
              the Tajik one 384 px at 375 px).
              `contents`, not `flex`: the wrappers must not become boxes of
              their own inside the row. */}
          <span className="hidden min-[390px]:contents">
            {!auth && CUSTOMIZER_ENABLED && <CustomizerTrigger />}
          </span>
          <span className="hidden md:contents">{!auth && <ThemeToggle />}</span>
        </div>
        <LocaleSwitch />
        <UserMenu />
      </div>
    </div>
  );
}
