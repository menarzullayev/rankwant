"use client";

import type { Route } from "next";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { StarIcon } from "@/icons";
import { ApiError, setFavourite } from "@/lib/api";

/** Arxiv qatoridagi ☆ — sahifani qayta yuklamasdan.
 *
 * Xato bo'lsa holat orqaga qaytariladi: yulduz to'lgan ko'rinib, aslida
 * saqlanmagan bo'lishi eng chalg'ituvchi holat. */
export function FavouriteToggle({
  slug,
  initial,
  title,
}: {
  slug: string;
  initial: boolean;
  title: string;
}) {
  const router = useRouter();
  const [on, setOn] = useState(initial);
  const [busy, setBusy] = useState(false);

  async function toggle() {
    if (busy) return;
    const next = !on;
    setOn(next);
    setBusy(true);
    try {
      await setFavourite(slug, next);
    } catch (caught) {
      setOn(!next);
      if (
        caught instanceof ApiError &&
        (caught.status === 401 || caught.status === 403)
      ) {
        router.push("/kirish?tab=kirish" as Route);
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <button
      type="button"
      onClick={toggle}
      aria-pressed={on}
      aria-label={`${title} — ${on ? "sevimlilardan olib tashlash" : "sevimlilarga qo'shish"}`}
      className={`rw-radius-sm p-1 transition rw-hover-bg ${on ? "rw-warn-ink" : "rw-faint"}`}
    >
      <StarIcon className="size-4" filled={on} />
    </button>
  );
}
