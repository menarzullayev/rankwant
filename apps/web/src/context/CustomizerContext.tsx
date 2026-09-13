"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import { useStyle } from "@/context/StyleContext";
import { useTheme } from "@/context/ThemeContext";
import type { A11yPrefs, AppearancePrefs } from "@/lib/api";
import {
  ACCENT_KEY,
  A11Y_KEY,
  APPEARANCE_KEY,
  announcePrefs,
  removeLocal,
  rememberAppearance,
  type StoredAccent,
} from "@/lib/prefs";
import {
  applyAccent,
  applyA11y,
  applyAppearance,
  applyStyle,
  previewAccent,
  type AccentResult,
} from "@/lib/theme/apply";
import {
  TEMPLATES,
  matchTemplate,
  templateAppearance,
  type Template,
} from "@/lib/theme/templates";

export const DEFAULT_APPEARANCE: AppearancePrefs = {
  style: "clay",
  accent: null,
  font: null,
  size: 100,
  density: "comfortable",
};

export const DEFAULT_A11Y: A11yPrefs = {
  vision: "normal",
  motion: "system",
  bigTargets: false,
  strongFocus: false,
};

function readJson<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : fallback;
  } catch {
    return fallback;
  }
}

/** Sozlagich holati.
 *
 *  Bu provayder HECH NARSANI saqlamaydi — u `localStorage` ga yozadi va
 *  hodisa yuboradi, hisobga esa `PrefsSync` yozadi. Sabab: provayderlar
 *  sessiyadan tashqarida turadi (bir xil naqsh mavzu va uslubda ham).
 */
const CustomizerContext = createContext<
  | {
      open: boolean;
      setOpen: (next: boolean) => void;
      toggle: () => void;
      appearance: AppearancePrefs;
      a11y: A11yPrefs;
      /** Joriy holat qaysi shablonga mos keladi (`null` — o'zgartirilgan). */
      template: Template | null;
      setAppearance: (patch: Partial<AppearancePrefs>) => void;
      setA11y: (patch: Partial<A11yPrefs>) => void;
      applyTemplate: (template: Template) => void;
      /** «Oxirgi o'zgarishni bekor qilish» (D25, 1-bosqich). */
      undo: () => void;
      canUndo: boolean;
      /** «Zavod sozlamalari» (D25, 3-bosqich) — tasdiq chaqiruvchida. */
      resetAll: () => void;
      /** Panel ko'rsatkichi uchun — qo'llamasdan o'lchaydi. */
      preview: (hue: number, sat: number) => AccentResult;
    }
  | undefined
>(undefined);

export function useCustomizer() {
  const context = useContext(CustomizerContext);
  if (!context) {
    throw new Error("useCustomizer CustomizerProvider ichida ishlatilishi kerak");
  }
  return context;
}

export function CustomizerProvider({ children }: { children: React.ReactNode }) {
  // Panel yopiq holda chiziladi, ya'ni SSR va birinchi klient renderi bir
  // xil bo'ladi va `localStorage` o'qish hidratsiya nomuvofiqligini
  // keltirmaydi.
  const [open, setOpen] = useState(false);
  const [appearance, setAppearanceState] = useState<AppearancePrefs>(() =>
    typeof window === "undefined"
      ? DEFAULT_APPEARANCE
      : readJson(APPEARANCE_KEY, DEFAULT_APPEARANCE),
  );
  const [a11y, setA11yState] = useState<A11yPrefs>(() =>
    typeof window === "undefined" ? DEFAULT_A11Y : readJson(A11Y_KEY, DEFAULT_A11Y),
  );
  // Bekor qilish uchun bitta qadam (D24/D25) — to'liq tarix emas.
  const [previous, setPrevious] = useState<AppearancePrefs | null>(null);

  const { setStyle } = useStyle();
  const { mode, setMode } = useTheme();

  /** Accent ni qo'llaydi va hisoblangan qiymatni qurilmaga keshlaydi. */
  const applyAndCacheAccent = useCallback(
    (next: AppearancePrefs): AccentResult => {
      if (!next.accent) {
        removeLocal(ACCENT_KEY);
        // Uslubning o'z rangi qaytadi — inline qiymatlar olib tashlanadi.
        for (const token of [
          "--rw-accent",
          "--rw-accent-fg",
          "--rw-accent-soft",
          "--rw-accent-ink",
        ]) {
          document.documentElement.style.removeProperty(token);
        }
        return { ok: true, button: null, ink: null };
      }
      const result = applyAccent(next.accent.hue, next.accent.sat);
      if (result.ok) {
        const style = next.style ?? "clay";
        const read = (token: string) =>
          getComputedStyle(document.documentElement).getPropertyValue(token).trim();
        const stored: StoredAccent & { style: string } = {
          style,
          accent: read("--rw-accent"),
          fg: read("--rw-accent-fg"),
          soft: read("--rw-accent-soft"),
          ink: read("--rw-accent-ink"),
        };
        try {
          localStorage.setItem(ACCENT_KEY, JSON.stringify(stored));
        } catch {
          // Private rejim — kesh yozilmaydi, sozlama sessiyada ishlaydi.
        }
      }
      return result;
    },
    [],
  );

  /** Tanlovni qo'llaydi, qurilmaga yozadi va hisobga yuboradi. */
  const commit = useCallback(
    (next: AppearancePrefs, nextA11y: A11yPrefs) => {
      applyAppearance(next);
      applyA11y(nextA11y);
      applyAndCacheAccent(next);
      rememberAppearance(next, nextA11y, null);
      // Hisobga — `PrefsSync` yozadi. Uslubni ham qo'shamiz, chunki
      // `StyleContext` uni boshqa yo'l bilan yozadi.
      announcePrefs({
        style: next.style,
        appearance: next,
        a11y: nextA11y,
      });
    },
    [applyAndCacheAccent],
  );

  const setAppearance = useCallback(
    (patch: Partial<AppearancePrefs>) => {
      setAppearanceState((current) => {
        setPrevious(current);
        const next = { ...current, ...patch };
        if (patch.style && patch.style !== current.style) {
          // Uslub almashsa rang ham o'zgaradi (D10) — yangi uslubning
          // fonlari boshqa, eski accent o'sha yerda o'qilmasligi mumkin.
          applyStyle(patch.style);
          setStyle(patch.style as Parameters<typeof setStyle>[0]);
        }
        commit(next, a11y);
        return next;
      });
    },
    [a11y, commit, setStyle],
  );

  const setA11y = useCallback(
    (patch: Partial<A11yPrefs>) => {
      setA11yState((current) => {
        const next = { ...current, ...patch };
        commit(appearance, next);
        return next;
      });
    },
    [appearance, commit],
  );

  const applyTemplate = useCallback(
    (template: Template) => {
      setAppearanceState((current) => {
        setPrevious(current);
        const next = templateAppearance(template, current);
        applyStyle(template.style);
        setStyle(template.style);
        if (template.theme) setMode(template.theme);
        commit(next, a11y);
        return next;
      });
    },
    [a11y, commit, setMode, setStyle],
  );

  const undo = useCallback(() => {
    setPrevious((prev) => {
      if (!prev) return prev;
      setAppearanceState(prev);
      applyStyle(prev.style ?? "clay");
      setStyle((prev.style ?? "clay") as Parameters<typeof setStyle>[0]);
      commit(prev, a11y);
      return null;
    });
  }, [a11y, commit, setStyle]);

  const resetAll = useCallback(() => {
    setPrevious(appearance);
    const next = { ...DEFAULT_APPEARANCE, accent: null };
    setAppearanceState(next);
    setA11yState(DEFAULT_A11Y);
    applyStyle(DEFAULT_APPEARANCE.style ?? "clay");
    setStyle(DEFAULT_APPEARANCE.style as Parameters<typeof setStyle>[0]);
    setMode("system");
    commit(next, DEFAULT_A11Y);
  }, [appearance, commit, setMode, setStyle]);

  const toggle = useCallback(() => setOpen((value) => !value), []);

  // `Ctrl+.` — barcha sahifalarda (D30). `Esc` panel ichida ishlanadi:
  // u fokus panelda bo'lganda yopilishi kerak, global emas.
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.ctrlKey && event.key === ".") {
        event.preventDefault();
        setOpen((value) => !value);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const template = useMemo(
    () => matchTemplate(appearance, a11y, mode),
    [appearance, a11y, mode],
  );

  const preview = useCallback((hue: number, sat: number) => previewAccent(hue, sat), []);

  return (
    <CustomizerContext.Provider
      value={{
        open,
        setOpen,
        toggle,
        appearance,
        a11y,
        template,
        setAppearance,
        setA11y,
        applyTemplate,
        undo,
        canUndo: previous !== null,
        resetAll,
        preview,
      }}
    >
      {children}
    </CustomizerContext.Provider>
  );
}

export { TEMPLATES };
