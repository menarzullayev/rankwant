"use client";

import { useEffect, useRef } from "react";

/** Telegram OAuth EMAS: u o'z widgetini chizadi va imzolangan ma'lumotni
 *  to'g'ridan-to'g'ri callback'ga yuboradi. Shu sababli bu yerda havola
 *  emas, provayderning o'z skripti turadi.
 *
 *  `next` — qaytish manzili (qaror 1). Sessiya bosqichi yo'q (Google va
 *  GitHub'dan farqli), shuning uchun manzil `data-auth-url` ga
 *  qo'shiladi: Telegram o'z imzosini o'sha manzilga qo'shib yuboradi. */
export function TelegramButton({ bot, next }: { bot: string; next?: string | null }) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const host = ref.current;
    if (!host || host.childElementCount > 0) return;
    const script = document.createElement("script");
    script.async = true;
    script.src = "https://telegram.org/js/telegram-widget.js?22";
    script.setAttribute("data-telegram-login", bot);
    script.setAttribute("data-size", "medium");
    script.setAttribute("data-radius", "8");
    // Bildirishnomalar Telegram'ga ham boradi (sozlamalar → Bildirishnomalar):
    // bot odamga faqat u ruxsat bergan bo'lsa yoza oladi.
    script.setAttribute("data-request-access", "write");
    script.setAttribute(
      "data-auth-url",
      `${window.location.origin}/api/v1/auth/telegram/callback/${
        next ? `?next=${encodeURIComponent(next)}` : ""
      }`,
    );
    host.appendChild(script);
  }, [bot, next]);

  // Vidjet Telegram niki: kengligini biz belgilay olmaymiz, shuning
  // uchun katak qolgan ikkitasi bilan bir balandlikda va markazda
  // turadi, ichidagisi esa sig'masa qisqaradi.
  return (
    <div
      ref={ref}
      className="flex h-11 items-center justify-center overflow-hidden rw-radius-sm"
    />
  );
}

