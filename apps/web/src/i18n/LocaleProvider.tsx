"use client";

import { createContext, useContext } from "react";

import { DEFAULT_LOCALE, registerMessages, type Locale, type MessageKey } from "./messages";

const LocaleContext = createContext<Locale>(DEFAULT_LOCALE);

/** Mijoz komponentlari `cookies()` ni o'qiy olmaydi — til yuqoridan beriladi.
 *
 *  Lug'at ham shu yerda keladi va SHU YERDA ro'yxatga olinadi: ilgari
 *  `layout.tsx` uni inline skript bilan uzatardi, lekin React o'sha
 *  elementni RSC uzatmasiga ham qo'shib, lug'at HTML'da IKKI NUSXADA
 *  ketardi (o'lchandi). Prop orqali esa faqat bir marta ketadi.
 *
 *  Ro'yxatga olish render paytida, bolalar chizilishidan OLDIN bo'ladi —
 *  shuning uchun pastdagi har qanday komponent `t()` ni xavfsiz
 *  chaqiradi. Amal idempotent (bir xil kalitga bir xil qiymat), ya'ni
 *  StrictMode'ning ikki marta chizishi ham zarar qilmaydi. */
export function LocaleProvider({
  locale,
  dict,
  children,
}: {
  locale: Locale;
  dict: Record<MessageKey, string>;
  children: React.ReactNode;
}) {
  registerMessages(locale, dict);
  return (
    <LocaleContext.Provider value={locale}>{children}</LocaleContext.Provider>
  );
}

export function useLocale(): Locale {
  return useContext(LocaleContext);
}
