import type { Metadata } from "next";
import "./globals.css";
import AppShell from "@/layout/AppShell";
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
 *  sozlamadagi foydalanuvchi har yuklanishda oq chaqnash ko'radi. */
const THEME_INIT = `try{var t=localStorage.getItem("theme");
if(t!=="light")document.documentElement.classList.add("dark")}catch(e){
document.documentElement.classList.add("dark")}`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang={DEFAULT_LOCALE} suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: THEME_INIT }} />
      </head>
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
