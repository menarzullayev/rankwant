"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import { useSession } from "@/context/SessionContext";
import { useStyle } from "@/context/StyleContext";
import { useTheme } from "@/context/ThemeContext";
import type { A11yPrefs, AppearancePrefs, ThemeTemplate } from "@/lib/api";
import {
  ACCENT_KEY,
  A11Y_KEY,
  APPEARANCE_KEY,
  TEMPLATES_KEY,
  announcePrefs,
  removeLocal,
  rememberAccent,
  rememberAppearance,
  type StoredAccent,
} from "@/lib/prefs";
import {
  applyAccent,
  applyAll,
  applyA11y,
  applyAppearance,
  applyStyle,
  previewAccent,
  type AccentResult,
} from "@/lib/theme/apply";
import { decodeAppearance, shareUrl, stripAppearance } from "@/lib/theme/share";
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
      /** Shaxsiy shablonlar (D21) — hisobda 5 tagacha, mehmonda 2 ta. */
      templates: ThemeTemplate[];
      saveTemplate: (name: string) => void;
      removeTemplate: (name: string) => void;
      applySaved: (template: ThemeTemplate) => void;
      /** Chegara: mehmon 2 ta, kirgan 5 ta (D21). */
      templateLimit: number;
      /** Panel ko'rsatkichi uchun — qo'llamasdan o'lchaydi. */
      preview: (hue: number, sat: number) => AccentResult;
      /** Joriy ko'rinishning ulashish havolasi (D22). */
      shareLink: () => string;
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

export function CustomizerProvider({
  siteAppearance,
  children,
}: {
  /** Jamoa belgilagan standart ko'rinish (D37). Bo'sh bo'lsa kod
   *  standarti ishlatiladi (D26: `clay`). */
  siteAppearance?: AppearancePrefs;
  children: React.ReactNode;
}) {
  // Panel yopiq holda chiziladi, ya'ni SSR va birinchi klient renderi bir
  // xil bo'ladi va `localStorage` o'qish hidratsiya nomuvofiqligini
  // keltirmaydi.
  const [open, setOpen] = useState(false);
  // Havoladagi sozlamalar (D22) ustun turadi: odam shu havolani ochdi,
  // ya'ni o'sha ko'rinishni ko'rishni xohladi. Effektda emas, boshlang'ich
  // qiymatda o'qiladi — effektda `setState` loyihada taqiqlangan va
  // kaskad render keltiradi.
  // Standart qiymat: jamoa belgilagani ustuvor, bo'lmasa kod standarti.
  // ⚠️ Bu FAQAT boshlang'ich qiymat — qurilmada yoki hisobda saqlangan
  // tanlov har doim ustun turadi (D37: mavjud foydalanuvchilarga
  // tegilmaydi).
  const fallback: AppearancePrefs = { ...DEFAULT_APPEARANCE, ...siteAppearance };
  const [appearance, setAppearanceState] = useState<AppearancePrefs>(() => {
    if (typeof window === "undefined") return fallback;
    return (
      decodeAppearance(window.location.search) ??
      readJson(APPEARANCE_KEY, fallback)
    );
  });
  const [a11y, setA11yState] = useState<A11yPrefs>(() =>
    typeof window === "undefined" ? DEFAULT_A11Y : readJson(A11Y_KEY, DEFAULT_A11Y),
  );
  const [templates, setTemplates] = useState<ThemeTemplate[]>(() =>
    typeof window === "undefined" ? [] : readJson(TEMPLATES_KEY, []),
  );
  // Bekor qilish uchun bitta qadam (D24/D25) — to'liq tarix emas.
  const [previous, setPrevious] = useState<AppearancePrefs | null>(null);

  const { setStyle } = useStyle();
  const { mode, setMode } = useTheme();
  const { user } = useSession();

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
        rememberAccent(stored);
      }
      return result;
    },
    [],
  );

  /** Tanlovni qo'llaydi, qurilmaga yozadi va hisobga yuboradi. */
  const commit = useCallback(
    (next: AppearancePrefs, nextA11y: A11yPrefs, nextTemplates: ThemeTemplate[] = []) => {
      applyAppearance(next);
      applyA11y(nextA11y);
      applyAndCacheAccent(next);
      rememberAppearance(next, nextA11y, nextTemplates);
      // Hisobga — `PrefsSync` yozadi. Uslubni ham qo'shamiz, chunki
      // `StyleContext` uni boshqa yo'l bilan yozadi.
      announcePrefs({
        style: next.style,
        appearance: next,
        a11y: nextA11y,
        templates: nextTemplates,
      });
    },
    [applyAndCacheAccent],
  );

  const setAppearance = useCallback(
    (patch: Partial<AppearancePrefs>) => {
      // ⚠️ Yon ta'sirlar updater ICHIDA emas: React updater'ni qayta
      // chaqirishi mumkin (StrictMode da ikki marta) va u sof bo'lishi
      // shart. Shuning uchun qiymat tashqarida hisoblanadi.
      setPrevious(appearance);
      const next = { ...appearance, ...patch };
      if (patch.style && patch.style !== appearance.style) {
        // Uslub almashsa rang ham o'zgaradi (D10) — yangi uslubning
        // fonlari boshqa, eski accent o'sha yerda o'qilmasligi mumkin.
        applyStyle(patch.style);
        setStyle(patch.style as Parameters<typeof setStyle>[0]);
      }
      setAppearanceState(next);
      commit(next, a11y);
    },
    [appearance, a11y, commit, setStyle],
  );

  const setA11y = useCallback(
    (patch: Partial<A11yPrefs>) => {
      const next = { ...a11y, ...patch };
      setA11yState(next);
      commit(appearance, next);
    },
    [appearance, a11y, commit],
  );

  const applyTemplate = useCallback(
    (template: Template) => {
      setPrevious(appearance);
      const next = templateAppearance(template, appearance);
      applyStyle(template.style);
      setStyle(template.style);
      if (template.theme) setMode(template.theme);
      setAppearanceState(next);
      commit(next, a11y);
    },
    [a11y, appearance, commit, setMode, setStyle],
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

  /** Mehmon 2 ta, kirgan 5 ta (D21) — `ui_prefs` cheksiz o'smasin. */
  const templateLimit = user ? 5 : 2;

  const saveTemplate = useCallback(
    (name: string) => {
      const clean = name.trim().slice(0, 24);
      if (!clean) return;
      // Bir xil nom (katta-kichik harf farqisiz) — ustidan yoziladi:
      // aks holda validator `unique` tekshiruvi 400 qaytarardi.
      const next = [
        ...templates.filter((row) => row.name.toLowerCase() !== clean.toLowerCase()),
        { name: clean, appearance, a11y },
      ].slice(-templateLimit);
      setTemplates(next);
      commit(appearance, a11y, next);
    },
    [a11y, appearance, commit, templateLimit, templates],
  );

  const removeTemplate = useCallback(
    (name: string) => {
      const next = templates.filter((row) => row.name !== name);
      setTemplates(next);
      commit(appearance, a11y, next);
    },
    [a11y, appearance, commit, templates],
  );

  const applySaved = useCallback(
    (template: ThemeTemplate) => {
      const next: AppearancePrefs = {
        ...DEFAULT_APPEARANCE,
        ...template.appearance,
      };
      const nextA11y: A11yPrefs = { ...DEFAULT_A11Y, ...template.a11y };
      setPrevious(appearance);
      applyStyle(next.style ?? "clay");
      setStyle((next.style ?? "clay") as Parameters<typeof setStyle>[0]);
      setAppearanceState(next);
      setA11yState(nextA11y);
      commit(next, nextA11y, templates);
    },
    [appearance, commit, setStyle, templates],
  );

  // Havoladan kelgan sozlamalar qo'llanadi va manzil TOZALANADI: aks
  // holda har yuklanishda qayta qo'llanib, odam o'z sozlamasini
  // o'zgartira olmay qolardi. Effektda `setState` yo'q — faqat tashqi
  // tizim (DOM va manzil) yangilanadi.
  useEffect(() => {
    const fromUrl = decodeAppearance(window.location.search);
    if (!fromUrl) return;
    applyAll(fromUrl, a11y);
    rememberAppearance(fromUrl, a11y);
    window.history.replaceState(null, "", stripAppearance(window.location.search));
    // Faqat mountda: keyingi o'zgarishlar `commit` orqali o'tadi.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

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

  const shareLink = useCallback(() => shareUrl(appearance), [appearance]);

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
        templates,
        saveTemplate,
        removeTemplate,
        applySaved,
        templateLimit,
        preview,
        shareLink,
      }}
    >
      {children}
    </CustomizerContext.Provider>
  );
}

export { TEMPLATES };
