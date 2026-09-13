/** Forma yuklanayotgan paytdagi ko'rinish.
 *
 *  `<Suspense>` bu sahifalarda `useSearchParams` uchun SHART, lekin
 *  fallback berilmasa karta bir lahza butunlay bo'sh qolardi va keyin
 *  to'lib ketardi — sahifa sakragandek ko'rinadi. Skeleton o'sha
 *  bo'shliqni oldindan egallaydi.
 *
 *  `aria-hidden`: bu shakl, ma'lumot emas. Ekran o'quvchi uni o'qishi
 *  shart emas — haqiqiy forma bir zumda keladi.
 */
export function AuthFormSkeleton() {
  return (
    <div className="flex flex-col gap-4" aria-hidden>
      {[0, 1, 2].map((i) => (
        <div key={i} className="flex flex-col gap-1.5">
          <div className="h-4 w-28 rw-radius-sm rw-hover-bg" />
          <div className="h-11 border rw-radius-sm rw-field-bg" />
        </div>
      ))}
      <div className="h-11 rw-radius-sm rw-hover-bg" />
    </div>
  );
}
