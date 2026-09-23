"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { useLocale } from "@/i18n/LocaleProvider";
import { getJson } from "@/lib/api";
import { log } from "@/lib/log";
import { Cache } from "./cache";
import { describeError } from "./useAction";

/** Jarayon davomidagi kesh — modul darajasida.
 *
 *  ⚠️ **Nega modul darajasi, React konteksti emas.** `useLoad` ni 15 ta
 *  fayl ishlatadi va ularning ba'zilari bir sahifada ikki marta bir xil
 *  endpoint'ni so'raydi (o'lchandi 2026-09-24: `SkillsSection.tsx` —
 *  `catalog` va `mine` ikki komponentda). Kontekst (Provider) qo'shsak,
 *  har bir chaqiruvchi uni o'rashi kerak bo'lardi — ya'ni 15 ta fayl
 *  o'zgarardi. Modul darajasi esa hech kimdan hech narsa talab qilmaydi.
 *
 *  ⚠️ Bu **xotira keshi**, HTTP keshi emas: sahifa yangilanganda
 *  tozalanadi. Ma'lumot foydalanuvchi harakati bilan o'zgaradi, ya'ni
 *  eski javobni uzoq saqlash xato ko'rsatish demakdir — `STALE_MS`
 *  shuning uchun qisqa.
 *
 *  Mantiq `./cache` da — u React'siz o'lchanadi (testlar), bu fayl esa
 *  faqat React qobig'i.
 */
const CACHE = new Cache();

/** Shu vaqt ichida javob yangi hisoblanadi — qayta so'ralmaydi. */
const STALE_MS = 30_000;

/** Keshni bo'shatadi — testlar va "hammasini yangilash" uchun. */
export function clearLoadCache(): void {
  CACHE.clear();
}

/** Faqat diagnostika/test uchun: keshlangan yozuvlar soni. */
export function loadCacheSize(): number {
  return CACHE.size();
}

export type LoadOptions = {
  /** `false` — yuklamaslik (masalan majburiy maydon to'ldirilmagan). */
  enabled?: boolean;
  /** `STALE_MS` ni chaqiruvchi bo'yicha o'zgartirish. */
  staleMs?: number;
};

/** Sahifa ochilganda GET — **kesh, dedup va qayta so'rash** bilan.
 *
 *  ## Nega kesh kerak
 *
 *  Ilgari bu yalang'och `useEffect` + `fetch` edi: har bir komponent
 *  o'zi so'rardi. `SkillsSection.tsx` bir sahifada `/skills/catalog/`
 *  va `/me/skills/` ni **ikki komponentda** so'raydi (ko'nikma va
 *  texnologiya bo'limlari), ya'ni sahifa ochilganda 4 ta so'rov ketardi —
 *  ikkisi ortiqcha. Kesh bilan 2 ta qoladi.
 *
 *  ## Ikki qavat
 *
 *  1. **Dedup** — bir vaqtda uchgan so'rovlar bitta `Promise` ni baham
 *     ko'radi. Eng muhimi: React 19 StrictMode effektni ikki marta
 *     yurgizadi, ya'ni dedupsiz har so'rov ikkilanardi.
 *  2. **Kesh** — `STALE_MS` ichida qayta so'ralmaydi.
 *
 *  `reload()` — keshni tashlab qayta so'raydi (`stale-while-revalidate`).
 */
export function useLoad<T>(path: string, options: LoadOptions = {}) {
  const { enabled = true, staleMs = STALE_MS } = options;
  const locale = useLocale();
  // ⚠️ Keshdan o'qish BOSHLANG'ICH holatda, effektda emas.
  //
  // Sabab: effekt ichidagi sinxron `setData` kaskad render beradi
  // (`react-hooks/set-state-in-effect` qoidasi shuni tutdi, 2026-09-24).
  // Kesh sinxron o'qiladi, ya'ni uni `useState` ning lazy
  // boshlang'ich funksiyasida olish mumkin — natijada keshlangan javob
  // birinchi renderdayoq ekranda bo'ladi, qo'shimcha render bo'lmaydi.
  //
  // `isFresh` ni shu yerda hisoblaymiz va effektga qayta hisoblatmaymiz:
  // effekt `initial` ga qarab so'rovni o'tkazib yuboradi.
  const [initial] = useState(() =>
    enabled && CACHE.isFresh(path, staleMs) ? (CACHE.value(path) as T) : null,
  );
  const [data, setData] = useState<T | null>(initial);
  const [error, setError] = useState("");
  const [version, setVersion] = useState(0);
  // Mount holati: `setState` unmount'dan keyin chaqirilmasin.
  const mounted = useRef(true);

  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
    };
  }, []);

  useEffect(() => {
    if (!enabled) return;
    // Keshdan birinchi renderda olingan bo'lsa, takror so'ramaymiz.
    if (version === 0 && initial !== null) return;

    // Dedup: bir xil so'rov uchayotgan bo'lsa — unga ulanamiz.
    let promise = CACHE.promise(path) as Promise<T> | undefined;
    if (!promise) {
      promise = getJson<T>(path);
      CACHE.startFlight(path, promise);
      promise.then(
        (value) => CACHE.settle(path, value),
        () => CACHE.fail(path),
      );
    }

    promise.then(
      (value) => {
        if (!mounted.current) return;
        setData(value);
        setError("");
      },
      (err: unknown) => {
        if (!mounted.current) return;
        const text = describeError(locale, err);
        setError(text);
        log.warn("data", "yuklash yiqildi", { path, error: text });
      },
    );
  }, [path, version, locale, enabled, staleMs, initial]);

  /** Keshni tashlab, qayta so'raydi (stale-while-revalidate).
   *
   *  ⚠️ **Ekrandagi qiymat SAQLANADI** (`setData(null)` yo'q). Sabab:
   *  mavjud 7 ta chaqiruv `reload()` ni amaldan KEYIN yurgizadi
   *  (o'chirish, saqlash), ya'ni ekranda ma'lumot bor. Uni `null` qilsak
   *  sahifa bir zumda skeletonga qaytardi va miltillardi — ilgari bunday
   *  emasdi. Yangi qiymat kelganda `setData` uni almashtiradi.
   *
   *  Keshni tozalash SHART: usiz `isFresh` tekshiruvi `STALE_MS` ichida
   *  eski javobni qaytarib, `reload()` hech narsa qilmasdi. */
  const reload = useCallback(() => {
    CACHE.invalidate(path);
    setVersion((v) => v + 1);
  }, [path]);

  return { data, setData, error, reload };
}
