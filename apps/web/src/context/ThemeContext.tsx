"use client";

import {
  createContext,
  useCallback,
  useContext,
  useSyncExternalStore,
} from "react";

type Theme = "light" | "dark";

const ThemeContext = createContext<
  { theme: Theme; toggleTheme: () => void } | undefined
>(undefined);

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context)
    throw new Error("useTheme ThemeProvider ichida ishlatilishi kerak");
  return context;
}

/** Haqiqat manbai — `<html>` dagi `dark` klassi. Uni `layout.tsx` dagi
 * skript hidratsiyadan OLDIN qo'yadi (aks holda qorong'u sozlamadagi
 * foydalanuvchi har yuklanishda oq chaqnash ko'radi), shuning uchun
 * React holati emas, DOM o'qiladi. */
function subscribe(onChange: () => void) {
  const observer = new MutationObserver(onChange);
  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["class"],
  });
  return () => observer.disconnect();
}

const getSnapshot = (): Theme =>
  document.documentElement.classList.contains("dark") ? "dark" : "light";

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const theme = useSyncExternalStore(
    subscribe,
    getSnapshot,
    () => "dark" as Theme,
  );

  const toggleTheme = useCallback(() => {
    const next: Theme = getSnapshot() === "dark" ? "light" : "dark";
    document.documentElement.classList.toggle("dark", next === "dark");
    try {
      localStorage.setItem("theme", next);
    } catch {
      // Private rejimda localStorage yozib bo'lmaydi — tema baribir ishlaydi.
    }
  }, []);

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}
