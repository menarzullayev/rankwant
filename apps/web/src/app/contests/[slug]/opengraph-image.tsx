import { ImageResponse } from "next/og";

import { t } from "@/i18n/messages";
import { getLocale } from "@/i18n/server";
import { api } from "@/lib/api";

export const alt = "RankWant musobaqasi";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

/** Sanani qo'lda formatlaydi.
 *
 *  `Intl` ATAYLAB ishlatilmaydi: edge runtime'da uning ma'lumotlari
 *  to'liq bo'lmasligi mumkin va natija muhitga qarab o'zgarib ketardi.
 */
function sana(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "";
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${pad(d.getUTCDate())}.${pad(d.getUTCMonth() + 1)}.${d.getUTCFullYear()}`;
}

/** Musobaqa havolasi ulashilganda chiqadigan karta.
 *
 *  Musobaqa e'lonlari Telegram'da tarqaladi, ya'ni karta «bu nima va
 *  qachon» degan savolga darhol javob berishi kerak — aks holda odam
 *  havolani ochmaydi.
 */
export default async function OgImage({ params }: { params: Promise<{ slug: string }> }) {
  const locale = await getLocale();
  const slug = decodeURIComponent((await params).slug);
  const contest = await api.contest(slug).catch(() => null);

  const title = contest?.title ?? slug;
  const holat = !contest
    ? ""
    : contest.is_running
      ? t(locale, "contest.running")
      : contest.is_finished
        ? t(locale, "contests.finished")
        : t(locale, "contest.notStarted");
  const holatRangi = !contest
    ? "#8f7bff"
    : contest.is_running
      ? "#4ade80"
      : contest.is_finished
        ? "#94a3b8"
        : "#8f7bff";
  const davr = contest ? `${sana(contest.start_at)} — ${sana(contest.end_at)}` : "";

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          padding: 64,
          background: "linear-gradient(135deg, #0b1026 0%, #1c2350 60%, #3a2d6b 100%)",
          color: "#ffffff",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
          <div style={{ fontSize: 34, fontWeight: 700, opacity: 0.9 }}>RankWant</div>
          <div style={{ fontSize: 28, opacity: 0.5 }}>{t(locale, "nav.contests")}</div>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 26 }}>
          {holat && (
            <div
              style={{
                display: "flex",
                alignSelf: "flex-start",
                fontSize: 26,
                padding: "6px 22px",
                borderRadius: 999,
                background: "rgba(255, 255, 255, 0.12)",
                color: holatRangi,
              }}
            >
              {holat}
            </div>
          )}
          <div style={{ fontSize: 68, fontWeight: 700, lineHeight: 1.15 }}>
            {title.length > 58 ? `${title.slice(0, 57)}…` : title}
          </div>
          {davr && <div style={{ fontSize: 32, opacity: 0.75 }}>{davr}</div>}
        </div>

        <div style={{ display: "flex", gap: 40, fontSize: 28, opacity: 0.7 }}>
          {contest && contest.problems.length > 0 && (
            <div style={{ display: "flex" }}>{contest.problems.length} masala</div>
          )}
          {contest?.is_rated && <div style={{ display: "flex" }}>Reytingli</div>}
          {!contest && <div style={{ display: "flex" }}>rankwant.uz</div>}
        </div>
      </div>
    ),
    size,
  );
}
