/** Sozlamalar bo'limlari — har biri o'z manzilida (`/settings/<id>`),
 *  ya'ni havolani ulashish yoki orqaga qaytish to'g'ri bo'limni ochadi. */
export const SECTIONS = [
  { id: "profil", key: "settings.nav.profile" },
  { id: "xavfsizlik", key: "settings.nav.security" },
  { id: "malumotlar", key: "settings.nav.info" },
  { id: "ijtimoiy", key: "settings.nav.social" },
  { id: "konikmalar", key: "settings.nav.skills" },
  { id: "karyera", key: "settings.nav.career" },
  { id: "jamoalar", key: "settings.nav.teams" },
  { id: "bildirishnomalar", key: "settings.nav.notifications" },
  { id: "korinish", key: "settings.nav.appearance" },
  { id: "hisob", key: "settings.nav.account" },
] as const;

export type SectionId = (typeof SECTIONS)[number]["id"];

export const isSection = (value: string): value is SectionId =>
  SECTIONS.some((s) => s.id === value);
