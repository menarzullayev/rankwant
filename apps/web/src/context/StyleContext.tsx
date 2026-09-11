"use client";

import {
  createContext,
  useCallback,
  useContext,
  useSyncExternalStore,
} from "react";

import { DEFAULT_STYLE, STYLE_IDS, type StyleId } from "@/layout/styles";
import { announcePrefs } from "@/lib/prefs";

const StyleContext = createContext<
  { style: StyleId; setStyle: (next: StyleId) => void } | undefined
>(undefined);

export function useStyle() {
  const context = useContext(StyleContext);
  if (!context)
    throw new Error("useStyle StyleProvider ichida ishlatilishi kerak");
  return context;
}

/** `ThemeContext` bilan bir xil sabab: haqiqat manbai `<html data-style>`,
 * uni `layout.tsx` skripti hidratsiyadan oldin qo'yadi. */
function subscribe(onChange: () => void) {
  const observer = new MutationObserver(onChange);
  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["data-style"],
  });
  return () => observer.disconnect();
}

function getSnapshot(): StyleId {
  const value = document.documentElement.dataset.style as StyleId | undefined;
  return value && STYLE_IDS.includes(value) ? value : DEFAULT_STYLE;
}

export function StyleProvider({ children }: { children: React.ReactNode }) {
  const style = useSyncExternalStore(
    subscribe,
    getSnapshot,
    () => DEFAULT_STYLE,
  );

  const setStyle = useCallback((next: StyleId) => {
    document.documentElement.dataset.style = next;
    try {
      localStorage.setItem("style", next);
    } catch {
      // Private rejimda yozib bo'lmaydi — uslub sessiya davomida ishlaydi.
    }
    announcePrefs({ style: next });
  }, []);

  return (
    <StyleContext.Provider value={{ style, setStyle }}>
      {children}
    </StyleContext.Provider>
  );
}
