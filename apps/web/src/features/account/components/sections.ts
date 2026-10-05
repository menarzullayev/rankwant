import type { MessageKey } from "@/i18n/messages";

/** Settings sections — six, each answering one question (decision of
 *  2026-10-05; there were ten). Every section has its own address
 *  (`/settings/<id>`), and a section with tabs keeps the tab in `?tab=`, so a
 *  shared link or the back button lands on the same view.
 *
 *  `hint` is the line under the name in the navigation: what is inside. */
export const SECTIONS = [
  {
    id: "profil",
    key: "settings.nav.profile",
    hint: "settings.navHint.profile",
    tabs: [],
  },
  {
    id: "ommaviy",
    key: "settings.nav.public",
    hint: "settings.navHint.public",
    tabs: [
      { id: "tashqi", key: "settings.tab.external" },
      { id: "konikmalar", key: "settings.nav.skills" },
      { id: "karyera", key: "settings.nav.career" },
      { id: "jamoalar", key: "settings.nav.teams" },
      { id: "bezaklar", key: "settings.tab.cosmetics" },
    ],
  },
  {
    id: "malumotlar",
    key: "settings.nav.privacy",
    hint: "settings.navHint.privacy",
    tabs: [
      { id: "malumot", key: "settings.nav.info" },
      { id: "maxfiylik", key: "settings.tab.privacy" },
      { id: "manzil", key: "settings.delivery" },
    ],
  },
  {
    id: "xavfsizlik",
    key: "settings.nav.security",
    hint: "settings.navHint.security",
    tabs: [],
  },
  {
    id: "bildirishnomalar",
    key: "settings.nav.notifyLook",
    hint: "settings.navHint.notify",
    tabs: [
      { id: "xabarlar", key: "settings.nav.notifications" },
      { id: "korinish", key: "settings.nav.appearance" },
    ],
  },
  {
    id: "hisob",
    key: "settings.nav.account",
    hint: "settings.navHint.account",
    tabs: [],
  },
] as const satisfies readonly {
  id: string;
  key: MessageKey;
  hint: MessageKey;
  tabs: readonly { id: string; key: MessageKey }[];
}[];

export type SectionId = (typeof SECTIONS)[number]["id"];

export const isSection = (value: string): value is SectionId =>
  SECTIONS.some((s) => s.id === value);

/** The tab a section opens on when the address names none, or one it does
 *  not have. `""` for a section without tabs. */
export function tabOf(section: SectionId, tab: string | undefined): string {
  const tabs: readonly { id: string }[] = SECTIONS.find((s) => s.id === section)?.tabs ?? [];
  return tabs.find((item) => item.id === tab)?.id ?? tabs[0]?.id ?? "";
}

/** Addresses of the ten-section layout. They are in bookmarks, in team
 *  invite links already sent, and in the provider's return URL, so each one
 *  keeps working and lands on the view that replaced it. */
const LEGACY: Record<string, string> = {
  ijtimoiy: "/settings/ommaviy",
  konikmalar: "/settings/ommaviy?tab=konikmalar",
  karyera: "/settings/ommaviy?tab=karyera",
  jamoalar: "/settings/ommaviy?tab=jamoalar",
  korinish: "/settings/bildirishnomalar?tab=korinish",
};

/** Where an old address goes now, with its own query carried along;
 *  `null` when the address is not an old one. */
export function legacyTarget(
  section: string,
  query: Record<string, string | undefined>,
): string | null {
  // Sign-in methods moved to Security, and `?social=` is the provider coming
  // back from linking one.
  const base = section === "ijtimoiy" && query.social ? "/settings/xavfsizlik" : LEGACY[section];
  if (!base) return null;
  const [path, own = ""] = base.split("?");
  const params = new URLSearchParams(own);
  for (const [key, value] of Object.entries(query)) {
    if (value !== undefined && !params.has(key)) params.set(key, value);
  }
  const tail = params.toString();
  return tail ? `${path}?${tail}` : path;
}
