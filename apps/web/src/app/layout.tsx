import type { Metadata } from "next";
import "./globals.css";
import AppShell from "@/layout/AppShell";
import { LocaleProvider } from "@/i18n/LocaleProvider";
import { getLocale } from "@/i18n/server";
import { DEFAULT_LOCALE } from "@/i18n/messages";

export const metadata: Metadata = {
  title: {
    default: "RankWant — reyting xohlaganlar uchun",
    template: "%s · RankWant",
  },
  description:
    "Sport dasturlash va informatika olimpiadasi platformasi: masala arxivi, " +
    "musobaqa va ochiq reyting.",
};

/** Tema klassini hidratsiyadan OLDIN qo'yadi — aks holda qorong'u
 * sozlamadagi foydalanuvchi har yuklanishda oq chaqnash ko'radi. */
const THEME_INIT = `try{var t=localStorage.getItem("theme");
if(t!=="light")document.documentElement.classList.add("dark")}catch(e){
document.documentElement.classList.add("dark")}`;

/** Uslub ham hidratsiyadan oldin qo'yiladi — `data-style` butun token
 * qatlamini almashtiradi, kechikkanda sahifa ko'z oldida sakrardi. */
const STYLE_INIT = `try{var s=localStorage.getItem("style");
document.documentElement.dataset.style=s||"clay"}catch(e){
document.documentElement.dataset.style="clay"}`;

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const locale = await getLocale();
  return (
    <html lang={locale} suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin=""
        />
        {/* Terminal monospace, editorial serif talab qiladi — uslub
            tanlanmaguncha kerak emas, shu bois `display=swap`. */}
        {/* eslint-disable-next-line @next/next/no-page-custom-font --
            qoida pages router uchun; bu root layout barcha sahifalarga tegishli */}
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Serif:ital,wght@0,400;0,600;1,400&display=swap"
        />
        <script dangerouslySetInnerHTML={{ __html: THEME_INIT }} />
        <script dangerouslySetInnerHTML={{ __html: STYLE_INIT }} />
      </head>
      <body>
        <LocaleProvider locale={locale}>
          <AppShell>{children}</AppShell>
        </LocaleProvider>
      </body>
    </html>
  );
}
