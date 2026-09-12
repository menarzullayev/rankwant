"use client";

import { useEffect, useState } from "react";

/** Davlat bayrog'i — 3:2 nisbatda (`country-flag-icons`, MIT).
 *
 * Nega emoji emas: Windows 10/11 bayroq emoji'ni CHIZMAYDI — u yerda
 * `🇺🇿` o'rniga «UZ» harflari ko'rinadi (Microsoft bayroqlarni o'z emoji
 * shriftidan ataylab chiqarib tashlagan). Auditoriya asosan Windows
 * bo'lgani uchun emoji yaroqsiz.
 *
 * Nega lazy: paket 249 bayroqni beradi va ularning hammasi bir modulda.
 * Ro'yxat sahifasida bir vaqtda faqat BITTA bayroq ko'rinadi (tanlangan
 * davlat), ya'ni hammasini boshlang'ich to'plamga qo'shish ortiqcha
 * bo'lardi. Modul sahifa interaktiv bo'lgach yuklanadi va jarayonda
 * KESHLANADI — ikkinchi chaqiruv tarmoqqa chiqmaydi.
 *
 * Ranglar `currentColor` EMAS: bayroq — brend belgisi, u temaga
 * bo'ysunmaydi (AuthForm'dagi `BRAND` ranglari kabi).
 */

type FlagComponent = React.ComponentType<{
  className?: string;
  title?: string;
  "aria-hidden"?: boolean;
}>;

let loaded: Record<string, FlagComponent> | null = null;
let loading: Promise<Record<string, FlagComponent>> | null = null;

function loadFlags(): Promise<Record<string, FlagComponent>> {
  if (loaded) return Promise.resolve(loaded);
  loading ??= import("country-flag-icons/react/3x2").then((mod) => {
    loaded = mod as unknown as Record<string, FlagComponent>;
    return loaded;
  });
  return loading;
}

export function CountryFlag({
  code,
  className = "",
  title,
}: {
  /** ISO 3166-1 alpha-2 — bo'sh yoki noma'lum bo'lsa hech narsa chizilmaydi. */
  code: string;
  className?: string;
  /** Berilmasa bayroq BEZAK hisoblanadi (`aria-hidden`) — yonida davlat
   *  nomi matn bo'lib turgan holat uchun. */
  title?: string;
}) {
  const iso = (code || "").toUpperCase();
  const valid = /^[A-Z]{2}$/.test(iso);
  // Natija QAYSI kod uchun kelgani bilan saqlanadi: kod almashganda eski
  // bayroq yangisi yuklanguncha ko'rinib qolmasin.
  const [state, setState] = useState<{
    for: string;
    Flag: FlagComponent;
  } | null>(null);

  useEffect(() => {
    if (!valid) return;
    let alive = true;
    loadFlags()
      .then((flags) => {
        const Flag = flags[iso];
        if (alive && Flag) setState({ for: iso, Flag });
      })
      .catch(() => undefined);
    return () => {
      alive = false;
    };
  }, [iso, valid]);

  const Flag = state?.for === iso ? state.Flag : null;
  if (!valid || !Flag) return null;

  return (
    <Flag
      aria-hidden={title ? undefined : true}
      title={title}
      className={`inline-block h-3.5 w-[21px] shrink-0 align-[-2px] rw-radius-sm ${className}`}
    />
  );
}
