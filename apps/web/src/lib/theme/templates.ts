/** Jamoa shablonlari — D41, sakkizta.
 *
 *  Shablon = uslub + mavzu + rang + shrift + zichlik (D19) + kit oilalari
 *  (D49), bir bosishda qo'llanadi. Keyin qo'lda o'zgartirilsa
 *  «o'zgartirilgan» deb belgilanadi.
 *
 *  Har birining ANIQ foydalanish holati bor — aks holda u shunchaki
 *  «yana bitta uslub» bo'lib qolardi. Uchta bir muhitli uslub ham
 *  kiritilgan (Konsol — terminal, Yumshoq — clay, Aurora), ya'ni D6
 *  (mavzuning avtomatik moslashuvi) shablon darajasida ham ishlaydi.
 *
 *  Rang — o'sha uslubning O'Z accent'i (D10: rang uslubga bog'liq), shuning
 *  uchun `accent: null` va qo'shimcha o'lchov talab qilmaydi.
 *
 *  Kit oilalari — sakkizta shablon bitta default-blokni ulashadi (D49).
 *  Apply tiklaydi; match solishtiradi. A11y TEGILMAYDI.
 */

import type { A11yPrefs, AppearancePrefs } from "@/lib/api";
import type { StyleId } from "@/layout/styles";
import { DEFAULT_FORM_VARIANT } from "@/lib/theme/form";
import { DEFAULT_ICON_PACK } from "@/lib/theme/icon-packs";
import { DEFAULT_LOADING_VARIANT } from "@/lib/theme/loading";
import { DEFAULT_OVERLAY_VARIANT } from "@/lib/theme/overlay";
import { DEFAULT_STATUS_VARIANT } from "@/lib/theme/status";
import { DEFAULT_VERDICT_VARIANT } from "@/lib/theme/verdict";

export type Template = {
  /** Kalit — tarjima uchun (`customizer.template.<id>`). */
  id: string;
  /** Uslub nomi — tarjima qilinmaydi, u brend nomi. */
  style: StyleId;
  /** Mavzu rejimi. `null` — joriysi qoladi (foydalanuvchi tanlovi). */
  theme: "light" | "dark" | "system" | null;
  font: AppearancePrefs["font"];
  density: AppearancePrefs["density"];
};

/** D49: shared kit identity for every built-in team template. */
export const TEMPLATE_KIT_DEFAULTS = {
  verdictStyle: DEFAULT_VERDICT_VARIANT,
  statusStyle: DEFAULT_STATUS_VARIANT,
  loadingStyle: DEFAULT_LOADING_VARIANT,
  overlayStyle: DEFAULT_OVERLAY_VARIANT,
  formStyle: DEFAULT_FORM_VARIANT,
  iconPack: DEFAULT_ICON_PACK,
} as const;

export const TEMPLATES: Template[] = [
  {
    id: "classic",
    style: "dashboard",
    theme: "system",
    font: null,
    density: "comfortable",
  },
  { id: "day", style: "flat", theme: "light", font: "inter", density: "comfortable" },
  { id: "night", style: "material", theme: "dark", font: "inter", density: "comfortable" },
  { id: "console", style: "terminal", theme: "dark", font: null, density: "compact" },
  { id: "journal", style: "editorial", theme: "light", font: null, density: "comfortable" },
  { id: "focus", style: "swiss", theme: "light", font: "roboto", density: "compact" },
  { id: "soft", style: "clay", theme: "light", font: "dm-sans", density: "comfortable" },
  { id: "aurora", style: "aurora", theme: "dark", font: "jakarta", density: "comfortable" },
];

export function kitMatches(
  appearance: AppearancePrefs,
  kit: typeof TEMPLATE_KIT_DEFAULTS = TEMPLATE_KIT_DEFAULTS,
): boolean {
  return (
    (appearance.verdictStyle ?? kit.verdictStyle) === kit.verdictStyle &&
    (appearance.statusStyle ?? kit.statusStyle) === kit.statusStyle &&
    (appearance.loadingStyle ?? kit.loadingStyle) === kit.loadingStyle &&
    (appearance.overlayStyle ?? kit.overlayStyle) === kit.overlayStyle &&
    (appearance.formStyle ?? kit.formStyle) === kit.formStyle &&
    (appearance.iconPack ?? kit.iconPack) === kit.iconPack
  );
}

/** Shablon tanlanganda qo'llanadigan ko'rinish (a11y TEGILMAYDI — u
 *  foydalanuvchining o'qish sozlamasi, shablonning bir qismi emas). */
export function templateAppearance(
  template: Template,
  current: AppearancePrefs,
): AppearancePrefs {
  return {
    ...current,
    style: template.style,
    // Rang uslubga bog'liq (D10) — yangi uslub o'z rangini olib keladi.
    accent: null,
    font: template.font,
    density: template.density,
    ...TEMPLATE_KIT_DEFAULTS,
  };
}

/** Joriy holat biror shablonga mos keladimi — mos kelsa «o'zgartirilgan»
 *  belgisi ko'rsatilmaydi. */
export function matchTemplate(
  appearance: AppearancePrefs,
  a11y: A11yPrefs,
  themeMode: string,
): Template | null {
  return (
    TEMPLATES.find(
      (template) =>
        template.style === appearance.style &&
        template.font === (appearance.font ?? null) &&
        template.density === (appearance.density ?? "comfortable") &&
        !appearance.accent &&
        (template.theme === null || template.theme === themeMode) &&
        a11y.vision !== "protan" &&
        a11y.vision !== "tritan" &&
        kitMatches(appearance),
    ) ?? null
  );
}
