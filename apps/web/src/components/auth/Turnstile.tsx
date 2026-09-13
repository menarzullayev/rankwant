"use client";

import { useCallback, useEffect, useRef, useState } from "react";

/** Cloudflare Turnstile — KO'RINMAS rejim (9-qaror).
 *
 * Foydalanuvchi odatda hech narsa ko'rmaydi: Cloudflare fonida token
 * beradi va u formaga qo'shilib ketadi. Faqat shubhali holatda Cloudflare
 * o'zi kichik tekshiruv oynasini chiqaradi.
 *
 * NEGA token bo'lmasa ham forma yuboriladi: skript yuklanmasa yoki
 * Cloudflare javob bermasa widget JIM qoladi. Token to'ldirilmasdan
 * yuborilgan so'rovni SERVER rad etadi (`TURNSTILE_FAIL_OPEN` bilan
 * boshqariladi) — ya'ni qaror bitta joyda, serverda qoladi. Agar
 * klientda «token yo'q — yubormaymiz» deb qo'yilsa, Turnstile
 * ishlamagan kunda sayt ham ishlamasdi.
 *
 * `siteKey` bo'sh bo'lsa (sozlanmagan) komponent hech narsa qilmaydi.
 */

type TurnstileApi = {
  render: (
    el: HTMLElement,
    opts: {
      sitekey: string;
      callback: (token: string) => void;
      "error-callback"?: () => void;
      "expired-callback"?: () => void;
      theme?: string;
      size?: string;
    },
  ) => string;
  remove: (id: string) => void;
};

declare global {
  interface Window {
    turnstile?: TurnstileApi;
  }
}

const SCRIPT_ID = "cf-turnstile-api";
const SRC = "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit";

export function Turnstile({
  siteKey,
  onToken,
}: {
  siteKey: string;
  onToken: (token: string) => void;
}) {
  const box = useRef<HTMLDivElement>(null);
  const [ready, setReady] = useState(false);

  // `onToken` — ota-komponentdagi `setCaptcha.bind(...)` bilan bir xil
  // barqaror havola bo'lishi kafolatlanmagan, ya'ni uni effekt
  // bog'liqligiga qo'ysak har renderda vidjet QAYTA yasalardi (token
  // yo'qoladi). Shuning uchun havola ref orqali uzatiladi va effekt
  // faqat `ready`/`siteKey` ga bog'lanadi.
  const emit = useRef(onToken);
  useEffect(() => {
    emit.current = onToken;
  }, [onToken]);

  // Skript bir marta yuklanadi: sahifa ikki marta renderlansa ham
  // ikkinchi `<script>` qo'shilmaydi.
  useEffect(() => {
    if (!siteKey) return;

    // Allaqachon yuklangan bo'lsa kutish SHART EMAS. Bu holat sahifa
    // ichidagi navigatsiyada uchraydi va uni `setReady` bilan effekt
    // ichida hal qilib bo'lmaydi (`react-hooks/set-state-in-effect`).
    if (window.turnstile) return;

    const present = document.getElementById(SCRIPT_ID) as HTMLScriptElement | null;
    if (present) {
      present.addEventListener("load", () => setReady(true), { once: true });
      return;
    }
    const script = document.createElement("script");
    script.id = SCRIPT_ID;
    script.src = SRC;
    script.async = true;
    script.defer = true;
    script.addEventListener("load", () => setReady(true), { once: true });
    document.head.appendChild(script);
  }, [siteKey]);

  // `ready` shart emas: `window.turnstile` — YAGONA haqiqat. `ready`
  // faqat qayta urinish uchun kerak, ya'ni u effektni qo'zg'atadi.
  useEffect(() => {
    const api = window.turnstile;
    if (!siteKey || !api || !box.current) return;
    const id = api.render(box.current, {
      sitekey: siteKey,
      size: "flexible",
      // Token muddati o'tgani yoki xato bo'lganda eski qiymat
      // tozalanadi: aks holda server allaqachon sarflangan tokenni
      // qayta tekshirib rad etardi.
      callback: (token) => emit.current(token),
      "error-callback": () => emit.current(""),
      "expired-callback": () => emit.current(""),
    });
    return () => api.remove(id);
  }, [ready, siteKey]);

  // Vidjet tayyor bo'lmaguncha ham joy egallamaydi (`size: flexible`
  // o'lchamni o'zi oladi), ya'ni forma sakramaydi.
  const hold = useCallback((node: HTMLDivElement | null) => {
    box.current = node;
  }, []);

  if (!siteKey) return null;
  return <div ref={hold} />;
}
