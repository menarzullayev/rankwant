"use client";

import { useEffect, useState } from "react";
import { regionName } from "@rankwant/shared/regions";

import { CopyButton } from "@/components/kit/CopyControl";
import { Badge } from "@/components/ui/Badge";
import { Dropdown } from "@/components/ui/Dropdown";
import { UserName } from "@/components/ui/Identity";
import { Checkbox } from "@/components/ui/SelectField";
import { API_BASE, getJson, type Standing } from "@/lib/api";
import type { StandingsPayload } from "../api/contests";
import { type Locale, t } from "@/i18n/messages";
import {
  EmptyRow,
  TBody,
  TD,
  TH,
  THead,
  TR,
  Table,
} from "@/components/ui/Table";

/** Hack ustuni: ball va qavsda muvaffaqiyatli/muvaffaqiyatsiz soni.
 *
 * Ball MANFIY bo'lishi mumkin (`contest_room` da −50), shuning uchun
 * ishorasi bilan yoziladi — nol bo'lsa esa e'tiborni tortmaydi. */
function HackCell({ row }: { row: Standing }) {
  // `Math.sign` — taqqoslash JUFTI o'rniga: `a > 0 ? … : a < 0 ? …`
  // yozuvida `check_hardcoded` `>` va `<` oralig'ini JSX matni deb
  // o'qiydi va qator yolg'on «qattiq yozilgan matn» bo'lib chiqadi.
  // Ishora bu yerda uchta holatni bildiradi, ya'ni niyat ham aniqroq.
  const sign = Math.sign(row.hack_score);
  const tone =
    sign === 0 ? "rw-faint" : sign === 1 ? "rw-ok-ink" : "rw-bad-ink";
  return (
    <TD align="right" className={`tabular-nums ${tone}`}>
      {sign === 1 ? `+${row.hack_score}` : row.hack_score}
      {(row.hacks_successful > 0 || row.hacks_unsuccessful > 0) && (
        <span className="ml-1 text-theme-xs rw-faint">
          ({row.hacks_successful}/{row.hacks_unsuccessful})
        </span>
      )}
    </TD>
  );
}

/** Place cell: an insider has none — a star, read out as «unrated»
 *  (ADR-0055, part 2). */
function PlaceCell({
  row,
  locale,
  mine = false,
  regional = false,
}: {
  row: Standing;
  locale: Locale;
  mine?: boolean;
  /** The region's own place (`region_rank`) instead of the overall one. */
  regional?: boolean;
}) {
  const tone = mine ? "rw-accent-ink" : "rw-strong";
  const place = regional ? row.region_rank : row.rank;
  if (row.is_disqualified) {
    return (
      <TD className="font-semibold rw-bad-ink">
        <span data-disqualified="">{t(locale, "standings.dq")}</span>
      </TD>
    );
  }
  if (!row.insider_role) {
    return <TD className={`font-semibold ${tone}`}>{place}</TD>;
  }
  return (
    <TD className={`font-semibold ${tone}`}>
      <span aria-hidden="true">*</span>
      <span className="sr-only">{t(locale, "standings.unofficial")}</span>
    </TD>
  );
}

function InsiderBadge({ row, locale }: { row: Standing; locale: Locale }) {
  if (!row.insider_role) return null;
  return (
    <span className="ml-2" data-insider={row.insider_role}>
      <Badge>{t(locale, `contest.role.${row.insider_role}`)}</Badge>
    </span>
  );
}

/** Standings jadvali.
 *
 * Jonli yangilanish POLLING orqali — SSE emas (pastdagi izohga qarang).
 * Ba'zi maktab va korporativ proxy'lar oqimni buferlaydi, ya'ni polling
 * baribir majburiy edi (test-strategy § compatibility).
 */
export function StandingsTable({
  slug,
  initial,
  live,
  locale,
  hacks = false,
}: {
  slug: string;
  initial: StandingsPayload;
  live: boolean;
  locale: Locale;
  /** Hack ustuni ko'rsatilsinmi (ADR-0020). Hack yoqilmagan musobaqada
   *  u har qatorda nol turadigan ortiqcha ustun bo'lardi. */
  hacks?: boolean;
}) {
  const [data, setData] = useState<StandingsPayload>(initial);
  // A school or regional olympiad reads its own table (decision 2026-11-10 ②).
  // The region travels in the link, so a table can be shared as it is.
  const [region, setRegion] = useState(initial.region);
  const [loading, setLoading] = useState(false);
  // Ommaviy jadval eng yaxshi 500 qatorni beradi — bu chegara CDN keshi
  // uchun. Undan pastdagi qatnashchi o'z natijasini ko'rishi uchun qator
  // ALOHIDA olinadi: uni umumiy javobga qo'shish javobni har foydalanuvchi
  // uchun boshqacha qilardi va keshni yo'q qilardi.
  const [me, setMe] = useState<Standing | null>(null);

  // Polling, SSE emas. Har SSE ulanish gunicorn ishchisini besh
  // daqiqagacha band qilardi va o'lchandi — to'rtta tomoshabin butun
  // API ni javobsiz qoldirardi. Jadval hamma uchun bir xil, ya'ni javob
  // CDN da keshlanadi: 110 000 tomoshabin origin'ga 10 soniyada bitta
  // so'rov bo'lib tushadi. Yangilanish 10 s o'rniga 15 s da.
  const tableUrl = (code: string) =>
    `${API_BASE}/contests/${slug}/standings/${code ? `?region=${encodeURIComponent(code)}` : ""}`;

  const chooseRegion = async (code: string) => {
    setRegion(code);
    const url = new URL(window.location.href);
    if (code) url.searchParams.set("region", code);
    else url.searchParams.delete("region");
    window.history.replaceState(window.history.state, "", url);
    setLoading(true);
    try {
      const res = await fetch(tableUrl(code));
      if (res.ok) setData(await res.json());
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!live) return;

    const poll = async () => {
      const res = await fetch(tableUrl(region));
      if (res.ok) setData(await res.json());
      // Kirmagan yoki qatnashmagan foydalanuvchida 404 — bu xato emas.
      setMe(
        await getJson<Standing>(`/contests/${slug}/standings/me/`).catch(
          () => null,
        ),
      );
    };

    void poll();
    const timer = setInterval(poll, 15_000);
    return () => clearInterval(timer);
    // `tableUrl` reads only `slug` and `region`.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [slug, live, region]);

  // Insiders take part unrated; a reader may hide them (ADR-0055, part 2).
  const [showInsiders, setShowInsiders] = useState(true);
  const hasInsiders = data.results.some((row) => row.insider_role);
  const rows = showInsiders
    ? data.results
    : data.results.filter((row) => !row.insider_role);

  const regional = data.region !== "";
  // One's own row comes from the full table: in a regional view it would
  // stand among people of another region.
  const meShown =
    !regional && me !== null && !data.results.some((row) => row.username === me.username);
  const place = (row: Standing, value: number | null) =>
    row.is_disqualified ? "DQ" : row.insider_role ? "*" : String(value ?? "");
  const tsv = rows
    .map((row) =>
      [
        ...(regional ? [place(row, row.region_rank)] : []),
        place(row, row.rank),
        row.username,
        row.solved_count,
        row.penalty,
      ].join("\t"),
    )
    .join("\n");
  const columns = 4 + (hacks ? 1 : 0) + (regional ? 1 : 0);
  const regionOptions = [
    { value: "", label: t(locale, "standings.allRegions") },
    ...data.regions.map((entry) => ({
      value: entry.code,
      label: regionName(entry.code, locale),
      trailing: <span className="tabular-nums rw-faint">{entry.count}</span>,
    })),
  ];

  return (
    <>
      {data.frozen && (
        <div className="mb-4 rw-radius-sm rw-warn-soft px-3 py-2 text-theme-sm rw-warn-ink">
          {t(locale, "standings.frozen")}
        </div>
      )}
      <div className="flex flex-wrap items-center justify-end gap-3 border-b rw-divider px-3 py-2">
        {(data.regions.length > 0 || regional) && (
          <div className="mr-auto w-56" data-region-filter="">
            <Dropdown
              size="sm"
              hideLabel
              label={t(locale, "standings.region")}
              value={region}
              options={regionOptions}
              onChange={(code) => void chooseRegion(code)}
              loading={loading}
            />
          </div>
        )}
        {hasInsiders && (
          <Checkbox
            checked={showInsiders}
            onChange={(event) => setShowInsiders(event.target.checked)}
            data-show-insiders=""
          >
            {t(locale, "standings.showInsiders")}
          </Checkbox>
        )}
        <CopyButton text={tsv} shape="label" size="sm" label={t(locale, "problem.copy")} />
      </div>
      {/* `<table>` va `<tbody>` saqlanadi — E2E shu selektorlarga tayanadi. */}
      <Table>
        <THead>
          {regional && <TH>{t(locale, "standings.regionPlace")}</TH>}
          <TH>{t(locale, regional ? "standings.overallPlace" : "standings.rank")}</TH>
          <TH>{t(locale, "standings.user")}</TH>
          <TH align="right">{t(locale, "standings.solved")}</TH>
          {hacks && <TH align="right">{t(locale, "standings.hacks")}</TH>}
          <TH align="right">{t(locale, "standings.penalty")}</TH>
        </THead>
        <TBody>
          {rows.map((row) => (
            <TR key={row.username}>
              {regional && <PlaceCell row={row} locale={locale} regional />}
              <PlaceCell row={row} locale={locale} />
              <TD>
                <UserName username={row.username} title={row.user_title} locale={locale} />
                <InsiderBadge row={row} locale={locale} />
              </TD>
              <TD align="right">{row.solved_count}</TD>
              {hacks && <HackCell row={row} />}
              <TD align="right" className="rw-faint">
                {row.penalty}
              </TD>
            </TR>
          ))}
          {meShown && me && (
            <TR key={me.username}>
              <PlaceCell row={me} locale={locale} mine />
              <TD className="rw-accent-ink">
                {me.username}{" "}
                <span className="rw-dim-2">· {t(locale, "standings.you")}</span>
                <InsiderBadge row={me} locale={locale} />
              </TD>
              <TD align="right">{me.solved_count}</TD>
              {hacks && <HackCell row={me} />}
              <TD align="right" className="rw-faint">
                {me.penalty}
              </TD>
            </TR>
          )}
          {rows.length === 0 && !meShown && (
            <EmptyRow colSpan={columns}>
              {t(locale, regional ? "standings.regionEmpty" : "common.empty")}
            </EmptyRow>
          )}
        </TBody>
      </Table>
    </>
  );
}
