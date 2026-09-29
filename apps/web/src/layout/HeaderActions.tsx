"use client";

import { usePathname } from "next/navigation";

import { CustomizerTrigger } from "@/components/customizer/CustomizerTrigger";
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

  return (
    <div className="ml-auto flex min-w-0 items-center gap-2">
      {!auth && <SearchBox />}
      <div className="relative z-20 flex shrink-0 items-center gap-2">
        <HeaderStatus />
        <UpdatesBell />
        {!auth && CUSTOMIZER_ENABLED && <CustomizerTrigger />}
        {!auth && <ThemeToggle />}
        <LocaleSwitch />
        <UserMenu />
      </div>
    </div>
  );
}
