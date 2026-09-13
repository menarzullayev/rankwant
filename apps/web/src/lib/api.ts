/** RankWant API mijozi.
 *
 * SSR da server tomonda chaqiriladi — session cookie uzatiladi
 * (ADR-0008: birinchi tomon web uchun cookie, PAT emas).
 */

/**
 * Brauzer va server bir xil manzildan foydalana olmaydi: brauzer host'dagi
 * `localhost:8000` ni ko'radi, konteyner ichidagi SSR esa u yerda hech
 * nima topmaydi (ECONNREFUSED). Shuning uchun server tomon uchun alohida
 * ichki manzil — sozlanmasa, ommaviy manzilga qaytadi.
 */
export const API_BASE =
  (typeof window === "undefined"
    ? process.env.API_BASE_INTERNAL || process.env.NEXT_PUBLIC_API_BASE
    : process.env.NEXT_PUBLIC_API_BASE) ?? "http://localhost:8000/api/v1";

export type Paginated<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

export type Problem = {
  /** Ommaviy raqam — `#0431`. Qoralamada `null`. */
  code: number | null;
  is_solved: boolean;
  is_favourite: boolean;
  rating: { average: number | null; count: number };
  has_editorial: boolean;
  /** Oxirgi urinishim verdikti — hech urinmaganda `null`. */
  my_verdict: string | null;
  /** Masala sahifasi ochilishi soni. */
  view_count: number;
  /** Yechilgan / urinilgan, foizda. Urinish bo'lmasa `null`. */
  success_rate: number | null;
  /** Judge tekshira oladimi. Import qilingan masalalarning bir qismida
   * hali test yo'q va ularga yuborish qabul qilinmaydi. */
  has_tests: boolean;
  slug: string;
  title: string;
  difficulty: number;
  level: string;
  level_label: string;
  topics: string[];
  solved_count: number;
  attempt_count: number;
};

export type Sample = { order: number; input: string; expected: string };

/** Masalada ruxsat etilgan til — limitlari allaqachon hisoblangan. */
export type ProblemLanguage = {
  code: string;
  name: string;
  version: string;
  time_limit_ms: number;
  memory_limit_kb: number;
  code_template: string;
};

export type SimilarProblem = {
  slug: string;
  title: string;
  difficulty: number;
  level: string;
  level_label: string;
  score: number;
};

export type Attachment = { name: string; url: string; size_bytes: number };

/** ADR-0013: `access` tahlil qaysi asosda ochilganini aytadi. */
export type EditorialState = {
  available: boolean;
  access: "anonymous" | "locked" | "free" | "solved" | "purchased" | "staff";
  price: number;
};

export type ProblemDetail = Problem & {
  samples: Sample[];
  statement: string;
  input_format: string;
  output_format: string;
  note: string;
  /** Ochilmagan bo'lsa serverdan bo'sh keladi — yashirin matn yo'q. */
  editorial: string;
  editorial_state: EditorialState;
  /** `has_profile` — nofaol import mualliflarining profil sahifasi yo'q. */
  author: {
    username: string;
    display_name: string;
    has_profile: boolean;
  } | null;
  rating: { average: number | null; count: number };
  my_rating: number | null;
  is_favourite: boolean;
  statement_locale: string;
  time_limit_ms: number;
  memory_limit_kb: number;
  checker_type: string;
  languages: ProblemLanguage[];
  similar: SimilarProblem[];
  attachments: Attachment[];
  votes: { up: number; down: number; mine: number };
  image: string;
  partial_scoring: boolean;
  /** Import qilingan arxivning xom reytingi (KEP 100–2400). */
  source_rating: number | null;
  source: string;
  source_url: string;
};

export type Contest = {
  slug: string;
  title: string;
  start_at: string;
  end_at: string;
  scoring_type: string;
  is_rated: boolean;
  is_running: boolean;
  is_finished: boolean;
  is_frozen: boolean;
};

export type ContestProblem = {
  index_letter: string;
  slug: string;
  title: string;
  points: number;
};

export type ContestDetail = Contest & {
  description: string;
  problems: ContestProblem[];
};

export type Standing = {
  rank: number;
  username: string;
  user_title: UserTitle | null;
  solved_count: number;
  penalty: number;
  last_ac_at: string | null;
};

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

export type PlatformStats = {
  users: number;
  problems: number;
  contests: number;
  attempts: number;
  statement_locales: string[];
};

export type Wallet = {
  balance: number;
  earned_today: number;
  remaining_today: number;
};

export type Quest = {
  code: string;
  type: "daily" | "weekly" | "achievement";
  title_uz: string;
  reward: number;
  done: boolean;
};

/** Haftalik marafon — har foydalanuvchiga o'z to'plami (PRD P1-9). */
export type Marathon = {
  week: string;
  reward: number;
  completed: boolean;
  solved_count: number;
  total: number;
  problems: (Problem & { marathon_solved: boolean })[];
};

export type Notification = {
  id: number;
  kind: string;
  title: string;
  body: string;
  is_read: boolean;
  created_at: string;
};

export type Post = {
  slug: string;
  kind: string;
  title: string;
  summary: string;
  author: string | null;
  published_at: string;
};

export type PostDetail = Post & { body: string };

export type Recommendation = {
  target_difficulty: number;
  results: Problem[];
};

export type Article = {
  slug: string;
  kind: "article" | "algorithm";
  title: string;
  summary: string;
  difficulty: number;
  topics: string[];
  reading_minutes: number;
  problem_count: number;
};

export type LinkedProblem = {
  slug: string;
  title: string;
  difficulty: number;
  role: string;
};

export type ArticleDetail = Article & {
  body: string;
  author: string | null;
  problems: LinkedProblem[];
};

export type ProblemStats = {
  total: number;
  verdicts: { verdict: string; count: number }[];
  languages: { language: string; count: number; solved: number }[];
  /** Har til uchun eng tez AC. Tillar aralashtirilmaydi. */
  fastest: {
    language: string;
    username: string;
    time_ms: number;
    memory_kb: number;
    created_at: string;
  }[];
};

/** Mavzu kesimidagi kuch. `stuck` — urinilgan, lekin yechilmagan. */
export type TopicSkill = {
  slug: string;
  label: string;
  total: number;
  solved: number;
  stuck: number;
  rating: number;
};

export type Solver = {
  username: string;
  rating_skills: number;
  language: string;
  time_ms: number;
  memory_kb: number;
  /** Yuborilgan manba uzunligi, belgi. */
  code_length: number;
  /** AC gacha bo'lgan urinishlar soni. */
  attempts: number;
  solved_at: string;
};

export type ArchiveProgress = {
  levels: { code: string; label: string; total: number; solved: number }[];
  total: number;
  solved: number;
};

export type Roadmap = {
  slug: string;
  title: string;
  description: string;
  step_count: number;
  /** Traektoriyaning nechta masalasi yechilgan (mehmonda 0). */
  solved_steps: number;
};

/** Urinishlar ro'yxatidagi filtrlar — KEP dagi kabi.
 *
 * `[so'rov qiymati, yorliq kaliti]`. So'rov qiymati vergulli bo'lishi
 * mumkin: `RE` ikkiga ajratilgandan keyin bitta «Bajarilishda xato»
 * filtri eski qatorlarni ham, yangi `RE_SIGNAL`/`RE_EXIT` ni ham
 * topishi kerak. Yorliq esa `verdict.<KOD>` orqali tarjima qilinadi. */
export const VERDICT_FILTERS = [
  ["AC", "verdict.AC"],
  ["WA", "verdict.WA"],
  ["PE", "verdict.PE"],
  ["TLE", "verdict.TLE"],
  ["MLE", "verdict.MLE"],
  ["RE,RE_SIGNAL,RE_EXIT", "verdict.RE"],
  ["CE", "verdict.CE"],
] as const;

export type Attempt = {
  id: number;
  username: string;
  user_title: UserTitle | null;
  problem: string;
  language: string;
  verdict: string;
  score: number;
  time_ms: number;
  memory_kb: number;
  failed_test_index: number | null;
  created_at: string;
  judged_at: string | null;
  /** Yuborilgan manba uzunligi, belgi. Kodning o'zi emas. */
  source_size: number;
};

export type Topic = {
  slug: string;
  name_uz: string;
  name_ru: string;
  name_en: string;
  parent: string | null;
};

export type Language = { code: string; name: string; version: string };

export type TestResult = {
  index: number;
  verdict: string;
  time_ms: number;
  memory_kb: number;
};

/** `source_code` va `compile_output` faqat urinish egasiga va xodimga
 * qaytariladi (backend IDOR himoyasi), shuning uchun ixtiyoriy. */
export type AttemptDetail = Attempt & {
  source_code?: string;
  compile_output?: string;
  test_results: TestResult[];
};

export type CustomRun = {
  id: number;
  language: string;
  verdict: string;
  stdout: string;
  compile_output: string;
  time_ms: number;
  memory_kb: number;
  created_at: string;
  judged_at: string | null;
};

export type Choice = { id: number; order: number; text: string };
export type Question = {
  id: number;
  text: string;
  difficulty: number;
  topics: string[];
  choices: Choice[];
};
export type Quiz = {
  slug: string;
  title: string;
  description: string;
  reward_qvant: number;
  question_count: number;
  best_score: number | null;
  created_at: string;
};
export type QuizDetail = Quiz & { questions: Question[] };
export type QuizResult = {
  id: number;
  score: number;
  total: number;
  qvant_awarded: number;
  review: {
    question_id: number;
    chosen: number | null;
    correct: number | null;
    is_correct: boolean;
    explanation: string;
  }[];
};

export type Arena = {
  slug: string;
  title: string;
  description: string;
  start_at: string;
  end_at: string;
  seconds_per_question: number;
  question_count: number;
  participant_count: number;
  reward_qvant: number;
  is_running: boolean;
  is_finished: boolean;
};
export type ArenaDetail = Arena & {
  current_index: number | null;
  joined: boolean;
};
export type ArenaCurrent = {
  index: number;
  deadline: string;
  seconds_per_question: number;
  question: Question;
  answered: boolean;
};
export type ArenaStanding = {
  rank: number;
  username: string;
  display_name: string;
  score: number;
  correct_count: number;
  total_ms: number;
};

export type Duel = {
  slug: string;
  title: string;
  status: "open" | "accepted" | "finished" | "cancelled";
  challenger: string;
  opponent: string | null;
  problem_count: number;
  difficulty: number;
  duration_minutes: number;
  start_at: string;
  end_at: string;
  is_running: boolean;
  winner: string | null;
  challenger_solved: number;
  opponent_solved: number;
  is_draw: boolean;
  problems: {
    order: number;
    slug: string;
    title: string;
    difficulty: number;
  }[];
  created_at: string;
};
export type DuelRecord = { wins: number; draws: number; losses: number };

export type Tournament = {
  slug: string;
  title: string;
  description: string;
  start_at: string;
  end_at: string;
  stage_count: number;
  is_running: boolean;
  is_finished: boolean;
};
export type TournamentStage = {
  order: number;
  title: string;
  contest: string;
  contest_title: string;
  start_at: string;
  end_at: string;
  weight: number;
  is_finished: boolean;
};
export type TournamentDetail = Tournament & { stages: TournamentStage[] };
export type TournamentStanding = {
  rank: number;
  username: string;
  display_name: string;
  points: number;
  solved_total: number;
  stages_played: number;
};

export type Hackathon = {
  slug: string;
  title: string;
  description: string;
  start_at: string;
  submission_deadline: string;
  end_at: string;
  submission_count: number;
  accepts_submissions: boolean;
  is_finished: boolean;
};
export type HackathonSubmission = {
  id: number;
  username: string;
  team_name: string;
  title: string;
  description: string;
  repo_url: string;
  demo_url: string;
  submitted_at: string;
  score: number | null;
  feedback: string;
};

export type CalendarEvent = {
  kind: "contest" | "arena" | "tournament" | "hackathon" | "duel";
  slug: string;
  title: string;
  start_at: string;
  end_at: string;
  is_rated?: boolean;
  submission_deadline?: string;
};

export type SearchResult = {
  q: string;
  problems: { slug: string; title: string; difficulty: number }[];
  users: { username: string; display_name: string; rating_skills: number }[];
  articles: { slug: string; title: string; kind: string }[];
  contests: { slug: string; title: string; start_at: string }[];
};

export type Classroom = {
  slug: string;
  name: string;
  description: string;
  owner: string;
  member_count: number;
  created_at: string;
};
export type ClassroomDetail = Classroom & {
  join_code?: string;
  is_active?: boolean;
  members?: {
    username: string;
    role: string;
    rating_skills: number;
    joined_at: string;
  }[];
};
export type Assignment = {
  id: number;
  title: string;
  description: string;
  problems: string[];
  due_at: string | null;
  created_at: string;
};

export type ShopItem = {
  code: string;
  category: string;
  title_uz: string;
  price: number;
  is_consumable: boolean;
  owned: boolean;
};

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
  | "social";

export type ThemeEffect = "none" | "fade" | "circle";

export type UiPrefs = { style?: string; sound?: boolean; effect?: ThemeEffect };

/** Tur bo'yicha kanal tanlovi — `{"duel": {"site": true, "telegram": false}}`. */
export type NotifyPrefs = Record<string, { site?: boolean; telegram?: boolean }>;

/** `/me/` — faqat egasiga qaytadigan to'liq yozuv. */
export type Me = {
  id: number;
  is_staff: boolean;
  username: string;
  email: string;
  display_name: string;
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

export type SkillName = {
  slug: string;
  name_uz: string;
  name_ru: string;
  name_en: string;
};

export type MySkill = {
  skill: string;
  name_uz: string;
  name_ru: string;
  name_en: string;
  level: number;
};

export type Technology = { slug: string; name: string };

export type Education = {
  organization: string;
  degree: string;
  start_year: number | null;
  end_year: number | null;
};

export type WorkRow = {
  company: string;
  title: string;
  start_year: number | null;
  end_year: number | null;
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
  info: Partial<Record<PrivacyField | "region" | "district" | "city" | "school_id", string>>;
  hidden_fields: PrivacyField[];
  is_owner: boolean;
  skills: (SkillName & { level: number })[];
  technologies: Technology[];
  educations: Education[];
  work: WorkRow[];
  external: ExternalProfile[];
  followers: number;
  following: number;
  /** Mehmon va egasining o'zi uchun `null`. */
  is_following: boolean | null;
  cosmetics: Cosmetics;
  title: UserTitle | null;
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

export type Purchase = {
  code: string;
  category: string;
  title_uz: string;
  title_ru: string;
  title_en: string;
  purchased_at: string;
  is_equipped: boolean;
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

export type TitleBand = {
  code: string;
  level: number;
  min: number;
  max: number | null;
};

export type UserTitle = { code: string; level: number };

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

/** `Retry-After` sarlavhasini soniyaga aylantiradi (15-qaror).
 *
 *  Sarlavha ikki shaklda bo'ladi: soniya (`"42"`) yoki HTTP-sana.
 *  DRF soniya qo'yadi, lekin oraliq proksi ham qo'shishi mumkin — shu
 *  sababli ikkalasi ham o'qiladi. O'qib bo'lmasa `0`: matn umumiy
 *  qoladi va taymer ko'rsatilmaydi, ya'ni noto'g'ri raqam va'da
 *  qilinmaydi. */
function retryAfterOf(res: Response): number {
  const raw = res.headers.get("Retry-After");
  if (!raw) return 0;
  const seconds = Number(raw);
  if (Number.isFinite(seconds) && seconds > 0) return Math.ceil(seconds);
  const at = Date.parse(raw);
  if (Number.isNaN(at)) return 0;
  return Math.max(0, Math.ceil((at - Date.now()) / 1000));
}

class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly code: string,
    message: string,
    /** Maydon xatolari — `{"email": ["Bu email band"]}`. */
    readonly details: Record<string, unknown> = {},
    /** 429 da server aytgan kutish soniyalari (15-qaror).
     *
     *  `Retry-After` sarlavhasidan: DRF uni o'zi qo'yadi va qancha
     *  kutishni ANIQ aytadi. Sarlavha bo'lmasa `0` — matn umumiy
     *  qoladi va taymer ko'rinmaydi. O'lchandi: ilgari bu qiymat
     *  umuman o'qilmasdi va odam «juda tez-tez» degan xabarni ko'rib,
     *  qancha kutishni bilmasdan qayta bosardi. */
    readonly retryAfter: number = 0,
  ) {
    super(message);
  }

  /**
   * Foydalanuvchiga ko'rsatiladigan matn.
   *
   * API maydon xatosida umumiy «Kiritilgan ma'lumot noto'g'ri» qaytaradi,
   * haqiqiy sabab esa `details` da qoladi — o'lchandi: band username
   * bilan ro'yxatdan o'tganda foydalanuvchi qaysi maydon xato ekanini
   * umuman bilmasdi.
   */
  get text(): string {
    const first = Object.values(this.details)[0];
    if (Array.isArray(first) && typeof first[0] === "string") return first[0];
    if (typeof first === "string") return first;
    return this.message;
  }

  /**
   * Bitta maydonning xatosi, yo'q bo'lsa `null`.
   *
   * NEGA KERAK (14-qaror): DRF maydon xatolarida `code` HAR DOIM
   * `"invalid"` bo'ladi — `{"error":{"code":"invalid","details":{"email":
   * ["Bu email band"]}}}`. Ya'ni «band email» ni kod bo'yicha ajratib
   * bo'lmaydi; yagona ishonchli belgi — `details` kaliti. `text` esa
   * BIRINCHI maydonni oladi, tartib esa DRF'ga bog'liq.
   */
  field(name: string): string | null {
    const value = this.details[name];
    if (Array.isArray(value) && typeof value[0] === "string") return value[0];
    if (typeof value === "string") return value;
    return null;
  }
}

async function get<T>(path: string, revalidate = 30): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    next: { revalidate },
    headers: { Accept: "application/json" },
  });
  if (!res.ok) {
    let code = "error";
    let message = res.statusText;
    try {
      const body = await res.json();
      code = body?.error?.code ?? code;
      message = body?.error?.message ?? message;
    } catch {
      /* javob JSON emas */
    }
    throw new ApiError(res.status, code, message, {}, retryAfterOf(res));
  }
  return (await res.json()) as T;
}

/**
 * Brauzerdan sessiya bilan yuboriladigan so'rov — POST, PUT, PATCH, DELETE.
 *
 * `credentials: "include"` shart: sessiya cookie'si boshqa origin'da
 * (API alohida portda), CORS esa `allow-credentials` qaytaradi (ADR-0008).
 * `FormData` yuborilsa `Content-Type` qo'yilmaydi — chegarani (boundary)
 * brauzer o'zi yozadi, qo'lda yozilgani esa faylni buzardi.
 */
async function send<T>(method: string, path: string, body?: unknown): Promise<T> {
  const headers: Record<string, string> = { Accept: "application/json" };
  // Sessiya bilan yuborilgan so'rovda DRF CSRF token talab qiladi. Anonim
  // login/register da cookie hali yo'q — o'shanda sarlavha ham kerak emas.
  const csrf = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/)?.[1];
  if (csrf) headers["X-CSRFToken"] = decodeURIComponent(csrf);
  const form = body instanceof FormData;
  if (body !== undefined && !form) headers["Content-Type"] = "application/json";

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    credentials: "include",
    headers,
    body: body === undefined ? undefined : form ? body : JSON.stringify(body),
  });
  const raw = await res.text();
  const parsed = raw ? JSON.parse(raw) : null;
  if (!res.ok) {
    throw new ApiError(
      res.status,
      parsed?.error?.code ?? "error",
      parsed?.error?.message ?? res.statusText,
      parsed?.error?.details ?? {},
      retryAfterOf(res),
    );
  }
  return parsed as T;
}

export const postJson = <T>(path: string, body: unknown) =>
  send<T>("POST", path, body);

/** Butun ro'yxatni almashtirish — ko'nikma, ta'lim, tashqi profil. */
export const putJson = <T>(path: string, body: unknown) =>
  send<T>("PUT", path, body);

export const patchJson = <T>(path: string, body: unknown) =>
  send<T>("PATCH", path, body);

export const deleteJson = <T>(path: string, body?: unknown) =>
  send<T>("DELETE", path, body);

/** Fayl yuklash — avatar. */
export const postForm = <T>(path: string, form: FormData) =>
  send<T>("POST", path, form);

/** Brauzerdan sessiya bilan GET — shaxsiy ma'lumot (sinf, duel masalalari). */
export async function getJson<T>(
  path: string,
  /** `signal` — yozayotgandagi tekshiruvda eskirgan so'rovni bekor qilish
   *  uchun: javoblar tartibsiz kelib, oxirgisi eskisi bo'lib qolmasin. */
  init?: { signal?: AbortSignal },
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    headers: { Accept: "application/json" },
    cache: "no-store",
    signal: init?.signal,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new ApiError(
      res.status,
      body?.error?.code ?? "error",
      body?.error?.message ?? res.statusText,
      body?.error?.details ?? {},
      retryAfterOf(res),
    );
  }
  return (await res.json()) as T;
}

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

/** Submit. Javob `PENDING` bilan qaytadi — verdikt keyin pollinglanadi. */
export function submitAttempt(body: {
  problem: string;
  language: string;
  source_code: string;
  contest?: string;
}): Promise<Attempt> {
  return postJson<Attempt>("/attempts/", body);
}

export const fetchAttempt = (id: number) =>
  getJson<AttemptDetail>(`/attempts/${id}/`);

export const fetchProblemAttempts = (slug: string, username?: string) =>
  getJson<Paginated<Attempt>>(
    `/attempts/?problem=${encodeURIComponent(slug)}` +
      (username ? `&username=${encodeURIComponent(username)}` : ""),
  );

/** PRD P0-4 — o'z kiritmasi bilan sinash. Urinish tarixiga tushmaydi. */
export function runCustomTest(body: {
  language: string;
  source_code: string;
  stdin: string;
}): Promise<CustomRun> {
  return postJson<CustomRun>("/custom-test/", body);
}

export const fetchCustomRun = (id: number) =>
  getJson<CustomRun>(`/custom-test/${id}/`);

export const setFavourite = (slug: string, on: boolean) =>
  on
    ? postJson<{ is_favourite: boolean }>(`/problems/${slug}/favourite/`, {})
    : deleteJson<{ is_favourite: boolean }>(`/problems/${slug}/favourite/`);

export const REPORT_REASONS = [
  ["statement", "Matnda xato"],
  ["tests", "Testlar noto'g'ri"],
  ["translation", "Tarjima xato"],
  ["duplicate", "Takroriy masala"],
  ["other", "Boshqa"],
] as const;

export const reportProblem = (slug: string, reason: string, comment: string) =>
  postJson<{ reported: boolean }>(`/problems/${slug}/report/`, {
    reason,
    comment,
  });

export const voteProblem = (slug: string, value: -1 | 0 | 1) =>
  postJson<{ up: number; down: number; mine: number }>(
    `/problems/${slug}/vote/`,
    {
      value,
    },
  );

export const unlockEditorial = (slug: string) =>
  postJson<{ editorial: string; price: number }>(
    `/problems/${slug}/editorial/`,
    {},
  );

export const rateProblem = (slug: string, score: number) =>
  postJson<{ average: number | null; count: number; my_rating: number }>(
    `/problems/${slug}/rate/`,
    { score },
  );

export const api = {
  // Mehmon bosh sahifasi raqamlari — serverda 60 s keshlanadi.
  stats: () => get<PlatformStats>("/stats/", 60),
  problems: (query = "") => get<Paginated<Problem>>(`/problems/${query}`),
  problem: (slug: string) => get<ProblemDetail>(`/problems/${slug}/`),
  contests: () => get<Paginated<Contest>>("/contests/"),
  contest: (slug: string) => get<ContestDetail>(`/contests/${slug}/`),
  // Standings tez o'zgaradi — kesh qisqa
  standings: (slug: string) =>
    get<{ frozen: boolean; results: Standing[] }>(
      `/contests/${slug}/standings/`,
      5,
    ),
  leaderboard: (school?: string) =>
    get<Paginated<UserPublic>>(
      `/users/?ordering=-rating_skills${school ? `&school=${school}` : ""}`,
    ),
  school: (id: string) => get<School>(`/schools/${id}/`),
  /** Maktab katalogi — nom bo'yicha qidiruv, viloyat/tuman bo'yicha filtr.
   *  Katalog moderator to'ldiradi (ADR-0017), ya'ni bu ro'yxat to'liq emas:
   *  topilmagan maktab erkin matn bo'lib qoladi. */
  schools: (params: { q?: string; region?: string; district?: string } = {}) => {
    const query = new URLSearchParams();
    if (params.q) query.set("q", params.q);
    if (params.region) query.set("region", params.region);
    if (params.district) query.set("district", params.district);
    return get<Paginated<School>>(`/schools/${query.size ? `?${query}` : ""}`);
  },
  user: (username: string) => get<UserPublic>(`/users/${username}/`),
  // Qvant — Phase 1. Balans va questlar shaxsiy, kesh yo'q.
  wallet: () => get<Wallet>("/qvant/wallet/", 0),
  quests: () => get<Quest[]>("/qvant/quests/", 0),
  marathon: () => get<Marathon>("/qvant/marathon/", 0),
  // Sitemap uchun — faqat slug kerak, lekin ro'yxat endpointi to'liq
  // yozuvni beradi. Soatiga bir marta chaqiriladi (app/sitemap.ts).
  problemSlugs: (page: number) =>
    get<Paginated<{ slug: string }>>(
      `/problems/?page=${page}&page_size=100`,
      3600,
    ),
  contestSlugs: (page: number) =>
    get<Paginated<{ slug: string }>>(
      `/contests/?page=${page}&page_size=100`,
      3600,
    ),
  articleSlugs: (page: number) =>
    get<Paginated<{ slug: string }>>(
      `/articles/?page=${page}&page_size=100`,
      3600,
    ),
  postSlugs: (page: number) =>
    get<Paginated<{ slug: string }>>(
      `/posts/?page=${page}&page_size=100`,
      3600,
    ),
  shop: () => get<ShopItem[]>("/qvant/shop/", 30),
  // Bildirishnomalar shaxsiy va tez o'zgaradi — keshlanmaydi
  notifications: () => get<Paginated<Notification>>("/notifications/", 0),
  recommendations: () => get<Recommendation>("/problems/recommendation/", 0),
  posts: () => get<Paginated<Post>>("/posts/"),
  post: (slug: string) => get<PostDetail>(`/posts/${slug}/`),
  // O'z o'qish kontenti — ADR-0005 differensiatori. SEO uchun keshlanadi.
  articles: () => get<Paginated<Article>>("/articles/", 300),
  article: (slug: string) => get<ArticleDetail>(`/articles/${slug}/`, 300),
  roadmaps: () => get<Roadmap[]>("/roadmaps/", 300),
  // Progress foydalanuvchiga xos — SSR da `getWithSession` bilan olinadi.
  progress: () => get<ArchiveProgress>("/problems/progress/", 0),
  problemSolvers: (slug: string, ordering = "first") =>
    get<{ count: number; results: Solver[] }>(
      `/problems/${slug}/solvers/?ordering=${ordering}`,
    ),
  problemStats: (slug: string) =>
    get<ProblemStats>(`/problems/${slug}/stats/`, 30),
  /** Masalaning barcha urinishlari — ochiq. Manba begonaga ko'rinmaydi
   * (backend uni faqat egasiga qaytaradi). */
  problemAttempts: (slug: string, query = "") =>
    get<Paginated<Attempt>>(
      `/attempts/?problem=${encodeURIComponent(slug)}${query ? `&${query}` : ""}`,
      0,
    ),
  attempts: () => get<Paginated<Attempt>>("/attempts/", 0),
  // Tillar deyarli o'zgarmaydi — judge obrazi bilan bir manbadan (ADR-0004).
  languages: () => get<Paginated<Language>>("/languages/", 300),
  // Filtr paneli mavzularni TO'LIQ ko'rsatishi kerak — birinchi 25 tasi
  // emas, aks holda tanlab bo'lmaydigan yorliqlar paydo bo'lardi.
  topics: () => get<Paginated<Topic>>("/topics/?page_size=100", 300),
  topicSkills: () => get<{ topics: TopicSkill[] }>("/problems/skills/"),
  quizzes: () => get<Paginated<Quiz>>("/quizzes/", 60),
  quiz: (slug: string) => get<QuizDetail>(`/quizzes/${slug}/`, 60),
  arenas: () => get<Paginated<Arena>>("/arena/", 10),
  arena: (slug: string) => get<ArenaDetail>(`/arena/${slug}/`, 0),
  arenaStandings: (slug: string) =>
    get<{ results: ArenaStanding[] }>(`/arena/${slug}/standings/`, 0),
  duels: () => get<Paginated<Duel>>("/duels/", 0),
  duel: (slug: string) => get<Duel>(`/duels/${slug}/`, 0),
  tournaments: () => get<Paginated<Tournament>>("/tournaments/", 60),
  tournament: (slug: string) =>
    get<TournamentDetail>(`/tournaments/${slug}/`, 60),
  tournamentStandings: (slug: string) =>
    get<{ results: TournamentStanding[] }>(
      `/tournaments/${slug}/standings/`,
      30,
    ),
  hackathons: () => get<Paginated<Hackathon>>("/hackathons/", 60),
  hackathon: (slug: string) => get<Hackathon>(`/hackathons/${slug}/`, 60),
  hackathonSubmissions: (slug: string) =>
    get<{ results: HackathonSubmission[] }>(
      `/hackathons/${slug}/submissions/`,
      0,
    ),
  calendar: () => get<{ results: CalendarEvent[] }>("/calendar/", 60),
  algorithms: () => get<Paginated<Article>>("/articles/?kind=algorithm", 300),
  ratingHistory: (username: string) =>
    get<Paginated<RatingChange>>(`/users/${username}/rating-history/`, 30),
  solved: (username: string) =>
    get<Paginated<SolvedProblem>>(`/users/${username}/solved/`, 30),
  // Profil statistikasi — backend foydalanuvchi bo'yicha keshlaydi.
  userStats: (username: string) =>
    get<UserStats>(`/users/${username}/stats/`, 30),
  userCalendar: (username: string, year?: number) =>
    get<Calendar>(
      `/users/${username}/calendar/${year ? `?year=${year}` : ""}`,
      30,
    ),
  problemMap: (username: string) =>
    get<{ problems: ProblemTile[] }>(`/users/${username}/problem-map/`, 30),
  ratingSeries: (username: string) =>
    get<RatingSeries>(`/users/${username}/rating-series/`, 30),
  userTopics: (username: string) =>
    get<{ topics: TopicStrength[] }>(`/users/${username}/topics/`, 60),
  userContests: (username: string, query = "") =>
    get<Paginated<ContestRow>>(`/users/${username}/contests/${query}`, 0),
  solvedPage: (username: string, query = "") =>
    get<Paginated<SolvedProblem>>(`/users/${username}/solved/${query}`, 0),
  attemptsQuery: (query: string) =>
    get<Paginated<Attempt>>(`/attempts/${query}`, 0),
};

export { ApiError };
