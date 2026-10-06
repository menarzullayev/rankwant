"use client";

import type { Route } from "next";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";

import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";
import { VERDICT_FILTERS } from "@/lib/api";
import { buildAttemptListHref } from "@/lib/problem-tabs";

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
  problem,
  size,
  ordering,
  activeCount,
}: {
  /** The problem whose tab this is; left out on the site-wide feed. */
  slug?: string;
  languages: { code: string; name: string }[];
  verdict?: string;
  language?: string;
  mine: boolean;
  username?: string;
  /** Feed only: the problem filter, as typed (a number or a slug). */
  problem?: string;
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
      //: `cursor` har filtr o'zgarishida tashlanadi (`buildAttemptsHref`
      //: ichida): eski kursor yangi ro'yxatning boshqa joyiga ishora qilardi.
      const merged = {
        verdict,
        language,
        mine: mine ? "true" : undefined,
        username,
        problem: slug ? undefined : problem,
        ordering,
        size,
        cursor: undefined,
        ...next,
      };
      return buildAttemptListHref(slug, merged) as Route;
    },
    [language, mine, ordering, problem, size, slug, username, verdict],
  );

  // The same debounce as the user search, for the feed's problem filter.
  const [problemDraft, setProblemDraft] = useState(problem ?? "");
  const problemSynced = useRef(problem ?? "");
  useEffect(() => {
    if ((problem ?? "") !== problemSynced.current) {
      problemSynced.current = problem ?? "";
      setProblemDraft(problem ?? "");
    }
  }, [problem]);
  useEffect(() => {
    if (slug || problemDraft === (problem ?? "")) return;
    const timer = window.setTimeout(() => {
      problemSynced.current = problemDraft;
      router.push(href({ problem: problemDraft.trim() || undefined }));
    }, SEARCH_DEBOUNCE_MS);
    return () => window.clearTimeout(timer);
  }, [href, problem, problemDraft, router, slug]);

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

  const scope = (active: boolean) =>
    `rw-radius-sm inline-flex min-h-9 items-center px-3 text-theme-xs font-medium transition rw-focus-ring ${
      active ? "rw-surface rw-strong" : "rw-dim"
    }`;

  const chip = (active: boolean) =>
    `rw-radius-sm px-2.5 py-1 text-theme-xs font-medium transition ${
      active ? "rw-accent-soft rw-accent-ink" : "rw-dim rw-hover-bg"
    }`;

  const field =
    "rw-radius-sm rw-field-bg min-h-9 border rw-divider px-2.5 py-1 text-theme-xs rw-strong";
  const signedIn = ready && Boolean(user);

  return (
    <div className="space-y-2">
      {/* The feed's first question is "whose attempts": everyone's or
          mine. On a problem's tab the same switch is a chip further down. */}
      {!slug && signedIn && (
        <div className="inline-flex rw-radius-sm rw-field-bg p-0.5">
          <Link href={href({ mine: undefined })} className={scope(!mine)} aria-current={!mine}>
            {t(locale, "attempts.scopeAll")}
          </Link>
          <Link href={href({ mine: "true" })} className={scope(mine)} aria-current={mine}>
            {t(locale, "attempts.scopeMine")}
          </Link>
        </div>
      )}

      <div className="flex flex-wrap items-center gap-2">
        <label className="flex items-center gap-2">
          <span className="sr-only">{t(locale, "attempts.searchLabel")}</span>
          <input
            type="search"
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            placeholder={t(locale, "attempts.searchPlaceholder")}
            className={`${field} w-44`}
          />
        </label>

        {!slug && (
          <label className="flex items-center gap-2">
            <span className="sr-only">{t(locale, "attempts.problemLabel")}</span>
            <input
              type="search"
              value={problemDraft}
              onChange={(event) => setProblemDraft(event.target.value)}
              placeholder={t(locale, "attempts.problemPlaceholder")}
              className={`${field} w-48`}
            />
          </label>
        )}

        {languages.length > 1 && (
          <label className="flex items-center gap-2">
            <span className="sr-only">{t(locale, "attempts.language")}</span>
            {/* A list, not chips: thirty-five languages as chips were four
                rows of internal codes above the table. */}
            <select
              value={language ?? ""}
              onChange={(event) => router.push(href({ language: event.target.value || undefined }))}
              className={`${field} max-w-[14rem]`}
            >
              <option value="">{t(locale, "filter.allLanguages")}</option>
              {languages.map((item) => (
                <option key={item.code} value={item.code}>
                  {item.name}
                </option>
              ))}
            </select>
          </label>
        )}

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

          {slug && signedIn && (
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
            <Link href={buildAttemptListHref(slug, {}) as Route} className="rw-accent-ink">
              {t(locale, "attempts.clearFilters")}
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
