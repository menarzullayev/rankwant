import type { Route } from "next";
import Link from "next/link";

import { t, type Locale } from "@/i18n/messages";
import type { UserTitle } from "@/lib/api";

import { MarkerText } from "@/components/MarkerText";

/** Ism rangi — unvon pog'onasidan (ADR-0018). Unvonsiz odam oddiy matn rangida. */
export const rankClass = (title: UserTitle | null | undefined) =>
  title ? `rw-rank-${title.level}` : "rw-strong";

/** Profilga havola, ism unvon rangida: reyting, standings, urinishlar bir xil ko'rinsin.
 *  Birinchi `marker` harf qora (yorug' rejimda) yoki oq (to'q rejimda) - ADR-0027 § L2,
 *  CF konvensiyasi ("LGM qora 1-harf"). */
export function UserName({
  username,
  name,
  title,
  locale,
  className = "",
}: {
  username: string;
  name?: string;
  title: UserTitle | null | undefined;
  locale: Locale;
  className?: string;
}) {
  const display = name || username;
  return (
    <Link
      href={`/users/${username}` as Route}
      title={title ? t(locale, `title.${title.code}`) : undefined}
      className={`font-medium rw-link-hover ${rankClass(title)} ${className}`}
    >
      {title && title.marker > 0 ? (
        <MarkerText text={display} marker={title.marker} />
      ) : (
        display
      )}
    </Link>
  );
}
