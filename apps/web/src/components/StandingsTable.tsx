"use client";

import { useEffect, useState } from "react";
import { API_BASE, type Standing } from "@/lib/api";
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

/** Standings jadvali.
 *
 * Jonli yangilanish SSE orqali (04-prd: WebSocket EMAS). Ba'zi maktab va
 * korporativ proxy'lar SSE ni buferlaydi — shuning uchun POLLING FALLBACK
 * majburiy (test-strategy § compatibility).
 */
export function StandingsTable({
  slug,
  initial,
  live,
  locale,
}: {
  slug: string;
  initial: Payload;
  live: boolean;
  locale: Locale;
}) {
  const [data, setData] = useState<Payload>(initial);

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
    };

    const timer = setInterval(poll, 15_000);
    return () => clearInterval(timer);
  }, [slug, live]);

  return (
    <>
      {data.frozen && (
        <div className="mb-4 rw-radius-sm rw-warn-soft px-3 py-2 text-theme-sm rw-warn-ink">
          {t(locale, "standings.frozen")}
        </div>
      )}
      {/* `<table>` va `<tbody>` saqlanadi — E2E shu selektorlarga tayanadi. */}
      <Table>
        <THead>
          <TH>{t(locale, "standings.rank")}</TH>
          <TH>{t(locale, "standings.user")}</TH>
          <TH align="right">{t(locale, "standings.solved")}</TH>
          <TH align="right">{t(locale, "standings.penalty")}</TH>
        </THead>
        <TBody>
          {data.results.map((row) => (
            <TR key={row.username}>
              <TD className="font-semibold rw-strong">{row.rank}</TD>
              <TD>{row.username}</TD>
              <TD align="right">{row.solved_count}</TD>
              <TD align="right" className="rw-faint">
                {row.penalty}
              </TD>
            </TR>
          ))}
          {data.results.length === 0 && (
            <EmptyRow colSpan={4}>{t(locale, "empty")}</EmptyRow>
          )}
        </TBody>
      </Table>
    </>
  );
}
