"use client";

import { useRouter } from "next/navigation";
import { useCallback, useEffect, useRef } from "react";

import { EVENT_RESYNC, EVENT_VERDICT, useEventStream } from "@/lib/useEventStream";

/** Hodisalar to'planishi — bitta RSC so'rovi uchun oyna.
 *
 * ⚠️ Sabab o'lchovli: gavjum musobaqada 500 verdict/10 s bo'ladi. Har
 * hodisa uchun alohida `router.refresh()` yuborilsa, oqim yuklamani
 * **kamaytirish** o'rniga ko'paytirardi — har yangilanish butun sahifani
 * qayta render qiladi. */
const REFRESH_DEBOUNCE_MS = 400;

type VerdictPayload = { problem?: string };

/** Jonli yangilanish — ADR-0029. Ko'rinadigan hech narsa chizmaydi.
 *
 * ⚠️ **Hodisa yuki holatga aylantirilmaydi.** `verdict` kelsa biz qatorni
 * qo'lda yangilamaymiz — server komponentini qayta o'qiymiz. Sabab
 * ADR-0029 §9: oqim optimallashtirish, haqiqat manbasi emas. Shu tufayli
 * yo'qolgan hodisa noto'g'ri holatga olib kelmaydi.
 */
export function AttemptLive({ problem }: { problem: string }) {
  const router = useRouter();
  const timer = useRef<number | null>(null);

  const refresh = useCallback(() => {
    if (timer.current !== null) return;
    timer.current = window.setTimeout(() => {
      timer.current = null;
      router.refresh();
    }, REFRESH_DEBOUNCE_MS);
  }, [router]);

  useEffect(
    () => () => {
      if (timer.current !== null) window.clearTimeout(timer.current);
    },
    [],
  );

  useEventStream({
    onEvent: (name, data) => {
      //: `resync` — replay buferi yetmadi, holat ishonchsiz: darhol o'qiymiz.
      if (name === EVENT_RESYNC) {
        refresh();
        return;
      }
      if (name !== EVENT_VERDICT) return;
      //: Boshqa masalaning verdikti bu sahifaga tegishli emas —
      //: usiz butun platforma oqimi har sahifani silkitardi.
      const payload = data as VerdictPayload | null;
      if (payload?.problem && payload.problem !== problem) return;
      refresh();
    },
  });

  return null;
}
