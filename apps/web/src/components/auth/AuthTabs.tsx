"use client";

import type { Route } from "next";
import Link from "next/link";
import { useSearchParams } from "next/navigation";

import { TAB_BAR, type TabId } from "@/lib/auth-tabs";
import { useLocale } from "@/i18n/LocaleProvider";
import { t, type MessageKey } from "@/i18n/messages";

/** Qurilish vaqtida `MessageKey` ekani tekshiriladi: kalit xato yozilsa
 *  `tsc` yiqiladi. `t()` esa noma'lum kalitni satr sifatida qaytarib,
 *  xatoni yashirardi. */
const LABEL: Record<TabId, MessageKey> = {
  login: "auth.tabLogin",
  register: "auth.tabRegister",
  "reset-password": "auth.tabReset",
};

/** Sahifadagi asosiy bo'limlar bitta manzilda (1-qaror). Ilgari uchta
 *  alohida sahifa bor edi va odam «parolni tiklash» ga o'tish uchun
 *  kirish sahifasidan chiqib, havolani izlashi kerak edi — endi u shu
 *  yerda, bir bosishda.
 *
 *  QATORDA IKKI BO'LIM: Login / Register. Uchinchisi
 *  (`reset-password`) — haqiqiy bo'lim bo'lib qolaveradi (manzili,
 *  xatdagi token, `/reset-password` yo'naltirishi ishlaydi), lekin
 *  qatorda ko'rsatilmaydi: uchta teng ustunda uning yozuvi har tilda
 *  deyarli kesilardi (tafsilot — `TAB_BAR` izohida, `lib/auth-tabs.ts`).
 *  Uni kirish formasidagi «Parolni unutdingizmi?» havolasi ochadi.
 *
 *  ROL TABLIST EMAS, va bu ataylab. `role="tablist"` ARIA'da klaviatura
 *  boshqaruvini talab qiladi: fokus halqa ichida aylanadi (`←`/`→`,
 *  `Home`/`End`) va panel `tabpanel` bo'lishi kerak. Bu yerda esa
 *  panellar SERVER komponenti, ya'ni klient fokusni ko'chira olmaydi —
 *  yarim bajarilgan tablist ekran o'quvchini chalg'itardi.
 *
 *  O'rniga oddiy havola: har biri HAQIQIY manzil (`?tab=...`), ya'ni
 *  o'rta tugma, yangi varaq va xatcho'p ishlaydi. Fokus oddiy Tab bilan
 *  yuriladi, `aria-current` esa qaysi biri tanlanganini aytadi. */
export function AuthTabs({ active }: { active: TabId }) {
  const locale = useLocale();
  const params = useSearchParams();
  //: `?next=` saqlanib o'tadi: himoyalangan sahifadan uchirilgan odam
  //: bo'limni almashtirsa ham qaytish manzili yo'qolmasin.
  const next = params.get("next");

  return (
    <nav aria-label={t(locale, "auth.tabHint")} className="mb-5">
      {/* `grid-cols-2` — `TAB_BAR` uzunligiga qarab qo'lda yozilgan.
          Tailwind sinf nomini dinamik yasay olmaydi (u build vaqtida
          skanerlanadi), ya'ni `grid-cols-${n}` ISHLAMAYDI. Ro'yxat
          o'zgarsa shu sinf ham qo'lda yangilanishi kerak — shuning
          uchun yonida `TAB_BAR` ga havola bor. */}
      <ul className="grid grid-cols-2 gap-1 border-b rw-divider">
        {TAB_BAR.map((tab) => {
          const current = tab === active;
          const query = new URLSearchParams({ tab });
          if (next) query.set("next", next);
          return (
            <li key={tab} className="min-w-0">
              <Link
                //: `typedRoutes` faqat STATIK marshrut qismini
                //: tekshiradi: `/kirish` + `?tab=…` — ruxsat etilgan
                //: shakl, ya'ni tip toraytirishi shart emas.
                href={`/kirish?${query}` as Route}
                scroll={false}
                aria-current={current ? "page" : undefined}
                className={`flex min-h-11 items-center justify-center px-1 pb-2 pt-1 text-center text-theme-sm transition rw-focus-ring ${
                  current
                    ? // Tanlangan bo'lim: rang YOLG'IZ tashuvchi emas
                      // (WCAG 1.4.1) — u qalin shrift va 2px chegara
                      // bilan ham ajraladi; `aria-current` esa ekran
                      // o'quvchi uchun aytadi.
                      "border-b-2 border-current font-semibold rw-strong"
                    : "border-b-2 border-transparent rw-dim hover:rw-strong"
                }`}
              >
                {/* Yozuv KESILMAYDI, kerak bo'lsa IKKI QATORGA o'raladi.
                    Sabab (o'lchandi, 320px — eng tor qo'llab-quvvatlanadigan
                    ekran): ikki ustundan biriga ~91px tegadi, o'zbekcha
                    "Ro'yxatdan o'tish" esa 105px talab qiladi. Ilgari bu
                    yerda `truncate` bor edi va yozuv "Ro'yxatdan…" bo'lib
                    qolardi. O'ralish uni to'liq saqlaydi: `min-h-11`
                    (44px) ikki qatorni ham bemalol ko'taradi, ya'ni
                    tegish maydoni kichrayib qolmaydi (WCAG 2.5.8).
                    Diqqat: shu sababli `Link` da `items-center` emas —
                    u o'ralgan matnni emas, butun blokni markazga tortardi. */}
                <span className="min-w-0 leading-snug">
                  {t(locale, LABEL[tab])}
                </span>
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
