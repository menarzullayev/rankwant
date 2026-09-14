import { ImageResponse } from "next/og";

import { DEFAULT_LOCALE, t } from "@/i18n/messages";
import { api } from "@/lib/api";

export const alt = "RankWant masalasi";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

/** Masala havolasi ulashilganda chiqadigan karta.
 *
 *  Nega statik brend rasmi yetmaydi: Telegram'da eng ko'p ulashiladigan
 *  sahifa — aynan masala. Bir xil karta o'rniga raqam, nom va qiyinlik
 *  ko'rinadi, ya'ni havola nima haqidaligini oldindan aytadi.
 *
 *  Fon `users/[username]` kartasi bilan bir oilada (to'q gradient) —
 *  ikki xil uslub bir lentada yonma-yon tursa sayt yig'ilmagandek
 *  ko'rinardi.
 */
export default async function OgImage({ params }: { params: Promise<{ slug: string }> }) {
  const slug = decodeURIComponent((await params).slug);
  // Xato bo'lsa karta BARIBIR chiziladi: sabab tarmoq yoki vaqtinchalik
  // nosozlik bo'lishi mumkin, ulashilgan havola esa rasmsiz qolmasligi
  // kerak — zaxira matn har doim bor.
  const problem = await api.problem(slug).catch(() => null);

  const code = problem?.code ? `#${String(problem.code).padStart(4, "0")}` : "Masala";
  const title = problem?.title ?? slug;
  const level = problem?.level_label ?? "";
  const topics = (problem?.topics ?? []).slice(0, 4);

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
          <div style={{ fontSize: 28, opacity: 0.5 }}>{t(DEFAULT_LOCALE, "nav.problems")}</div>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 24 }}>
            <div style={{ fontSize: 40, fontWeight: 700, color: "#8f7bff" }}>{code}</div>
            {level && (
              <div
                style={{
                  display: "flex",
                  fontSize: 26,
                  padding: "6px 20px",
                  borderRadius: 999,
                  background: "rgba(143, 123, 255, 0.22)",
                  color: "#cfc4ff",
                }}
              >
                {level}
              </div>
            )}
          </div>
          <div style={{ fontSize: 68, fontWeight: 700, lineHeight: 1.15 }}>
            {title.length > 64 ? `${title.slice(0, 63)}…` : title}
          </div>
          {topics.length > 0 && (
            <div style={{ display: "flex", gap: 14 }}>
              {topics.map((topic) => (
                <div
                  key={topic}
                  style={{
                    display: "flex",
                    fontSize: 24,
                    padding: "6px 18px",
                    borderRadius: 10,
                    background: "rgba(255, 255, 255, 0.1)",
                    opacity: 0.85,
                  }}
                >
                  {topic}
                </div>
              ))}
            </div>
          )}
        </div>

        <div style={{ display: "flex", fontSize: 28, opacity: 0.6 }}>
          {/* `ImageResponse` is a module-level export: it has no request
              scope, so it cannot await the locale. This counter keeps the
              unit word in Uzbek; the fallback beside it is the brand. The
              same limitation is recorded for `alt=` at the top of this
              file. */}
          {problem?.solved_count ? `${problem.solved_count} yechilgan` : "rankwant.uz"}
        </div>
      </div>
    ),
    size,
  );
}
