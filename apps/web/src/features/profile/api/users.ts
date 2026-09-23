/** Public users: profiles, ratings, statistics, achievements, schools. */

import type { PrivacyField } from "@/features/account";
import type { TitleBand, UserTitle } from "@/lib/identity";

export type UserPublic = {
  username: string;
  display_name: string;
  avatar_url: string;
  bio: string;
  /** ISO 3166-1 alpha-2 — bayroq uchun. Yashirilgan bo'lsa bo'sh satr
   *  (reyting jadvali ommaviy, ya'ni `hidden_fields` hisobga olinadi). */
  country: string;
  /** Unvon — Contests reytingidan; reytingli musobaqasiz `null` (ADR-0018). */
  title: UserTitle | null;
  /** Eng yuqori pog'ona — `max_rating_contest` bo'yicha, `title` bilan bir
   *  xil guard (ADR-0027). `cf_max_title` dan farqi: bu RankWant zinapoyasi. */
  max_title: UserTitle | null;
  /** Manbadagi daraja nomi (`newbie`…`legendary grandmaster`, ADR-0026).
   *  `title` dan ALOHIDA tizim: `title` RankWant'da HISOBLANADI, bu esa
   *  tashqi profildan KELADI. Ikkalasi ham ko'rsatilishi mumkin. */
  cf_title: string;
  /** Manbadagi eng yuqori daraja. Bo'sh satr — ma'lumot yo'q. */
  cf_max_title: string;
  /** Tashqi profildagi do'stlar soni (ADR-0026). */
  friend_count: number;
  /** Profil banneri. `avatar_url` dan farqli — katta fon rasmi.
   *  Yashirilgan bo'lsa bo'sh satr (maxfiylik maydoni). */
  title_photo_url: string;
  rating_skills: number;
  rating_contest: number;
  /** Phase 1 da yoqildi — ADR-0006 fazali ochilish */
  rating_activity: number;
  /** Phase 3 — duel qurilgach ochildi */
  rating_challenges: number;
  /** Faqat /me/ da keladi */
  is_staff?: boolean;
  /** Faqat /me/ da keladi — profil kartasidagi uchta yutuq. */
  pinned_achievements?: string[];
  /** Faqat /me/ da keladi — boshqa odamning pochtasi tasdiqlanganini
   *  ko'rsatish kerak emas, shuning uchun ommaviy profilda yo'q. */
  email_verified?: boolean;
  /** Faqat /me/ da keladi — ommaviy profilda pochta ko'rsatilmaydi. */
  email?: string;
  /** Faqat /me/ da keladi — ulangan provayderlar. */
  social?: string[];
  streak_count: number;
  /** Longest streak reached (ADR-0024). */
  streak_max: number;
  /** Problems solved; the leaderboard can sort by it (ADR-0024). */
  solved_count: number;
  date_joined: string;
  /** Reyting bo'yicha o'rin. Ro'yxat javobida bo'sh — faqat profilda. */
  ranks: Partial<Record<RatingKind, number>>;
  /** Erishilgan eng yuqori qiymat. Ro'yxat javobida bo'sh. */
  max_ratings: Partial<Record<RatingKind, number>>;
  /** Daraja kesimida yechilganlar. Ro'yxat javobida bo'sh. */
  solved_by_level: { code: string; label: string; solved: number }[];
};

export type RatingKind = "skills" | "contest" | "activity" | "challenges";

export type RatingChange = {
  rating_type: string;
  value_before: number;
  value_after: number;
  delta: number;
  reason: string;
  ref_type: string;
  ref_id: string;
  seed: number | null;
  rank: number | null;
  created_at: string;
};

export type SolvedProblem = {
  slug: string;
  /** Ommaviy raqam — `#0431`. */
  code: number | null;
  title: string;
  difficulty: number;
  difficulty_at_solve: number;
  first_ac_at: string;
  best_time_ms: number | null;
  best_memory_kb: number | null;
  /** AC olgan tillar kodi — `cpp23`, `py313`. */
  languages: string[];
};

export type SkillName = {
  slug: string;
  name_uz: string;
  name_ru: string;
  name_en: string;
};

export type Technology = { slug: string; name: string };

export type Education = {
  organization: string;
  degree: string;
  start_year: number | null;
  start_month: number | null;
  end_year: number | null;
  end_month: number | null;
  current: boolean;
};

export type WorkRow = {
  company: string;
  title: string;
  start_year: number | null;
  start_month: number | null;
  end_year: number | null;
  end_month: number | null;
  current: boolean;
};

export type SkillBadge = {
  text: string;
  icon: string;
  color: string;
};

export type ExternalKind =
  | "codeforces"
  | "atcoder"
  | "leetcode"
  | "linkedin"
  | "telegram"
  | "github"
  | "instagram"
  | "x"
  | "youtube"
  | "kaggle"
  | "blog";

export type ExternalProfile = {
  kind: ExternalKind;
  handle: string;
  rating: number | null;
  max_rating: number | null;
  rank: string;
};

export type UserMini = {
  username: string;
  display_name: string;
  avatar_url: string;
  title: UserTitle | null;
  /** Eng yuqori pogona - `max_rating_contest` boyicha (ADR-0027). */
  max_title: UserTitle | null;
};

export type TeamRole = "owner" | "member";

export type Team = {
  id: number;
  name: string;
  join_code: string;
  created_at: string;
  members: (UserMini & { role: TeamRole; joined_at: string })[];
  role: TeamRole | null;
};

export type Cosmetics = {
  cover: string | null;
  frame: string | null;
  badge: string | null;
};

/** `/users/<nom>/profile/` — yashirilgan maydonlar begonaga kelmaydi. */
export type PublicProfile = {
  username: string;
  display_name: string;
  avatar_url: string;
  bio: string;
  date_joined: string;
  info: Partial<
    Record<PrivacyField | "region" | "district" | "city" | "school_id", string>
  > & { websites?: string[] };
  hidden_fields: PrivacyField[];
  is_owner: boolean;
  skills: (SkillName & { level: number })[];
  technologies: Technology[];
  badges: SkillBadge[];
  educations: Education[];
  work: WorkRow[];
  external: ExternalProfile[];
  followers: number;
  following: number;
  /** Mehmon va egasining o'zi uchun `null`. */
  is_following: boolean | null;
  cosmetics: Cosmetics;
  title: UserTitle | null;
  /** Eng yuqori pogona - `max_rating_contest` boyicha (ADR-0027). */
  max_title: UserTitle | null;
  /** Manbadagi daraja (ADR-0026) — `title` dan alohida, hisoblanmaydi. */
  cf_title: string;
  cf_max_title: string;
  friend_count: number;
  /** Banner — `title_photo` maxfiylik maydoni bilan yashiriladi. */
  title_photo_url: string;
  roles: ProfileRole[];
  /** Yashirilgan yoki hech qachon kirmagan — `null`. */
  last_seen: string | null;
  online: boolean;
  pinned: PinnedAchievement[];
  coach: CoachRef[];
};

export type CoachRef = { username: string; display_name: string; title: UserTitle | null };

/** Obunachilar jadvali — maktab va onlayn holat egasining maxfiylik tanlovi bilan. */
export type Follower = UserMini & {
  school: string;
  rating_contest: number;
  last_seen: string | null;
};

export type School = {
  id: number;
  name: string;
  kind: "school" | "lyceum" | "university" | "other";
  region: string;
  district: string;
  city: string;
  members: number;
};

export type CertificateTier = "gold" | "silver" | "bronze" | "top10" | "participant";

export type Certificate = {
  id: string;
  name: string;
  username: string;
  contest: { slug: string; title: string; end_at: string };
  place: number;
  participants: number;
  tier: CertificateTier;
  issued_at: string;
};

export type ProfileRole =
  | { code: "staff" | "author" | "jury" }
  | { code: "champion"; contest: string; contest_title: string };

export type AchievementTier = "bronze" | "silver" | "gold";

export type PinnedAchievement = {
  code: string;
  group: Achievement["group"];
  target: number;
  tier: AchievementTier;
};

export type ActivityEvent =
  | {
      type: "contest";
      at: string;
      ref: string;
      delta: number;
      value_after: number;
      rank: number | null;
    }
  | {
      type: "quest";
      at: string;
      code: string;
      title_uz: string;
      title_ru: string;
      title_en: string;
      awarded: number;
    }
  | {
      type: "hard_solve";
      at: string;
      ref: string;
      title: string;
      difficulty: number;
    };

export type Achievement = {
  code: string;
  group: "solve" | "streak" | "contest" | "profile";
  target: number;
  progress: number;
  done: boolean;
  tier: AchievementTier;
  /** Egalari faol foydalanuvchilarning necha foizi. */
  rarity: number;
  achieved_at: string | null;
  pinned: boolean;
};

export type LevelStat = {
  code: string;
  label: string;
  solved: number;
  total: number;
};

export type LanguageStat = {
  code: string;
  name: string;
  accepted: number;
  errors: number;
};

/** `/users/<nom>/stats/` — yechilgan/jami, daraja kesimi, tillar, verdiktlar. */
export type UserStats = {
  solved: number;
  total: number;
  levels: LevelStat[];
  attempts: number;
  accepted: number;
  languages: LanguageStat[];
  verdicts: { verdict: string; count: number }[];
};

export type CalendarDay = { date: string; attempts: number; solved: number };

export type Calendar = {
  year: number;
  years: number[];
  days: CalendarDay[];
  attempts: number;
  solved: number;
  streak: { current: number; longest: number };
  hidden?: boolean;
};

export type ProblemTile = {
  code: number | null;
  slug: string;
  title: string;
  level: string;
  rate: number | null;
  state: "solved" | "attempted" | "untouched";
};

export type RatingPoint = {
  at: string;
  before: number;
  after: number;
  delta: number;
  reason: string;
  ref: string;
  /** Musobaqa nomi — faqat Contests nuqtalarida. */
  title: string;
  rank: number | null;
};

/** Umumiy identitet tiplari — endi global qatlamda (`lib/identity`),
 *  chunki `contests`, `problems`, `hackathons` ham ishlatadi. */
export type { TitleBand, UserTitle } from "@/lib/identity";

export type RatingSeries = {
  series: Record<RatingKind | "contest", RatingPoint[]>;
  bands: TitleBand[];
  title: UserTitle | null;
};

export type TopicStrength = {
  slug: string;
  label: string;
  name_uz: string;
  name_ru: string;
  name_en: string;
  total: number;
  solved: number;
  stuck: number;
  rating: number;
};

export type ContestRow = {
  slug: string;
  title: string;
  rank: number;
  /** Teng natija oralig'i — `rank_from < rank_to` bo'lsa «33–35». */
  rank_from: number;
  rank_to: number;
  solved: number;
  score: number;
  rating: { before: number | null; after: number | null; delta: number } | null;
  problems: number;
  participants: number;
  start_at: string;
  duration_min: number;
  is_rated: boolean;
  virtual: boolean;
};
