"use client";

import { useCustomizer } from "@/context/CustomizerContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { VERDICT_ICONS, VerdictIconQuestion } from "@/icons/verdict-icons";
import {
  DEFAULT_VERDICT_VARIANT,
  GROUP_HINT_KEY,
  verdictColors,
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
 *  ⚠️ **Notanish kod yashirilmaydi.** `verdictOf()` `null` qaytarsa, xom kod
 *  ko'rsatiladi (kulrang + savol ikonkasi). Ilgari noma'lum kod `PD` ga
 *  tushardi va 23 koddan 14 tasi «Navbatda» bo'lib ko'rinardi — buni hech
 *  kim sezmasdi.
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
  /** Verdikt kaliti (`AC`, `WA`, `TLE`…). Notanish bo'lsa xom ko'rinadi. */
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
  const style = variant ?? appearance.verdictStyle ?? DEFAULT_VERDICT_VARIANT;

  // Noma'lum kod: xom matn, kulrang, savol ikonkasi.
  const known = def !== null;
  const code = known ? def.key : String(verdict ?? "").trim();
  if (!code) return null;

  const Icon = known ? VERDICT_ICONS[def.key] : VerdictIconQuestion;
  const { color, soft } = verdictColors(def);
  const label = known ? t(locale, def.labelKey) : code;
  const hintKey = known ? (def.hintKey ?? GROUP_HINT_KEY(def.group)) : "verdict.group.unknown.hint";
  const hint = t(locale, hintKey);
  const pct = percent !== undefined ? `${percent}%` : "";

  // ── ① Faqat rangli nishon ──────────────────────────────────────────
  const badge = (
    <span className="rw-verdict rw-verdict-badge" style={{ color, background: soft }}>
      {code}
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
    <span className="rw-verdict rw-verdict-icon" style={{ color }}>
      <Icon className="size-[1.15em]" />
      <span>{code}</span>
    </span>
  );

  // ── ④ Ikonka + to'liq nom ──────────────────────────────────────────
  const full = (
    <span className="rw-verdict rw-verdict-full" style={{ color }}>
      <Icon className="size-[1.15em]" />
      <span>{label}</span>
    </span>
  );

  // ── ⑤ Rangli doira + oq ikonka ─────────────────────────────────────
  const circle = (
    <span
      className="rw-verdict rw-verdict-circle"
      style={{ background: color }}
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
      <i style={{ background: color }} />
      <span>{code}</span>
    </span>
  );

  // ── ⑦ Chegara + ikonka ─────────────────────────────────────────────
  const box = (
    <span
      className="rw-verdict rw-verdict-box"
      style={{ color }}
      title={label}
      role="img"
      aria-label={label}
    >
      <Icon className="size-[1.05em]" />
    </span>
  );

  // ── ⑧ Chap chiziq + ikonka + nom ───────────────────────────────────
  const bar = (
    <span className="rw-verdict rw-verdict-bar" style={{ borderColor: color, color }}>
      <Icon className="size-[1.05em]" />
      <span>{label}</span>
    </span>
  );

  // ── ⑨ Ikonka + kod + foiz ──────────────────────────────────────────
  const percentBody = (
    <span className="rw-verdict rw-verdict-percent" style={{ color }}>
      <Icon className="size-[1.15em]" />
      <span>{code}</span>
      {pct && <em className="rw-verdict-pct">{pct}</em>}
    </span>
  );

  // ── ⑩ Katta ikonka (karta) ─────────────────────────────────────────
  const card = (
    <span className="rw-verdict rw-verdict-card">
      <Icon className="rw-verdict-card-icon" />
      <b style={{ color }}>{label}</b>
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
