"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useSyncExternalStore,
} from "react";

import { announcePrefs, themeEffect, writeLocal } from "@/lib/prefs";

/** Foydalanuvchi TANLAGAN rejim (D5). */
export type ThemeMode = "light" | "dark" | "system";
/** Qo'llangan mavzu — `system` bu yerda allaqachon yechilgan. */
export type Theme = "light" | "dark";

const MODE_KEY = "theme";

/** Tugma markazi — doira effekti shu nuqtadan yoyiladi. */
type Origin = { x: number; y: number };

const ThemeContext = createContext<
  | {
      /** Qo'llangan mavzu: `light` yoki `dark`. */
      theme: Theme;
      /** Tanlangan rejim: `light`, `dark` yoki `system`. */
      mode: ThemeMode;
      toggleTheme: (origin?: Origin) => void;
      setMode: (next: ThemeMode) => void;
      /** Eski nom — aniq mavzu o'rnatadi (`system` ni yechib tashlaydi). */
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

const isMode = (value: unknown): value is ThemeMode =>
  value === "light" || value === "dark" || value === "system";

function readMode(): ThemeMode {
  try {
    const raw = localStorage.getItem(MODE_KEY);
    return isMode(raw) ? raw : "system";
  } catch {
    // Private rejim — o'qib bo'lmaydi. Standart `system`.
    return "system";
  }
}

/** Haqiqat manbai — `<html>` dagi `dark` klassi. Uni `layout.tsx` dagi
 *  skript hidratsiyadan OLDIN qo'yadi (aks holda qorong'u sozlamadagi
 *  foydalanuvchi har yuklanishda oq chaqnash ko'radi), shuning uchun
 *  React holati emas, DOM o'qiladi. */
function subscribeDom(onChange: () => void) {
  const observer = new MutationObserver(onChange);
  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["class"],
  });
  return () => observer.disconnect();
}

const getSnapshot = (): Theme =>
  document.documentElement.classList.contains("dark") ? "dark" : "light";

const prefersDark = () => window.matchMedia("(prefers-color-scheme: dark)").matches;

const resolve = (mode: ThemeMode): Theme =>
  mode === "system" ? (prefersDark() ? "dark" : "light") : mode;

/** Rejimni yozadi va DOM ni yangilaydi. `system` ham shu yerdan o'tadi —
 *  ya'ni `localStorage` da TANLOV saqlanadi, yechilgan mavzu emas. */
function apply(mode: ThemeMode) {
  writeLocal(MODE_KEY, mode);
  document.documentElement.classList.toggle("dark", resolve(mode) === "dark");
}

/** Rejim o'zgarganini bildiradi. `useSyncExternalStore` DOM ni kuzatadi,
 *  lekin `localStorage` ni emas — shuning uchun alohida kanal kerak. */
const modeListeners = new Set<() => void>();

function subscribeMode(onChange: () => void) {
  modeListeners.add(onChange);
  return () => {
    modeListeners.delete(onChange);
  };
}

function emitMode() {
  for (const listener of modeListeners) listener();
}

type ViewTransition = { ready: Promise<void>; finished: Promise<void> };

/** Almashish effekti (sozlamalar → Ko'rinish). View Transitions yo'q
 *  brauzerda va `prefers-reduced-motion` da mavzu shunchaki almashadi. */
function applyWithEffect(mode: ThemeMode, origin?: Origin) {
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
    apply(mode);
    return;
  }
  const root = document.documentElement;
  root.dataset.vt = effect;
  const transition = start.call(document, () => apply(mode));
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
    subscribeDom,
    getSnapshot,
    () => "dark" as Theme,
  );
  const mode = useSyncExternalStore(
    subscribeMode,
    readMode,
    () => "system" as ThemeMode,
  );

  // OS mavzusi o'zgarganda FAQAT `system` rejimida qayta qo'llanadi.
  // Effektda `setState` YO'Q — DOM o'zgaradi, `useSyncExternalStore` uni
  // `MutationObserver` orqali o'zi sezadi (`react-hooks/set-state-in-effect`).
  // OS o'zgarishi animatsiya qilinmaydi: u foydalanuvchi harakati emas.
  useEffect(() => {
    if (mode !== "system") return;
    const query = window.matchMedia("(prefers-color-scheme: dark)");
    const onChange = () => apply("system");
    query.addEventListener("change", onChange);
    return () => query.removeEventListener("change", onChange);
  }, [mode]);

  const setMode = useCallback((next: ThemeMode) => {
    applyWithEffect(next);
    announcePrefs({ theme: next });
    emitMode();
  }, []);

  const toggleTheme = useCallback((origin?: Origin) => {
    // `system` da turib bosilsa — qarama-qarshi ANIQ rejimga o'tadi:
    // odam tugmani bosdi, ya'ni endi o'zi qaror qildi.
    const next: Theme = getSnapshot() === "dark" ? "light" : "dark";
    applyWithEffect(next, origin);
    announcePrefs({ theme: next });
    emitMode();
  }, []);

  const setTheme = useCallback((next: Theme) => setMode(next), [setMode]);

  return (
    <ThemeContext.Provider
      value={{ theme, mode, toggleTheme, setMode, setTheme }}
    >
      {children}
    </ThemeContext.Provider>
  );
}
