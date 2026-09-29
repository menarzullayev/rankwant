"use client";

import { useEffect } from "react";

import { useUpdates } from "@/context/UpdatesContext";

/** Yozuv ochilganda uni o'qilgan deb belgilaydi (qaror 7).
 *
 *  Ko'rinmas komponent: batafsil sahifa SERVER komponenti bo'lib qoladi
 *  (SEO — ADR-0003), belgilash esa brauzerda sessiya bilan ketadi.
 *
 *  Mehmon uchun so'rov yuborilmaydi — buni `UpdatesProvider` ichidagi
 *  `markRead` hal qiladi (`user` bo'lmasa darhol qaytadi), ya'ni bu
 *  yerda ikkinchi tekshiruv kerak emas.
 */
export function UpdateReadMarker({ id }: { id: number }) {
  const { markRead } = useUpdates();

  useEffect(() => {
    void markRead([id]);
  }, [id, markRead]);

  return null;
}
