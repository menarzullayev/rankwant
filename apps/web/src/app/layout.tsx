import type { Metadata } from "next";
import "./globals.css";
import AppShell from "@/layout/AppShell";
import { LocaleProvider } from "@/i18n/LocaleProvider";
import { getLocale } from "@/i18n/server";
import { DEFAULT_LOCALE } from "@/i18n/messages";
import { SITE_URL } from "@/lib/site";

const TITLE = "RankWant — reyting xohlaganlar uchun";
const DESCRIPTION =
  "Sport dasturlash va informatika olimpiadasi platformasi: masala arxivi, " +
  "musobaqa va ochiq reyting.";

/** Ijtimoiy ulashish rasmi — `tools/og-image.py` bilan generatsiya
 *  qilinadi (1200×630). Statik: har sahifa uchun chekka render narxini
 *  to'lamaslik uchun zaxira qatlam bo'lib turadi, qimmatli marshrutlar
 *  esa o'z dinamik rasmini ustidan yozadi. */
const OG_IMAGE = "/brand/og-default.png";

/** Tuzilmaviy ma'lumot (schema.org).
 *
 *  Qidiruv tizimiga sayt NIMA ekanini mashina o'qiydigan shaklda
 *  aytadi: brend, logotip va sayt nomi. Uchala raqobatchida ham yo'q,
 *  ya'ni bu yerda ustunlik bor.
 *
 *  Ataylab faqat `Organization` + `WebSite`: `Event` va
 *  `LearningResource` sahifa darajasida qo'shiladi, chunki ular
 *  sahifaning haqiqiy mazmunini bilishni talab qiladi. */
const JSON_LD = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": `${SITE_URL}/#organization`,
      name: "RankWant",
      url: SITE_URL,
      logo: `${SITE_URL}/brand/mark-512.png`,
      description: DESCRIPTION,
    },
    {
      "@type": "WebSite",
      "@id": `${SITE_URL}/#website`,
      url: SITE_URL,
      name: "RankWant",
      description: DESCRIPTION,
      publisher: { "@id": `${SITE_URL}/#organization` },
    },
  ],
};

export const metadata: Metadata = {
  // `metadataBase` bo'lmasa Next nisbiy `og:url` yozadi va Telegram
  // kabi mijozlar uni o'qiy olmaydi — ulashilgan havola yalang'och
  // manzil bo'lib chiqadi.
  metadataBase: new URL(SITE_URL),
  title: { default: TITLE, template: "%s · RankWant" },
  description: DESCRIPTION,
  // O'z-o'ziga havola qiluvchi canonical: `?` bilan kelgan filtrli
  // variantlar va til cookie'si bilan ochilgan nusxalar bitta manzilga
  // yig'iladi. `"./"` — «shu sahifaning o'zi»; har sahifa uchun alohida
  // yozib chiqish shart emas.
  alternates: { canonical: "./" },
  // Ikonkalar `public/brand/` da tayyor turadi (`tools/brand.py`), lekin
  // shu yerda e'lon qilinmasa brauzer ularni UMUMAN so'ramaydi: yorliq
  // belgisi, iOS bosh ekrani va PWA ishlamay qoladi.
  icons: {
    icon: [
      { url: "/brand/mark-32.png", sizes: "32x32", type: "image/png" },
      { url: "/brand/mark-96.png", sizes: "96x96", type: "image/png" },
    ],
    apple: [
      { url: "/brand/mark-180.png", sizes: "180x180", type: "image/png" },
    ],
  },
  openGraph: {
    type: "website",
    siteName: "RankWant",
    title: TITLE,
    description: DESCRIPTION,
    url: "/",
    images: [
      { url: OG_IMAGE, width: 1200, height: 630, alt: TITLE },
    ],
  },
  // `summary_large_image` — rasm karta bo'ylab cho'ziladi. `summary`
  // bilan kichik kvadrat chiqadi va 1200×630 rasm mazmunsiz qolardi.
  twitter: {
    card: "summary_large_image",
    title: TITLE,
    description: DESCRIPTION,
    images: [OG_IMAGE],
  },
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
        <script
          type="application/ld+json"
          // Tuzilmaviy ma'lumot — Next'ning `metadata` qatlami buni
          // chiqarmaydi, shuning uchun qo'lda. `JSON.stringify` XSS
          // bermaydi: obyekt build paytida qurilgan, foydalanuvchi
          // kiritgan matn yo'q.
          dangerouslySetInnerHTML={{ __html: JSON.stringify(JSON_LD) }}
        />
      </head>
      <body>
        <LocaleProvider locale={locale}>
          <AppShell>{children}</AppShell>
        </LocaleProvider>
      </body>
    </html>
  );
}
