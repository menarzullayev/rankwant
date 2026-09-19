/** The signed-in user: session, settings and preferences, auth providers. */

// Navigatsiya tiplari — yagona manba `nav-config.ts`. Shu yerda qayta
// yozilsa, ikkisi vaqt o'tib ajralib ketardi (va `check_hardcoded.py`
// ularni qattiq yozilgan matn deb topardi).
import type { NavMode, NavShape } from "@/layout/nav-config";
import type { VerdictVariant } from "@/lib/theme/verdict";
import type { StatusVariant } from "@/lib/theme/status";
import type { LoadingVariant } from "@/lib/theme/loading";
import type { IconPackId } from "@/lib/theme/icon-packs";
import { API_BASE, getJson } from "./client";

/** Profilda yashirish mumkin bo'lgan maydonlar (`core.models.PRIVACY_FIELDS`). */
export type PrivacyField =
  | "email"
  | "birth_date"
  | "country"
  | "school"
  | "grade"
  | "website"
  | "online"
  | "coach"
  | "social"
  /** Profil banneri — yuklangan rasm, shuning uchun yashirilishi mumkin (ADR-0026). */
  | "title_photo";

export type ThemeEffect = "none" | "fade" | "circle";

/** Ko'rinish guruhi — sxema v2 (D33).
 *
 *  ⚠️ `theme` bu yerda YO'Q: mavzu `User.theme` maydonida saqlanadi.
 *  Uni bu yerga ham qo'shish bir xil ma'noni ikki joyda saqlardi. */
/** Karta uslubi (D54) — `globals.css` dagi `[data-card]` bloklari. */
export type CardStyle = "default" | "outline" | "flat" | "soft" | "square";

/** Fon naqshi (D55) — `globals.css` dagi `[data-pattern]` bloklari. */
export type BgPattern = "none" | "grid" | "dots" | "diagonal" | "mesh";

export type AppearancePrefs = {
  style?: string;
  /** TUS sifatida saqlanadi, tayyor rang emas (D42) — yorqinlik har muhit
   *  uchun alohida hisoblanadi. `null` — uslubning o'z rangi. */
  accent?: { hue: number; sat: number } | null;
  /** `null` — uslubning o'z shrifti (D14). */
  font?: string | null;
  /** Sarlavhalar uchun alohida shrift (D53). `null` — matn shrifti bilan
   *  bir xil. Shrift juftligi — tipografikaning asosiy usuli: serif
   *  sarlavha + sans matn kabi. */
  fontHeading?: string | null;
  /** Ildiz shrift o'lchami foizi — 75…150 (D45). 100 = odatiy. */
  size?: number;
  /** Tipografik shkala zichligi — 0.90…1.15 (D45). 1 = odatiy. */
  scale?: number;
  /** Qator balandligi ko'paytirgichi — 0.9…1.4 (D47). 1 = uslubning o'zi. */
  lineHeight?: number;
  /** Harf oralig'i qo'shimchasi, `em` — −0.02…0.06 (D47). */
  tracking?: number;
  /** Kontent kengligi, `px` — 1000…1800 (D48). */
  width?: number;
  density?: "compact" | "comfortable" | "spacious";
  /** Navigatsiya joylashuvi (D46) — `nav-config.ts` dagi `NavMode`. */
  navMode?: NavMode;
  /** Yuqori panel shakli (D46) — `nav-config.ts` dagi `NavShape`. */
  navShape?: NavShape;
  /** Karta uslubi (D54): chegara · soya · burchak. */
  card?: CardStyle;
  /** Fon naqshi (D55). `none` — tekis fon. */
  pattern?: BgPattern;
  /** Judge natijasi ko'rinishi (D57). `auto` — ekranga qarab. */
  verdictStyle?: VerdictVariant;
  /** Holat xabari ko'rinishi (D60). `auto` — ekranga qarab. */
  statusStyle?: StatusVariant;
  /** Yuklanish ko'rinishi (D62). */
  loadingStyle?: LoadingVariant;
  /** Ikonka to'plami (D10/D11). Qamrov: `nav`/`action`/`status`
   *  o'zgaradi, `verdict`/`brand` qat'iy (D20 ①). */
  iconPack?: IconPackId;
};

export type A11yPrefs = {
  /** `protan` protanopiya VA deuteranopiya uchun (D44). */
  vision?: "normal" | "protan" | "tritan";
  /** Harakat darajasi (D49). `system` — OS ga ergashadi, `full` — hammasi,
   *  `mild` — o'tishlar qoladi, dekorativ effektlar o'chadi, `off` — hech narsa. */
  motion?: "system" | "full" | "mild" | "off";
  bigTargets?: boolean;
  strongFocus?: boolean;
};

export type ThemeTemplate = {
  name: string;
  appearance: AppearancePrefs;
  a11y: A11yPrefs;
  /** Theme mode captured with the template. Templates saved before it
   *  existed have none, and applying them keeps the current mode. */
  theme?: "light" | "dark" | "system";
};

/** `User.ui_prefs` — v2, guruhlangan va versiyalangan (D33).
 *
 *  `sound`/`effect` yuqorida qoldi: ular ko'rinish emas, qaytarish
 *  aloqasi — guruhga ko'chirish eski klientni buzardi. */
export type UiPrefs = {
  version?: number;
  appearance?: AppearancePrefs;
  /** Kuchli rejim (D9) — UI flag bilan O'CHIQ (D43). */
  tokens?: Record<string, string>;
  a11y?: A11yPrefs;
  templates?: ThemeTemplate[];
  /** Problemset toggles that follow the account (ADR-0024). */
  problemset?: { hideTags?: boolean; hideSolved?: boolean };
  sound?: boolean;
  effect?: ThemeEffect;
};

/** `User.ShirtSize` — olympiad prizes (ADR-0024). */
export type ShirtSize = "XS" | "S" | "M" | "L" | "XL" | "XXL" | "3XL";

/** Tur bo'yicha kanal tanlovi — `{"duel": {"site": true, "telegram": false}}`. */
export type NotifyPrefs = Record<string, { site?: boolean; telegram?: boolean }>;

/** `/me/` — faqat egasiga qaytadigan to'liq yozuv. */
export type Me = {
  id: number;
  is_staff: boolean;
  username: string;
  email: string;
  display_name: string;
  /** Real name for certificates and olympiad lists; never public (ADR-0024). */
  first_name: string;
  last_name: string;
  email_verified: boolean;
  social: string[];
  has_password: boolean;
  avatar_url: string;
  bio: string;
  locale: string;
  theme: string;
  country: string;
  region: string;
  district: string;
  city: string;
  school_ref: number | null;
  /** Katalogdagi maktab nomi — `school_ref` bo'lsa. */
  school_name: string;
  school: string;
  grade: string;
  website: string;
  birth_date: string | null;
  /** Aloqa uchun telefon. IXTIYORIY va ommaviy profilga chiqmaydi —
   *  faqat hisobni tiklash va bildirishnomalar uchun. */
  phone: string;
  /** Owner-only, like `phone`. */
  shirt_size: ShirtSize | "";
  hidden_fields: PrivacyField[];
  ui_prefs: UiPrefs;
  notify_prefs: NotifyPrefs;
  /** `free_at` bo'sh — bepul almashtirish hozir mavjud. */
  username_change: { free_at: string | null; price: number };
  rating_skills: number;
  rating_contest: number;
  rating_activity: number;
  streak_count: number;
  streak_freeze_until: string | null;
  date_joined: string;
};

export type SessionRow = {
  id: number;
  user_agent: string;
  ip: string | null;
  created_at: string;
  last_seen: string;
  current: boolean;
};

export type MySkill = {
  skill: string;
  name_uz: string;
  name_ru: string;
  name_en: string;
  level: number;
};

export type AuthProviders = {
  providers: string[];
  telegram_bot: string;
  /** Turnstile SAYT kaliti (9-qaror). Bo'sh satr — sozlanmagan, ya'ni
   *  frontend vidjetni yuklamaydi va server tekshiruvi ham o'chiq. */
  turnstile_site_key: string;
};

/** Sozlangan ijtimoiy provayderlar — SERVER komponentidan chaqiriladi.
 *
 * Ro'yxat brauzerda emas, serverda olinadi va tugmalar HTML ga qo'shilib
 * keladi. Sabab o'lchandi: brauzerda olinganda so'rov yiqilsa yoki JS
 * umuman ishga tushmasa (iPhone'da shunday bo'ldi) foydalanuvchi hech
 * qanday xabarsiz BARCHA ijtimoiy kirish yo'llarini yo'qotardi.
 * Google va GitHub tugmasi — oddiy havola, ularga JS umuman kerak emas.
 */
export async function fetchProviders(): Promise<AuthProviders> {
  try {
    return await getJson<AuthProviders>("/auth/providers/");
  } catch {
    return { providers: [], telegram_bot: "", turnstile_site_key: "" };
  }
}

/** Joriy sessiya — brauzerda. Kirmagan bo'lsa `null`. */
export async function fetchMe(): Promise<Me | null> {
  const res = await fetch(`${API_BASE}/me/`, {
    credentials: "include",
    headers: { Accept: "application/json" },
    cache: "no-store",
  });
  return res.ok ? ((await res.json()) as Me) : null;
}
