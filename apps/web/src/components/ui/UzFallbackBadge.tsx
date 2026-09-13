import { t, type Locale } from "@/i18n/messages";

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
