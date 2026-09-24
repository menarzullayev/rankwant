/** Skelet yuklanish (S19).
 *
 * Sahifa `force-dynamic`, ya'ni har o'tishda server javobini kutadi.
 * Skeletsiz bu paytda ekran bo'sh qoladi va keyin jadval paydo bo'lib
 * layout sakraydi. Skelet jadvalning O'Z shaklini takrorlaydi — shunda
 * sakrash bo'lmaydi.
 *
 * `animate-pulse` ATAYLAB ishlatilmadi: `prefers-reduced-motion` ni
 * hurmat qilish uchun statik fon yetarli, harakat esa bu yerda hech
 * qanday ma'no tashimaydi.
 */
export default function Loading() {
  return (
    <div className="space-y-6" aria-busy="true">
      <div className="h-7 w-64 rw-radius-sm rw-field-bg" />

      <div className="flex flex-wrap gap-2">
        {Array.from({ length: 7 }).map((_, index) => (
          <div key={index} className="h-6 w-16 rw-radius-sm rw-field-bg" />
        ))}
      </div>

      <div className="rw-radius overflow-hidden border rw-divider">
        <div className="h-9 rw-field-bg" />
        {Array.from({ length: 10 }).map((_, index) => (
          <div key={index} className="h-11 border-t rw-divider rw-field-bg opacity-60" />
        ))}
      </div>
    </div>
  );
}
