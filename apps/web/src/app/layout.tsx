import type { Metadata } from "next";
import { cookies } from "next/headers";
import {
  DM_Sans,
  Lexend,
  IBM_Plex_Mono,
  IBM_Plex_Serif,
  Inter,
  Plus_Jakarta_Sans,
  Roboto,
} from "next/font/google";
import AppShell from "@/layout/AppShell";
import { LocaleProvider } from "@/i18n/LocaleProvider";
import { localeAlternatesFor } from "@/i18n/locale-alternates.server";
import { getLocaleState } from "@/i18n/server";
import { dictionaryUrl } from "@/i18n/messages.server";
import type { Me } from "@/lib/api";
import { api, type AppearancePrefs } from "@/lib/api";
import { getSessionUser } from "@/lib/api.server";
import { STYLE_IDS, type StyleId } from "@/layout/styles";
import { styleInit, teamDefaultLiteral } from "@/lib/theme/first-paint";
import { MARKUP_COOKIE, parseMarkupCookie } from "@/lib/prefs";
import { SITE_INDEXABLE, SITE_URL } from "@/lib/site";

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

/** Foydalanuvchi tanlaydigan shriftlar (D13).
 *
 *  ⚠️ `preload: false` — SHART: `next/font` fayllarni o'zimizda saqlaydi
 *  (tashqi so'rov yo'q, maxfiylik saqlanadi), lekin preload qilinsa
 *  brauzer TO'RTALASINI ham yuklab olardi. Usiz faqat tanlangani
 *  yuklanadi — `@font-face` e'lon qilinadi, lekin ishlatilmaguncha
 *  so'ralmaydi.
 *
 *  Uslublar o'z shriftini saqlaydi (D14): `[data-font]` faqat neytral
 *  uslublarga ta'sir qiladi, chunki `globals.css` da `[data-style]`
 *  bloklari `--rw-font` ni o'ziga yozadi va u ustun turadi.
 */
const inter = Inter({
  subsets: ["latin", "latin-ext", "cyrillic"],
  weight: ["400", "500", "600"],
  variable: "--rw-inter",
  display: "swap",
  preload: false,
});

const jakarta = Plus_Jakarta_Sans({
  subsets: ["latin", "latin-ext"],
  weight: ["400", "500", "600"],
  variable: "--rw-jakarta",
  display: "swap",
  preload: false,
});

const roboto = Roboto({
  subsets: ["latin", "latin-ext", "cyrillic"],
  weight: ["400", "500", "700"],
  variable: "--rw-roboto",
  display: "swap",
  preload: false,
});

const dmSans = DM_Sans({
  subsets: ["latin", "latin-ext"],
  weight: ["400", "500", "600"],
  variable: "--rw-dm-sans",
  display: "swap",
  preload: false,
});

/** O'qish qiyinchiligi uchun (D52). Lexend — harf shakllari ataylab
 *  bir-biridan uzoq qilib chizilgan, so'zlar "yopishib" ko'rinmaydi.
 *  Bu shunchaki "boshqa shrift" emas: tadqiqotlar o'qish tezligini
 *  sezilarli oshirishini ko'rsatgan, shuning uchun u alohida turadi —
 *  umumiy shrift ro'yxatiga aralashmaydi. */
const lexend = Lexend({
  subsets: ["latin", "latin-ext"],
  weight: ["400", "500", "600"],
  variable: "--rw-lexend",
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

export async function generateMetadata(): Promise<Metadata> {
  // `metadataBase` bo'lmasa Next nisbiy `og:url` yozadi va Telegram
  // kabi mijozlar uni o'qiy olmaydi — ulashilgan havola yalang'och
  // manzil bo'lib chiqadi.
  //
  // `?lang=` self-canonical + hreflang (HITL 2026-09-20). Filtr query
  // (`contest`, `page`) canonical'ga kirmaydi — nisbiy `./` yo'lni
  // oladi, `LANG_PARAM_HEADER` esa faqat havola tilini qo'shadi.
  return {
    metadataBase: new URL(SITE_URL),
    title: { default: TITLE, template: "%s · RankWant" },
    description: DESCRIPTION,
    // Until launch every page is noindex, nofollow (see SITE_INDEXABLE).
    robots: SITE_INDEXABLE ? undefined : { index: false, follow: false },
    alternates: await localeAlternatesFor("./"),
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
}

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

/** Sozlagich tanlovi — hidratsiyadan OLDIN, chaqnashsiz.
 *
 *  Accent HISOBLANGAN holda saqlanadi (`rw:accent`), chunki uni hosil
 *  qilish uchun fon yorqinligini o'lchash kerak — bu yerda DOM hali
 *  tayyor emas. Keshlangan qiymat faqat USLUB mos kelsa qo'llanadi:
 *  D10 bo'yicha rang uslubga bog'liq, ya'ni uslub almashsa accent ham
 *  o'zgaradi va eski qiymat noto'g'ri bo'lardi.
 *
 *  Hech qanday xato ko'rsatilmaydi: bu bezak, sinishi mumkin emas.
 *
 *  ⚠️ CHEGARA QO'YILADI. Ilgari `size` to'g'ridan-to'g'ri yozilardi va
 *  buzilgan `localStorage` (`size: 9999`) ildiz shriftini 1599 px ga
 *  chiqarib, sahifani o'qib bo'lmas holga keltirardi — o'lchandi.
 *  Qiymatlar `lib/theme/typography.ts` dagi `SIZE_MIN/SIZE_MAX/SIZE_STEP`
 *  bilan MOS bo'lishi shart: bu satr SSR paytida, modul importidan oldin
 *  bajariladi, shuning uchun funksiyani chaqirib bo'lmaydi. */
// With nothing saved on this device, the team default (D37) applies here as
// well: font, density and the rest. Before, it existed only in the panel's
// state (APP-14).
function appearanceInit(teamDefault: AppearancePrefs): string {
  return `try{
var r=document.documentElement;
var a=JSON.parse(localStorage.getItem("rw:appearance")||${teamDefaultLiteral(teamDefault)});
if(a.font)r.dataset.font=a.font;
if(a.density)r.dataset.density=a.density;
var sz=(typeof a.size==="number"&&isFinite(a.size))?Math.min(150,Math.max(75,Math.round(a.size/5)*5)):100;
if(sz!==100)r.style.fontSize=sz+"%";
r.dataset.nav=(a.navMode==="topnav")?"topnav":"sidenav";
r.dataset.navShape=(a.navShape==="slim"||a.navShape==="stacked")?a.navShape:"default";
if(a.card&&a.card!=="default")r.dataset.card=a.card;
if(a.pattern&&a.pattern!=="none")r.dataset.pattern=a.pattern;
var VD=["auto","badge","plain","icon","full","circle","dot","box","bar","percent","card"];
if(VD.indexOf(a.verdictStyle)>0)r.dataset.verdict=a.verdictStyle;
var ST=["auto","text","iconText","badge","circle","dot","box","alert","soft","outline","stack"];
if(ST.indexOf(a.statusStyle)>0)r.dataset.status=a.statusStyle;
var LD=["spinner","ring","skeleton","shimmer","dotsBounce","dotsFade","bars","iconSpin","pulseIcon","progress"];
if(LD.indexOf(a.loadingStyle)>=0)r.dataset.loading=a.loadingStyle;
// Ikonka to'plami (D10). Atribut — ko'rinadigan iz; ikonkani React
// almashartiradi. Standart (lucide) uchun atribut yozilmaydi.
var IP=["lucide","phosphor","phosphorSolid","phosphorDuotone","heroicons","heroiconsSolid","tabler","bootstrap","remix","simple"];
if(IP.indexOf(a.iconPack)>0)r.dataset.iconPack=a.iconPack;
var OV=["qogoz","soyabon","projektor","orol"];
if(OV.indexOf(a.overlayStyle)>0)r.dataset.overlay=a.overlayStyle;
var FM=["maydon","qator","karta","jadval","orol"];
if(FM.indexOf(a.formStyle)>0)r.dataset.form=a.formStyle;
// Markup o'zgaruvchi uchtasini cookie'ga ham yozamiz (D61). Sabab: SSR
// ularni cookie'dan o'qiydi, ya'ni cookie yo'q bo'lsa server standart
// ko'rinishni chizadi va hidratsiya buziladi. Bu qator ESKI
// foydalanuvchilar uchun bir martalik ko'prik: localStorage da qiymat
// bor, cookie hali yo'q. Keyin rememberAppearance ikkalasini birga
// yozadi, ya'ni bu shart bajarilgan holda qoladi.
// D62: overlay/form dataset only — o= and f= stay out of rw:markup.
try{var m=[];if(VD.indexOf(a.verdictStyle)>0)m.push("v="+a.verdictStyle);if(ST.indexOf(a.statusStyle)>0)m.push("s="+a.statusStyle);if(LD.indexOf(a.loadingStyle)>=0)m.push("l="+a.loadingStyle);if(IP.indexOf(a.iconPack)>0)m.push("p="+a.iconPack);if(m.length)document.cookie="rw:markup="+m.join("&")+";path=/;max-age=31536000;SameSite=Lax";}catch(e){}
var k=JSON.parse(localStorage.getItem("rw:a11y")||"{}");
if(k.vision&&k.vision!=="normal")r.dataset.vision=k.vision;
if(k.motion==="reduce")r.dataset.motion="reduce";
if(k.bigTargets)r.dataset.targets="big";
if(k.strongFocus)r.dataset.focus="strong";
var c=JSON.parse(localStorage.getItem("rw:accent")||"null");
if(c&&c.style===r.dataset.style){
r.style.setProperty("--rw-accent",c.accent);
r.style.setProperty("--rw-accent-fg",c.fg);
r.style.setProperty("--rw-accent-soft",c.soft);
r.style.setProperty("--rw-accent-ink",c.ink);}
}catch(e){}`;
}

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // Til ham, sessiya ham cookie'ga bog'liq — ketma-ket kutish o'rniga
  // birga o'qiladi. `getSessionUser` cookie bo'lmasa so'rov yubormaydi,
  // ya'ni anonim tashrifchi ortiqcha `/me/` 401 ni ko'rmaydi.
  // Standart ko'rinish (D37) SERVERDA olinadi va prop bo'lib uzatiladi.
  // Mijozda so'ralsa, u kelguncha standart ko'rinish chaqnaydi; bundan
  // tashqari bu qiymat `useState` boshlang'ich qiymatida kerak, ya'ni
  // sinxron bo'lishi shart.
  // Markup o'zgaruvchi sozlamalar cookie'dan (D61). Sabab `MARKUP_COOKIE`
  // da: ular HTML tuzilishini o'zgartiradi, ya'ni SSR ham ularni bilishi
  // shart — aks holda React hidratsiya xatosi beradi.
  const [cookieStore, { locale, auto }, me, siteAppearance] = await Promise.all([
    cookies(),
    getLocaleState(),
    getSessionUser<Me>(),
    api
      .siteAppearance()
      .then((row) => row.appearance)
      .catch(() => ({}) as AppearancePrefs),
  ]);
  const markupAppearance = parseMarkupCookie(cookieStore.get(MARKUP_COOKIE)?.value);

  // A style the codebase does not know falls back to `clay`: a stale team
  // default must not leave `data-style` pointing at no stylesheet.
  const teamStyle = STYLE_IDS.includes(siteAppearance.style as StyleId)
    ? (siteAppearance.style as StyleId)
    : "clay";

  // Faqat AKTIV tilning lug'ati mijozga ketadi. Ilgari o'ntasi ham JS
  // to'plamida bo'lardi — o'lchandi: 91 kB tarmoqda, holbuki bitta til
  // uchun 34 kB yetadi. Since 2026-09-18 it is a separate cached file, not
  // part of the page. As a `LocaleProvider` prop it was serialized into
  // every HTML response: 72 kB of 142 kB, and a third of the render CPU. An
  // inline script would be worse, because React copies inline scripts into
  // the RSC payload as well. Only the address travels now.
  const dictionary = dictionaryUrl(locale);
  return (
    <html
      lang={locale}
      className={`${plexMono.variable} ${plexSerif.variable} ${inter.variable} ${jakarta.variable} ${roboto.variable} ${dmSans.variable} ${lexend.variable}`}
      suppressHydrationWarning
    >
      <head>
        <script dangerouslySetInnerHTML={{ __html: THEME_INIT }} />
        <script dangerouslySetInnerHTML={{ __html: styleInit(teamStyle) }} />
        <script dangerouslySetInnerHTML={{ __html: appearanceInit(siteAppearance) }} />
        {/* Async: it must not block the first paint. If it has not run by
            hydration, `LocaleProvider` waits for it. */}
        <script src={dictionary} async />
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
        <LocaleProvider locale={locale} dictionaryUrl={dictionary} auto={auto}>
          <AppShell
            initialUser={me}
            siteAppearance={siteAppearance}
            markupAppearance={markupAppearance}
          >
            {children}
          </AppShell>
        </LocaleProvider>
      </body>
    </html>
  );
}
