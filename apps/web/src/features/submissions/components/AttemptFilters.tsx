"use client";

import type { Route } from "next";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";

import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";
import { VERDICT_FILTERS } from "@/lib/api";

/** Sahifa o'lchami variantlari (S14). Backend `page_size` ni allaqachon
 *  qabul qiladi (`max_page_size=100`), ya'ni bu qo'shimcha API ishi
 *  talab qilmaydi. */
const PAGE_SIZES = [25, 50, 100];

/** Qidiruv kechikishi, ms. Har harfda so'rov yuborilsa 891 qatorli
 *  masalada bitta odam yozayotganda o'nlab so'rov ketardi. */
const SEARCH_DEBOUNCE_MS = 300;

/** Urinishlar oqimining filtrlari.
 *
 * Ommabop masalada urinish minglab bo'ladi va filtrsiz ro'yxat o'qib
 * bo'lmaydigan oqimga aylanadi — KEP ham shu uchtasini beradi: verdikt,
 * til va «faqat meniki».
 *
 * Havolalar, tugma emas: holat URL da qoladi, ya'ni sahifani ulashsa
 * ham, orqaga qaytsa ham o'sha ro'yxat ochiladi. Bu qoida
 * `username`/`ordering`/`size` uchun ham amal qiladi.
 */
export function AttemptFilters({
  slug,
  languages,
  verdict,
  language,
  mine,
  username,
  size,
  ordering,
  activeCount,
}: {
  slug: string;
  languages: string[];
  verdict?: string;
  language?: string;
  mine: boolean;
  username?: string;
  size?: string;
  ordering?: string;
  /** Nechta filtr faol — ko'rsatkich uchun. */
  activeCount: number;
}) {
  const locale = useLocale();
  const { user, ready } = useSession();
  const router = useRouter();

  const [draft, setDraft] = useState(username ?? "");
  //: Foydalanuvchi yozayotganda URL yangilanadi, lekin input qiymati
  //: serverdan qaytgan qiymat bilan qayta yozilmasligi kerak — aks
  //: holda kursоr sakraydi. Shuning uchun faqat tashqi o'zgarishni
  //: kuzatamiz.
  const synced = useRef(username ?? "");
  useEffect(() => {
    if ((username ?? "") !== synced.current) {
      synced.current = username ?? "";
      setDraft(username ?? "");
    }
  }, [username]);

  const href = useCallback(
    (next: Record<string, string | undefined>): Route => {
      const params = new URLSearchParams();
      //: `cursor` har filtr o'zgarishida tashlanadi: eski kursor yangi
      //: ro'yxatning boshqa joyiga ishora qilardi.
      const merged = {
        verdict,
        language,
        mine: mine ? "true" : undefined,
        username,
        ordering,
        size,
        cursor: undefined,
        ...next,
      };
      for (const [key, value] of Object.entries(merged)) {
        if (value) params.set(key, value);
      }
      return `/problems/${slug}/status${params.size ? `?${params}` : ""}` as Route;
    },
    [language, mine, ordering, size, slug, username, verdict],
  );

  //: Qidiruv — debounce bilan, URL orqali (S10). Mijozda filtrlash
  //: MUMKIN EMAS: ro'yxat kursorli, ya'ni faqat joriy 25 qator ichida
  //: qidirardi va «topilmadi» degan yolg'on javob berardi.
  useEffect(() => {
    if (draft === (username ?? "")) return;
    const timer = window.setTimeout(() => {
      synced.current = draft;
      router.push(href({ username: draft || undefined }));
    }, SEARCH_DEBOUNCE_MS);
    return () => window.clearTimeout(timer);
  }, [draft, href, router, username]);

  const chip = (active: boolean) =>
    `rw-radius-sm px-2.5 py-1 text-theme-xs font-medium transition ${
      active ? "rw-accent-soft rw-accent-ink" : "rw-dim rw-hover-bg"
    }`;

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap items-center gap-2">
        <label className="flex items-center gap-2">
          <span className="sr-only">{t(locale, "attempts.searchLabel")}</span>
          <input
            type="search"
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            placeholder={t(locale, "attempts.searchPlaceholder")}
            className="rw-radius-sm rw-field-bg w-44 border rw-divider px-2.5 py-1 text-theme-xs rw-strong"
          />
        </label>

        <span className="ml-auto flex items-center gap-1.5">
          <span className="rw-faint text-theme-xs">{t(locale, "attempts.pageSize")}</span>
          {PAGE_SIZES.map((option) => (
            <Link
              key={option}
              href={href({ size: option === 25 ? undefined : String(option) })}
              className={chip(String(option) === (size ?? "25"))}
            >
              {option}
            </Link>
          ))}
        </span>
      </div>

      {/* Yopishqoq (S09): 891 qatorli sahifada filtr ekrandan chiqib
          ketsa, foydalanuvchi uni esdan chiqaradi va «nega ro'yxat
          g'alati?» degan savol qoladi. */}
      <div
        className="sticky top-0 z-20 -mx-1 space-y-1.5 px-1 py-2"
        style={{ background: "var(--rw-ground)" }}
      >
        <div className="flex flex-wrap items-center gap-1.5">
          <Link href={href({ verdict: undefined })} className={chip(!verdict)}>
            {t(locale, "attempts.allVerdicts")}
          </Link>
          {VERDICT_FILTERS.map(([value, key]) => (
            <Link
              key={value}
              href={href({ verdict: value })}
              className={chip(verdict === value)}
            >
              {t(locale, key)}
            </Link>
          ))}

          {languages.length > 1 && (
            <>
              <span className="mx-1 rw-faint">·</span>
              <Link href={href({ language: undefined })} className={chip(!language)}>
                {t(locale, "filter.allLanguages")}
              </Link>
              {languages.map((code) => (
                <Link
                  key={code}
                  href={href({ language: code })}
                  className={chip(language === code)}
                >
                  {code}
                </Link>
              ))}
            </>
          )}

          {ready && user && (
            <Link
              href={href({ mine: mine ? undefined : "true" })}
              className={`ml-auto ${chip(mine)}`}
            >
              {t(locale, "filter.onlyMine")}
            </Link>
          )}
        </div>

        {/* Faol filtr ko'rsatkichi (S11). Usiz «faqat meniki» yoqilganda
            ro'yxat butunlay o'zgaradi-yu, sabab ko'rinmaydi — eng ko'p
            uchraydigan UX tupigi. */}
        {activeCount > 0 && (
          <div className="flex flex-wrap items-center gap-2 text-theme-xs rw-faint">
            <span>{fill(t(locale, "attempts.activeFilters"), { count: activeCount })}</span>
            <Link href={`/problems/${slug}/status` as Route} className="rw-accent-ink">
              {t(locale, "attempts.clearFilters")}
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
