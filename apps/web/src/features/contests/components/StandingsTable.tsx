"use client";

import { useEffect, useState } from "react";

import { CopyAllBar } from "@/components/kit/CopyControl";
import { UserName } from "@/components/ui/Identity";
import { API_BASE, getJson, type Standing } from "@/lib/api";
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

type Payload = { frozen: boolean; results: Standing[] };

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
  initial: Payload;
  live: boolean;
  locale: Locale;
  /** Hack ustuni ko'rsatilsinmi (ADR-0020). Hack yoqilmagan musobaqada
   *  u har qatorda nol turadigan ortiqcha ustun bo'lardi. */
  hacks?: boolean;
}) {
  const [data, setData] = useState<Payload>(initial);
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
  useEffect(() => {
    if (!live) return;

    const poll = async () => {
      const res = await fetch(`${API_BASE}/contests/${slug}/standings/`);
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
  }, [slug, live]);

  const meShown =
    me !== null && !data.results.some((row) => row.username === me.username);
  const tsv = data.results
    .map((row) => `${row.rank}\t${row.username}\t${row.solved_count}\t${row.penalty}`)
    .join("\n");

  return (
    <>
      {data.frozen && (
        <div className="mb-4 rw-radius-sm rw-warn-soft px-3 py-2 text-theme-sm rw-warn-ink">
          {t(locale, "standings.frozen")}
        </div>
      )}
      <CopyAllBar text={tsv} label={t(locale, "problem.copy")} />
      {/* `<table>` va `<tbody>` saqlanadi — E2E shu selektorlarga tayanadi. */}
      <Table>
        <THead>
          <TH>{t(locale, "standings.rank")}</TH>
          <TH>{t(locale, "standings.user")}</TH>
          <TH align="right">{t(locale, "standings.solved")}</TH>
          {hacks && <TH align="right">{t(locale, "standings.hacks")}</TH>}
          <TH align="right">{t(locale, "standings.penalty")}</TH>
        </THead>
        <TBody>
          {data.results.map((row) => (
            <TR key={row.username}>
              <TD className="font-semibold rw-strong">{row.rank}</TD>
              <TD>
                <UserName username={row.username} title={row.user_title} locale={locale} />
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
              <TD className="font-semibold rw-accent-ink">{me.rank}</TD>
              <TD className="rw-accent-ink">
                {me.username}{" "}
                <span className="rw-dim-2">· {t(locale, "standings.you")}</span>
              </TD>
              <TD align="right">{me.solved_count}</TD>
              {hacks && <HackCell row={me} />}
              <TD align="right" className="rw-faint">
                {me.penalty}
              </TD>
            </TR>
          )}
          {data.results.length === 0 && !meShown && (
            <EmptyRow colSpan={hacks ? 5 : 4}>{t(locale, "common.empty")}</EmptyRow>
          )}
        </TBody>
      </Table>
    </>
  );
}
