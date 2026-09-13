import type { Metadata } from "next";
import { IBM_Plex_Mono, IBM_Plex_Serif } from "next/font/google";
import "./globals.css";
import AppShell from "@/layout/AppShell";
import { LocaleProvider } from "@/i18n/LocaleProvider";
import { getLocale } from "@/i18n/server";
import { DEFAULT_LOCALE } from "@/i18n/messages";
import { messagesFor } from "@/i18n/messages.server";
import type { Me } from "@/lib/api";
import { getSessionUser } from "@/lib/api.server";
import { SITE_URL } from "@/lib/site";

const TITLE = "RankWant — reyting xohlaganlar uchun";

/** Uslub shriftlari — endi o'z domenimizdan beriladi: `next/font`
 *  ularni BUILD vaqtida yuklab oladi va `/_next/static/media/` dan
 *  xizmat qiladi, ya'ni ishlash paytida Google'ga hech qanday so'rov
 *  ketmaydi (ilgari `fonts.googleapis.com` dan render-bloklovchi CSS
 *  olinardi).
 *
 * `preload: false` ATAYLAB. Bu ikki oilani 12 uslubdan faqat ikkitasi
 * ishlatadi (`terminal` va `editorial`), standart uslub esa `clay` —
 * ya'ni ko'pchilik foydalanuvchi ularni umuman ko'rmaydi. Preload
 * bo'lsa brauzer fayllarni DARHOL tortardi; usiz esa `@font-face`
 * faqat haqiqatan ishlatilganda yuklanadi.
 *
 * `cyrillic` — ru/kk/ky/tg uchun, `latin-ext` — tr va qoraqalpoq
 * harflari uchun. Usiz o'sha tillarda matn zaxira shriftga tushardi.
 */
const plexMono = IBM_Plex_Mono({
  subsets: ["latin", "latin-ext", "cyrillic"],
  weight: ["400", "500", "600"],
  variable: "--rw-plex-mono",
  display: "swap",
  preload: false,
});

const plexSerif = IBM_Plex_Serif({
  subsets: ["latin", "latin-ext", "cyrillic"],
  weight: ["400", "600"],
  style: ["normal", "italic"],
  variable: "--rw-plex-serif",
  display: "swap",
  preload: false,
});
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
/** Mavzu rejimi: `light` | `dark` | `system`. Qiymat yo'q bo'lsa — `system`
 *  (D5). `system` OS sozlamasiga ergashadi: OS darajasida qorong'i rejim
 *  ishlatadigan odam har sayt uchun qo'lda o'chirmaydi.
 *
 *  Skript hidratsiyadan OLDIN ishlaydi, shuning uchun `localStorage` dan
 *  o'qiladi (sessiya hali yo'q) — bu `lib/prefs.ts` dagi naqsh bilan bir
 *  xil. `catch` ham qorong'iga tushadi: private rejimda o'qib bo'lmasa,
 *  oq chaqnash ko'rsatishdan ko'ra qorong'i boshlash yaxshi. */
const THEME_INIT = `try{var m=localStorage.getItem("theme")||"system";
var d=m==="dark"||(m==="system"&&window.matchMedia("(prefers-color-scheme: dark)").matches);
if(d)document.documentElement.classList.add("dark")}catch(e){
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
  // Til ham, sessiya ham cookie'ga bog'liq — ketma-ket kutish o'rniga
  // birga o'qiladi. `getSessionUser` cookie bo'lmasa so'rov yubormaydi,
  // ya'ni anonim tashrifchi ortiqcha `/me/` 401 ni ko'rmaydi.
  const [locale, me] = await Promise.all([getLocale(), getSessionUser<Me>()]);

  // Faqat AKTIV tilning lug'ati mijozga ketadi. Ilgari o'ntasi ham JS
  // to'plamida bo'lardi — o'lchandi: 91 kB tarmoqda, holbuki bitta til
  // uchun 34 kB yetadi. U `LocaleProvider` ga PROP bo'lib uzatiladi,
  // inline skript bilan emas: React inline `<script>` elementini RSC
  // uzatmasiga ham qo'shib, lug'at HTML'da ikki nusxada ketardi.
  return (
    <html
      lang={locale}
      className={`${plexMono.variable} ${plexSerif.variable}`}
      suppressHydrationWarning
    >
      <head>
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
        <LocaleProvider locale={locale} dict={messagesFor(locale)}>
          <AppShell initialUser={me}>{children}</AppShell>
        </LocaleProvider>
      </body>
    </html>
  );
}
