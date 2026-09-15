import { Loading } from "@/components/ui/Loading";

/** Forma yuklanayotgan paytdagi ko'rinish.
 *
 *  `<Suspense>` bu sahifalarda `useSearchParams` uchun SHART, lekin
 *  fallback berilmasa karta bir lahza butunlay bo'sh qolardi va keyin
 *  to'lib ketardi — sahifa sakragandek ko'rinadi. Yuklanish ko'rsatkichi
 *  o'sha bo'shliqni oldindan egallaydi.
 *
 *  ⚠️ Ilgari bu yerda qo'lda yasalgan, forma shakliga moslangan skeleton
 *  bor edi (`aria-hidden` bilan). Endi umumiy `Loading` ishlatiladi —
 *  sabab: foydalanuvchi sozlagichda yuklanish ko'rinishini tanlaydi va u
 *  **shu yerda ham** amal qilishi kerak. Forma shakli yo'qoladi, lekin
 *  tanlov izchil bo'ladi; `aria-hidden` ham kerak emas, chunki `Loading`
 *  `role="status"` beradi va kutishni ekran o'quvchiga aytadi. */
export function AuthFormSkeleton() {
  return <Loading variant="skeleton" lines={4} />;
}
