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

/** Sessiya cookie'ga bog'liq. SSR uni `api.server.ts` dagi `getWithSession`
 * orqali ko'radi — `RootLayout` shu yo'l bilan o'qib, natijani `initialUser`
 * sifatida beradi. Holat shu yerda saqlanadi, shunda kirgandan keyin header
 * darhol yangilanadi. */
export function SessionProvider({
  initialUser,
  children,
}: {
  /** SSR aniqlagan sessiya. `undefined` — aniqlanmagan, mijoz o'zi so'raydi;
   * `null` — SSR tekshirdi va foydalanuvchi yo'q, so'rov kerak emas. */
  initialUser?: Me | null;
  children: React.ReactNode;
}) {
  const [user, setUser] = useState<Me | null>(initialUser ?? null);
  // SSR javob bergan bo'lsa `ready` darhol `true`: aks holda header bir kadr
  // «chaqnamaydi» va sahifa sakragandek ko'rinadi.
  const [ready, setReady] = useState(initialUser !== undefined);

  const reload = useCallback(async () => {
    const me = await fetchMe().catch(() => null);
    setUser(me);
    setReady(true);
  }, []);

  useEffect(() => {
    // SSR sessiyani allaqachon aniqlagan bo'lsa, mount'da so'rov
    // yuborilmaydi. Anonim tashrifchi uchun bu so'rov 401 bo'lardi: javob
    // to'g'ri, lekin brauzer uni konsolga xato qilib yozadi va Lighthouse
    // `errors-in-console` auditini yiqitadi.
    if (initialUser !== undefined) return;
    // Sessiya faqat brauzerda o'qiladi, ya'ni mount'dan keyin so'rov
    // yuborishdan boshqa yo'l yo'q. Qoida render tsiklini nazarda tutadi —
    // bu yerda holat bir marta, javob kelganda o'rnatiladi.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void reload();
  }, [reload, initialUser]);

  const clear = useCallback(() => setUser(null), []);

  return (
    <SessionContext.Provider value={{ user, ready, reload, clear }}>
      {children}
    </SessionContext.Provider>
  );
}
