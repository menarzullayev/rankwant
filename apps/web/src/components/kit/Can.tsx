"use client";

import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";

/** Huquq tekshiruvi — bitta joyda, takrorlanmasin.
 *
 *  Nega kerak: `is_staff` sharti ilgari uch joyda qo'lda yozilgan edi
 *  (`admin/layout.tsx`, `layout/UserMenu.tsx`, `kit/CommandPalette.tsx`).
 *  Uchtasi bir xil mantiqni takrorlardi, ya'ni huquq qoidasi o'zgarsa
 *  (masalan `moderator` guruhi qo'shilsa) uchtasini ham topib tahrirlash
 *  kerak bo'lardi — biri albatta o'tkazib yuborilardi.
 *
 *  ⚠️ Bu **UI qatlami**, himoya emas. Haqiqiy tekshiruv API'da
 *  (`core/permissions.py`: `HasScope`, `StaffGroup`). Bu komponent faqat
 *  ko'rinishni yashiradi — backend ruxsat bermasa, so'rov baribir 403
 *  qaytadi.
 *
 *  Uch xil ishlatish:
 *
 *  ```tsx
 *  <Can perm="staff">…</Can>              // ruxsat bo'lsa ko'rsatadi
 *  <Can perm="staff" fallback={<p>…</p>}/> // aks holda muqobil
 *  const ok = useCan("staff");            // shartsiz o'qish
 *  ```
 */
export type Permission = "staff" | "authenticated";

/** Bitta huquqni shartsiz o'qiydi (hook — shartsiz chaqirilishi kerak).
 *
 *  `ready` — sessiya aniqlanmaguncha `false` qaytaradi: aks holda
 *  sahifa bir kadr «ruxsat yo'q» ko'rsatib, keyin sakrab qolardi. */
export function useCan(perm: Permission): boolean {
  const { user, ready } = useSession();
  if (!ready) return false;
  if (perm === "authenticated") return user !== null;
  return user?.is_staff === true;
}

export function Can({
  perm,
  children,
  fallback = null,
}: {
  /** Kerakli huquq — `Permission` ro'yxatidan. */
  perm: Permission;
  /** Ruxsat bo'lganda ko'rsatiladigan kontent. */
  children: React.ReactNode;
  /** Ruxsat bo'lmasa ko'rsatiladigan muqobil. Standart — hech nima. */
  fallback?: React.ReactNode;
}) {
  const allowed = useCan(perm);
  return <>{allowed ? children : fallback}</>;
}

/** Ruxsat yo'qligi ekrani — `Can` uchun tayyor `fallback`.
 *
 *  Sahifa darajasida ishlatiladi: `admin/layout.tsx` avval qo'lda
 *  `Card` + matn chizardi, ya'ni bu ham nusxa edi. */
export function Forbidden() {
  const locale = useLocale();
  return (
    <p className="text-theme-sm rw-dim" role="alert">
      {t(locale, "admin.forbidden")}
    </p>
  );
}
