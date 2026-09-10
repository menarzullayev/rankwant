"use client";

import { usePathname } from "next/navigation";

import { SidebarProvider, useSidebar } from "@/context/SidebarContext";
import { SessionProvider } from "@/context/SessionContext";
import { StyleProvider } from "@/context/StyleContext";
import { ThemeProvider } from "@/context/ThemeContext";
import AppFooter from "./AppFooter";
import AppHeader from "./AppHeader";
import { VerifyBanner } from "@/components/VerifyBanner";
import { WelcomeNotice } from "@/components/WelcomeNotice";
import AppSidebar from "./AppSidebar";
import { SkipLink } from "./SkipLink";

/** Bir ish uchun ochilgan sahifalar: yon panel ham, tasdiqlash banneri
 *  ham bu yerda ko'rinmaydi. O'lchandi — panel bilan birinchi maydonga
 *  yetish uchun 33 marta Tab bosish kerak edi va sahifada 44 ta
 *  fokuslanadigan element bor edi. Sarlavha qoladi: til tanlash va
 *  logotip kerak. */
const BARE = ["/login", "/register", "/parolni-tiklash", "/emailni-tasdiqlash"];

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
        {!bare && <VerifyBanner />}
        <main id="main" className="mx-auto max-w-[1400px] p-4 md:p-6">
          {children}
        </main>
        <AppFooter />
      </div>
    </div>
  );
}

export default function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <StyleProvider>
      <ThemeProvider>
        <SessionProvider>
          <SidebarProvider>
            <Shell>{children}</Shell>
          </SidebarProvider>
        </SessionProvider>
      </ThemeProvider>
    </StyleProvider>
  );
}
