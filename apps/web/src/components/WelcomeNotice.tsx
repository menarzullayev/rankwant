"use client";

import { useSearchParams } from "next/navigation";
import { useState } from "react";

import { useSession } from "@/context/SessionContext";
import { Button } from "@/components/ui/Button";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { postJson } from "@/lib/api";

/** Ro'yxatdan o'tgandan keyingi bir martalik xabar.
 *
 * Kod SHU YERDA kiritiladi. Alohida sahifaga o'tish bir qadam ko'p va
 * odam pochtadan kodni ko'chirib kelganda o'sha qadam eng ko'p
 * yo'qotadigan joy bo'ladi. Xatdagi havola ham ishlashda davom etadi —
 * backend ikkalasini ham qabul qiladi.
 *
 * Yopilgach qaytmaydi: tasdiqlanmaganini `VerifyBanner` eslatib turadi.
 */
export function WelcomeNotice() {
  const locale = useLocale();
  const params = useSearchParams();
  const { user, reload } = useSession();
  const [closed, setClosed] = useState(false);
  const [busy, setBusy] = useState(false);
  const [bad, setBad] = useState(false);

  if (closed || params.get("welcome") !== "1") return null;
  if (!user || user.email_verified !== false) return null;

  const sentTo = t(locale, "auth.verifySentTo").replace("{email}", user.email ?? "");

  return (
    <div className="rw-ok-soft px-4 py-3 text-theme-sm rw-ok-ink">
      <div className="mx-auto flex max-w-[1400px] flex-wrap items-center justify-center gap-3">
        <span>
          <strong>{t(locale, "auth.welcome")}</strong> {sentTo}
        </span>
        <form
          className="flex items-center gap-2"
          onSubmit={(event) => {
            event.preventDefault();
            const code = String(new FormData(event.currentTarget).get("code") ?? "");
            setBusy(true);
            setBad(false);
            postJson("/auth/email/verify/", { code, username: user.username })
              .then(() => reload())
              .then(() => setClosed(true))
              .catch(() => setBad(true))
              .finally(() => setBusy(false));
          }}
        >
          <input
            name="code"
            inputMode="numeric"
            pattern="[0-9]{6}"
            maxLength={6}
            required
            aria-label={t(locale, "auth.verifyTitle")}
            aria-invalid={bad || undefined}
            className="h-9 w-24 rw-radius-sm border px-3 text-center tracking-widest rw-strong outline-none rw-focus-ring rw-field-bg"
          />
          <Button type="submit" busy={busy} className="h-9 px-3">
            {t(locale, "auth.verifyTitle")}
          </Button>
        </form>
        {bad && <span className="rw-bad-ink">{t(locale, "auth.verifyFail")}</span>}
        <button
          type="button"
          onClick={() => setClosed(true)}
          className="underline rw-focus-ring"
        >
          {t(locale, "auth.dismiss")}
        </button>
      </div>
    </div>
  );
}
