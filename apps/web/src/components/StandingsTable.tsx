"use client";

import { useEffect, useState } from "react";
import { API_BASE, type Standing } from "@/lib/api";
import { type Locale, t } from "@/i18n/messages";

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

  useEffect(() => {
    if (!live) return;

    let source: EventSource | null = null;
    let pollTimer: ReturnType<typeof setInterval> | null = null;
    let sawEvent = false;

    const poll = async () => {
      const res = await fetch(`${API_BASE}/contests/${slug}/standings/`);
      if (res.ok) setData(await res.json());
    };

    const startPolling = () => {
      if (pollTimer) return;
      pollTimer = setInterval(poll, 15_000);
    };

    try {
      source = new EventSource(`${API_BASE}/contests/${slug}/standings/stream/`);
      source.addEventListener("standings", (event) => {
        sawEvent = true;
        setData(JSON.parse((event as MessageEvent).data));
      });
      source.onerror = () => {
        source?.close();
        startPolling();
      };
      // Proxy oqimni buferlayotgan bo'lsa hodisa kelmaydi — 20 s dan keyin
      // polling'ga o'tamiz.
      setTimeout(() => {
        if (!sawEvent) startPolling();
      }, 20_000);
    } catch {
      startPolling();
    }

    return () => {
      source?.close();
      if (pollTimer) clearInterval(pollTimer);
    };
  }, [slug, live]);

  return (
    <>
      {data.frozen && (
        <p className="mb-2 text-sm" style={{ color: "var(--accent)" }}>
          {t(locale, "standings.frozen")}
        </p>
      )}
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left" style={{ color: "var(--muted)" }}>
            <th className="pb-2">{t(locale, "standings.rank")}</th>
            <th className="pb-2">{t(locale, "standings.user")}</th>
            <th className="pb-2 text-right">{t(locale, "standings.solved")}</th>
            <th className="pb-2 text-right">{t(locale, "standings.penalty")}</th>
          </tr>
        </thead>
        <tbody>
          {data.results.map((row) => (
            <tr
              key={row.username}
              className="border-t"
              style={{ borderColor: "var(--border)" }}
            >
              <td className="py-2">{row.rank}</td>
              <td className="py-2">{row.username}</td>
              <td className="py-2 text-right">{row.solved_count}</td>
              <td className="py-2 text-right" style={{ color: "var(--muted)" }}>
                {row.penalty}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {data.results.length === 0 && (
        <p style={{ color: "var(--muted)" }}>{t(locale, "empty")}</p>
      )}
    </>
  );
}
