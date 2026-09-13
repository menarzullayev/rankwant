"use client";

import { createContext, useContext } from "react";

import { DEFAULT_LOCALE, registerMessages, type Locale, type MessageKey } from "./messages";

const LocaleContext = createContext<Locale>(DEFAULT_LOCALE);
/** Til avtomatik aniqlanganmi — «Avtomatik» variantining belgisi shu.
 *
 *  `locale` doim ANIQ til bo'ladi (`Accept-Language` dan yechilgan),
 *  ya'ni qaysi holatdaligini faqat shu bayroq bildiradi. */
const AutoContext = createContext<boolean>(true);

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
  auto = true,
  children,
}: {
  locale: Locale;
  dict: Record<MessageKey, string>;
  /** Til `Accept-Language` dan aniqlanganmi (ya'ni odam tanlamaganmi). */
  auto?: boolean;
  children: React.ReactNode;
}) {
  // `evict = true`: KLIENTDA faqat aktiv til kerak, ya'ni oldingi
  // lug'atni o'chirish xotirani tejaydi. Serverda esa bu bayroq
  // qo'yilmaydi — `messages.server.ts` o'nta tilni ham ro'yxatga oladi
  // va ularning barchasi birinchi SSR chizishida kerak bo'ladi.
  registerMessages(locale, dict, true);
  return (
    <AutoContext.Provider value={auto}>
      <LocaleContext.Provider value={locale}>{children}</LocaleContext.Provider>
    </AutoContext.Provider>
  );
}

export function useLocale(): Locale {
  return useContext(LocaleContext);
}

export function useLocaleAuto(): boolean {
  return useContext(AutoContext);
}
