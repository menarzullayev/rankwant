"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";

import { fetchMe, type Me } from "@/lib/api";

type Session = {
  user: Me | null;
  /** Sessiya hali aniqlanmagan bo'lsa `false` — UI chaqnamasligi uchun. */
  ready: boolean;
  reload: () => Promise<void>;
  clear: () => void;
};

const SessionContext = createContext<Session | undefined>(undefined);

export function useSession() {
  const context = useContext(SessionContext);
  if (!context)
    throw new Error("useSession SessionProvider ichida ishlatilishi kerak");
  return context;
}

/** Sessiya cookie'ga bog'liq, ya'ni serverda o'qib bo'lmaydi: sahifalar
 * `force-dynamic` bo'lsa ham cookie SSR fetch'iga uzatilmaydi. Holat
 * bu yerda saqlanadi, shunda kirgandan keyin header darhol yangilanadi. */
export function SessionProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<Me | null>(null);
  const [ready, setReady] = useState(false);

  const reload = useCallback(async () => {
    const me = await fetchMe().catch(() => null);
    setUser(me);
    setReady(true);
  }, []);

  useEffect(() => {
    // Sessiya faqat brauzerda o'qiladi (cookie SSR fetch'iga uzatilmaydi),
    // ya'ni mount'dan keyin so'rov yuborishdan boshqa yo'l yo'q. Qoida
    // render tsiklini nazarda tutadi — bu yerda holat bir marta, javob
    // kelganda o'rnatiladi.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void reload();
  }, [reload]);

  const clear = useCallback(() => setUser(null), []);

  return (
    <SessionContext.Provider value={{ user, ready, reload, clear }}>
      {children}
    </SessionContext.Provider>
  );
}
