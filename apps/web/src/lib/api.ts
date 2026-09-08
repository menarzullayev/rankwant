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
  solved_count: number;
  penalty: number;
  last_ac_at: string | null;
};

export type UserPublic = {
  username: string;
  display_name: string;
  avatar_url: string;
  bio: string;
  rating_skills: number;
  rating_contest: number;
  /** Phase 1 da yoqildi — ADR-0006 fazali ochilish */
  rating_activity: number;
  /** Phase 3 — duel qurilgach ochildi */
  rating_challenges: number;
  /** Faqat /me/ da keladi */
  is_staff?: boolean;
  streak_count: number;
  date_joined: string;
};

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
  title: string;
  difficulty: number;
  difficulty_at_solve: number;
  first_ac_at: string;
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
  solvers: {
    username: string;
    language: string;
    time_ms: number;
    memory_kb: number;
    created_at: string;
  }[];
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

export type Attempt = {
  id: number;
  username: string;
  problem: string;
  language: string;
  verdict: string;
  score: number;
  time_ms: number;
  memory_kb: number;
  failed_test_index: number | null;
  created_at: string;
  judged_at: string | null;
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

class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly code: string,
    message: string,
  ) {
    super(message);
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
    throw new ApiError(res.status, code, message);
  }
  return (await res.json()) as T;
}

/**
 * Brauzerdan yuboriladigan POST — auth uchun.
 *
 * `credentials: "include"` shart: sessiya cookie'si boshqa origin'da
 * (API alohida portda), CORS esa `allow-credentials` qaytaradi (ADR-0008).
 * Anonim login/register uchun DRF CSRF talab qilmaydi.
 */
export async function postJson<T>(path: string, body: unknown): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Accept: "application/json",
  };
  // Sessiya bilan yuborilgan POST da DRF CSRF token talab qiladi. Anonim
  // login/register da cookie hali yo'q — o'shanda sarlavha ham kerak emas.
  const csrf = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/)?.[1];
  if (csrf) headers["X-CSRFToken"] = decodeURIComponent(csrf);

  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    credentials: "include",
    headers,
    body: JSON.stringify(body),
  });
  const raw = await res.text();
  const parsed = raw ? JSON.parse(raw) : null;
  if (!res.ok) {
    throw new ApiError(
      res.status,
      parsed?.error?.code ?? "error",
      parsed?.error?.message ?? res.statusText,
    );
  }
  return parsed as T;
}

/** Brauzerdan sessiya bilan DELETE — `postJson` bilan bir xil CSRF talabi. */
export async function deleteJson<T>(path: string): Promise<T> {
  const headers: Record<string, string> = { Accept: "application/json" };
  const csrf = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/)?.[1];
  if (csrf) headers["X-CSRFToken"] = decodeURIComponent(csrf);

  const res = await fetch(`${API_BASE}${path}`, {
    method: "DELETE",
    credentials: "include",
    headers,
  });
  const raw = await res.text();
  const parsed = raw ? JSON.parse(raw) : null;
  if (!res.ok) {
    throw new ApiError(
      res.status,
      parsed?.error?.code ?? "error",
      parsed?.error?.message ?? res.statusText,
    );
  }
  return parsed as T;
}

/** Brauzerdan sessiya bilan GET — shaxsiy ma'lumot (sinf, duel masalalari). */
export async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    headers: { Accept: "application/json" },
    cache: "no-store",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new ApiError(
      res.status,
      body?.error?.code ?? "error",
      body?.error?.message ?? res.statusText,
    );
  }
  return (await res.json()) as T;
}

/** Joriy sessiya — brauzerda. Kirmagan bo'lsa `null`. */
export async function fetchMe(): Promise<UserPublic | null> {
  const res = await fetch(`${API_BASE}/me/`, {
    credentials: "include",
    headers: { Accept: "application/json" },
    cache: "no-store",
  });
  return res.ok ? ((await res.json()) as UserPublic) : null;
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
  leaderboard: () =>
    get<Paginated<UserPublic>>("/users/?ordering=-rating_skills"),
  user: (username: string) => get<UserPublic>(`/users/${username}/`),
  // Qvant — Phase 1. Balans va questlar shaxsiy, kesh yo'q.
  wallet: () => get<Wallet>("/qvant/wallet/", 0),
  quests: () => get<Quest[]>("/qvant/quests/", 0),
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
  problemStats: (slug: string) =>
    get<ProblemStats>(`/problems/${slug}/stats/`, 30),
  /** Masalaning barcha urinishlari — ochiq. Manba begonaga ko'rinmaydi
   * (backend uni faqat egasiga qaytaradi). */
  problemAttempts: (slug: string, cursor = "") =>
    get<Paginated<Attempt>>(
      `/attempts/?problem=${encodeURIComponent(slug)}${cursor ? `&cursor=${encodeURIComponent(cursor)}` : ""}`,
      0,
    ),
  attempts: () => get<Paginated<Attempt>>("/attempts/", 0),
  // Tillar deyarli o'zgarmaydi — judge obrazi bilan bir manbadan (ADR-0004).
  languages: () => get<Paginated<Language>>("/languages/", 300),
  // Filtr paneli mavzularni TO'LIQ ko'rsatishi kerak — birinchi 25 tasi
  // emas, aks holda tanlab bo'lmaydigan yorliqlar paydo bo'lardi.
  topics: () => get<Paginated<Topic>>("/topics/?page_size=100", 300),
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
};

export { ApiError };
