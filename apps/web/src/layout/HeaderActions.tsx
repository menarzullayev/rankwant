"use client";

import { usePathname } from "next/navigation";

import { CustomizerTrigger } from "@/components/customizer/CustomizerTrigger";
import UpdatesBell from "@/components/UpdatesBell";
import { CUSTOMIZER_ENABLED } from "@/lib/theme/flag";

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
 *  Mavzu tugmasi bu yerda YO'Q (D3): palitra — CustomizerTrigger.
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
        <LocaleSwitch />
        <UserMenu />
      </div>
    </div>
  );
}
