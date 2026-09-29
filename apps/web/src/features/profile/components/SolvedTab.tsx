import type { Route } from "next";
import Link from "next/link";

import { DifficultyBadge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { Pager } from "@/components/ui/Pager";
import { Segmented } from "@/components/ui/Segmented";
import {
  EmptyRow,
  TBody,
  TD,
  TH,
  THead,
  TR,
  Table,
} from "@/components/ui/Table";
import { t, type Locale } from "@/i18n/messages";
import { api } from "@/lib/api";
import { formatDate, padCode } from "@rankwant/shared/format";
import { BrandIcon, languageIcon } from "@/lib/tech-icons";

type Query = { view?: string; q?: string; ordering?: string; page?: string };

const PAGE_SIZE = 50;
const ORDERINGS: [string, string][] = [
  ["", "profile.sortDifficulty"],
  ["-first_ac_at", "profile.sortNewest"],
  ["first_ac_at", "profile.sortOldest"],
  ["title", "profile.sortTitle"],
];

const chip = (active: boolean) =>
  `rw-radius-sm px-2.5 py-1 text-theme-xs font-medium transition ${
    active ? "rw-accent-soft rw-accent-ink" : "rw-dim rw-hover-bg"
  }`;

/** Ko'rinish qiymatlari — URL'ga ketadi, ya'ni o'zgarmas bo'lishi shart.
 *  Konstantada saqlanadi: `check_hardcoded.py` ternary ichidagi literalni
 *  qattiq yozilgan matn deb o'qiydi va yolg'on qizaradi. */
const VIEW = { chips: "chips", table: "table" } as const;

/** Yechilganlar: chiplar (ixcham) yoki jadval (AC vaqti, eng yaxshi natija, tillar). */
export async function SolvedTab({
  username,
  query,
  locale,
}: {
  username: string;
  query: Query;
  locale: Locale;
}) {
  const page = Math.max(1, Number(query.page) || 1);
  const table = query.view === "table";
  const params = new URLSearchParams({ page: String(page), page_size: String(PAGE_SIZE) });
  if (query.q) params.set("q", query.q);
  if (query.ordering) params.set("ordering", query.ordering);
  const data = await api.solvedPage(username, `?${params}`);

  const base = `/users/${username}/solved`;
  const href = (next: Partial<Query>): Route => {
    const merged: Query = { ...query, page: undefined, ...next };
    const out = new URLSearchParams();
    for (const [key, value] of Object.entries(merged)) if (value) out.set(key, value);
    return `${base}${out.size ? `?${out}` : ""}` as Route;
  };

  return (
    <Card bodyClassName="p-0">
      <div className="flex flex-wrap items-center gap-3 border-b rw-divider px-5 py-4">
        <Segmented
          label={t(locale, "filter.viewLabel")}
          value={table ? VIEW.table : VIEW.chips}
          options={[
            {
              value: VIEW.chips,
              label: t(locale, "profile.viewChips"),
              href: href({ view: undefined }),
            },
            {
              value: VIEW.table,
              label: t(locale, "profile.viewTable"),
              href: href({ view: "table" }),
            },
          ]}
        />
        <form action={base} className="flex min-w-0 flex-1 gap-2">
          {query.view && <input type="hidden" name="view" value={query.view} />}
          {query.ordering && <input type="hidden" name="ordering" value={query.ordering} />}
          <label className="min-w-0 flex-1">
            <span className="sr-only">{t(locale, "profile.search")}</span>
            <input
              type="search"
              name="q"
              defaultValue={query.q ?? ""}
              placeholder={t(locale, "profile.searchSolved")}
              className="h-9 w-full rw-radius-sm border rw-line px-3 text-theme-sm rw-strong rw-field-bg rw-focus-ring rw-placeholder rw-fm-inp"
            />
          </label>
        </form>
        <div className="flex flex-wrap gap-1">
          {ORDERINGS.map(([value, key]) => (
            <Link
              key={value || "default"}
              href={href({ ordering: value || undefined })}
              className={chip((query.ordering ?? "") === value)}
            >
              {t(locale, key)}
            </Link>
          ))}
        </div>
      </div>

      {table ? (
        <Table>
          <THead>
            <TH>#</TH>
            <TH>{t(locale, "problems.name")}</TH>
            <TH>{t(locale, "problems.difficulty")}</TH>
            <TH>{t(locale, "profile.firstAc")}</TH>
            <TH align="right">{t(locale, "profile.bestTime")}</TH>
            <TH align="right">{t(locale, "profile.bestMemory")}</TH>
            <TH>{t(locale, "profile.languagesCol")}</TH>
          </THead>
          <TBody>
            {data.results.map((row) => (
              <TR key={row.slug}>
                <TD className="font-mono rw-faint">{padCode(row.code)}</TD>
                <TD>
                  <Link href={`/problems/${row.slug}` as Route} className="font-medium rw-strong rw-link-hover">
                    {row.title}
                  </Link>
                </TD>
                <TD>
                  <DifficultyBadge value={row.difficulty} />
                </TD>
                <TD className="rw-dim">{formatDate(row.first_ac_at, locale)}</TD>
                <TD align="right" className="tabular-nums">
                  {row.best_time_ms ?? "—"} ms
                </TD>
                <TD align="right" className="tabular-nums">
                  {row.best_memory_kb ?? "—"} KB
                </TD>
                <TD>
                  <span className="flex flex-wrap gap-1">
                    {row.languages.map((code) => {
                      const icon = languageIcon(code);
                      return (
                        <span key={code} title={code} className="flex size-6 items-center justify-center rw-radius-sm rw-chip">
                          {icon ? <BrandIcon icon={icon} className="size-3.5" /> : <span className="text-theme-2xs">{code.slice(0, 2)}</span>}
                        </span>
                      );
                    })}
                  </span>
                </TD>
              </TR>
            ))}
            {data.results.length === 0 && <EmptyRow colSpan={7}>{t(locale, "common.empty")}</EmptyRow>}
          </TBody>
        </Table>
      ) : (
        <div className="flex flex-wrap gap-2 px-5 py-4">
          {data.results.map((row) => (
            <Link
              key={row.slug}
              href={`/problems/${row.slug}` as Route}
              className="flex items-center gap-2 rw-radius-sm border rw-line px-3 py-1.5 text-theme-sm transition rw-hover-line"
              // Joriy va yechilgandagi qiyinlik farq qilsa — qayta baholangan.
              title={
                row.difficulty !== row.difficulty_at_solve
                  ? `${row.difficulty_at_solve} → ${row.difficulty} (${t(locale, "profile.rerated")})`
                  : undefined
              }
            >
              <span className="rw-strong">{row.title}</span>
              <DifficultyBadge value={row.difficulty} />
              {row.difficulty !== row.difficulty_at_solve && (
                <span className="rw-warn-ink" aria-hidden="true">
                  *
                </span>
              )}
            </Link>
          ))}
          {data.results.length === 0 && <p className="text-theme-sm rw-faint">{t(locale, "common.empty")}</p>}
        </div>
      )}
      <Pager
        locale={locale}
        page={page}
        count={data.count}
        pageSize={PAGE_SIZE}
        href={(to) => {
          const out = new URLSearchParams();
          for (const [key, value] of Object.entries({ ...query, page: String(to) })) if (value) out.set(key, value);
          return `${base}?${out}` as Route;
        }}
      />
    </Card>
  );
}
