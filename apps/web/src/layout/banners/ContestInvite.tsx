"use client";

import type { Route } from "next";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useState } from "react";

import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";

/** AtCoder/Codeforces taklifi — 16-qaror.
 *
 * FAQAT bir marta, 2-qadamdan keyin (`?welcome=2`). Sabab: tashqi
 * platformadagi natija reytingni ANIQLASHTIRADI, lekin uni darhol
 * talab qilish yangi hisobni to'xtatib qo'yardi — odam hali hech
 * narsa yechmagan, natija esa o'sha yerda.
 *
 * `WelcomeNotice` bilan bir vaqtda chiqmaydi: u `welcome=1` ni,
 * bu `welcome=2` ni kutadi va 2-qadam `1` ni `2` ga almashtiradi.
 *
 * Havola `settings/ijtimoiy` ga — ATAYLAB shu bo'lim, chunki
 * Codeforces/AtCoder tutqichlari aynan o'sha yerda kiritiladi
 * (`settings/SocialSection.tsx` dagi `{ kind: "codeforces" }` va
 * `{ kind: "atcoder" }`). 2-qadam tugagach odam allaqachon shu
 * sahifaga ega — yangi sahifa yasash ortiqcha bo'lardi.
 */
export function ContestInvite() {
  const locale = useLocale();
  const params = useSearchParams();
  const [closed, setClosed] = useState(false);

  if (closed || params.get("welcome") !== "2") return null;

  return (
    <div className="rw-accent-soft px-4 py-3 text-theme-sm rw-accent-ink">
      <div className="rw-content mx-auto flex flex-wrap items-center justify-center gap-3">
        <span>{t(locale, "auth.contestInvite")}</span>
        <Link
          href={"/settings/ijtimoiy" as Route}
          className="underline rw-focus-ring"
        >
          {t(locale, "auth.contestInviteCta")}
        </Link>
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
