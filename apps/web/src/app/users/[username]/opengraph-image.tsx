import { ImageResponse } from "next/og";

import { DEFAULT_LOCALE, t } from "@/i18n/messages";
import { api } from "@/lib/api";
import { SITE_URL } from "@/lib/site";

export const alt = "RankWant";

/** Unvon ranglari to'q fonda — `globals.css` dagi dashboard.dark palitrasi.
 *  16 ta pog'onaning palitra-dizayner tomonidan ko'tarilgan hexlari
 *  (ADR-0027 § L2: 1-3 grey, 4-5 green, 6-7 cyan, 8 blue, 9 violet, 10-11 orange,
 *  12-16 red). */
const RANK_ON_DARK = [
  "#8b94a4", "#8b94a4", "#8b94a4",                                  // 1 quark, 2 atom, 3 molecule
  "#28a95e", "#28a95e",                                            // 4 droplet, 5 meteorite
  "#16a2b1", "#16a2b1",                                            // 6 comet, 7 moon
  "#6093eb",                                                       // 8 planet
  "#a681e7",                                                       // 9 star
  "#e9710f", "#e9710f",                                            // 10 supernova, 11 pulsar
  "#ea6d69", "#ea6d69", "#ea6d69", "#ea6d69", "#ea6d69",          // 12..16 magnetar/cosmos
];
/** Nutella marker ink on the OG card. Dark surface, white ink. */
const NUTELLA_INK_DARK = "#ffffff";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

/** Havola ulashilganda chiqadigan karta: rasm, ism, reytinglar, yechilganlar.
 *
 *  Rasm faqat PNG yoki JPEG bo'lsa qo'yiladi: karta chizuvchi (Satori)
 *  WebP ni o'qiy olmaydi, brauzerda qirqilgan avatar esa ko'pincha WebP. */
export default async function OgImage({ params }: { params: Promise<{ username: string }> }) {
  const username = decodeURIComponent((await params).username);
  const [user, stats] = await Promise.all([
    api.user(username).catch(() => null),
    api.userStats(username).catch(() => null),
  ]);
  const name = user ? user.display_name || user.username : username;
  const title = user?.title ?? null;
  const avatar = user?.avatar_url && /\.(png|jpg)$/.test(user.avatar_url) ? user.avatar_url : null;
  const numbers: [string, number | string][] = user
    ? [
        ["Skills", user.rating_skills],
        ["Contests", user.rating_contest],
        [t(DEFAULT_LOCALE, "leaderboard.activity"), user.rating_activity],
        [t(DEFAULT_LOCALE, "profile.solvedTitle"), stats ? `${stats.solved} / ${stats.total}` : "—"],
      ]
    : [];

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
        <div style={{ display: "flex", alignItems: "center", gap: 32 }}>
          {avatar ? (
            // `next/image` bu yerda ishlamaydi: u brauzer optimizatsiyasi
            // (lazy load, srcset) qiladi, bu esa satori orqali SERVERDA
            // rasmga aylantiriladi. `<img>` — yagona to'g'ri variant.
            // eslint-disable-next-line @next/next/no-img-element
            <img src={avatar} width={160} height={160} alt="" style={{ borderRadius: 80 }} />
          ) : (
            <div
              style={{
                width: 160,
                height: 160,
                borderRadius: 80,
                background: "#6d5dfc",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 80,
                fontWeight: 700,
              }}
            >
              {name.charAt(0).toUpperCase()}
            </div>
          )}
          <div style={{ display: "flex", flexDirection: "column" }}>
            <div style={{ fontSize: 64, fontWeight: 700 }}>{name}</div>
            <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
              <div style={{ fontSize: 32, opacity: 0.8 }}>{`@${username}`}</div>
              {title && (() => {
                const text = t(DEFAULT_LOCALE, `title.${title.code}`);
                const head = text.slice(0, title.marker);
                const rest = text.slice(title.marker);
                return (
                  <div
                    style={{
                      display: "flex",
                      fontSize: 26,
                      fontWeight: 600,
                      padding: "2px 16px",
                      borderRadius: 999,
                      border: `2px solid ${RANK_ON_DARK[title.level - 1]}`,
                      color: RANK_ON_DARK[title.level - 1],
                    }}
                  >
                    {head.length > 0 && (
                      <span style={{ color: NUTELLA_INK_DARK }}>{head}</span>
                    )}
                    {rest}
                  </div>
                );
              })()}
            </div>
          </div>
        </div>
        <div style={{ display: "flex", gap: 24 }}>
          {numbers.map(([label, value]) => (
            <div
              key={label}
              style={{
                display: "flex",
                flexDirection: "column",
                padding: "20px 28px",
                borderRadius: 20,
                background: "rgba(255, 255, 255, 0.1)",
              }}
            >
              <div style={{ fontSize: 26, opacity: 0.75 }}>{label}</div>
              <div style={{ fontSize: 48, fontWeight: 700 }}>{String(value)}</div>
            </div>
          ))}
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", fontSize: 28, opacity: 0.85 }}>
          <div>RankWant</div>
          <div>{new URL(SITE_URL).host}</div>
        </div>
      </div>
    ),
    size,
  );
}
