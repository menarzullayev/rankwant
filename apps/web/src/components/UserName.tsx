import type { Route } from "next";
import Link from "next/link";

import { t, type Locale } from "@/i18n/messages";
import type { UserTitle } from "@/lib/api";

/** Ism rangi — unvon pog'onasidan (ADR-0018). Unvonsiz odam oddiy matn rangida. */
export const rankClass = (title: UserTitle | null | undefined) =>
  title ? `rw-rank-${title.level}` : "rw-strong";

/** Profilga havola, ism unvon rangida: reyting, standings, urinishlar bir xil ko'rinsin. */
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
  return (
    <Link
      href={`/users/${username}` as Route}
      title={title ? t(locale, `title.${title.code}`) : undefined}
      className={`font-medium rw-link-hover ${rankClass(title)} ${className}`}
    >
      {name || username}
    </Link>
  );
}
