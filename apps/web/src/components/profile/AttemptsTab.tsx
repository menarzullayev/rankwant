import type { Route } from "next";
import Link from "next/link";

import { Card } from "@/components/ui/Card";
import {
  EmptyRow,
  TBody,
  TD,
  TH,
  THead,
  TR,
  Table,
} from "@/components/ui/Table";
import { VerdictBadge } from "@/components/VerdictBadge";
import { t, type Locale } from "@/i18n/messages";
import { api, VERDICT_FILTERS } from "@/lib/api";
import { formatDate } from "@/lib/format";

type Filters = { problem?: string; verdict?: string; language?: string; cursor?: string };

const chip = (active: boolean) =>
  `rw-radius-sm px-2.5 py-1 text-theme-xs font-medium transition ${
    active ? "rw-accent-soft rw-accent-ink" : "rw-dim rw-hover-bg"
  }`;

/** Foydalanuvchining urinishlari — masala, til va verdikt bo'yicha.
 *  Manba kodi bu yerda yo'q: u faqat egasiga ochiladi (IDOR qoidasi). */
export async function AttemptsTab({
  username,
  filters,
  locale,
}: {
  username: string;
  filters: Filters;
  locale: Locale;
}) {
  const query = new URLSearchParams({ username });
  for (const [key, value] of Object.entries(filters)) if (value) query.set(key, value);
  const [data, languages] = await Promise.all([
    api.attemptsQuery(`?${query}`),
    api.languages(),
  ]);

  const base = `/users/${username}/urinishlar`;
  const href = (next: Partial<Filters>): Route => {
    const merged: Filters = { ...filters, cursor: undefined, ...next };
    const params = new URLSearchParams();
    for (const [key, value] of Object.entries(merged)) if (value) params.set(key, value);
    return `${base}${params.size ? `?${params}` : ""}` as Route;
  };
  const cursorOf = (url: string | null) =>
    url ? (new URL(url).searchParams.get("cursor") ?? undefined) : undefined;
  const newer = cursorOf(data.previous);
  const older = cursorOf(data.next);

  return (
    <Card bodyClassName="p-0">
      <div className="space-y-2 border-b rw-line px-5 py-4">
        {filters.problem && (
          <p className="flex flex-wrap items-center gap-2 text-theme-sm">
            <span className="rw-dim">{t(locale, "problems.name")}:</span>
            <Link href={`/problems/${filters.problem}` as Route} className="font-medium rw-strong hover:underline">
              {filters.problem}
            </Link>
            <Link href={href({ problem: undefined })} className={chip(false)}>
              × {t(locale, "profile.clearFilter")}
            </Link>
          </p>
        )}
        <div className="flex flex-wrap items-center gap-1.5">
          <Link href={href({ verdict: undefined })} className={chip(!filters.verdict)}>
            {t(locale, "attempts.allVerdicts")}
          </Link>
          {VERDICT_FILTERS.map(([value, key]) => (
            <Link key={value} href={href({ verdict: value })} className={chip(filters.verdict === value)}>
              {t(locale, key)}
            </Link>
          ))}
        </div>
        <div className="flex flex-wrap items-center gap-1.5">
          <Link href={href({ language: undefined })} className={chip(!filters.language)}>
            {t(locale, "profile.allLanguages")}
          </Link>
          {languages.results.map((language) => (
            <Link
              key={language.code}
              href={href({ language: language.code })}
              className={chip(filters.language === language.code)}
            >
              {language.name}
            </Link>
          ))}
        </div>
      </div>
      <Table>
        <THead>
          <TH>#</TH>
          <TH>{t(locale, "problems.name")}</TH>
          <TH>{t(locale, "attempts.language")}</TH>
          <TH>{t(locale, "attempts.verdict")}</TH>
          <TH align="right">ms</TH>
          <TH align="right">KB</TH>
          <TH align="right">{t(locale, "profile.date")}</TH>
        </THead>
        <TBody>
          {data.results.map((attempt) => (
            <TR key={attempt.id}>
              <TD className="rw-faint">{attempt.id}</TD>
              <TD>
                <Link
                  href={href({ problem: attempt.problem })}
                  className="rw-link-hover"
                  title={t(locale, "profile.filterByProblem")}
                >
                  {attempt.problem}
                </Link>
              </TD>
              <TD className="rw-faint">{attempt.language}</TD>
              <TD>
                <VerdictBadge verdict={attempt.verdict} locale={locale} />
              </TD>
              <TD align="right">{attempt.time_ms}</TD>
              <TD align="right">{attempt.memory_kb}</TD>
              <TD align="right" className="rw-faint">
                {formatDate(attempt.created_at, locale, { dateStyle: "medium", timeStyle: "short" })}
              </TD>
            </TR>
          ))}
          {data.results.length === 0 && <EmptyRow colSpan={7}>{t(locale, "empty")}</EmptyRow>}
        </TBody>
      </Table>
      {(newer || older) && (
        <nav className="flex justify-between border-t rw-line px-5 py-3 text-theme-sm">
          {newer ? (
            <Link href={href({ cursor: newer })} className="rw-accent-ink hover:underline">
              ← {t(locale, "profile.prev")}
            </Link>
          ) : (
            <span />
          )}
          {older && (
            <Link href={href({ cursor: older })} className="rw-accent-ink hover:underline">
              {t(locale, "profile.next")} →
            </Link>
          )}
        </nav>
      )}
    </Card>
  );
}
