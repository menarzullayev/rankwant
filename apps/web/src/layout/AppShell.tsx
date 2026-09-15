"use client";

import { usePathname } from "next/navigation";

import {
  CustomizerProvider,
  useCustomizer,
} from "@/context/CustomizerContext";
import { SidebarProvider, useSidebar } from "@/context/SidebarContext";
import { clampNavMode, clampNavShape } from "./nav-config";
import { PrefsSync } from "@/context/PrefsSync";
import { SessionProvider } from "@/context/SessionContext";
import { StyleProvider } from "@/context/StyleContext";
import { ThemeProvider } from "@/context/ThemeContext";
import { UpdatesProvider } from "@/context/UpdatesContext";
import type { AppearancePrefs, Me } from "@/lib/api";
import AppFooter from "./AppFooter";
import AppHeader from "./AppHeader";
import { VerifyBanner } from "@/components/VerifyBanner";
import { Customizer } from "@/components/customizer/Customizer";
import { CUSTOMIZER_ENABLED } from "@/lib/theme/flag";
import { GeoNudge } from "@/components/GeoNudge";
import { ContestInvite } from "@/components/ContestInvite";
import { WelcomeNotice } from "@/components/WelcomeNotice";
import AppSidebar from "./AppSidebar";
import AppTopNav from "./AppTopNav";
import { SkipLink } from "./SkipLink";

/** Bir ish uchun ochilgan sahifalar: yon panel ham, tasdiqlash banneri
 *  ham bu yerda ko'rinmaydi. O'lchandi — panel bilan birinchi maydonga
 *  yetish uchun 33 marta Tab bosish kerak edi va sahifada 44 ta
 *  fokuslanadigan element bor edi. Sarlavha qoladi: til tanlash va
 *  logotip kerak.
 *
 *  Login/register/reset — bitta manzil (`/login?tab=`), shuning uchun
 *  ro'yxatda ham bitta yozuv. `/register` va `/reset-password` shu
 *  manzilga 307 bilan yo'naltiradi.
 *
 *  Yo'naltiruvchi manzillar baribir shu ro'yxatda TURADI: `redirect()`
 *  klientga javob qaytarishdan oldin `usePathname()` hali ESKI qiymatni
 *  ko'rsatadi, ya'ni ro'yxatda bo'lmasa ikki bo'limli karta bir lahza
 *  yon panel va banner bilan chizilardi. */
const BARE = [
  "/login",
  "/register",
  "/reset-password",
  "/verify-email",
  // Ro'yxatdan o'tishning 2-qadami — oqimning davomi, ya'ni yon panel
  // ham, banner ham kerak emas: odam hali saytga kirmagan.
  "/onboarding",
];

/** Sahifalar SERVER komponenti bo'lib qoladi — bu yerga `children` sifatida
 * uzatiladi, ya'ni SSR (ADR-0003 dagi SEO sababi) buzilmaydi. */
function Shell({ children }: { children: React.ReactNode }) {
  const { isExpanded, isHovered, isMobileOpen, closeMobileSidebar } =
    useSidebar();
  // Navigatsiya rejimi — `AppearancePrefs` dan (D46). Sidenav'da yon panel
  // va uning chegarasi bo'ladi, topnav'da esa panel o'rnini `AppTopNav`
  // egallaydi va hech qanday chap chegara qolmaydi.
  const { appearance } = useCustomizer();
  const navMode = clampNavMode(appearance.navMode);
  const navShape = clampNavShape(appearance.navShape);
  const pathname = usePathname();
  const bare = BARE.includes(pathname);
  const wide = isExpanded || isHovered;
  const sidenav = navMode === "sidenav" && !bare;

  return (
    <div className="min-h-screen">
      {/* WCAG 2.4.1 — klaviatura foydalanuvchisi har sahifada yigirmata
          yon menyu havolasini bosib o'tmasin. Faqat fokusda ko'rinadi. */}
      <SkipLink />
      {sidenav && <AppSidebar />}
      {sidenav && isMobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-gray-900/50 lg:hidden"
          onClick={closeMobileSidebar}
        />
      )}
      <div
        className={
          sidenav
            ? `transition-all duration-300 ${wide ? "lg:ml-[260px]" : "lg:ml-[86px]"}`
            : ""
        }
      >
        {navMode === "topnav" && !bare ? (
          <AppTopNav shape={navShape} />
        ) : (
          <AppHeader />
        )}
        {!bare && <WelcomeNotice />}
        {!bare && <ContestInvite />}
        {!bare && <VerifyBanner />}
        {/* Kontekstli nudge (qaror 16): mavjud hisoblarda mamlakat bo'sh —
            banner shu bo'shliqni yumshoq yo'l bilan yopadi. Faqat kirgan
            va to'ldirmagan odamga ko'rinadi, yopilsa qaytmaydi. */}
        {!bare && <GeoNudge />}
        {/* Kenglik `--rw-content-width` dan (D48) — sozlagichda erkin
            tanlanadi. Tailwind sinfi qotib qolgan edi va katta monitorda
            odam o'qish uchun tor/keng qilib o'zgartira olmasdi. */}
        <main id="main" className="rw-content mx-auto p-4 md:p-6">
          {children}
        </main>
        <AppFooter />
      </div>
    </div>
  );
}

export default function AppShell({
  initialUser,
  siteAppearance,
  children,
}: {
  /** `RootLayout` SSR da o'qigan sessiya. Berilmasa mijoz o'zi so'raydi. */
  initialUser?: Me | null;
  /** Jamoa belgilagan standart ko'rinish (D37) — bo'sh bo'lsa kod
   *  standarti ishlatiladi (D26). */
  siteAppearance?: AppearancePrefs;
  children: React.ReactNode;
}) {
  return (
    <StyleProvider>
      <ThemeProvider>
        {/* ⚠️ TARTIB MUHIM: `CustomizerProvider` `useSession()` ni
            chaqiradi (shablon chegarasi kirgan/mehmonga bog'liq — D21),
            ya'ni u `SessionProvider` dan KEYIN turishi SHART. Ilgari
            teskari edi va butun daraxt yiqilardi: sahifa 200 qaytarardi
            (HTML qobig'i chiziladi), lekin React ishga tushmay, ekran
            bo'sh qolardi. Buni faqat brauzer ko'rsatdi — CI ham,
            `curl` ham ko'rmadi. */}
        <SessionProvider initialUser={initialUser}>
          <CustomizerProvider siteAppearance={siteAppearance}>
            <PrefsSync />
            <UpdatesProvider>
              <SidebarProvider>
                <Shell>{children}</Shell>
              </SidebarProvider>
            </UpdatesProvider>
            {/* Suzuvchi tugma va panel — `Shell` dan tashqarida, chunki
                ular sahifa tuzilishiga bog'liq emas va `bare` sahifalarda
                ham kerak bo'lishi mumkin. Bayroq o'chiq bo'lsa umuman
                chizilmaydi (D38). */}
            {CUSTOMIZER_ENABLED && <Customizer />}
          </CustomizerProvider>
        </SessionProvider>
      </ThemeProvider>
    </StyleProvider>
  );
}
