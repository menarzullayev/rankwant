"use client";

import { Status as StatusBadge } from "@/components/ui/Status";

/** Amal natijasi uchun qulay qobiq — global `Status` (D60) ustidan.
 *
 *  ⚠️ Global `Status` o'nta ko'rinishni biladi, lekin chaqiruvchilar
 *  ko'pincha «xato bo'lsa ko'rsat, saqlangan bo'lsa tasdiqla» naqshini
 *  xohlaydi. Ilgari bu naqsh `features/account/components/section-kit.tsx`
 *  ichida alohida nusxa sifatida yashardi va boshqa feature'larni
 *  sozlamalar bo'limiga bog'lardi. Endi u umumiy qatlamda. */

export function Status({
  error,
  done,
  text,
}: {
  error?: string;
  done?: boolean;
  text?: string;
}) {
  if (error) return <StatusBadge status="bad" variant="soft" label={error} alert />;
  if (done) return <StatusBadge status="ok" variant="text" live />;
  return null;
}

/** Kichik izoh satri — bo'lim/form ostida. */
export function Hint({ children }: { children: React.ReactNode }) {
  return <p className="text-theme-sm rw-dim">{children}</p>;
}
