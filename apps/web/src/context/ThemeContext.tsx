"use client";

import {
  createContext,
  useCallback,
  useContext,
  useSyncExternalStore,
} from "react";

import { announcePrefs, themeEffect, writeLocal } from "@/lib/prefs";

type Theme = "light" | "dark";

/** Tugma markazi — doira effekti shu nuqtadan yoyiladi. */
type Origin = { x: number; y: number };

const ThemeContext = createContext<
  | {
      theme: Theme;
      toggleTheme: (origin?: Origin) => void;
      setTheme: (next: Theme) => void;
    }
  | undefined
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

function apply(next: Theme) {
  document.documentElement.classList.toggle("dark", next === "dark");
  writeLocal("theme", next);
}

type ViewTransition = { ready: Promise<void>; finished: Promise<void> };

/** Almashish effekti (sozlamalar → Ko'rinish). View Transitions yo'q
 *  brauzerda va `prefers-reduced-motion` da mavzu shunchaki almashadi. */
function applyWithEffect(next: Theme, origin?: Origin) {
  const effect = themeEffect();
  const start = (
    document as Document & {
      startViewTransition?: (update: () => void) => ViewTransition;
    }
  ).startViewTransition;
  if (
    effect === "none" ||
    !start ||
    window.matchMedia("(prefers-reduced-motion: reduce)").matches
  ) {
    apply(next);
    return;
  }
  const root = document.documentElement;
  root.dataset.vt = effect;
  const transition = start.call(document, () => apply(next));
  transition.finished.finally(() => delete root.dataset.vt);
  if (effect !== "circle") return;
  const { x, y } = origin ?? { x: window.innerWidth, y: 0 };
  const radius = Math.hypot(
    Math.max(x, window.innerWidth - x),
    Math.max(y, window.innerHeight - y),
  );
  transition.ready
    .then(() =>
      root.animate(
        {
          clipPath: [
            `circle(0px at ${x}px ${y}px)`,
            `circle(${radius}px at ${x}px ${y}px)`,
          ],
        },
        {
          duration: 450,
          easing: "ease-in-out",
          pseudoElement: "::view-transition-new(root)",
        },
      ),
    )
    .catch(() => {});
}

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const theme = useSyncExternalStore(
    subscribe,
    getSnapshot,
    () => "dark" as Theme,
  );

  const toggleTheme = useCallback((origin?: Origin) => {
    const next: Theme = getSnapshot() === "dark" ? "light" : "dark";
    applyWithEffect(next, origin);
    announcePrefs({ theme: next });
  }, []);

  const setTheme = useCallback((next: Theme) => {
    if (next === getSnapshot()) return;
    applyWithEffect(next);
    announcePrefs({ theme: next });
  }, []);

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}
