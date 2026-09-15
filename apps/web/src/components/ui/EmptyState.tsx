"use client";

import { EMPTY_ICONS } from "@/icons/phosphor";

/** Bo'sh holat va xato ekrani (D61).
 *
 *  Uchta shakl — foydalanuvchi shularni tanladi. Bu **foydalanuvchi
 *  sozlamasi emas**: shakl vaziyatga qarab tanlanadi (quyidagi jadval).
 *  Foydalanuvchi sozlamasi bo'lishi uchun shakllar bir xil vaziyatda
 *  almashinishi kerak edi — bu yerda esa ular turli vaziyatlar uchun.
 *
 *  | Variant        | Ko'rinish                          | Qayerda                     |
 *  |----------------|------------------------------------|-----------------------------|
 *  | `full`         | ikonka + sarlavha + tavsiya + tugma| asosiy ro'yxat, dashboard   |
 *  | `card`         | ramkali karta, yuqoridagi to'rtlik | sahifaning markaziy maydoni |
 *  | `illustration` | katta och doira + ikonka + matn    | landing, onboarding, 404    |
 *
 *  ⚠️ **To'rt qismning hammasi shart emas, lekin `hint` va `action`
 *  tavsiya etiladi.** Sabab: bo'sh sahifa foydalanuvchiga «nima bo'ldi?»
 *  va «endi nima qilaman?» degan ikki savolni qoldiradi. Faqat sarlavha
 *  berilsa, ikkinchisiga javob bo'lmaydi va odam orqaga qaytadi.
 *
 *  ⚠️ Ikonka `aria-hidden` (matn yonida), ya'ni ekran o'quvchi ortiqcha
 *  narsa o'qimaydi. Sarlavha `<b>`, tavsiya `<em>` — uslub `globals.css`
 *  da, ya'ni sahifa o'z shriftini o'ylab topmaydi.
 */
export type EmptyStateVariant = "full" | "card" | "illustration";

export function EmptyState({
  icon = "empty",
  title,
  hint,
  action,
  variant = "full",
  className = "",
}: {
  /** `EMPTY_ICONS` kaliti — sahifa o'zi ikonka o'ylab topmasin. */
  icon?: keyof typeof EMPTY_ICONS;
  /** Nima bo'ldi — qisqa sarlavha. */
  title: string;
  /** Endi nima qilaman — bir qatorli tavsiya. */
  hint?: string;
  /** Amal tugmasi. `href` bo'lsa havola, aks holda tugma. */
  action?: { label: string; href?: string; onClick?: () => void };
  variant?: EmptyStateVariant;
  className?: string;
}) {
  const Icon = EMPTY_ICONS[icon] ?? EMPTY_ICONS.empty;
  const shape = variant;

  const button = action
    ? action.href
      ? (
          <a className="rw-empty-btn" href={action.href}>
            {action.label}
          </a>
        )
      : (
          <button type="button" className="rw-empty-btn" onClick={action.onClick}>
            {action.label}
          </button>
        )
    : null;

  const text = (
    <>
      <b>{title}</b>
      {hint && <em>{hint}</em>}
    </>
  );

  if (shape === "illustration") {
    return (
      <div className={`rw-empty rw-empty-illu ${className}`}>
        <span className="rw-empty-illu-bg">
          <Icon className="size-[4.5em]" />
        </span>
        {text}
        {button}
      </div>
    );
  }

  if (shape === "card") {
    return (
      <div className={`rw-empty rw-empty-card ${className}`}>
        <span className="rw-empty-soft">
          <Icon className="size-[1.75em]" />
        </span>
        {text}
        {button}
      </div>
    );
  }

  return (
    <div className={`rw-empty rw-empty-full ${className}`}>
      <Icon className="size-[2em]" />
      {text}
      {button}
    </div>
  );
}
