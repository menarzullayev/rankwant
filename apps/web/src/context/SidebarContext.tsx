"use client";

import { createContext, useContext, useEffect, useState, useSyncExternalStore } from "react";

const EXPANDED_KEY = "rw:sidenav-expanded";

type SidebarContextType = {
  isExpanded: boolean;
  isMobileOpen: boolean;
  isHovered: boolean;
  toggleSidebar: () => void;
  toggleMobileSidebar: () => void;
  closeMobileSidebar: () => void;
  /** Mobil ro'yxatni ochadi — topnav'ning burger tugmasi uchun (D46). */
  openMobileSidebar: () => void;
  setIsHovered: (value: boolean) => void;
};

const SidebarContext = createContext<SidebarContextType | undefined>(undefined);

export function useSidebar() {
  const context = useContext(SidebarContext);
  if (!context)
    throw new Error("useSidebar SidebarProvider ichida ishlatilishi kerak");
  return context;
}

/** Yig'ilgan holat qurilmada — hisobga yozilmaydi (appearance PATCH
 *  hozir qo'shimcha kalitlarni 400 qiladi). `useSyncExternalStore`:
 *  effektda `setState` loyihada taqiqlangan. */
const expandedListeners = new Set<() => void>();

function subscribeExpanded(onChange: () => void) {
  expandedListeners.add(onChange);
  return () => {
    expandedListeners.delete(onChange);
  };
}

let cachedExpanded: boolean | null = null;

function readExpanded(): boolean {
  if (cachedExpanded !== null) return cachedExpanded;
  try {
    cachedExpanded = localStorage.getItem(EXPANDED_KEY) !== "0";
  } catch {
    cachedExpanded = true;
  }
  return cachedExpanded;
}

function writeExpanded(value: boolean) {
  cachedExpanded = value;
  try {
    localStorage.setItem(EXPANDED_KEY, value ? "1" : "0");
  } catch {
    // Private rejim — sessiya davomida kesh orqali ishlaydi.
  }
  for (const listener of expandedListeners) listener();
}

export function SidebarProvider({ children }: { children: React.ReactNode }) {
  const isExpanded = useSyncExternalStore(
    subscribeExpanded,
    readExpanded,
    () => true,
  );
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  useEffect(() => {
    const onResize = () => {
      const mobile = window.innerWidth < 1024;
      setIsMobile(mobile);
      if (!mobile) setIsMobileOpen(false);
    };
    onResize();
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);

  return (
    <SidebarContext.Provider
      value={{
        // Mobil ekranda yig'ilgan sidebar ma'nosiz — u overlay bo'lib ochiladi.
        isExpanded: isMobile ? false : isExpanded,
        isMobileOpen,
        isHovered,
        toggleSidebar: () => writeExpanded(!readExpanded()),
        toggleMobileSidebar: () => setIsMobileOpen((v) => !v),
        closeMobileSidebar: () => setIsMobileOpen(false),
        openMobileSidebar: () => setIsMobileOpen(true),
        setIsHovered,
      }}
    >
      {children}
    </SidebarContext.Provider>
  );
}
