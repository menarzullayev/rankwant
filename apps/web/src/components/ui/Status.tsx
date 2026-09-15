"use client";

import { useCustomizer } from "@/context/CustomizerContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { STATUS_ICONS } from "@/icons/phosphor";
import {
  DEFAULT_STATUS_VARIANT,
  statusOf,
  type StatusVariant,
} from "@/lib/theme/status";

/** Interfeys holati — o'nta ko'rinishda (D60).
 *
 *  **Bitta komponent, o'nta variant.** Hammasi bir xil ma'lumotdan
 *  oziqlanadi (`lib/theme/status.ts`): holat → rang, fon, nom, izoh.
 *
 *  | Variant     | Ko'rinish                   | Qayerda                    |
 *  |-------------|-----------------------------|----------------------------|
 *  | `text`    ① | faqat rangli matn           | zich joy, hisoblagich      |
 *  | `iconText`② | ikonka + rang + matn        | forma natijasi, umumiy qator|
 *  | `badge`   ③ | yumaloq nishon              | ro'yxat qatori, teg        |
 *  | `circle`  ④ | rangli doira + oq ikonka    | mobil, kalendar            |
 *  | `dot`     ⑤ | rangli nuqta + matn         | log, «onlayn» belgisi      |
 *  | `box`     ⑥ | ramkali kvadrat             | ikonka paneli              |
 *  | `alert`   ⑦ | chap chiziq + matn          | sahifa yuqorisi            |
 *  | `soft`    ⑧ | yumshoq fonli karta         | forma natijasi, panel      |
 *  | `outline` ⑨ | ramkali karta               | xato tafsiloti             |
 *  | `stack`   ⑩ | katta karta (ustma-ust)     | bo'sh sahifa, onboarding   |
 *  | `auto`      | ekranga qarab tanlaydi      | standart                   |
 *
 *  ⚠️ `label` va `hint` odatda kontekstdan keladi (`«O'zgarishlar
 *  saqlandi»`), ya'ni ular `t()` bilan emas, chaqiruvchi tomonidan
 *  beriladi. Berilmasa — holatning umumiy nomi va izohi ishlatiladi.
 *
 *  ⚠️ **Matnsiz variantlar** (`circle`, `box`) `aria-label` oladi.
 *  `live` berilsa `role="status"` (muloyim), `alert` berilsa
 *  `role="alert"` (darhol) qo'yiladi — xato uchun ikkinchisi to'g'ri.
 */
export function Status({
  status,
  variant,
  label,
  hint,
  live = false,
  alert = false,
  children,
  className = "",
}: {
  /** Holat kaliti (`ok`, `warn`, `bad`, `info`). Notanish bo'lsa — `info`. */
  status: string;
  /** Ko'rinishni majburan tanlash. Berilmasa — foydalanuvchi sozlamasi. */
  variant?: StatusVariant;
  /** Kontekst matni. Berilmasa — holatning umumiy nomi. */
  label?: string;
  /** Qo'shimcha izoh (faqat `soft`, `outline`, `stack` da ko'rinadi). */
  hint?: string;
  /** O'zgaradigan xabar — ekran o'quvchi muloyim e'lon qiladi
   *  (`role="status"`, `aria-live="polite"`). */
  live?: boolean;
  /** **Xato** xabari — ekran o'quvchi DARHOL e'lon qilsin
   *  (`role="alert"`, ya'ni assertive). `live` dan ustun turadi.
   *
   *  ⚠️ Farq amaliy: `polite` joriy gapni tugatishini kutadi, `assertive`
   *  gapni BO'LADI. Saqlash xatosi uchun kutish noto'g'ri — odam tugmani
   *  qayta bosib, ikkinchi xato yasashi mumkin. Ilgari bu naqsh har
   *  joyda qo'lda `role="alert"` deb yozilardi. */
  alert?: boolean;
  /** Yorliqdan KEYIN qo'shiladigan tugunlar.
   *
   *  ⚠️ Alohida tugun bo'lishi ataylab: `AuthForm` da kutish soniyasi shu
   *  yerda turadi. U `label` satriga qo'shilsa, har soniyada butun xato
   *  qayta e'lon qilinar va ekran o'quvchi uni qayta-qayta o'qib chiqardi.
   *  `label` bir marta, `children` o'z-o'zidan yangilanadi. */
  children?: React.ReactNode;
  className?: string;
}) {
  const locale = useLocale();
  const { appearance } = useCustomizer();
  const def = statusOf(status);
  const Icon = STATUS_ICONS[def.key];
  const style = variant ?? appearance.statusStyle ?? DEFAULT_STATUS_VARIANT;

  if (!Icon) return null;

  const text = label ?? t(locale, def.labelKey);
  const sub = hint ?? t(locale, def.hintKey);
  const { color, soft } = def;
  const announce = alert || live;
  const liveProps = announce
    ? alert
      ? { role: "alert" as const }
      : { role: "status" as const, "aria-live": "polite" as const }
    : {};

  // ── ① Faqat rangli matn ────────────────────────────────────────────
  const textOnly = (
    <span className="rw-status rw-status-text" style={{ color }} {...liveProps}>
      {text}
      {children}
    </span>
  );

  // ── ② Ikonka + rang + matn ─────────────────────────────────────────
  const iconText = (
    <span className="rw-status rw-status-icon" style={{ color }} {...liveProps}>
      <Icon className="size-[1.1em]" />
      <span>{text}{children}</span>
    </span>
  );

  // ── ③ To'ldirilgan nishon ──────────────────────────────────────────
  const badge = (
    <span
      className="rw-status rw-status-badge"
      style={{ color, background: soft }}
      {...liveProps}
    >
      <Icon className="size-[0.95em]" />
      <span>{text}{children}</span>
    </span>
  );

  // ── ④ Rangli doira + oq ikonka ─────────────────────────────────────
  const circle = (
    <span
      className="rw-status rw-status-circle"
      style={{ background: color }}
      title={text}
      role="img"
      aria-label={text}
    >
      <Icon className="size-[0.85em]" />
    </span>
  );

  // ── ⑤ Rangli nuqta + matn ──────────────────────────────────────────
  const dot = (
    <span className="rw-status rw-status-dot" {...liveProps}>
      <i style={{ background: color }} />
      <span>{text}{children}</span>
    </span>
  );

  // ── ⑥ Ramkali kvadrat ──────────────────────────────────────────────
  const box = (
    <span
      className="rw-status rw-status-box"
      style={{ color }}
      title={text}
      role="img"
      aria-label={text}
    >
      <Icon className="size-[1.05em]" />
    </span>
  );

  // ── ⑦ Chap chiziq ──────────────────────────────────────────────────
  // ⚠️ Nom `alert` EMAS: u endi prop (`role="alert"` uchun) va
  // soyada qolsa `announce` hisobi buzilardi.
  const alertBar = (
    <span
      className="rw-status rw-status-alert"
      style={{ borderColor: color, color }}
      {...liveProps}
    >
      <Icon className="size-[1.05em]" />
      <span>{text}{children}</span>
    </span>
  );

  // ── ⑧ Yumshoq fonli karta ──────────────────────────────────────────
  const softCard = (
    <span className="rw-status rw-status-soft" style={{ background: soft, color }} {...liveProps}>
      <Icon className="size-[1.25em]" />
      <span className="rw-status-col">
        <b>{text}{children}</b>
        <em>{sub}</em>
      </span>
    </span>
  );

  // ── ⑨ Ramkali karta ────────────────────────────────────────────────
  const outline = (
    <span className="rw-status rw-status-outline" style={{ borderColor: color, color }} {...liveProps}>
      <Icon className="size-[1.25em]" />
      <span className="rw-status-col">
        <b>{text}{children}</b>
        <em>{sub}</em>
      </span>
    </span>
  );

  // ── ⑩ Katta karta (ustma-ust) ──────────────────────────────────────
  const stack = (
    <span className="rw-status rw-status-stack" style={{ background: soft, color }} {...liveProps}>
      <Icon className="size-[1.6em]" />
      <b>{text}{children}</b>
      <em>{sub}</em>
    </span>
  );

  // ── `auto` — ekranga qarab ─────────────────────────────────────────
  // Uch nusxa chiziladi, CSS faqat bittasini ko'rsatadi. Sabab verdikt
  // bilan bir xil: `matchMedia` SSR'da chaqnash beradi (serverda o'lcham
  // noma'lum), CSS esa buni chaqnashsiz bajaradi.
  if (style === "auto") {
    return (
      <span className={`rw-status-auto ${className}`}>
        <span className="rw-only-mobile">{circle}</span>
        <span className="rw-only-tablet">{iconText}</span>
        <span className="rw-only-desktop">{iconText}</span>
      </span>
    );
  }

  const body =
    style === "text" ? textOnly
    : style === "iconText" ? iconText
    : style === "badge" ? badge
    : style === "circle" ? circle
    : style === "dot" ? dot
    : style === "box" ? box
    : style === "alert" ? alertBar
    : style === "soft" ? softCard
    : style === "outline" ? outline
    : stack;

  return <span className={className}>{body}</span>;
}
