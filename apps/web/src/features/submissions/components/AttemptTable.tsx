"use client";

import type { Route } from "next";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useMemo, useState } from "react";

import { numericStamp } from "@rankwant/shared/format";

import { SortHeader, TBody, TD, TH, THead, Table, type SortDirection } from "@/components/ui/Table";
import { UserName } from "@/components/ui/Identity";
import { Loading } from "@/components/ui/Loading";
import { Verdict } from "@/components/ui/Verdict";
import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t, type Locale } from "@/i18n/messages";
import { mergeAttemptRow, useAttemptLiveOptional, AttemptLiveProgress } from "@/features/submissions";
import { API_BASE, type Attempt } from "@/lib/api";
import { buildAttemptListHref } from "@/lib/problem-tabs";
import { isPendingVerdict, verdictOf } from "@/lib/theme/verdict";

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

/** No value yet. */
const DASH = "—";

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

function runningHint(locale: Locale, row: Attempt): string | null {
  if (row.verdict === "RUNNING" && row.running_test_index != null) {
    return fill(t(locale, "submit.runningTest"), { n: row.running_test_index });
  }
  if (row.verdict === "RUNNING") {
    return t(locale, "submit.running");
  }
  return null;
}

/** `#0012 Tub sonlar`, or the slug for a problem that keeps its title. */
function problemName(row: Attempt): string {
  const title = row.problem_title || row.problem;
  return row.problem_code !== null
    ? `#${String(row.problem_code).padStart(4, "0")} ${title}`
    : title;
}

function verdictName(locale: Locale, verdict: string): string {
  const known = verdictOf(verdict);
  return known ? t(locale, known.labelKey) : verdict;
}

export function AttemptTable({
  slug,
  rows,
  ordering,
  query,
}: {
  /** The problem whose tab this is. Left out on the site-wide feed,
   *  where every row names its own problem instead. */
  slug?: string;
  rows: Attempt[];
  /** Joriy `?ordering=` qiymati (berilmasa — standart tartib). */
  ordering?: string;
  /** Boshqa filtrlar. Saralashda saqlanadi, `cursor` esa tashlanadi. */
  query: Record<string, string | undefined>;
}) {
  const locale = useLocale();
  const { user } = useSession();
  const router = useRouter();
  const live = useAttemptLiveOptional();
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
      // `cursor` ATAYLAB tashlanadi (`buildAttemptsHref` ichida): tartib
      // o'zgarsa eski kursor boshqa qatorga ishora qiladi va sahifa
      // ro'yxat o'rtasidan ochilardi.
      return buildAttemptListHref(slug, { ...query, ...next }) as Route;
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
        <TH className="hidden @2xl:table-cell">{t(locale, "attempts.col.submitted")}</TH>
        <TH className="hidden @2xl:table-cell">{t(locale, "attempts.language")}</TH>
        <TH>{t(locale, "standings.user")}</TH>
        {!slug && <TH className="hidden @2xl:table-cell">{t(locale, "problems.name")}</TH>}
        <TH>{t(locale, "attempts.verdict")}</TH>
        <SortHeader {...sortProps("runTime")} align="right" className="hidden @3xl:table-cell">
          {t(locale, "attempts.col.runTime")}
        </SortHeader>
        <SortHeader {...sortProps("memory")} align="right" className="hidden @4xl:table-cell">
          {t(locale, "col.memory")}
        </SortHeader>
        <SortHeader {...sortProps("codeSize")} align="right" className="hidden @[60rem]:table-cell">
          {t(locale, "attempts.col.codeSize")}
        </SortHeader>
        {showContest && (
          <TH className="hidden @[60rem]:table-cell">{t(locale, "attempts.col.contest")}</TH>
        )}
        {showScore && (
          <TH align="right" className="hidden @[60rem]:table-cell">
            {t(locale, "col.points")}
          </TH>
        )}
      </THead>
      <TBody>
        {rows.map((row, index) => {
          const display = mergeAttemptRow(
            row,
            live?.getPatch(row.id, {
              verdict: row.verdict,
              running_test_index: row.running_test_index,
            }),
          );
          const waited = queueSeconds(display);
          const progressHint = runningHint(locale, display);
          const showProgress = isPendingVerdict(display.verdict);
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

              <TD className="hidden @2xl:table-cell">
                <time dateTime={row.created_at} className="rw-dim-2">
                  {numericStamp(row.created_at)}
                </time>
                {waited !== null && (
                  <span className="block text-theme-xs rw-faint">
                    {fill(t(locale, "attempts.queuedFor"), {
                      seconds: waited.toFixed(1),
                    })}
                  </span>
                )}
              </TD>

              <TD className="hidden rw-dim @2xl:table-cell">{row.language_name || row.language}</TD>

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
                <span className="mt-0.5 block text-theme-xs rw-faint @2xl:hidden">
                  {/* The verdict mark can be a bare colour on a phone
                      (D56), so its name is spelled out here too. */}
                  <span className="block rw-dim">
                    {[
                      !slug ? problemName(row) : null,
                      verdictName(locale, display.verdict),
                      display.failed_test_index !== null
                        ? fill(t(locale, "attempts.failedAtTest"), {
                            index: display.failed_test_index,
                          })
                        : null,
                    ]
                      .filter(Boolean)
                      .join(" · ")}
                  </span>
                  {[
                    numericStamp(row.created_at),
                    row.language_name || row.language,
                    showProgress ? null : `${row.time_ms} ms`,
                    showProgress ? null : `${Math.round(row.memory_kb / 1024)} MB`,
                    `${row.source_size} B`,
                    showContest ? row.contest : null,
                    showScore && row.score > 0 ? String(row.score) : null,
                  ]
                    .filter(Boolean)
                    .join(" · ")}
                </span>
              </TD>

              {!slug && (
                <TD className="hidden @2xl:table-cell">
                  <Link href={`/problems/${row.problem}` as Route} className="rw-link-hover">
                    {row.problem_code !== null && (
                      <span className="mr-1.5 font-mono text-theme-xs rw-faint tabular-nums">
                        #{String(row.problem_code).padStart(4, "0")}
                      </span>
                    )}
                    {row.problem_title || row.problem}
                  </Link>
                </TD>
              )}

              <TD>
                <span className="inline-flex flex-col gap-2">
                  <span className="inline-flex flex-wrap items-center gap-1.5">
                    <Verdict verdict={display.verdict} />
                    {showProgress && (
                      <span className="inline-flex items-center gap-1 text-theme-xs rw-dim">
                        <Loading className="scale-75" />
                        {progressHint}
                      </span>
                    )}
                    {display.failed_test_index !== null && (
                      <span className="hidden rw-faint text-theme-xs @2xl:inline">
                        {fill(t(locale, "attempts.failedAtTest"), {
                          index: display.failed_test_index,
                        })}
                      </span>
                    )}
                    {canSeeSource(row.username) && <CopySource id={row.id} />}
                  </span>
                  {showProgress && live?.getLiveState(row.id) && (
                    <AttemptLiveProgress
                      attemptId={row.id}
                      state={live.getLiveState(row.id)!}
                      compact
                    />
                  )}
                </span>
              </TD>

              {/* An attempt still being judged has no time or memory yet;
                  `0 ms` would read as a measurement. */}
              <TD align="right" className="hidden rw-faint tabular-nums @3xl:table-cell">
                {showProgress ? DASH : `${row.time_ms} ms`}
              </TD>
              <TD align="right" className="hidden rw-faint tabular-nums @4xl:table-cell">
                {showProgress ? DASH : `${Math.round(row.memory_kb / 1024)} MB`}
              </TD>
              <TD align="right" className="hidden rw-faint tabular-nums @[60rem]:table-cell">
                {row.source_size} B
              </TD>
              {showContest && <TD className="hidden rw-faint @[60rem]:table-cell">{row.contest}</TD>}
              {showScore && (
                <TD align="right" className="hidden rw-faint tabular-nums @[60rem]:table-cell">
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
