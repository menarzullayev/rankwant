"use client";

import { useState } from "react";

import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { ApiError, postJson } from "@/lib/api";

/** Tasdiqlanmagan pochta haqida eslatma.
 *
 * ESLATMA, to'siq emas: tasdiqlanmagan hisob platformada to'liq ishlaydi.
 * Qattiq qilinsa xat yetib bormagan odam butunlay yo'qolardi, tasdiq esa
 * asosan bizga kerak — pochtasi ishlamaydigan hisob parolini tiklay
 * olmaydi.
 *
 * ── Holatlar (`sending` paytida tugma ko'rinmaydi) ────────────────────
 *   idle    → «Xatni qayta yuborish» tugmasi
 *   sending → «Yuborilmoqda…» (tugma o'chirilgan, takroriy bosish yo'q)
 *   sent    → «Xat yuborildi»
 *   error   → xato matni + tugma qaytadi
 *
 * NEGA `sending` ALOHIDA: kuniga 3 marta (`PER_USER_HOUR`) yuborish
 * mumkin, ya'ni javob bir zumda kelmaydi va odam tugmani qayta bosadi.
 * Har bosish yangi so'rov — kvota esa cheklangan (kunlik shift 700 ta).
 * Ya'ni «yuborilmoqda» holati shunchaki qulaylik emas, u KVOTANI
 * tejaydi.
 *
 * NEGA XATO KO'RSATILADI: ilgari xato jimgina yutilardi va tugma
 * qaytardi. Odam nima bo'lganini bilmasdan qayta bosardi — 429
 * (throttle) da esa kutish kerakligi umuman aytilmasdi. Endi server
 * aytgan kutish soniyasi (`Retry-After`) ham ko'rsatiladi.
 */
export function VerifyBanner() {
  const locale = useLocale();
  const { user } = useSession();
  const [state, setState] = useState<"idle" | "sending" | "sent" | "error">("idle");
  const [retryAfter, setRetryAfter] = useState(0);

  if (!user || user.email_verified !== false) return null;

  const send = () => {
    setState("sending");
    setRetryAfter(0);
    postJson("/auth/email/resend/", {})
      .then(() => setState("sent"))
      .catch((err: unknown) => {
        // `Retry-After` — server qancha kutishni ANIQ aytadi (15-qaror).
        // Sarlavha bo'lmasa `0` — matn umumiy qoladi.
        setRetryAfter(err instanceof ApiError ? err.retryAfter : 0);
        setState("error");
      });
  };

  return (
    <div className="rw-warn-soft px-4 py-2 text-center text-theme-sm rw-warn-ink">
      {t(locale, "auth.verifyPending")}{" "}
      {state === "sent" && (
        <span className="font-medium">{t(locale, "auth.verifySent")}</span>
      )}
      {state === "sending" && <span className="font-medium">{t(locale, "auth.verifySending")}</span>}
      {state === "error" && (
        <span role="alert" className="rw-bad-ink">
          {t(locale, "auth.verifyResendFail")}
          {retryAfter > 0 && (
            <>
              {" "}
              {t(locale, "auth.throttledWait").replace("{seconds}", String(retryAfter))}
            </>
          )}{" "}
          <button
            type="button"
            onClick={send}
            className="font-medium underline rw-focus-ring"
          >
            {t(locale, "auth.verifyResend")}
          </button>
        </span>
      )}
      {state === "idle" && (
        <button
          type="button"
          onClick={send}
          className="font-medium underline rw-focus-ring"
        >
          {t(locale, "auth.verifyResend")}
        </button>
      )}
    </div>
  );
}
