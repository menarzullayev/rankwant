"use client";

import { usePathname } from "next/navigation";

import { SidebarProvider, useSidebar } from "@/context/SidebarContext";
import { PrefsSync } from "@/context/PrefsSync";
import { SessionProvider } from "@/context/SessionContext";
import { StyleProvider } from "@/context/StyleContext";
import { ThemeProvider } from "@/context/ThemeContext";
import type { Me } from "@/lib/api";
import AppFooter from "./AppFooter";
import AppHeader from "./AppHeader";
import { VerifyBanner } from "@/components/VerifyBanner";
import { GeoNudge } from "@/components/GeoNudge";
import { ContestInvite } from "@/components/ContestInvite";
import { WelcomeNotice } from "@/components/WelcomeNotice";
import AppSidebar from "./AppSidebar";
import { SkipLink } from "./SkipLink";

/** Bir ish uchun ochilgan sahifalar: yon panel ham, tasdiqlash banneri
 *  ham bu yerda ko'rinmaydi. O'lchandi — panel bilan birinchi maydonga
 *  yetish uchun 33 marta Tab bosish kerak edi va sahifada 44 ta
 *  fokuslanadigan element bor edi. Sarlavha qoladi: til tanlash va
 *  logotip kerak.
 *
 *  Kirish/ro'yxat/tiklash — bitta manzil (`/kirish?tab=`), shuning uchun
 *  ro'yxatda ham bitta yozuv. Eski uchta manzil (`/login`, `/register`,
 *  `/parolni-tiklash`) bu yerga 307 bilan yo'naltiradi.
 *
 *  Eski manzillar baribir shu ro'yxatda TURADI: `redirect()` klientga
 *  javob qaytarishdan oldin `usePathname()` hali ESKI qiymatni
 *  ko'rsatadi, ya'ni ro'yxatda bo'lmasa ikki bo'limli karta bir lahza
 *  yon panel va banner bilan chizilardi. Bu allaqachon `/login` uchun
 *  amalda bo'lgan — endi izoh shuni aynan aytadi. */
const BARE = [
  "/kirish",
  "/login",
  "/register",
  "/parolni-tiklash",
  "/emailni-tasdiqlash",
  // Ro'yxatdan o'tishning 2-qadami — oqimning davomi, ya'ni yon panel
  // ham, banner ham kerak emas: odam hali saytga kirmagan.
  "/qoshimcha-malumot",
];

/** Sahifalar SERVER komponenti bo'lib qoladi — bu yerga `children` sifatida
 * uzatiladi, ya'ni SSR (ADR-0003 dagi SEO sababi) buzilmaydi. */
function Shell({ children }: { children: React.ReactNode }) {
  const { isExpanded, isHovered, isMobileOpen, closeMobileSidebar } =
    useSidebar();
  const pathname = usePathname();
  const bare = BARE.includes(pathname);
  const wide = isExpanded || isHovered;

  return (
    <div className="min-h-screen">
      {/* WCAG 2.4.1 — klaviatura foydalanuvchisi har sahifada yigirmata
          yon menyu havolasini bosib o'tmasin. Faqat fokusda ko'rinadi. */}
      <SkipLink />
      {!bare && <AppSidebar />}
      {!bare && isMobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-gray-900/50 lg:hidden"
          onClick={closeMobileSidebar}
        />
      )}
      <div
        className={
          bare
            ? ""
            : `transition-all duration-300 ${wide ? "lg:ml-[260px]" : "lg:ml-[86px]"}`
        }
      >
        <AppHeader />
        {!bare && <WelcomeNotice />}
        {!bare && <ContestInvite />}
        {!bare && <VerifyBanner />}
        {/* Kontekstli nudge (qaror 16): mavjud hisoblarda mamlakat bo'sh —
            banner shu bo'shliqni yumshoq yo'l bilan yopadi. Faqat kirgan
            va to'ldirmagan odamga ko'rinadi, yopilsa qaytmaydi. */}
        {!bare && <GeoNudge />}
        <main id="main" className="mx-auto max-w-[1400px] p-4 md:p-6">
          {children}
        </main>
        <AppFooter />
      </div>
    </div>
  );
}

export default function AppShell({
  initialUser,
  children,
}: {
  /** `RootLayout` SSR da o'qigan sessiya. Berilmasa mijoz o'zi so'raydi. */
  initialUser?: Me | null;
  children: React.ReactNode;
}) {
  return (
    <StyleProvider>
      <ThemeProvider>
        <SessionProvider initialUser={initialUser}>
          <PrefsSync />
          <SidebarProvider>
            <Shell>{children}</Shell>
          </SidebarProvider>
        </SessionProvider>
      </ThemeProvider>
    </StyleProvider>
  );
}
