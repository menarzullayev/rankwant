import { localNameInfo, t, type Locale } from "@/i18n/messages";

/** O'zbekcha nom yonidagi kichik `uz` belgisi.
 *
 *  Nega kerak (qaror 10): kontent nomlari (mavzu, ko'nikma) faqat
 *  uz/ru/en ustunlarida saqlanadi. `kk`, `zh`, `kaa` va boshqa olti
 *  tilda sayt interfeysi tarjima qilingan, nomlar esa o'zbekcha
 *  qoladi. Belgisiz foydalanuvchi o'zbekcha matnni o'z tilidagi
 *  tarjima deb o'ylaydi — bu jimgina yolg'on.
 *
 *  Belgining O'ZI tarjima qilinmaydi (`uz` — til kodi, hamma joyda
 *  bir xil), lekin uning izohi tarjima qilinadi va `title` bilan
 *  ko'rsatiladi. Ekran o'quvchi uchun matn `sr-only` — nomning
 *  davomi bo'lib o'qiladi.
 */
export type NameRow = { name_uz: string; name_ru: string; name_en: string };

/** Nom + qaytish belgisi — sahifa matni uchun.
 *
 *  Chaqiruv joylari `localNameInfo(...).locale === null &&` shartini
 *  takrorlamasin: shart shu yerda, ya'ni uni o'zgartirish kerak bo'lsa
 *  bitta joyda o'zgaradi. 2026-09-19 gacha bu shart yetti joyda
 *  takrorlanardi va oltitasida umuman yo'q edi.
 */
export function ContentName({ row, locale }: { row: NameRow; locale: Locale }) {
  const info = localNameInfo(row, locale);
  return (
    <>
      {info.text}
      {info.locale === null && <UzFallbackBadge locale={locale} />}
    </>
  );
}

/** Nom + belgi — MATN konteksti uchun.
 *
 *  Native `<option>` ichiga JSX sig'maydi, ya'ni chip o'rniga matn
 *  qo'shimchasi ishlatiladi. Belgining o'zi tarjima qilinadi
 *  (`locale.contentUz`) — qattiq yozilgan `(uz)` bo'lardi, u esa
 *  xitoylik foydalanuvchiga hech narsa aytmaydi.
 */
export function contentNameText(row: NameRow, locale: Locale): string {
  const info = localNameInfo(row, locale);
  return info.locale === null
    ? `${info.text} · ${t(locale, "locale.contentUz")}`
    : info.text;
}

export function UzFallbackBadge({ locale }: { locale: Locale }) {
  const label = t(locale, "content.uzOnly");
  return (
    <>
      <span
        title={label}
        aria-hidden="true"
        className="ml-1.5 shrink-0 rounded rw-chip px-1 align-middle
 text-theme-xs font-semibold uppercase rw-dim-2"
      >
        uz
      </span>
      <span className="sr-only"> ({label})</span>
    </>
  );
}
