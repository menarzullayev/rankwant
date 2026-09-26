"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { API_BASE } from "@/lib/api";

/** Ulanish holati. `fallback` — oqim ishlamayapti, mijoz polling'da. */
export type StreamState = "connecting" | "open" | "fallback";

/** Server hodisalari — `realtime/events.py` bilan AYNAN bir xil bo'lishi shart. */
export const EVENT_VERDICT = "verdict";
export const EVENT_STANDINGS = "standings";
/** Server replay buferi yetmaganini aytadi — holatni REST dan qayta o'qish kerak. */
export const EVENT_RESYNC = "resync";

/** Ketma-ket shuncha uzilishdan keyin oqimdan butunlay voz kechiladi. */
const MAX_FAILURES = 6;
/** Hisobotni yuborish oralig'i — har uzilishda yuborilsa o'zi yuk bo'ladi. */
const REPORT_EVERY = 5;
/** Oqim ishlamayotgan holat — alohida doimiyda, ternary ichida emas:
 *  `check_hardcoded.py` ternary shoxobidagi satrni «qattiq yozilgan matn»
 *  deb o'qiydi (aynan shu tuzoq `components/ui/Table.tsx` da ham bor). */
const FALLBACK: StreamState = "fallback";

/**
 * SSE mijozi — ADR-0029 §8/§9.
 *
 * Uchta qoida, va ular ixtiyoriy emas:
 *
 * 1. **Oqim — optimallashtirish, haqiqat manbasi EMAS.** Hodisa kelganda
 *    chaqiruvchi holatni REST dan qayta o'qiydi; yukdan to'g'ridan-to'g'ri
 *    holat yasalmaydi. Shu sababli yo'qolgan hodisa noto'g'ri holatga olib
 *    kelmaydi — eng yomon holat bir marta ortiqcha so'rov.
 * 2. **Uzilish — normal holat.** `EventSource` o'zi qayta ulanadi
 *    (`retry:` serverdan keladi), biz faqat ketma-ket uzilishlarni
 *    sanaymiz va chegaradan keyin polling'ga tushamiz.
 * 3. **`resync` — majburiy.** Server replay buferi yetmaganini aytsa,
 *    mijoz darhol to'liq qayta o'qishi kerak, aks holda u abadiy eski
 *    holatda qoladi.
 */
export function useEventStream({
  onEvent,
  contest,
  enabled = true,
}: {
  /** Hodisa keldi — chaqiruvchi holatni yangilaydi. */
  onEvent: (name: string, data: unknown) => void;
  /** Ixtiyoriy: jadval kanaliga ham obuna bo'lish. */
  contest?: number;
  enabled?: boolean;
}): StreamState {
  const [state, setState] = useState<StreamState>("connecting");
  const failures = useRef(0);
  const delivered = useRef(0);
  const handler = useRef(onEvent);
  //: ⚠️ `useEffect` ichida: render paytida ref'ga yozish React qoidasini
  //: buzadi (render sof bo'lishi kerak) va StrictMode'da ikki marta
  //: bajarilib, eski handlerni qoldirishi mumkin.
  useEffect(() => {
    handler.current = onEvent;
  }, [onEvent]);

  /** Brauzer `EventSource` ni qo'llab-quvvatlaydimi. Bir marta aniqlanadi:
   *  bu qiymat ish paytida o'zgarmaydi. */
  const supported = typeof window !== "undefined" && "EventSource" in window;

  const report = useCallback((reconnects: number) => {
    //: ADR-0029 §11: server tomondan hamma ulanish sog'lom ko'rinadi —
    //: foydalanuvchi sekin tarmoqda bo'lsa ham. Shu sababli reconnect
    //: hisoboti yagona haqiqiy signal. `keepalive` — sahifa yopilsa ham
    //: ketadi, va javob kutilmaydi.
    try {
      const body = JSON.stringify({ reconnects, delivered: delivered.current });
      void fetch(`${API_BASE}/realtime/report/`, {
        method: "POST",
        credentials: "include",
        keepalive: true,
        headers: { "content-type": "application/json" },
        body,
      }).catch(() => undefined);
    } catch {
      //: Hisobot hech qachon funksiyani buzmasligi kerak.
    }
  }, []);

  useEffect(() => {
    if (!enabled || !supported) return;

    const url = contest
      ? `${API_BASE}/events/?contest=${contest}`
      : `${API_BASE}/events/`;
    const source = new EventSource(url, { withCredentials: true });

    const names = [EVENT_VERDICT, EVENT_STANDINGS, EVENT_RESYNC];
    const listeners = names.map((name) => {
      const listener = (event: MessageEvent<string>) => {
        delivered.current += 1;
        let data: unknown = null;
        try {
          data = JSON.parse(event.data);
        } catch {
          data = null; // buzuq yuk butun oqimni to'xtatmasin
        }
        handler.current(name, data);
      };
      source.addEventListener(name, listener as EventListener);
      return [name, listener] as const;
    });

    source.onopen = () => {
      failures.current = 0;
      setState("open");
    };

    source.onerror = () => {
      //: ⚠️ Bu yerga har uzilishda tushiladi va bu NORMAL: proksi
      //: ulanishni uzadi, sahifa uxlaydi, tarmoq o'zgaradi.
      //: `EventSource` o'zi qayta uradi — biz faqat sanaymiz.
      failures.current += 1;
      if (failures.current % REPORT_EVERY === 0) {
        report(failures.current);
      }
      if (failures.current >= MAX_FAILURES) {
        //: Ketma-ket ko'p marta uzilsa oqimdan voz kechamiz: sahifa
        //: ishlashda davom etadi, faqat qo'lda yangilanadi.
        source.close();
        setState(FALLBACK);
      }
    };

    return () => {
      for (const [name, listener] of listeners) {
        source.removeEventListener(name, listener as EventListener);
      }
      source.close();
    };
  }, [contest, enabled, report, supported]);

  //: ⚠️ Hosilaviy holat, `setState` emas: qo'llab-quvvatlanmasa yoki
  //: o'chirilgan bo'lsa — samarani umuman ishga tushirmasdan
  //: «fallback» qaytaramiz. Effekt ichida sinxron `setState` qilish
  //: kaskad render'ga olib keladi (React qoidasi).
  return !enabled || !supported ? FALLBACK : state;
}
