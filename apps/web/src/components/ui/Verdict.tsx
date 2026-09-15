"use client";

import { useCustomizer } from "@/context/CustomizerContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { VERDICT_ICONS } from "@/icons/verdict-icons";
import {
  DEFAULT_VERDICT_VARIANT,
  verdictOf,
  type VerdictVariant,
} from "@/lib/theme/verdict";

/** Judge natijasi — o'nta ko'rinishda (D56/D57/D59).
 *
 *  **Bitta komponent, o'nta variant.** Hammasi bir xil ma'lumotdan
 *  oziqlanadi (`lib/theme/verdict.ts`): kalit → nom, rang, ikonka. Farq
 *  faqat batafsil darajasida:
 *
 *  | Variant    | Ko'rinish              | Nima yetkazadi        | Qayerda          |
 *  |------------|------------------------|-----------------------|------------------|
 *  | `badge`  ① | rangli nishon + kod    | holat nomi            | zich jadval      |
 *  | `plain`  ② | faqat ikonka (rangsiz) | faqat shakl           | eng izchil ro'yxat|
 *  | `icon`   ③ | ikonka + kod           | holat + vizual signal | urinishlar       |
 *  | `full`   ④ | ikonka + to'liq nom    | holat + sabab         | masala sahifasi  |
 *  | `circle` ⑤ | to'ldirilgan doira     | faqat signal          | mobil, ixcham    |
 *  | `dot`    ⑥ | rangli nuqta + kod     | holat, yengil         | log ro'yxati     |
 *  | `box`    ⑦ | chegara + ikonka       | faqat signal, ramkali | ikonka paneli    |
 *  | `bar`    ⑧ | chap chiziq + nom      | holat, chetlangan     | ogohlantirish    |
 *  | `percent`⑨ | ikonka + kod + foiz    | holat + natija foizi  | baholash         |
 *  | `card`   ⑩ | katta ikonka + izoh    | holat + tushuntirish  | natija kartasi   |
 *  | `auto`     | ekranga qarab tanlaydi | —                     | standart         |
 *
 *  ⚠️ **Matnsiz variantlar** (`plain`, `box`, `circle`) `aria-label` va
 *  `title` oladi — aks holda ekran o'quvchi verdiktni o'qiy olmaydi.
 *  Matnli variantlarda ikonka `aria-hidden` (matn yonida ortiqcha ovoz).
 */
export function Verdict({
  verdict,
  variant,
  percent,
  className = "",
}: {
  /** Verdikt kaliti (`AC`, `WA`, `TLE`…). Notanish bo'lsa — `PD`. */
  verdict: string;
  /** Ko'rinishni majburan tanlash. Berilmasa — foydalanuvchi sozlamasi. */
  variant?: VerdictVariant;
  /** Test foizi — faqat `percent` (⑨) variantida ko'rinadi. */
  percent?: number;
  className?: string;
}) {
  const locale = useLocale();
  const { appearance } = useCustomizer();
  const def = verdictOf(verdict);
  const Icon = VERDICT_ICONS[def.key];
  const style = variant ?? appearance.verdictStyle ?? DEFAULT_VERDICT_VARIANT;

  if (!Icon) return null;

  const label = def.label;
  const hint = t(locale, def.hintKey);
  const pct = percent !== undefined ? `${percent}%` : "";

  // ── ① Faqat rangli nishon ──────────────────────────────────────────
  const badge = (
    <span
      className="rw-verdict rw-verdict-badge"
      style={{ color: def.color, background: def.background }}
    >
      {def.key}
    </span>
  );

  // ── ② Faqat ikonka — rangsiz, eng izchil ───────────────────────────
  const plain = (
    <span className="rw-verdict rw-verdict-plain" title={label} role="img" aria-label={label}>
      <Icon className="size-[1.35em]" />
    </span>
  );

  // ── ③ Ikonka + kod ─────────────────────────────────────────────────
  const icon = (
    <span className="rw-verdict rw-verdict-icon" style={{ color: def.color }}>
      <Icon className="size-[1.15em]" />
      <span>{def.key}</span>
    </span>
  );

  // ── ④ Ikonka + to'liq nom ──────────────────────────────────────────
  const full = (
    <span className="rw-verdict rw-verdict-full" style={{ color: def.color }}>
      <Icon className="size-[1.15em]" />
      <span>{label}</span>
    </span>
  );

  // ── ⑤ Rangli doira + oq ikonka ─────────────────────────────────────
  const circle = (
    <span
      className="rw-verdict rw-verdict-circle"
      style={{ background: def.color }}
      title={label}
      role="img"
      aria-label={label}
    >
      <Icon className="size-[0.85em]" />
    </span>
  );

  // ── ⑥ Rangli nuqta + kod ───────────────────────────────────────────
  const dot = (
    <span className="rw-verdict rw-verdict-dot">
      <i style={{ background: def.color }} />
      <span>{def.key}</span>
    </span>
  );

  // ── ⑦ Chegara + ikonka ─────────────────────────────────────────────
  const box = (
    <span
      className="rw-verdict rw-verdict-box"
      style={{ color: def.color }}
      title={label}
      role="img"
      aria-label={label}
    >
      <Icon className="size-[1.05em]" />
    </span>
  );

  // ── ⑧ Chap chiziq + ikonka + nom ───────────────────────────────────
  const bar = (
    <span className="rw-verdict rw-verdict-bar" style={{ borderColor: def.color, color: def.color }}>
      <Icon className="size-[1.05em]" />
      <span>{label}</span>
    </span>
  );

  // ── ⑨ Ikonka + kod + foiz ──────────────────────────────────────────
  const percentBody = (
    <span className="rw-verdict rw-verdict-percent" style={{ color: def.color }}>
      <Icon className="size-[1.15em]" />
      <span>{def.key}</span>
      {pct && <em className="rw-verdict-pct">{pct}</em>}
    </span>
  );

  // ── ⑩ Katta ikonka (karta) ─────────────────────────────────────────
  const card = (
    <span className="rw-verdict rw-verdict-card">
      <Icon className="rw-verdict-card-icon" />
      <b style={{ color: def.color }}>{label}</b>
      <span className="rw-verdict-card-hint">{hint}</span>
    </span>
  );

  // ── `auto` — ekranga qarab ─────────────────────────────────────────
  // Uch nusxa chiziladi, CSS faqat bittasini ko'rsatadi. Sabab: React
  // `matchMedia` bilan ekran o'lchamini kuzatish SSR'da chaqnash beradi
  // (serverda o'lcham noma'lum), CSS esa buni chaqnashsiz bajaradi.
  if (style === "auto") {
    return (
      <span className={`rw-verdict-auto ${className}`}>
        <span className="rw-only-mobile">{circle}</span>
        <span className="rw-only-tablet">{icon}</span>
        <span className="rw-only-desktop">{full}</span>
      </span>
    );
  }

  const body =
    style === "badge" ? badge
    : style === "plain" ? plain
    : style === "icon" ? icon
    : style === "circle" ? circle
    : style === "dot" ? dot
    : style === "box" ? box
    : style === "bar" ? bar
    : style === "percent" ? percentBody
    : style === "card" ? card
    : full;

  return <span className={className}>{body}</span>;
}
