"use client";

import { SidebarProvider, useSidebar } from "@/context/SidebarContext";
import { SessionProvider } from "@/context/SessionContext";
import { ThemeProvider } from "@/context/ThemeContext";
import AppHeader from "./AppHeader";
import AppSidebar from "./AppSidebar";

/** Sahifalar SERVER komponenti bo'lib qoladi — bu yerga `children` sifatida
 *  uzatiladi, ya'ni SSR (ADR-0003 dagi SEO sababi) buzilmaydi. */
function Shell({ children }: { children: React.ReactNode }) {
  const { isExpanded, isHovered, isMobileOpen, closeMobileSidebar } = useSidebar();
  const wide = isExpanded || isHovered;

  return (
    <div className="min-h-screen">
      <AppSidebar />
      {isMobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-gray-900/50 lg:hidden"
          onClick={closeMobileSidebar}
        />
      )}
      <div className={`transition-all duration-300 ${wide ? "lg:ml-[260px]" : "lg:ml-[86px]"}`}>
        <AppHeader />
        <main className="mx-auto max-w-[1400px] p-4 md:p-6">{children}</main>
      </div>
    </div>
  );
}

export default function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider>
      <SessionProvider>
        <SidebarProvider>
          <Shell>{children}</Shell>
        </SidebarProvider>
      </SessionProvider>
    </ThemeProvider>
  );
}
