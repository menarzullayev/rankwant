"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";

import { useSession } from "@/context/SessionContext";
import { fetchUpdateUnreadCount, markUpdatesRead } from "@/lib/api";

/** O'qilmagan o'zgarishlar soni — qo'ng'iroq belgisi va nav chipi uchun.
 *
 *  NEGA KONTEXST: sonni ikki joy ko'rsatadi (header'dagi belgi va yon
 *  menyudagi chip). Har biri o'zi so'rasa sahifa ochilishida ikkita bir
 *  xil so'rov ketardi va ular orasida vaqtincha mos kelmagan son
 *  ko'rinardi. Bu yerda bitta so'rov, bitta holat.
 */
type UpdatesState = {
  /** O'qilmaganlar soni. Mehmon uchun har doim `0`. */
  count: number;
  /** Shundan harakatga chaqiruvchilari (`breaking`, `deprecated`). */
  actionable: number;
  /** O'qilgan deb belgilash; `ids` berilmasa — hammasi. */
  markRead: (ids?: number[]) => Promise<void>;
  /** Sonni serverdan qayta o'qish. */
  refresh: () => Promise<void>;
};

const UpdatesContext = createContext<UpdatesState | undefined>(undefined);

export function useUpdates() {
  const context = useContext(UpdatesContext);
  if (!context)
    throw new Error("useUpdates UpdatesProvider ichida ishlatilishi kerak");
  return context;
}

export function UpdatesProvider({ children }: { children: React.ReactNode }) {
  const { user, ready } = useSession();
  const [count, setCount] = useState(0);
  const [actionable, setActionable] = useState(0);

  const refresh = useCallback(async () => {
    const body = await fetchUpdateUnreadCount().catch(() => null);
    setCount(body?.count ?? 0);
    setActionable(body?.actionable ?? 0);
  }, []);

  useEffect(() => {
    // Mehmon uchun so'rov YUBORILMAYDI: endpoint `IsAuthenticated` talab
    // qiladi, ya'ni 401 qaytardi va brauzer uni konsolga xato qilib
    // yozardi (Lighthouse `errors-in-console`).
    if (!ready || !user) return;
    // Sessiya faqat brauzerda o'qiladi, ya'ni mount'dan keyin so'rov
    // yuborishdan boshqa yo'l yo'q. Qoida render tsiklini nazarda tutadi —
    // bu yerda holat bir marta, javob kelganda o'rnatiladi.
    // (`SessionContext` dagi bilan bir xil istisno.)
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void refresh();
  }, [ready, user, refresh]);

  // Chiqqandan keyin son NOLGA ko'rinadi, lekin holat o'chirilmaydi:
  // effekt ichida `setState` chaqirish taqiqlangan (react-hooks
  // `set-state-in-effect` — u kaskad render keltiradi) va bunga ehtiyoj
  // ham yo'q. Qayta kirganda effekt baribir serverdan qayta o'qiydi.
  const markRead = useCallback(
    async (ids?: number[]) => {
      // Mehmon uchun so'rov YUBORILMAYDI: `mark-read` `IsAuthenticated`
      // talab qiladi, ya'ni 401 qaytardi. Belgilanadigan holat ham yo'q —
      // `UpdateRead` yozuvi faqat kirgan foydalanuvchida bo'ladi.
      if (!user) return;
      const body = await markUpdatesRead(ids).catch(() => null);
      // Faqat server tasdiqlasa qayta o'qiymiz: aks holda belgi
      // o'chib, keyingi so'rovda yana paydo bo'lardi.
      if (body) await refresh();
    },
    [user, refresh],
  );

  return (
    <UpdatesContext.Provider
      value={{
        count: user ? count : 0,
        actionable: user ? actionable : 0,
        markRead,
        refresh,
      }}
    >
      {children}
    </UpdatesContext.Provider>
  );
}
