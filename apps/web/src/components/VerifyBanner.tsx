"use client";

import { useState } from "react";

import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { postJson } from "@/lib/api";

/** Tasdiqlanmagan pochta haqida eslatma.
 *
 * ESLATMA, to'siq emas: tasdiqlanmagan hisob platformada to'liq ishlaydi.
 * Qattiq qilinsa xat yetib bormagan odam butunlay yo'qolardi, tasdiq esa
 * asosan bizga kerak — pochtasi ishlamaydigan hisob parolini tiklay
 * olmaydi.
 */
export function VerifyBanner() {
  const locale = useLocale();
  const { user } = useSession();
  const [sent, setSent] = useState(false);
  const [busy, setBusy] = useState(false);

  if (!user || user.email_verified !== false) return null;

  return (
    <div className="rw-warn-soft px-4 py-2 text-center text-theme-sm rw-warn-ink">
      {t(locale, "auth.verifyPending")}{" "}
      {sent ? (
        <span className="font-medium">{t(locale, "auth.verifySent")}</span>
      ) : (
        <button
          type="button"
          disabled={busy}
          onClick={() => {
            setBusy(true);
            postJson("/auth/email/resend/", {})
              .then(() => setSent(true))
              .catch(() => setSent(false))
              .finally(() => setBusy(false));
          }}
          className="font-medium underline rw-focus-ring disabled:opacity-60"
        >
          {t(locale, "auth.verifyResend")}
        </button>
      )}
    </div>
  );
}
