import { CN, ES, GB, KG, KZ, RU, TJ, TR, UZ } from "country-flag-icons/react/3x2";

import type { Locale } from "@/i18n/messages";

/** Til → ISO 3166-1. `en` uchun GB (locale picker an'anasi).
 *  `kaa` da ISO yo'q — Qoraqalpog'iston bayrog'i qo'lda. */
const ISO = {
  uz: UZ,
  ru: RU,
  en: GB,
  kk: KZ,
  ky: KG,
  tg: TJ,
  tr: TR,
  zh: CN,
  es: ES,
} as const;

const FLAG_CLASS = "h-3.5 w-[21px] shrink-0 overflow-hidden rw-radius-sm";

function KarakalpakFlag() {
  return (
    <svg viewBox="0 0 20 14" className={FLAG_CLASS} aria-hidden>
      <rect width="20" height="14" fill="#1eb53a" />
      <rect width="20" height="9.2" fill="#f7c200" />
      <rect width="20" height="4.6" fill="#0099b5" />
      <rect y="4.4" width="20" height="0.4" fill="#ce1126" />
      <rect y="9.2" width="20" height="0.4" fill="#ce1126" />
    </svg>
  );
}

export function LocaleFlag({ code }: { code: Locale }) {
  if (code === "kaa") return <KarakalpakFlag />;
  const Flag = ISO[code];
  return <Flag aria-hidden className={FLAG_CLASS} />;
}
