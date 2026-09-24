"use client";

import type { Route } from "next";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useMemo, useState } from "react";

import { SortHeader, TBody, TD, TH, THead, Table, type SortDirection } from "@/components/ui/Table";
import { UserName } from "@/components/ui/Identity";
import { Verdict } from "@/components/ui/Verdict";
import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { dateTime, fill, t } from "@/i18n/messages";
import { API_BASE, type Attempt } from "@/lib/api";

/** Saralanadigan ustun → API `ordering` maydoni.
 *
 *  Faqat sonli va o'zgarmas maydonlar: `username`/`verdict` ni saralash
 *  891 qatorli oqimda ma'noli emas, ustiga backendda indekssiz. Bu
 *  ro'yxat `ATTEMPT_ORDERINGS` bilan AYNAN bir xil bo'lishi shart —
 *  aks holda tugma bosiladi, javob esa o'zgarmaydi (bir marta shunday
 *  bo'lgan: parametr sxemada bor edi, lekin sahifalagich uni bosib
 *  ketardi).
 */
const SORTABLE = {
  runTime: "time_ms",
  memory: "memory_kb",
  codeSize: "source_size",
} as const;

type SortColumn = keyof typeof SORTABLE;

/** Yo'nalish — alohida DOIMIYLAR, ternary ichida emas.
 *  `check_hardcoded.py` ternary shoxobidagi satrni «qattiq yozilgan
 *  matn» deb o'qiydi (aynan shu tuzoq `components/ui/Table.tsx` da ham
 *  yozib qo'yilgan), ya'ni tekshiruv yolg'on qizarardi. */
const ASC: SortDirection = "asc";
const DESC: SortDirection = "desc";

/** Navbat kutish chegarasi, soniya. Undan qisqasi ko'rsatilmaydi —
 *  normal holatda sud darhol boshlanadi va raqam shovqin bo'lardi. */
const QUEUE_MIN_SECONDS = 0.5;

function queueSeconds(row: Attempt): number | null {
  if (!row.judged_at) return null;
  const waited = (Date.parse(row.judged_at) - Date.parse(row.created_at)) / 1000;
  return waited >= QUEUE_MIN_SECONDS ? waited : null;
}

/** Saralash tugmasi bosilganda keyingi `ordering`.
 *
 *  Yangi ustun — KAMAYISH tartibidan boshlanadi: «eng tez» bosilganda
 *  eng tez yechim yuqorida bo'lishi kerak, eng sekin emas. Faol ustun
 *  qayta bosilsa yo'nalish almashadi.
 */
function nextOrdering(column: SortColumn, current: string | undefined): string {
  const field = SORTABLE[column];
  return current === `-${field}` ? field : `-${field}`;
}

export function AttemptTable({
  slug,
  rows,
  ordering,
  query,
}: {
  slug: string;
  rows: Attempt[];
  /** Joriy `?ordering=` qiymati (berilmasa — standart tartib). */
  ordering?: string;
  /** Boshqa filtrlar. Saralashda saqlanadi, `cursor` esa tashlanadi. */
  query: Record<string, string | undefined>;
}) {
  const locale = useLocale();
  const { user } = useSession();
  const router = useRouter();
  const [focusIndex, setFocusIndex] = useState(0);

  /** Manba kodni nusxalash huquqi. Backend baribir tekshiradi (IDOR),
   *  bu yerdagi shart faqat tugmani KO'RSATMASLIK uchun: bosilganda
   *  hech narsa qaytarmaydigan tugma yolg'on va'da bo'lardi. */
  const canSeeSource = useCallback(
    (username: string) => Boolean(user) && (user!.is_staff || user!.username === username),
    [user],
  );

  /** Ustunlar SHARTLI (S01): `contest` va `score` ko'p qatorda bo'sh
   *  bo'ladi, shuning uchun ular faqat shu sahifada qiymat bo'lsa
   *  chiziladi. Bo'sh ustun joyni bekorga yeb, jadvalni siqardi. */
  const showContest = useMemo(() => rows.some((row) => row.contest), [rows]);
  const showScore = useMemo(() => rows.some((row) => row.score > 0), [rows]);

  const href = useCallback(
    (next: Record<string, string | undefined>) => {
      const params = new URLSearchParams();
      // `cursor` ATAYLAB tashlanadi: tartib o'zgarsa eski kursor boshqa
      // qatorga ishora qiladi va sahifa ro'yxat o'rtasidan ochilardi.
      for (const [key, value] of Object.entries({
        ...query,
        cursor: undefined,
        ...next,
      })) {
        if (value) params.set(key, value);
      }
      return `/problems/${slug}/status${params.size ? `?${params}` : ""}` as Route;
    },
    [query, slug],
  );

  const sortProps = useCallback(
    (column: SortColumn) => {
      const field = SORTABLE[column];
      const direction: SortDirection = ordering === field ? ASC : DESC;
      return {
        active: ordering === field || ordering === `-${field}`,
        direction,
        onSort: () => router.push(href({ ordering: nextOrdering(column, ordering) })),
      };
    },
    [href, ordering, router],
  );

  const open = useCallback((id: number) => router.push(`/attempts/${id}`), [router]);

  /** ↑ ↓ + Enter (S17). Roving tabindex: FAQAT bitta qator tab-stop,
   *  qolganlari `-1`. Usiz Tab bilan yurish 25 qator uchun 25 marta
   *  bosish demak bo'lardi. */
  const onRowKeyDown = useCallback(
    (event: React.KeyboardEvent<HTMLTableRowElement>, index: number, id: number) => {
      if (event.key === "ArrowDown") {
        event.preventDefault();
        setFocusIndex(Math.min(rows.length - 1, index + 1));
      } else if (event.key === "ArrowUp") {
        event.preventDefault();
        setFocusIndex(Math.max(0, index - 1));
      } else if (event.key === "Enter") {
        event.preventDefault();
        open(id);
      }
    },
    [open, rows.length],
  );

  return (
    <Table>
      <THead>
        <TH className="w-20">#</TH>
        <TH className="hidden sm:table-cell">{t(locale, "attempts.col.submitted")}</TH>
        <TH className="hidden sm:table-cell">{t(locale, "attempts.language")}</TH>
        <TH>{t(locale, "standings.user")}</TH>
        <TH>{t(locale, "attempts.verdict")}</TH>
        <SortHeader {...sortProps("runTime")} align="right" className="hidden sm:table-cell">
          {t(locale, "attempts.col.runTime")}
        </SortHeader>
        <SortHeader {...sortProps("memory")} align="right" className="hidden md:table-cell">
          {t(locale, "col.memory")}
        </SortHeader>
        <SortHeader {...sortProps("codeSize")} align="right" className="hidden lg:table-cell">
          {t(locale, "attempts.col.codeSize")}
        </SortHeader>
        {showContest && (
          <TH className="hidden lg:table-cell">{t(locale, "attempts.col.contest")}</TH>
        )}
        {showScore && (
          <TH align="right" className="hidden lg:table-cell">
            {t(locale, "col.points")}
          </TH>
        )}
      </THead>
      <TBody>
        {rows.map((row, index) => {
          const waited = queueSeconds(row);
          return (
            <tr
              key={row.id}
              // Butun qator bosiladi (S15) va klaviatura bilan yuriladi
              // (S17). `<TR>` bu proplarni qabul qilmaydi, shuning uchun
              // sinflar o'sha komponentdan ko'chirilgan.
              // `role="row"` — `<tr>` ning o'zi shu rolga ega, lekin
              // ochiq yozilgan: `onClick` li element uchun `role`
              // talab qilinadi (`tools/check_a11y.py`).
              role="row"
              tabIndex={focusIndex === index ? 0 : -1}
              onKeyDown={(event) => onRowKeyDown(event, index, row.id)}
              onFocus={() => setFocusIndex(index)}
              onClick={(event) => {
                // Ichkaridagi havola o'z ishini qilsin: `stopPropagation`
                // uchun o'ram `<span>` qo'yilsa, u klaviaturasiz
                // interaktiv element bo'lib qolardi.
                if ((event.target as HTMLElement).closest("a")) return;
                open(row.id);
              }}
              className="transition rw-hover-bg cursor-pointer rw-focus-ring"
            >
              {/* Ichma-ich `<a>` HTML da taqiqlangan, shuning uchun qator
                  `<a>` emas. Klaviatura va ekran o'quvchi uchun HAQIQIY
                  havola shu yerda turadi; sichqoncha uchun butun qator
                  ishlaydi. */}
              <TD className="font-mono text-theme-xs rw-faint tabular-nums">
                <Link
                  href={`/attempts/${row.id}`}
                  className="rw-link-hover"
                  tabIndex={-1}
                  aria-label={t(locale, "attempts.rowOpen")}
                >
                  {row.id}
                </Link>
              </TD>

              <TD className="hidden sm:table-cell">
                <time dateTime={row.created_at} className="rw-dim-2">
                  {dateTime(row.created_at, locale)}
                </time>
                {waited !== null && (
                  <span className="block text-theme-xs rw-faint">
                    {fill(t(locale, "attempts.queuedFor"), {
                      seconds: waited.toFixed(1),
                    })}
                  </span>
                )}
              </TD>

              <TD className="hidden rw-dim sm:table-cell">{row.language}</TD>

              <TD>
                <span className="inline-flex items-center gap-1.5">
                  {row.is_first_solver && (
                    <span
                      className="rw-radius-sm rw-accent-soft rw-accent-ink px-1.5 py-0.5 text-theme-xs"
                      title={t(locale, "attempts.firstSolver")}
                    >
                      ✓
                    </span>
                  )}
                  <UserName
                    username={row.username}
                    title={row.user_title}
                    locale={locale}
                  />
                </span>
                {/* MOBIL — ikki qatorli stack (S20). Ustunlar
                    YASHIRILMAYDI, shu yerga ko'chadi: hech narsa
                    yo'qolmaydi. `sm` dan yuqorida ko'rinmaydi. */}
                <span className="mt-0.5 block text-theme-xs rw-faint sm:hidden">
                  {[
                    dateTime(row.created_at, locale),
                    row.language,
                    `${row.time_ms} ms`,
                    `${Math.round(row.memory_kb / 1024)} MB`,
                    `${row.source_size} B`,
                    showContest ? row.contest : null,
                    showScore && row.score > 0 ? String(row.score) : null,
                  ]
                    .filter(Boolean)
                    .join(" · ")}
                </span>
              </TD>

              <TD>
                <span className="inline-flex flex-wrap items-center gap-1.5">
                  <Verdict verdict={row.verdict} />
                  {row.failed_test_index !== null && (
                    <span className="rw-faint text-theme-xs">
                      {fill(t(locale, "attempts.failedAtTest"), {
                        index: row.failed_test_index,
                      })}
                    </span>
                  )}
                  {canSeeSource(row.username) && <CopySource id={row.id} />}
                </span>
              </TD>

              <TD align="right" className="hidden rw-faint tabular-nums sm:table-cell">
                {row.time_ms} ms
              </TD>
              <TD align="right" className="hidden rw-faint tabular-nums md:table-cell">
                {Math.round(row.memory_kb / 1024)} MB
              </TD>
              <TD align="right" className="hidden rw-faint tabular-nums lg:table-cell">
                {row.source_size} B
              </TD>
              {showContest && <TD className="hidden rw-faint lg:table-cell">{row.contest}</TD>}
              {showScore && (
                <TD align="right" className="hidden rw-faint tabular-nums lg:table-cell">
                  {row.score}
                </TD>
              )}
            </tr>
          );
        })}
      </TBody>
    </Table>
  );
}

/** Manba kodni nusxalash (S16).
 *
 *  ⚠️ Kod RO'YXAT javobida YO'Q: `AttemptSerializer` uni qaytarmaydi,
 *  chunki manba faqat egasiga va xodimga ochiladi (IDOR himoyasi).
 *  Shuning uchun nusxa bosilganda `GET /attempts/{id}/` ketadi — ro'yxat
 *  javobi og'irlashmaydi, huquqni esa backend tekshiradi. Tugma ham
 *  faqat o'sha qatorlarda chiziladi (o'chirilgan tugma emas).
 */
function CopySource({ id }: { id: number }) {
  const locale = useLocale();
  const [state, setState] = useState<"idle" | "busy" | "done" | "fail">("idle");

  const copy = useCallback(async () => {
    setState("busy");
    try {
      const response = await fetch(`${API_BASE}/attempts/${id}/`, {
        credentials: "include",
      });
      if (!response.ok) throw new Error(String(response.status));
      const body = (await response.json()) as { source_code?: string };
      if (!body.source_code) throw new Error("empty source");
      await navigator.clipboard.writeText(body.source_code);
      setState("done");
    } catch {
      setState("fail");
    }
    window.setTimeout(() => setState("idle"), 1500);
  }, [id]);

  const label =
    state === "done"
      ? t(locale, "problem.copied")
      : state === "fail"
        ? t(locale, "problem.copyFailed")
        : t(locale, "attempts.copySource");

  return (
    <button
      type="button"
      onClick={(event) => {
        event.stopPropagation();
        void copy();
      }}
      disabled={state === "busy"}
      title={label}
      aria-label={label}
      className="rw-radius-sm rw-faint rw-hover-bg rw-focus-ring px-1 py-0.5 text-theme-xs"
    >
      {state === "done" ? "✓" : state === "fail" ? "!" : "⧉"}
    </button>
  );
}
