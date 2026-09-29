import type { Route } from "next";
import Link from "next/link";

import { t, type Locale } from "@/i18n/messages";
import type { UserTitle } from "@/lib/identity";

import { MarkerText } from "@/components/ui/Identity";

/** Ism rangi — unvon pog'onasining RANG GURUHI bo'yicha (ADR-0027 § L2).
 *  16 pog'ona faqat 7 xil rang ishlatadi: kulrang 1-3, yashil 4-5, zang 6-7,
 *  ko'k 8, binafsha 9, olov 10-11, qizil 12-16. CSS'da ham xuddi shu 7 ta
 *  `--rw-rank-{guruh}` o'zgaruvchisi bor — 16 ta takrorlanuvchi e'lon yo'q. */
export const rankClass = (title: UserTitle | null | undefined) =>
  title ? `rw-rank-${title.colour_group}` : "rw-strong";

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
