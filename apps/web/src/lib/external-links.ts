import type { ExternalProfile } from "@/lib/api";

/** Tashqi va ijtimoiy havolalar — profil kartasi va «Shaxsiy» tabi bitta manbadan. */
export const EXTERNAL_LABEL: Record<string, string> = {
  codeforces: "Codeforces",
  atcoder: "AtCoder",
  leetcode: "LeetCode",
  linkedin: "LinkedIn",
  telegram: "Telegram",
  github: "GitHub",
  instagram: "Instagram",
  x: "X",
  youtube: "YouTube",
  kaggle: "Kaggle",
  blog: "Blog",
};

export const hostOf = (url: string) => {
  try {
    return new URL(url).hostname;
  } catch {
    return url;
  }
};

export function externalUrl(row: ExternalProfile): string {
  const handle = encodeURIComponent(row.handle);
  switch (row.kind) {
    case "codeforces":
      return `https://codeforces.com/profile/${handle}`;
    case "atcoder":
      return `https://atcoder.jp/users/${handle}`;
    case "leetcode":
      return `https://leetcode.com/u/${handle}/`;
    case "telegram":
      return `https://t.me/${handle}`;
    case "github":
      return `https://github.com/${handle}`;
    case "instagram":
      return `https://instagram.com/${handle}`;
    case "x":
      return `https://x.com/${handle}`;
    case "youtube":
      return `https://youtube.com/@${handle}`;
    case "kaggle":
      return `https://www.kaggle.com/${handle}`;
    default:
      return row.handle;
  }
}

/** Ko'rsatiladigan qism: havola turlarida domen, qolganlarida taxallus. */
export const externalShown = (row: ExternalProfile) =>
  row.kind === "blog" || row.kind === "linkedin" ? hostOf(row.handle) : row.handle;
